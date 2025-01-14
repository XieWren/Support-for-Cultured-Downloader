# import Python's standard libraries
import re
import time
import json
import pathlib
import asyncio
from typing import Union, Optional, Any

# import local files
if (__package__ is None or __package__ == ""):
    from spinner import Spinner
    from schemas.config import ConfigSchema
    from errors import APIServerError
    from constants import CONSTANTS as C
    from logger import logger
else:
    from .spinner import Spinner
    from .schemas.config import ConfigSchema
    from .errors import APIServerError
    from .constants import CONSTANTS as C
    from .logger import logger

# import third-party libraries
import httpx
from colorama import Fore as F
from pydantic import BaseModel
import aiofiles.os as aiofiles_os
import pydantic.error_wrappers as pydantic_error_wrappers 

def website_to_readable_format(website: str) -> str:
    """Converts a website string to a readable format.

    Args:
        website (str): 
            The website to convert.

    Returns:
        str: 
            The readable format of the website.
    """
    readable_table = {
        "fantia": "Fantia",
        "pixiv_fanbox": "Pixiv Fanbox",
    }
    if (website not in readable_table):
        raise ValueError(f"Invalid website: {website}")
    return readable_table[website]

def log_api_error(error_msg: str) -> None:
    """Log any errors such as Cultured Downloader API's 5XX errors.

    Args:
        error_msg (str):
            The error message to log.

    Returns:
        None

    Raise:
        APIServerError after logging the error message.
    """
    logger.error(f"API Server Error:\n{error_msg}")
    raise APIServerError(error_msg)

def validate_schema(schema: BaseModel, data: Union[str, dict, list], 
                    return_bool: Optional[bool] = True, log_failure: Optional[bool] = True) -> Union[bool, BaseModel]:
    """Validates the data against the schema

    Args:
        schema (BaseModel): 
            The pydantic base model object to validate against
        data (str | dict | list):
            The data to validate
        return_bool (bool, optional):
            Whether to return a boolean or the pydantic base model object. Defaults to True.
        log_failure (bool, optional):
            Whether to log the failure of validation. Defaults to True.

    Returns:
        Union[bool, BaseModel]:
            False if the data is invalid, otherwise the pydantic base model object with the data or a boolean.
    """
    if (not isinstance(data, Union[str, dict, list])):
        return False

    try:
        if (isinstance(data, str)):
            pydantic_obj = schema.parse_raw(data)
        else:
            pydantic_obj = schema.parse_obj(data)
        return pydantic_obj if (not return_bool) else True
    except (pydantic_error_wrappers.ValidationError) as e:
        if (log_failure):
            logger.info(
                "Data is invalid when validated against the schema, " \
                f"{schema.__name__}: {e}\n\nData: {data}"
            )
        return False

def print_danger(message: Any, **kwargs) -> None:
    """Print a message in red.

    Args:
        message (Any):
            The message to print.
        kwargs:
            Any keyword arguments to pass to the print function.

    Returns:
        None
    """
    print(f"{F.LIGHTRED_EX}{message}{F.RESET}", **kwargs)

def print_warning(message: Any, **kwargs) -> None:
    """Print a message in light yellow.

    Args:
        message (Any):
            The message to print.
        kwargs:
            Any keyword arguments to pass to the print function.

    Returns:
        None
    """
    print(f"{F.LIGHTYELLOW_EX}{message}{F.RESET}", **kwargs)

def print_success(message: Any, **kwargs) -> None:
    """Print a message in green.

    Args:
        message (Any):
            The message to print.
        kwargs:
            Any keyword arguments to pass to the print function.

    Returns:
        None
    """
    print(f"{F.LIGHTGREEN_EX}{message}{F.RESET}", **kwargs)

