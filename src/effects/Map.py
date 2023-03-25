import os

from asciimatics.effects import Effect

from src.utils.map import gen_map


class Map(Effect):
    def __init__(self, screen, **kwargs):
        super(Map, self).__init__(screen, **kwargs)
        self.bg = gen_map(screen.width, screen.height)
        self.last_width = screen.width

    def _update(self, frame_no):
        # self.screen.has_resized is not available in non-screen.play context
        term_size = os.get_terminal_size()
        if term_size.columns != self.last_width:
            self.bg = gen_map(term_size.columns, term_size.lines)
            self.last_width = term_size.columns
            self.screen.clear()

        for y, line in enumerate(self.bg.splitlines()):
            for x, c in enumerate(line):
                self._screen.print_at(c, x, y)

    # Needed for threading, as the class won't instantiate without these abstract methods defined
    def reset(self):
        """
        Function to reset the effect when replaying the scene.
        """

    # Needed for threading, as the class won't instantiate without these abstract methods defined
    def stop_frame(self):
        """
        Last frame for this effect.  A value of zero means no specific end.
        """
