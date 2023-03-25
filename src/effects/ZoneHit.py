from asciimatics.effects import Effect
from asciimatics.screen import Screen

from src.const import TILE_H, TILE_W


class ZoneHit(Effect):
    def __init__(
        self,
        screen,
        country,
        asn,
        as_org,
        src_ip,
        x,
        y,
        symbol="X",
        color: int = Screen.COLOUR_RED,
        bold_symbol=True,
        **kwargs,
    ):
        super(ZoneHit, self).__init__(screen, **kwargs)
        self.src_ip = src_ip
        self.country = country
        self.as_org = as_org
        self.asn = asn
        if as_org:
            self.as_org = f"[AS{self.asn}] {self.as_org}"

        self.symbol = symbol
        self._screen = screen
        self.color = color
        self.x = x
        self.y = y
        self.symbol_attr = Screen.A_BOLD if bold_symbol else Screen.A_NORMAL
        self.country_offset = 0
        self.ip_offset = 2

        if self.as_org:
            self.country_offset -= 1
            self.ip_offset -= 1

    def _update(self, frame_no):
        for height_offset in range(TILE_H):
            for width_offset in range(TILE_W):
                self._screen.print_at(
                    self.symbol,
                    self.x + width_offset,
                    self.y + height_offset,
                    self._screen.COLOUR_RED,
                    self._screen.A_BOLD,
                )

        self._screen.print_at(
            self.src_ip,
            (self.x - ((len(self.src_ip) // 2) - TILE_W // 2)),
            self.y - TILE_H // 2 - self.ip_offset,
            Screen.COLOUR_YELLOW,
            Screen.A_BOLD,
        )
        self._screen.print_at(
            self.country,
            (self.x - ((len(self.country) // 2) - TILE_W // 2)),
            self.y - TILE_H // 2 - self.country_offset,
            Screen.COLOUR_CYAN,
        )
        if self.as_org:
            self._screen.print_at(
                self.as_org,
                (self.x - ((len(self.as_org) // 2) - TILE_W // 2)),
                self.y - TILE_H // 2,
                Screen.COLOUR_MAGENTA,
            )

    @property
    def stop_frame(self):
        return self._stop_frame

    def reset(self):
        pass