def save_key_prompt() -> bool:
    """Prompt the user where necessary if they want to save their 
    generated secret key on their computer or to Cultured Downloader API."""
    if (C.KEY_ID_TOKEN_JSON_PATH.exists() and C.KEY_ID_TOKEN_JSON_PATH.is_file()):
        return False

    if (C.SECRET_KEY_PATH.exists() and C.SECRET_KEY_PATH.is_file()):
        return True

    save_key = get_input(
        input_msg="Enter your desired action (API, LOCAL): ",
        inputs=("api", "local"),
        extra_information="""
Would you like to save your secret key on your computer or on Cultured Downloader API?

If you were to save it on Cultured Downloader API, 
key rotations will be enabled for you and it is more secure if your computer is being shared.
Important Note: If you are currently using a proxy such as a VPN, please disable it as the saved key
is mapped to your IP address (Don't worry as your IP address is hashed on our database).

However, if you prefer faster loading speed than security, 
you can instead opt for your key to be saved locally on your computer.

TLDR (Too long, didn't read):
Enter \"API\" to save your secret key to Cultured Downloader API for security,
\"LOCAL\" otherwise to save it locally on your computer for faster loading time.
""")
    return True if (save_key == "local") else False

def load_configs() -> ConfigSchema:
    """Load the configs from the config file.

    Returns:
        ConfigSchema: 
            The configs loaded from the config file.
    """
    configs = {}
    if (C.CONFIG_JSON_FILE_PATH.exists() and C.CONFIG_JSON_FILE_PATH.is_file()):
        with open(C.CONFIG_JSON_FILE_PATH, "r") as f:
            configs = json.load(f)

    schema_obj = validate_schema(schema=ConfigSchema, data=configs, return_bool=False)
    if (schema_obj is False):
        # If the config JSON data is invalid,
        # reset the config file to the default values 
        # and save it to the config JSON file.
        schema_obj = ConfigSchema(**{})
        edit_configs(new_configs=schema_obj.dict())

    # check if the download directory exists
    download_dir = pathlib.Path(schema_obj.download_directory)
    if (not download_dir.exists() or not download_dir.is_dir()):
        # if the download directory does not exist,
        # reset to the user's desktop folder path.
        schema_obj.download_directory = str(pathlib.Path.home().joinpath("Desktop", "cultured-downloader"))

    return schema_obj

def edit_configs(new_configs: dict) -> None:
    """Edit the configs in the config file.

    Args:
        new_configs (dict):
            The new configuration to save to the config file.

    Returns:
        None
    """
    with open(C.CONFIG_JSON_FILE_PATH, "w") as f:
        json.dump(new_configs, f, indent=4)

def change_download_directory(configs: Optional[ConfigSchema] = None, 
                              print_message: Optional[bool] = False) -> None:
    """Change the download directory in the config file.

    Args:
        configs (ConfigSchema, optional):
            The configs to edit. If None, the configs will be loaded from the config file.
        print_message (bool, optional):
            Whether to print the messages to the user to inform them that the changes have been saved
            but will require the user to re-run the program for the changes to take effect.

    Returns:
        None
    """
    if (configs is None):
        configs = load_configs()

    print_warning(f"Your current download directory is\n{configs.download_directory}")
    change_download_directory = get_input(
        input_msg="Do you want to change your download directory? (y/N): ",
        inputs=("y", "n"),
        default="n"
    )
    if (change_download_directory == "y"):
        while (True):
            try:
                download_directory_path = input("Enter your new download directory (X to cancel): ").strip()
            except (EOFError):
                continue
            except (KeyboardInterrupt):
                print_danger("Changing of download directory has been cancelled.")
                return

            if (download_directory_path == ""):
                print_danger("Please enter a valid download directory.\n")
                continue

            if (download_directory_path.lower() == "x"):
                print_warning("Cancelled changing webdriver's download directory.")
                break

            download_directory_path = pathlib.Path(download_directory_path)
            if (not download_directory_path.exists() or not download_directory_path.is_dir()):
                print_danger("Download directory does not exist, please create it first and try again.\n")
                continue

            download_directory_path = str(download_directory_path)
            if (configs.download_directory == download_directory_path):
                print_danger("Download directory is already set to that.\n")
                continue

            configs.download_directory = download_directory_path
            edit_configs(configs.dict())
            print_success(f"Download directory successfully changed to\n{download_directory_path}")

            if (print_message):
                print_danger(
                    "\nNotice: You will need to re-run the program for the changes to take effect in the current webdriver instance." \
                    "\nHowever, as of now, the changes does not affect the download process and you can continue to download as usual."
                )

            break
    print()

