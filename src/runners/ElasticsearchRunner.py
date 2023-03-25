import asyncio
import json
from uuid import uuid4

import time

import utm
from asciimatics.exceptions import StopApplication
from asciimatics.scene import Scene
from elasticsearch import Elasticsearch

from src.config import Config
from src.const import TIMERANGE_PLACEHOLDER
from src.effects.Map import Map
from src.runners.Base import Base
from src.utils.date import to_duration


class ElasticsearchRunner(Base):
    def __init__(self, local_data_path=""):
        super(ElasticsearchRunner, self).__init__(local_data_path)

        if not self.local_data_path:
            self.interval = to_duration(self.raw_interval)
            self.interval_as_sec = self.interval.seconds
            self.query = Config["elasticsearch"]["fetch_query"]
            self.query = self.query.replace(
                TIMERANGE_PLACEHOLDER, f"now-{self.raw_interval}"
            )
            self.es = Elasticsearch(
                [
                    {
                        "host": Config["elasticsearch"]["host"],
                        "port": Config["elasticsearch"]["port"],
                    }
                ],
                api_key=(
                    Config["elasticsearch"]["api"]["id"],
                    Config["elasticsearch"]["api"]["key"],
                ),
            )
            print(
                f"Connecting to '{Config['elasticsearch']['host']}:{Config['elasticsearch']['port']}'..."
            )

            if not self.es.ping():
                raise ConnectionRefusedError

            print("OK")

    def run(self):
        map_scene = Map(self._screen)
        scenes = [Scene([map_scene], -1)]
        self._screen.set_scenes(scenes)

        try:
            # Schedule the first call to display_date()
            self._loop.call_soon(self._update_screen)
            self._loop.call_soon(self.compute_next_scenes)
            self._loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self._loop.close()
            self._screen.close()

    def fetch_next_data_from_es(self):
        res = self.es.search(index="melody-*", body=self.query, scroll="1m", size=10000)
        data = []
        for hit in res["hits"]["hits"]:
            hit["_source"]["_id"] = hit["_id"]
            data.append(hit["_source"])
        while len(res["hits"]["hits"]) > 0:
            res = self.es.scroll(scroll_id=res["_scroll_id"], scroll="1m")
            for hit in res["hits"]["hits"]:
                hit["_source"]["_id"] = hit["_id"]
                data.append(hit["_source"])

        return data

    def fetch_next_data_from_local(self):
        data = []
        counter = 0

        for raw_line in self.local_data_file:
            line = json.loads(raw_line)
            counter += 1
            line["_source"]["_id"] = line["_id"]
            data.append(line["_source"])
            if counter == self.local_chunk_size:
                break

        if counter < self.local_chunk_size:
            # EOF
            self.local_data_file.seek(0)

        return data

    def get_fresh_data(self):
        return (
            self.fetch_next_data_from_local()
            if self.local_data_path
            else self.fetch_next_data_from_es()
        )
