import enum
from rich.panel import Panel


class Color(enum.Enum):
    INFO = "#88c0d0"
    WARNING = "#ebcb8b"
    DANGER = "#bf616a"
    SUCCESS = "#a3be8c"

    def __str__(self):
        return self.value


def create_panel(
    title: str = "Undefined", content: str = "Undefined", color: Color = Color.INFO
) -> Panel:
    """Create a panel with a title and content

    Parameters
    ----------
    title : str, optional
        The title of the panel, by default "Undefined"
    content : str, optional
        The content of the panel, by default "Undefined"
    color : Color, optional
        The color of the panel, by default Color.INFO

    Returns
    -------
    Panel
        The panel with the title and content
    """
    return Panel(
        content,
        title=title,
        border_style=str(color),
        title_align="left",
    )