def get_input(input_msg: str, inputs: Optional[Union[tuple[str], list[str]]] = None, 
              regex: re.Pattern[str] = None, default: Optional[str] = None, warning: str = None, 
              extra_information: Optional[str] = None, is_case_sensitive: Optional[bool] = False) -> str:
    """Get the expected input from the user.

    Args:
        input_msg (str):
            The message to print to the user.
        inputs (tuple[str] | list[str], optional):
            The inputs that the user can enter.
            Note: inputs must be lowercase but will be converted to lowercase string as a failsafe.
            If this is passed in, regex parameter cannot be passed in!
        regex (re.Pattern[str], optional):
            The regex pattern to match the input against.
            If this is passed in, inputs parameter cannot be passed in!
        default (str, optional):
            The default input to be returned if the user doesn't enter anything.
        warning (str, optional):
            The warning message to print to the user if the input is invalid.
        extra_information (str, optional):
            The extra information to print to the user before the input message.
        is_case_sensitive (bool, optional):
            Whether the input is case sensitive or not. 
            If so, the inputs and the user's input will not be converted to lowercase.

    Returns:
        The input the user entered.

    Raises:
        ValueError:
            If the inputs and regex are both passed in.
    """
    if (inputs and regex):
        raise ValueError("inputs and regex cannot be passed in together")

    if (inputs is not None and (not isinstance(inputs, tuple) and not isinstance(inputs, list))):
        raise TypeError("inputs must be a tuple or a list")
    if (regex is not None and not isinstance(regex, re.Pattern)):
        raise TypeError("regex must be a re.Pattern")
    if (warning is not None and not isinstance(warning, str)):
        raise TypeError("warning must be a str")

    if (inputs is not None):
        # fail-safe if the list or tuple passed in does not contain strings
        if (not is_case_sensitive):
            inputs = tuple(str(inp).lower() for inp in inputs)
        else:
            inputs = tuple(str(inp) for inp in inputs)

    while (True):
        if (extra_information is not None):
            print_warning(extra_information)

        try:
            user_input = input(input_msg).strip()
        except (EOFError):
            continue

        if (not is_case_sensitive):
            user_input = user_input.lower()

        if (inputs is not None and user_input in inputs):
            return user_input
        elif (regex is not None and regex.match(user_input)):
            return user_input
        elif (default is not None and user_input == ""):
            print("\033[A", input_msg, default, sep="")
            return default
        else:
            print_danger(f"Sorry, please enter a valid input." if (warning is None) else warning)

