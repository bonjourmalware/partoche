from random import randint

import crayons
from asciimatics.effects import Effect
from asciimatics.screen import Screen

from src.config import Config
from src.const import TILE_H, TILE_W
from src.effects.HitText import HitText
from src.effects.TunableRingExplosion import TunableRingExplosion


class Hit(Effect):
    symbol = Config.get("pin_emoji", "📍") if Config.get("emoji") else "⊗"

    def __init__(
        self,
        screen,
        country,
        city,
        asn,
        as_org,
        src_ip,
        x,
        y,
        explode=False,
        explosion_width=8,
        hit_zone=False,
        symbol=symbol,
        color: int = Screen.COLOUR_RED,
        bold_symbol=True,
        **kwargs,
    ):
        super(Hit, self).__init__(screen, **kwargs)
        self.hit_zone = hit_zone
        as_org = f"[AS{asn}] {as_org}"
        if city:
            country = f"{country} ({city})"
        else:
            country = f"{country}"

        self.explode = explode
        self.explosion_width = explosion_width
        self.symbol = symbol
        self._screen = screen
        self.color = color
        self.x = x
        self.y = y
        self.symbol_attr = Screen.A_BOLD if bold_symbol else Screen.A_NORMAL
        self.texts = []

        for text_params in [
            {
                "text": src_ip,
                "offset_y": 2,
                "color": Screen.COLOUR_YELLOW,
                "bold": True,
            },
            {
                "text": country,
                "offset_y": 1,
                "color": Screen.COLOUR_CYAN,
                "bold": False,
            },
            {
                "text": as_org,
                "offset_y": 0,
                "color": Screen.COLOUR_MAGENTA,
                "bold": False,
            },
        ]:

            text_x = self.x - (len(text_params["text"]) // 2)
            text_y = self.y - 1 - text_params["offset_y"]

            self.texts.append(
                HitText(
                    text_params["text"],
                    text_x,
                    text_y,
                    text_params["color"],
                    bold=text_params["bold"],
                )
            )
        if self.explode:
            explosion_width = self.explosion_width
            self.explosion = TunableRingExplosion(
                self._screen,
                self.x,
                self.y,
                explosion_width * 2,
                width=explosion_width,
                color=randint(1, 6),
            )

    def _update(self, frame_no):
        if self.explode:
            self.explosion.update()

        self._draw()

    def _draw(self):
        if self.hit_zone:
            self.print_zone()
        else:
            self._screen.print_at(
                self.symbol, self.x, self.y, self.color, self.symbol_attr
            )

        for text in self.texts:
            text.draw(self._screen)

    def print_zone(self):
        for height_offset in range(TILE_H):
            for width_offset in range(TILE_W):
                self._screen.print_at(
                    self.symbol,
                    self.x + width_offset,
                    self.y + height_offset,
                    self._screen.COLOUR_RED,
                    self._screen.A_BOLD,
                )

    @property
    def stop_frame(self):
        return self._stop_frame

    def reset(self):
        pass
