import asyncio
import datetime

import geoip2.database
import time
import utm
from asciimatics.exceptions import StopApplication
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from flag import flag

from dateutil.parser import parse as dt_parse

from src.config import Config
from src.effects.Hit import Hit
from src.effects.Map import Map
from src.utils.coordinates import map_utm_zone_to_term, utm_zone_to_coordinates


class Base:
    def __init__(self, local_data_path=""):
        self.data = []
        self.loading_time_offset = 0
        self.hit_zone = Config.get("hit_zone", False)
        self.enable_emoji = Config["emoji"]
        self.tail_hit = None
        self.frame_timing = 1 / Config["fps"]
        self.raw_interval = Config["elasticsearch"]["interval"]
        self.local_data_cursor = 0
        self.local_chunk_size = 10000
        self.local_chunk_idx = 0
        self.loop = True

        self.geoip_city_reader = geoip2.database.Reader(
            "./data/geoip/GeoLite2-City.mmdb"
        )
        self.geoip_asn_reader = geoip2.database.Reader("./data/geoip/GeoLite2-ASN.mmdb")

        self.local_data_path = local_data_path
        if self.local_data_path:
            self.local_data_file = open(self.local_data_path)
        else:
            self.local_data_file = None

        self._screen = Screen.open()
        self._loop = asyncio.get_event_loop()

    def run(self):
        map_scene = Scene([Map(self._screen)], -1, clear=True)
        scenes = [map_scene]
        self._screen.set_scenes(scenes)

        try:
            self._loop.call_soon(self._update_screen)
            self._loop.call_soon(self.compute_next_scenes)
            self._loop.run_forever()
        finally:
            # Blocking call interrupted by self._loop.stop()
            self._loop.close()
            self._screen.close()

    def get_fresh_data(self):
        raise NotImplemented

    def compute_next_scenes(self):
        self.data = self.get_fresh_data()
        head_hit = None

        if self.tail_hit:  # Fetch the last hit handled by the previous data harvest
            for hit in self.data:
                if self.tail_hit["_id"] == hit["_id"]:
                    head_hit = hit
                    break

            if not head_hit:
                # If the last hit from the last series is not found in the fresh dataset (which can happen if the timing
                # is too short)
                # Then set the first hit of the fresh data set as the oldest hit for this set (aka. head_hit)
                head_hit = self.data[0]

            for hit in self.data:
                if hit["_id"] == head_hit["_id"]:
                    break

                # Trim every hit before the first that have not been seen yet
                self.data.remove(hit)

        self.setup_future_animation_timing()
        data_total_runtime = dt_parse(self.data[-1]["timestamp"]) - dt_parse(
            self.data[0]["timestamp"]
        )
        self.tail_hit = list(self.data)[-1]

        # Start loading new chunks 30 seconds before the last hit is shown
        next_load_delay = data_total_runtime - datetime.timedelta(seconds=30)
        self._loop.call_later(next_load_delay.total_seconds(), self.compute_next_scenes)

    def setup_future_animation_timing(self):
        triggers = []
        # start = time.now()

        earliest = next(iter(self.data))  # Get the first hit
        for hit in self.data:
            earliest_ts = dt_parse(earliest["timestamp"])
            current_ts = dt_parse(hit["timestamp"])

            if current_ts < earliest_ts:
                earliest = hit
        time_offset = dt_parse(earliest["timestamp"])

        for hit in self.data:
            try:
                lat = hit["geoip"]["latitude"]
                lon = hit["geoip"]["longitude"]
            except KeyError:
                # Missing geo info, skipping this one
                continue

            try:
                easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
            except (TypeError, utm.OutOfRangeError):
                continue

            if self.hit_zone:
                start, _ = map_utm_zone_to_term(zone_number, zone_letter)
                x = start[0]
                y = start[1]
            else:
                x, y = utm_zone_to_coordinates(
                    easting, northing, zone_number, zone_letter
                )

            hit_ts = dt_parse(hit["timestamp"])
            trigger_in = (hit_ts - time_offset).total_seconds()
            hitmark = self.qualify(hit, x, y)

            triggers.append((trigger_in, hitmark))

        for trigger_in, hitmark in triggers:
            self._loop.call_later(trigger_in, self._trigger_mark, hitmark)

    def _trigger_mark(self, mark):
        self._screen.current_scene.add_effect(mark)

    def _update_screen(self):
        try:
            self._loop.call_later(self.frame_timing, self._update_screen)

            a = self._loop.time()
            self._screen.draw_next_frame()
            b = self._loop.time()
            if b - a < self.frame_timing:
                # Just in case time has jumped (e.g. time change), ensure we only delay for self.frame_time seconds
                pause = min(self.frame_timing, a + self.frame_timing - b)
                time.sleep(pause)

        except StopApplication:
            exit()

    def qualify(self, hit, x, y):
        hitmark_symbol = None
        visibility_duration = 1 * Config["fps"]  # 1 second

        country_name = hit["geoip"].get("country_name", "N/A")
        city_name = hit["geoip"].get("city_name", "")
        asn = hit["geoip"].get("asn", "N/A")
        as_org = hit["geoip"].get("as_org", "N/A")
        src_ip = hit["src_ip"]

        if self.enable_emoji:
            hitmark_symbol = ""
            if matches := hit["matches"]:
                for emoji, match_cats in Config["matches_emoji"].items():
                    if matches in match_cats:
                        hitmark_symbol += emoji

                for el in ["profile", "action"]:
                    for emoji, names in Config[f"{el}_emoji"].items():
                        if matches in names:
                            hitmark_symbol += emoji

            if ip_rep := hit.get("ip_rep"):
                rep_emojis = ""
                for emoji, reps in Config["reputation_emoji"].items():
                    if ip_rep in reps:
                        rep_emojis += emoji

                src_ip = f"{rep_emojis} {src_ip}"

        if Config.get("emoji") and (country_code3 := hit["geoip"].get("country_code3")):
            country_flag = flag(country_code3)
            country_name = f"{country_flag} {country_name}"

        hitmark = Hit(
            self._screen,
            country_name,
            city_name,
            asn,
            as_org,
            src_ip,
            x,
            y,
            symbol=hitmark_symbol if hitmark_symbol else Hit.symbol,
            explode=True,
            explosion_width=Config["hit_radius"],
            hit_zone=self.hit_zone,
            delete_count=visibility_duration,
        )

        return hitmark