def get_user_download_choices(website: str, block_gdrive_downloads: bool) -> Union[tuple[bool, bool, bool], tuple[bool, bool, bool, bool, bool], None]:
    """Prompt the user and get their download preferences.

    Args:
        website (str):
            The website to get the download preferences for.
            If the website is "fantia", gdrive and detection of 
            other file hosting provider links will be disabled.
        block_gdrive (bool):
            Whether to block gdrive links from being downloaded.
            If it's for Fantia, the user would not be prompted if they would like to download gdrive links.
            Otherwise, for Pixiv Fanbox, the user would be prompted if they would like to download or detect gdrive links.

    Returns:
        A tuple of boolean or None if the user cancels the download process:
            (download_images, download_thumbnail, download_attachment).\n
            If the website is not "fantia", the tuple will have an additional last 2 booleans:
                download_gdrive_links/detect_gdrive_links, detect_other_download_links
    """
    while (True):
        download_images = get_input(
            input_msg="Download images? (Y/n/x to cancel): ",
            inputs=("y", "n", "x"),
            default="y"
        )
        if (download_images == "x"):
            return

        download_thumbnail = get_input(
            input_msg="Download thumbnail? (Y/n/x to cancel): ",
            inputs=("y", "n", "x"),
            default="y"
        )
        if (download_thumbnail == "x"):
            return

        download_attachments = get_input(
            input_msg="Download attachments? (Y/n/x to cancel): ",
            inputs=("y", "n", "x"),
            default="y"
        )
        if (download_attachments == "x"):
            return

        download_flags = [
            download_images == "y", 
            download_thumbnail == "y",
            download_attachments == "y"
        ]
        if (website != "fantia"):
            if (not block_gdrive_downloads):
                download_gdrive_links = get_input(
                    input_msg="Download Google Drive links? (Y/n/x to cancel): ",
                    inputs=("y", "n", "x"),
                    default="y"
                )
            else:
                # Since the user did not configure Google OAuth2 yet, detect GDrive links instead.
                detect_gdrive_links = get_input(
                    input_msg="Detect Google Drive links (Note: Configure Google OAuth2 to enable downloads)? (Y/n/x to cancel): ",
                    inputs=("y", "n", "x"),
                    default="y"
                )
                download_gdrive_links = detect_gdrive_links
            if (download_gdrive_links == "x"):
                return

            detect_other_download_links = get_input(
                input_msg="Detect other download links such as MEGA links? (Y/n/x to cancel): ",
                inputs=("y", "n", "x"),
                default="y"
            )
            if (detect_other_download_links == "x"):
                return

            download_flags.extend([
                download_gdrive_links == "y", 
                detect_other_download_links == "y"
            ])

        if (not any(download_flags)):
            print_danger("Please select at least one download option...\n")
        else:
            return tuple(download_flags)

def split_url_input(user_input: str) -> list[str]:
    """Split the user input into a list of URLs and removes any duplicates.

    Args:
        user_input (str):
            The user input to split.

    Returns:
        A list of URLs.
    """
    urls_arr = [url.strip() for url in user_input.split(sep=",")]
    unique_urls = list(dict.fromkeys(urls_arr, None))
    if (len(unique_urls) != len(urls_arr)):
        print_danger("Warning: Duplicate URLs have been removed from your input...")

    return unique_urls

def get_page_nums(user_inputs: list[str], website: str, input_name: Optional[str] = "URL(s)") -> Union[list[str], list[tuple[str, int, int]]]:
    """Get the page numbers for each input in the user_inputs array.

    Args:
        user_inputs (list[str]):
            An array of inputs to get the page numbers for.
        website (str):
            The website to get the page numbers for.

    Returns:
        A list of URLs with the page num query parameters or a list of tuples of user inputs and page numbers.
    """
    print_warning(
        f"\nPlease enter the page numbers you wish to download from corresponding to the {input_name} you entered." \
        f"\nFor example, if you entered 2 {input_name}, you will enter something like '1, 1-3' to indicate " \
        f"that you wish to download from the 1st page of the first {input_name} and the 1st to 3rd page of the second {input_name}."
    )
    page_num_prompt = "\nPlease enter {} (X to cancel): ".format(
        f"{len(user_inputs)} page numbers corresponding to the entered {input_name}" \
        if (len(user_inputs) > 1) \
        else "a page number"
    )
    while (True):
        try:
            page_inputs = input(page_num_prompt).strip()
        except (EOFError):
            continue

        if (page_inputs == ""):
            print_danger("User Error: Please enter a page number")
            continue
        elif (page_inputs in ("X", "x")):
            return

        page_nums_arr = page_inputs.split(sep=",")
        if (len(page_nums_arr) != len(user_inputs)):
            print_danger(
                f"User Error: The number of page numbers entered does not match the number of {input_name} entered"
            )
            continue

        url_with_page_nums_arr = []
        for idx, page_num in enumerate(page_nums_arr):
            page_num = page_num.strip()
            if (C.PAGE_NUM_REGEX.fullmatch(page_num) is None):
                print_danger(f"User Error: The page number, {page_num}, is invalid.")
                print_danger("Please enter in the correct format such as '1, 1-3' and try again.")
                break

            is_fantia = (website == "fantia")
            page_nums = page_num.split(sep="-", maxsplit=1)
            if (len(page_nums) == 1):
                if (website == "pixiv"):
                    url_with_page_nums_arr.append(
                        (user_inputs[idx], int(page_nums[0]), int(page_nums[0]))
                    )
                elif (website in ("pixiv_fanbox", "fantia")):
                    formatted_url = user_inputs[idx] + f"?page={page_nums[0]}"
                    if (is_fantia):
                        # Ensure that the pages go by newest to oldest
                        formatted_url += "&q[s]=newer&q[tag]="

                    url_with_page_nums_arr.append(formatted_url)
                continue

            # if a range was given, make sure the range is valid
            page_nums = [int(page_num) for page_num in page_nums]
            if (page_nums[0] > page_nums[1]):
                page_nums[0], page_nums[1] = page_nums[1], page_nums[0]

            if (website == "pixiv"):
                url_with_page_nums_arr.append((user_inputs[idx], page_nums[0], page_nums[1]))
                continue

            for page_num in range(page_nums[0], page_nums[1] + 1):
                formatted_url = user_inputs[idx] + f"?page={page_num}"
                if (is_fantia):
                    # Ensure that the pages go by newest to oldest
                    formatted_url += "&q[s]=newer&q[tag]="

                url_with_page_nums_arr.append(formatted_url)
        else:
            return url_with_page_nums_arr

