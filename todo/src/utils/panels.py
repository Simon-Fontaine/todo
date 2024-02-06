import enum
from rich.panel import Panel


class Color(enum.Enum):
    INFO = "#88c0d0"
    WARNING = "#ebcb8b"
    DANGER = "#bf616a"
    SUCCESS = "#a3be8c"

    def __str__(self):
        return self.value


def create_panel(title: str, content: str, color: Color = Color.INFO) -> Panel:
    return Panel(
        content,
        title=title,
        border_style=str(color),
        title_align="left",
    )
