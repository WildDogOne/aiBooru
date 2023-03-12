# Tables
from rich.console import Console
from rich.traceback import install

# from rich.pretty import pprint

console = Console()

install(show_locals=True)

## Logging Handler
import logging
from rich.logging import RichHandler

FORMAT = "%(asctime)s %(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            # locals_max_length=None,
            # locals_max_string=None,
            # tracebacks_word_wrap=False,
            # show_path=True,
        )
    ],
)

logger = logging.getLogger("rich")