def get_user_urls(website: str, creator_page: bool) -> Union[list[str], None]:
    """Get the URLs from the user.

    Args:
        website (str):
            The website the user is downloading from.
        creator_page (bool):
            Whether the user is downloading from a creator's page or not.

    Returns:
        list[str] | None: 
            The list of validated URLs, None if the user wishes to exit.
    """
    url_guide_and_regex_table = {
        "fantia": (
            ("https://fantia.jp/posts/1234567", C.FANTIA_POST_REGEX),
            ("https://fantia.jp/fanclubs/1234/posts", C.FANTIA_CREATOR_POSTS_REGEX)
        ),
        "pixiv_fanbox": (
            ("https://www.fanbox.cc/@creator_name/posts/1234567 or " \
             "https://creator_name.fanbox.cc/posts/1234567", C.PIXIV_FANBOX_POST_REGEX),
            ("https://www.fanbox.cc/@creator_name/posts or " \
             "https://creator_name.fanbox.cc/posts", C.PIXIV_FANBOX_CREATOR_POSTS_REGEX)
        )
    }
    if (website not in url_guide_and_regex_table):
        raise ValueError(f"Invalid website: {website}")

    extra_info = "This option is for URL(s) such as "
    url_guide, input_regex = url_guide_and_regex_table[website][creator_page]
    extra_info += url_guide
    extra_info += "\nAdditionally, you can enter multiple URLs separated by a comma."
    print_warning(extra_info)

    while (True):
        try:
            user_input = input("\nEnter URL(s) (X to cancel): ").strip()
        except (EOFError):
            continue

        if (user_input == ""):
            print_danger("User Error: Please enter a URL")
            continue
        elif (user_input in ("X", "x")):
            return

        formatted_urls = []
        unique_urls = split_url_input(user_input)
        for url in unique_urls:
            # Since a url can end with a slash,
            # remove it so for the regex validations
            # and to add GET parameters to the url.
            if (url.endswith("/")):
                url = url[:-1]

            if (input_regex.fullmatch(url) is not None):
                if (creator_page and not url.endswith("/posts")):
                    url += "/posts"
                formatted_urls.append(url)
                continue

            error_msg = "User Error: The URL, {url}, is invalid.\n" \
                        "Please make sure {suggestion} correct and try again.".format(
                            url=url,
                            suggestion="all the URLs entered are" \
                                        if (len(unique_urls) > 1) \
                                        else "the URL entered is"
                        )
            print_danger(error_msg)
            break
        else:
            # print out the formatted URLs and confirm with the user
            print_warning("\nThe following URLs will be downloaded:\n{urls}".format(
                urls=", ".join(formatted_urls)
            ))
            confirm = get_input(
                input_msg="Do you wish to download from these URLs? (Y/n): ",
                inputs=("y", "n"),
                default="y",
            )
            if (confirm == "n"):
                continue

            # Since there is no need to get more inputs 
            # from the user for downloading posts,
            # return the formatted URLs.
            if (not creator_page):
                return formatted_urls
            else:
                break

    # get page number from user
    return get_page_nums(
        website=website, 
        user_inputs=formatted_urls
    )

