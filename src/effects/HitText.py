from asciimatics.screen import Screen


class HitText:
    def __init__(self, text, x, y, color, bold=False):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.bold = bold
        self.attr = Screen.A_BOLD if bold else Screen.A_NORMAL

    def draw(self, screen):
        screen.print_at(
            self.text,
            self.x,
            self.y,
            self.color,
            self.attr,
        )
