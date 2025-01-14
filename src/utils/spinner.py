# import Python's standard libraries
import time
import types
import asyncio
import itertools
import threading
import functools
from typing import Callable, Union, Optional, Type

# import third-party libraries
from colorama import Fore as F, Style as S

# import local files
if (__package__ is None or __package__ == ""):
    from spinner_types import SpinnerTypes
else:
    from .spinner_types import SpinnerTypes

def convert_str_to_ansi(colour: Union[str, None]) -> str:
    """Convert a string to ANSI escape code using colorama.

    Args:
        colour (str | None): 
            The colour string to convert. (None is converted to empty string)

    Returns:
        str: The ANSI escape code.
    """
    colour_table = {
        None: "",
        "black": F.BLACK,
        "red": F.RED,
        "green": F.GREEN,
        "yellow": F.YELLOW,
        "blue": F.BLUE,
        "magenta": F.MAGENTA,
        "cyan": F.CYAN,
        "white": F.WHITE,
        "light_black": F.LIGHTBLACK_EX,
        "light_red": F.LIGHTRED_EX,
        "light_green": F.LIGHTGREEN_EX,
        "light_yellow": F.LIGHTYELLOW_EX,
        "light_blue": F.LIGHTBLUE_EX,
        "light_magenta": F.LIGHTMAGENTA_EX,
        "light_cyan": F.LIGHTCYAN_EX,
        "light_white": F.LIGHTWHITE_EX,
    }
    if (isinstance(colour, str)):
        colour = colour.lower()

    if (colour not in colour_table):
        raise ValueError("Invalid colour option.")

    return colour_table[colour]

def format_success_msg(msg: Union[str, None]) -> Union[str, None]:
    """Format the success message with a check mark.

    Args:
        msg (str | None):
            The message to format.

    Returns:
        str | None: 
            The formatted message.
    """
    if (msg is None):
        return
    else:
        return " ".join([f"{F.LIGHTGREEN_EX}✓", msg, S.RESET_ALL])

def format_error_msg(msg: Union[str, None]) -> Union[str, None]:
    """Format the error message with a cross.

    Args:
        msg (str | None):
            The message to format.

    Returns:
        str | None:
            The formatted message.
    """
    if (msg is None):
        return
    else:
        return " ".join([f"{F.LIGHTRED_EX}✗", msg, S.RESET_ALL])

class Spinner:
    """Spinner class for displaying a spinner animation
    with a text message in the terminal on a separate thread.

    Inspired by 
        - https://github.com/manrajgrover/halo
        - https://stackoverflow.com/questions/4995733/how-to-create-a-spinning-command-line-cursor
    """
    CLEAR_LINE = "\033[K"
    def __init__(self, 
        message: str,
        colour: Optional[str] = None,
        spinner_type: str = "dots",
        spinner_position: Optional[str] = "left",
        completion_msg: Optional[str] = None,
        cancelled_msg: Optional[str] = None) -> None:
        """Constructs the spinner object.

        Args:
            message (str):
                The message to display along with the spinner.
            colour (str | None):
                The colour of the spinner. (default: None for default terminal colour)
            spinner_type (str):
                The type of spinner to display. (default: "dots")
            spinner_position (str | None):
                The position of the spinner. (default: "left")
            completion_msg (str | None):
                The message to display when the spinner has stopped. (default: None which will clear the line that the spinner was on)
            cancelled_msg (str | None):
                The message to display when the spinner has stopped due to a KeyboardInterrupt error. (default: None which will clear the line that the spinner was on)
        """
        # Spinner configurations below
        spinner_info = self.load_spinner(spinner_type=spinner_type)
        self.__spinner = itertools.cycle(spinner_info["frames"])
        self.__interval = 0.001 * spinner_info["interval"]
        self.message = message
        self.completion_msg = format_success_msg(completion_msg)
        self.cancelled_msg = format_error_msg(cancelled_msg)
        self.__colour = convert_str_to_ansi(colour)
        self.__position = spinner_position.lower()
        if (self.__position not in ("left", "right")):
            raise ValueError("Invalid spinner position.")

        # Spinner thread and event below
        self.__spinner_thread = None
        self.__stop_event = None

    def load_spinner(self, spinner_type: str) -> list[str]:
        """Load the spinner type from the SpinnerTypes Enum object."""
        if (spinner_type not in SpinnerTypes.__members__):
            raise ValueError(
                f"Invalid spinner type, '{spinner_type}'.\n" \
                "Please refer to the SpinnerTypes enum or refer to " \
                "https://github.com/sindresorhus/cli-spinners/blob/main/spinners.json " \
                "for a list of valid spinner types."
            )
        return SpinnerTypes[spinner_type].value

    def get_spin(self) -> itertools.cycle:
        """returns the spinner cycle."""
        return self.__spinner

    def __run_spinner(self):
        """Run and display the spinner animation with the text message."""
        print("\r", self.CLEAR_LINE, end="", sep="") # clear any existing text on the same line
        while (not self.__stop_event.is_set()):
            print(
                f"\r{self.__colour}",
                "{} {}".format(
                    *(
                        (self.message, next(self.__spinner)) 
                        if (self.__position == "right") 
                        else (next(self.__spinner), self.message)
                    ,)[0]
                ),
                S.RESET_ALL,
                sep="",
                end=""
            )
            time.sleep(self.__interval)

    def start(self):
        """Start the spinner and returns self."""
        self.__stop_event = threading.Event()
        self.__spinner_thread = threading.Thread(target=self.__run_spinner, daemon=True)
        self.__spinner_thread.start()
        return self

    def stop(self, manually_stopped: Optional[bool] = False, error: Optional[bool] = False) -> None:
        """Stop the spinner.

        Args:
            manually_stopped (bool):
                Whether the spinner was stopped manually. (default: False)
            error (bool):
                Whether the spinner was stopped due to an error. (default: False)

        Returns:
            None
        """
        if (self.__spinner_thread is not None and self.__spinner_thread.is_alive()):
            self.__stop_event.set()
            self.__spinner_thread.join()

        if (not error):
            if (manually_stopped):
                if (self.cancelled_msg is not None):
                    print("\r", self.CLEAR_LINE, self.cancelled_msg, sep="", end="")
                    return
            else:
                if (self.completion_msg is not None):
                    print("\r", self.CLEAR_LINE, self.completion_msg, sep="", end="")
                    return

        print("\r", self.CLEAR_LINE, end=S.RESET_ALL, sep="")

    def __enter__(self):
        """Start the spinner object and to be used in a context manager and returns self."""
        return self.start()

    def __exit__(self, 
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        traceback: Optional[types.TracebackType]) -> None:
        """Stops the spinner when used in a context manager."""
        if (exc_type is not None):
            if (exc_type is asyncio.CancelledError or issubclass(exc_type, KeyboardInterrupt)):
                self.stop(manually_stopped=True)
            else:
                self.stop(error=True)
        else:
            self.stop()

    def __call__(self, func: Callable):
        """Allow the spinner object to be used as a regular function decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

    def __str__(self) -> str:
        """Returns the string representation of the spinner object."""
        return f"Spinner<message={self.message}, colour={self.__colour}, spinner_type={self.__spinner}, spinner_position={self.__position}, completion_msg={self.completion_msg}, cancelled_msg={self.cancelled_msg}>"

    def __repr__(self) -> str:
        """Returns the string representation of the spinner object."""
        return self.__str__()

# Test codes below
if (__name__ == "__main__"):
    import time

    with Spinner("loading", colour="yellow", spinner_position="left", spinner_type="material", completion_msg="Done", cancelled_msg="Cancelled\n") as s:
        time.sleep(12)