def pixiv_get_ids_or_tags(download_option: str) -> list:
    """Get the IDs of the Pixiv posts/artists or tag names to download from the user.

    Args:
        download_option (str): 
            The download option the user chose.

    Returns:
        list: 
            The list of IDs or tag names to download from.
    """
    if (not isinstance(download_option, str)):
        raise TypeError("download_option must be an str")
    if (download_option not in ("1", "2", "3")):
        raise ValueError(f"Invalid download option: {download_option}")

    download_table = {
        "1": {
            # download illust IDs
            "get_page_num": False,
            "regex": C.PIXIV_ILLUST_URL_REGEX
        },
        "2": {
            # download artist IDs
            "get_page_num": True,
            "regex": C.PIXIV_ARTIST_URL_REGEX
        },
        "3": {
            # download tag names
            "get_page_num": True,
            "regex": None,
        }
    }

    input_prompt = "Enter URL(s) (X to cancel): "
    if (download_option == "3"):
        input_prompt = "Enter tag name(s) (X to cancel): "

    while (True):
        try:
            user_input = input(input_prompt).strip()
        except (EOFError):
            return

        if (user_input == ""):
            print_danger("User Error: You cannot leave this empty!")
            continue
        elif (user_input in ("X", "x")):
            return

        pixiv_ids = []
        unique_urls = split_url_input(user_input)
        regex: re.Pattern[str] = download_table[download_option]["regex"]
        if (regex is None):
            pixiv_ids = unique_urls # tag names
        else:
            has_invalid_urls = False
            for url in unique_urls:
                match = regex.fullmatch(url)
                if (match is not None):
                    pixiv_ids.append(match.group(2))
                    continue

                has_invalid_urls = True
                error_msg = "User Error: The URL, {url}, is invalid.\n" \
                            "Please make sure {suggestion} correct and try again.".format(
                                url=url,
                                suggestion="all the URLs entered are" \
                                            if (len(unique_urls) > 1) \
                                            else "the URL entered is"
                            )
                print_danger(error_msg)
                break
            if (has_invalid_urls):
                continue

        if (not download_table[download_option]["get_page_num"]):
            return pixiv_ids

        # get page number from user
        inputs_with_page_nums = get_page_nums(
            website="pixiv",
            user_inputs=pixiv_ids,
            input_name="URL(s)" if (download_option != "3") else "tag name(s)"
        )
        if (inputs_with_page_nums is None):
            return

        if (download_option != "3"):
            # for Pixiv artist URLs, the sort order 
            # is always "new to old" (i.e. descending)
            return inputs_with_page_nums

        extra_information = """Tag Name Download Order:
1. From newest to oldest illustration
2. From oldest to newest illustration
3. From most popular to least popular illustration
X. Cancel downloads
"""
        get_sort_order = get_input(
            "Enter the download order for the tag name(s): ",
            inputs=("1", "2", "3", "x"),
            default="1",
            extra_information=extra_information
        )
        if (get_sort_order == "x"):
            return

        sort_order_table = {
            "1": "date_desc",
            "2": "date_asc",
            "3": "popular_desc"
        }
        formatted_tag_name_arr = []
        for tag_name, min_page_num, max_page_num in inputs_with_page_nums:
            formatted_tag_name_arr.append(
                (tag_name, min_page_num, max_page_num, sort_order_table[get_sort_order])
            )
        return formatted_tag_name_arr

def delete_empty_and_old_logs() -> None:
    """Delete all empty log files and log files
    older than 30 days except for the current day's log file.

    Returns:
        None
    """
    for log_file in C.LOG_FOLDER_PATH.iterdir():
        if (log_file.is_file() and log_file != C.TODAYS_LOG_FILE_PATH):
            file_info = log_file.stat()
            if (file_info.st_size == 0 or file_info.st_mtime < (time.time() - 2592000)):
                try:
                    log_file.unlink()
                except (PermissionError, FileNotFoundError):
                    pass

@Spinner(
    message="Checking for an active internet connection...",
    colour="light_yellow",
    spinner_type="arc",
    spinner_position="left"
)
def check_internet_connection() -> bool:
    """Check if the user has an internet connection by sending a HEAD request to google.com

    Returns:
        bool: 
            True if the user has an internet connection, False otherwise.
    """
    with httpx.Client(http2=True, headers=C.BASE_REQ_HEADERS, timeout=5) as client:
        try:
            client.head("https://www.google.com")
        except (httpx.ConnectError, httpx.ConnectTimeout):
            return False
    return True

def delete_cookies(website: str) -> None:
    """Delete the cookies for the given website if the user wishes to.

    Args:
        website (str):
            The website's cookies to delete.

    Returns:
        None
    """
    if (website == "pixiv_fanbox"):
        cookie_path = C.PIXIV_FANBOX_COOKIE_PATH
    elif (website == "fantia"):
        cookie_path = C.FANTIA_COOKIE_PATH
    else:
        raise ValueError(f"Invalid website: {website}")

    if (cookie_path.exists() and cookie_path.is_file()):
        readable_website_name = website_to_readable_format(website)
        confirm_delete = get_input(
            input_msg=f"Do you want to delete your saved cookies for {readable_website_name} as well? (y/N): ",
            inputs=("y", "n"),
            default="n"
        )
        if (confirm_delete == "y"):
            cookie_path.unlink()
            print_success(
                f"Successfully deleted your saved cookies for {readable_website_name}."
            )

def user_has_saved_cookies() -> bool:
    """Check if the user has saved cookies for Fantia and Pixiv Fanbox.

    Returns:
        bool: 
            True if the user has saved any cookies, False otherwise.
    """
    return ((C.FANTIA_COOKIE_PATH.exists() and C.FANTIA_COOKIE_PATH.is_file()) or \
            (C.PIXIV_FANBOX_COOKIE_PATH.exists() and C.PIXIV_FANBOX_COOKIE_PATH.is_file()))

def remove_illegal_chars_in_path(string: str) -> str:
    """Remove illegal characters in a path name.

    Args:
        string (str):
            The string to remove illegal characters from.

    Returns:
        str: 
            The path name with illegal characters replaced with a dash.
    """
    string = string.replace(".", " ")
    return C.ILLEGAL_PATH_CHARS_REGEX.sub(
        repl="-", 
        string=string.strip()
    )

def remove_folder_if_empty(folder_path: pathlib.Path) -> None:
    """Removes the folder if it is empty.

    Args:
        folder_path (pathlib.Path):
            The folder path to remove if it is empty.

    Returns:
        None
    """
    if (not folder_path.exists() or not folder_path.is_dir()):
        return

    if (not any(folder_path.iterdir())):
        folder_path.rmdir()

async def async_file_exists(file_path: pathlib.Path) -> bool:
    """Check if the given file exists asynchronously.

    Args:
        file_path (pathlib.Path):
            The file path to check if it exists.

    Returns:
        bool: 
            True if the file exists, False otherwise.
    """
    return await aiofiles_os.path.exists(file_path) and await aiofiles_os.path.isfile(file_path)

async def async_folder_exists(folder_path: pathlib.Path) -> bool:
    """Check if the given folder exists asynchronously.

    Args:
        folder_path (pathlib.Path):
            The folder path to check if it exists.

    Returns:
        bool: 
            True if the folder exists, False otherwise.
    """
    return await aiofiles_os.path.exists(folder_path) and await aiofiles_os.path.isdir(folder_path)

async def async_remove_file(file_path: pathlib.Path) -> None:
    """Remove the file if it exists asynchronously.

    Args:
        file_path (pathlib.Path):
            The file path to remove.

    Returns:
        None
    """
    if (await async_file_exists(file_path)):
        try:
            await aiofiles_os.unlink(file_path)
        except (PermissionError):
            pass

async def async_remove_folder(folder_path: pathlib.Path, has_files_ok: Optional[bool] = False) -> None:
    """Remove the folder if it exists asynchronously.

    Args:
        folder_path (pathlib.Path):
            The folder path to remove.
        has_files_ok (bool, optional):
            Whether or not it is okay if the folder has files in it as the folder would not be deleted. 
            Defaults to False which will raise an error if the folder has files in it.

    Returns:
        None
    """
    if (await async_folder_exists(folder_path)):
        try:
            await aiofiles_os.rmdir(folder_path)
        except (OSError):
            if (not has_files_ok):
                raise

async def async_mkdir(folder_path: pathlib.Path, 
                      parents: Optional[bool] = False, exist_ok: Optional[bool] = False) -> None:
    """Create the folder if it doesn't exist asynchronously.

    Args:
        folder_path (pathlib.Path):
            The folder path to create.
        parents (Optional[bool], optional):
            Whether to create the parent folders if they don't exist. Defaults to False.
        exist_ok (Optional[bool], optional):
            Whether to not throw an error if the folder already exists. Defaults to False.

    Returns:
        None
    """
    if (parents):
        return await aiofiles_os.makedirs(folder_path, exist_ok=exist_ok)

    try:
        return await aiofiles_os.mkdir(folder_path)
    except (OSError):
        if (not exist_ok):
            raise

def log_critical_details_for_post(post_folder: pathlib.Path, message: str, 
                                  log_filename: Optional[str] = "read_me.log", 
                                  ignore_if_exists: Optional[bool] = False) -> None:
    """Log critical details about a post to a log file.

    Args:
        post_folder (pathlib.Path):
            The path to the post's folder.
        message (str):
            The message to log.
        log_filename (Optional[str], optional):
            The name of the log file. Defaults to "read_me.log".
        ignore_if_exists (Optional[bool], optional):
            Whether to ignore logging if the log file already exists and has data in it. Defaults to False.
    """
    post_folder.mkdir(parents=True, exist_ok=True)
    log_file = post_folder.joinpath(log_filename)
    if (ignore_if_exists and log_file.exists() and log_file.is_file() and log_file.stat().st_size > 0):
        return

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message)
        f.write("\n")

def call_async_result(executed_async_tasks: set[asyncio.Task]) -> None:
    """Call and get the result of the executed async tasks.

    Args:
        executed_async_tasks (set):
            The set of executed async tasks.

    Returns:
        None
    """
    for task in executed_async_tasks:
        # will get the returned value of the 
        # async function or raise any uncaught exceptions
        task.result()  

async def check_download_tasks(tasks: set[asyncio.Task], all_completed: bool) -> tuple[set[asyncio.Task], set[asyncio.Task]]:
    """Awaits and check the given tasks and raises any errors that may have occurred.

    Args:
        tasks (set[asyncio.Task]):
            The tasks to await.

    Returns:
        tuple[set[asyncio.Task], set[asyncio.Task]]:
            The tasks that have finished and the tasks that are still running.

    Raises:
        asyncio.CancelledError:
            If the download process has been cancelled by the user (via Ctrl+C).
    """
    if (tasks):
        if (all_completed):
            return_when = asyncio.ALL_COMPLETED
        else:
            return_when = asyncio.FIRST_COMPLETED

        try:
            done, download_tasks = await asyncio.wait(
                tasks,
                return_when=return_when
            )
            call_async_result(done)
            return done, download_tasks
        except (asyncio.CancelledError):
            for task in tasks:
                task.cancel()
            raise
    else:
        return set(), set()