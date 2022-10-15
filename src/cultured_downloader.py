# import Python's standard libraries
import sys
if (sys.version_info[0] < 3 or sys.version_info[1] < 9):
    print("This program requires Python version 3.9 or higher!")
    input("Please press ENTER to exit...")
    sys.exit(1)
import asyncio
import webbrowser

# import local libraries
from utils import *
from utils import danbooru
from utils import __version__, __author__, __license__

# import third-party libraries
from urllib3 import exceptions as urllib3_exceptions
from colorama import Fore as F, init as colorama_init

if (C.USER_PLATFORM == "Windows"):
    # escape ANSI escape sequences on Windows terminal
    colorama_init(autoreset=False, convert=True)

    # A temporary fix for ProactorBasePipeTransport issues on
    # Windows OS Machines that may appear for older versions of Python
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def print_main_menu(login_status: dict[str, bool], 
                    drive_service: Union[str, None], pixiv_api: Union[PixivAPI, None], 
                    danbooru_profile:danbooru.UserProfile) -> None:
    """Print the menu for the user to read and enter their desired action.

    Args:
        login_status (dict[str, bool]):
            The login status of the user,
            E.g. {"pixiv_fanbox": False, "fantia": True}
        drive_service (Any | None):
            The Google Drive API Service Object if it exists, None otherwise.
        pixiv_api (PixivAPI | None):
            The PixivAPI object if it exists, None otherwise.
        danbooru_profile (danbooru.UserProfile):
            The danbooru.UserProfile object, set to default variables if does not exist.

    Returns:
        None
    """
    fantia_status = login_status.get("fantia")
    pixiv_fanbox_status = login_status.get("pixiv_fanbox")
    print(f"""{F.LIGHTYELLOW_EX}
> Login Status...
> Fantia: {'Logged In' if (fantia_status) else 'Guest (Not logged in)'}
> Pixiv Fanbox: {'Logged In' if (pixiv_fanbox_status) else 'Guest (Not logged in)'}
> {danbooru_profile}
{C.END}
------------ {F.LIGHTYELLOW_EX}Download Options{C.END} ------------
    {F.GREEN}1. Download Fantia Posts{C.END}
    {F.LIGHTCYAN_EX}2. Download Pixiv Illustrations{C.END}
    {F.YELLOW}3. Download Pixiv Fanbox Posts{C.END}
    {F.BLUE}4. Download Danbooru Posts{C.END}

------------- {F.LIGHTYELLOW_EX}Config Options{C.END} -------------
    {F.LIGHTBLUE_EX}5. Change Default Download Folder{C.END}""")

    if (drive_service is None):
        print(f"""    {F.LIGHTBLUE_EX}6. Add Google Drive API Key{C.END}""")
    else:
        print(f"""    {F.LIGHTBLUE_EX}6. Remove Saved Google Drive API Key{C.END}""")

    if (pixiv_api is None):
        print(f"""    {F.LIGHTBLUE_EX}7. Configure Pixiv OAuth{C.END}""")
    else:
        print(f"""    {F.LIGHTBLUE_EX}7. Remove Saved Pixiv refresh token{C.END}""")

    if (danbooru_profile.id is None):
        print(f"""    {F.LIGHTBLUE_EX}8. Add Danbooru API Key{C.END}""")
    else:
        print(f"""    {F.LIGHTBLUE_EX}8. Remove Saved Danbooru API Key{C.END}""")

    if (not fantia_status or not pixiv_fanbox_status):
        print(f"    {F.LIGHTBLUE_EX}9. Login{C.END}")
    if (fantia_status or pixiv_fanbox_status):
        print(f"    {F.LIGHTBLUE_EX}10. Logout{C.END}")

    print(f"\n------------- {F.LIGHTYELLOW_EX}Other Options{C.END} -------------")
    print(f"    {F.LIGHTRED_EX}Y. Report a bug{C.END}")
    print(f"    {F.RED}X. Shutdown the program{C.END}")
    print()

def print_fantia_menu() -> None:
    """Print the Fantia menu for the user to read and enter their desired action.

    Args:
        None

    Returns:
        None
    """
    print(f"""
------------ {F.LIGHTGREEN_EX}Fantia Download Options{C.END} ------------

  {F.LIGHTYELLOW_EX}1. Download images from Fantia post(s){C.END}
  {F.LIGHTYELLOW_EX}2. Download all Fantia posts from creator(s){C.END}
  {F.LIGHTRED_EX}B. Return to Main Menu{C.END}

-------------------------------------------------""")

def print_pixiv_fanbox_menu() -> None:
    """Print the Pixiv Fanbox menu for the user to read and enter their desired action.

    Returns:
        None
    """
    print(f"""
------------ {F.YELLOW}Pixiv Fanbox Download Options{C.END} ------------

  {F.LIGHTYELLOW_EX}1. Download images from pixiv Fanbox post(s){C.END}
  {F.LIGHTYELLOW_EX}2. Download all pixiv Fanbox posts from a creator(s){C.END}
  {F.LIGHTRED_EX}B. Return to Main Menu{C.END}

-------------------------------------------------------""")

def print_pixiv_menu() -> None:
    """Print the Pixiv menu for the user to read and enter their desired action.

    Returns:
        None
    """
    print(f"""
----------- {F.LIGHTCYAN_EX}Pixiv Download Options{C.END} -----------

  {F.LIGHTYELLOW_EX}1. Download illustration(s){C.END}
  {F.LIGHTYELLOW_EX}2. Download from artist(s)/illustrator(s){C.END}
  {F.LIGHTYELLOW_EX}3. Download using tag name(s){C.END}
  {F.LIGHTRED_EX}B. Return to Main Menu{C.END}

----------------------------------------------""")

def configure_danbooru_auth() -> None:
    while True:
        username = input("Enter Username (leave blank to cancel): ")

        if username != "":
            print(f"{F.LIGHTBLUE_EX}You can get your API key here: {C.DANBOORU_API_KEY_LOGIN}{C.END}")
            while True:    
                api_key = input("Enter API Key (leave blank to cancel, -h for help): ")

                if api_key == "-h":
                    guide_tab = webbrowser.open(C.DANBOORU_API_KEY_GUIDE_PAGE, new=1)
                    if guide_tab:
                        print_success("Opened a new tab in your browser to the guide.")
                    else:
                        print_warning(f"Failed to open browser tab. Please open the following URL manually: {C.DANBOORU_API_KEY_GUIDE_PAGE}\n")
                
                elif api_key != "":
                    try:
                        data = danbooru.get_user_data(username, api_key)

                        save_danbooru_auth(username, api_key)
                        danbooru.username = username
                        danbooru.api_key = api_key
                        danbooru.user_profile = data
                    except ValueError as error:
                        print_danger(error)
                    return
                else:
                    print()
                    break
            continue
        return

def danbooru_pool_download_menu(pool:danbooru.Pool):
    mode = "order"
    limit = pool.post_count
    direction = ">"
    pivot = 0

    while True:
        print(f"""\
Limit: {F.LIGHTYELLOW_EX}{limit}{C.END}\t\
Range: {F.LIGHTYELLOW_EX}{direction} {pivot}{C.END}\t\
By {F.LIGHTYELLOW_EX if mode == "id" else F.LIGHTBLACK_EX}id{C.END}\
/{F.LIGHTYELLOW_EX if mode == "order" else F.LIGHTBLACK_EX}order{C.END}
{pool}

-------- {F.LIGHTGREEN_EX}Customise Downloads{C.END} --------
{F.LIGHTYELLOW_EX}
1. Edit post limit
2. Edit post range
3. Toggle filter type{F.LIGHTCYAN_EX}
4. Begin download{F.LIGHTRED_EX}
B. Return
{C.END}
-------------------------------------""")
        settings = get_input("Enter command: ", inputs = ("B", "1", "2", "3", "4"))
        if settings == "1":
            limit = input("Enter new limit: ")
            while not limit.isdecimal():
                print_danger("Please enter a positive whole number.")
                limit = input("Enter new limit: ")        
            limit = min(int(limit), pool.post_count)

        elif settings == "2":
            pivot = input("Please enter a pivot point: ")
            while not pivot.isdecimal():
                print_danger("Please enter a positive whole number.")
                pivot = input("Please enter a pivot point: ")

            pivot = min(int(pivot), 10000000)
            direction = get_input("Please enter the direction relative to the pivot (\"<\" or \">\"): ", inputs = ("<", ">"))

        elif settings == "3":
            mode = "order" if mode == "id" else "id"

        elif settings == "4":
            try:
                asyncio.run(pool.save(mode, limit, direction, pivot))
                return
            except KeyboardInterrupt:
                return
        else:
            return
        print()

def danbooru_artist_download_menu(artist:danbooru.Artist):
    limit = 200
    direction = ">"
    pivot = 0
    while True:
        print(f"""\
Limit: {F.LIGHTYELLOW_EX}{limit}{C.END}\t\
Range: {F.LIGHTYELLOW_EX}{direction} {pivot}{C.END}
{artist}

-------- {F.LIGHTGREEN_EX}Customise Downloads{C.END} --------
{F.LIGHTYELLOW_EX}
1. Edit post limit
2. Edit post range{F.LIGHTCYAN_EX}
3. Begin download{F.LIGHTRED_EX}
B. Return
{C.END}
-------------------------------------""")
        settings = get_input("Enter command: ", inputs = ("B", "1", "2", "3"))
        if settings == "1":
            limit = input("Enter new limit: ")
            while not limit.isdecimal():
                print_danger("Please enter a positive whole number.")
                limit = input("Enter new limit: ")        
            limit = min(int(limit), 200)

        elif settings == "2":
            pivot = input("Please enter a pivot point: ")
            while not pivot.isdecimal():
                print_danger("Please enter a positive whole number.")
                pivot = input("Please enter a pivot point: ")

            pivot = min(int(pivot), 10000000)
            direction = get_input("Please enter the direction relative to the pivot (\"<\" or \">\"): ", inputs = ("<", ">"))

        elif settings == "3":
            try:
                asyncio.run(artist.save(limit, direction, pivot))
                return
            except KeyboardInterrupt:
                print("\rKeyboard Interrupted")
                return
        else:
            return
        print()

def danbooru_download_menu():
    while True:
        print(f"""\
----------- {F.LIGHTGREEN_EX}Danbooru Download Options{C.END} -----------
{F.LIGHTYELLOW_EX}
1. Download individual posts
2. Download images by pool
3. Download images by artist tag (200 max){F.LIGHTBLUE_EX}
4. Toggle current image size {F.LIGHTCYAN_EX}\
({danbooru.image_size}){F.LIGHTRED_EX}
B. Return to Main Menu{C.END}

-------------------------------------------------""")
        selection = get_input("Enter Command: ", inputs=("B", "1", "2", "3", "4"))
        if selection == "1":
            post_id = input("Enter post ID: ")
            while not post_id.isdecimal():
                print_danger("Please enter a positive whole number.")
                post_id = input("Enter post ID: ")

            response = danbooru.fetch_resource(post_id, "post")
            message = danbooru.verify_response(post_id, "post", response)

            if message is not None:
                print_warning(message)
            else:
                print_success("\nPost successfully fetched.")
                post = danbooru.Post(post_id, response.json(), detailed=True)
                print(post)
                if get_input("Download post? (Y/n): ", inputs=("y", "n"), default="y") == "y":
                    asyncio.run(post.save())
                
        elif selection == "2":
            pool_id = input("Enter pool ID: ")
            while not pool_id.isdecimal():
                print_danger("Please enter a positive whole number.")
                pool_id = input("Enter pool ID: ")

            response = danbooru.fetch_resource(pool_id, "pool")
            message = danbooru.verify_response(pool_id, "pool", response)

            if message is not None:
                print(message)
            else:
                print_success("\nPool successfully fetched.")
                pool = danbooru.Pool(pool_id, response.json())
                danbooru_pool_download_menu(pool)

        elif selection == "3":
            artist_id = input("Enter artist ID: ")
            while not artist_id.isdecimal():
                print_danger("Please enter a positive whole number.")
                artist_id = input("Enter artist ID: ")

            response = danbooru.fetch_resource(artist_id, "artist")
            message = danbooru.verify_response(artist_id, "artist", response)

            if message is not None:
                print(message)
            else:
                print_success("\nArtist successfully fetched.")
                artist = danbooru.Artist(artist_id, response.json())
                danbooru_artist_download_menu(artist)

        elif selection == "4":
            danbooru.image_size = "small" if danbooru.image_size == "large" else "large"

        else:
            return
        print()

def main_program(driver: webdriver.Chrome, configs: ConfigSchema) -> None:
    """Main program function."""
    login_status = {}
    drive_service = get_gdrive_service()
    pixiv_api = get_pixiv_api()
    danbooru.auto_init()

    if (user_has_saved_cookies()):
        load_cookies = get_input(
            input_msg="Do you want to load in saved cookies to the current webdriver instance? (Y/n): ",
            inputs=("y", "n"),
            default="y"
        )
        if (load_cookies == "y"):
            load_cookies_to_webdriver(driver=driver, login_status=login_status)

    fantia_login_result = pixiv_fanbox_login_result = None
    if (not login_status.get("fantia", False)):
        fantia_login_result = login(
            current_driver=driver,
            website="fantia",
            login_status=login_status
        )
    else:
        print_success(format_success_msg("Successfully loaded Fantia cookies."))

    if (not login_status.get("pixiv_fanbox", False)):
        pixiv_fanbox_login_result = login(
            current_driver=driver,
            website="pixiv_fanbox",
            login_status=login_status
        )
    else:
        print_success(format_success_msg("Successfully loaded Pixiv Fanbox cookies."))

    save_cookies(*[fantia_login_result, pixiv_fanbox_login_result])
    def download_process(website: str, creator_page: bool) -> None:
        """Download process for Fantia and Pixiv Fanbox."""
        try:
            asyncio.run(execute_download_process(
                website=website,
                creator_page=creator_page,
                download_path=configs.download_directory,
                driver=driver,
                login_status=login_status,
                drive_service=drive_service
            ))
        except (KeyboardInterrupt):
            return
        except (urllib3_exceptions.MaxRetryError):
            print_danger("Connection error, please try again later.")

    def nested_menu(website: str) -> None:
        """Nested menu for Fantia and Pixiv Fanbox."""
        while (True):
            if (website == "fantia"):
                print_fantia_menu()
            elif (website == "pixiv_fanbox"):
                print_pixiv_fanbox_menu()
            else:
                raise ValueError("Invalid website name.")

            download_option = get_input(
                input_msg="Enter download option: ",
                inputs=("1", "2", "b"),
                warning="Invalid download option, please enter a valid option from the menu above."
            )
            if (download_option == "1"):
                download_process(website=website, creator_page=False)
            elif (download_option == "2"):
                download_process(website=website, creator_page=True)
            else:
                return

    while (True):
        print_main_menu(
            login_status=login_status, 
            drive_service=drive_service,
            pixiv_api=pixiv_api,
            danbooru_profile=danbooru.user_profile
        )
        user_action = get_input(
            input_msg="Enter command: ", 
            regex=C.CMD_REGEX, 
            warning="Invalid command input, please enter a valid command from the menu above."
        )
        if (user_action == "x"):
            return

        elif (user_action == "1"):
            # Download from Fantia post(s)
            nested_menu(website="fantia")

        elif (user_action == "2"):
            # Download illustrations from Pixiv
            if (pixiv_api is None):
                temp_pixiv_api = PixivAPI()
                print_warning("Missing Pixiv refresh token, starting Pixiv OAuth process...")
                refresh_token = temp_pixiv_api.start_oauth_flow()
                if (refresh_token is not None):
                    pixiv_api = temp_pixiv_api
                else:
                    continue

            while (True):
                print_pixiv_menu()
                pixiv_download_option = get_input(
                    input_msg="Enter download option: ",
                    inputs=("1", "2", "3", "b"),
                    warning="Invalid download option, please enter a valid option from the menu above."
                )
                if (pixiv_download_option in ("1", "2", "3")):
                    convert_ugoira = get_input(
                        input_msg="Do you want to convert Ugoira to GIF? (if found) (Y/n/x to cancel): ",
                        inputs=("y", "n", "x"),
                        default="y",
                        extra_information="Note: Converting Ugoira (animated images) to gifs will take a while to convert."
                    )
                    if (convert_ugoira == "x"):
                        continue
                    convert_ugoira = (convert_ugoira == "y")

                    if (convert_ugoira):
                        delete_ugoira_zip = get_input(
                            input_msg="Do you want to delete the downloaded Ugoira zip file after converting to GIF? (Y/n/x to cancel): ",
                            inputs=("y", "n", "x"),
                            default="y"
                        )
                        if (delete_ugoira_zip == "x"):
                            continue
                        delete_ugoira_zip = (delete_ugoira_zip == "y")
                    else:
                        delete_ugoira_zip = False

                    def run_pixiv_download(illust_id_arr: Optional[list] = None, 
                                           user_id_arr: Optional[list] = None, 
                                           tag_name_arr: Optional[list] = None) -> None:
                        """Run Pixiv download process."""
                        try:
                            asyncio.run(
                                pixiv_api.download_multiple_illust(
                                    base_folder_path=configs.download_directory,
                                    convert_ugoira=convert_ugoira,
                                    illust_id_arr=illust_id_arr,
                                    user_id_arr=user_id_arr,
                                    tag_name_arr=tag_name_arr,
                                    delete_ugoira_zip=delete_ugoira_zip,
                                )
                            )
                        except (KeyboardInterrupt):
                            return

                    if (pixiv_download_option == "1"):
                        # Download illustration(s)
                        illust_ids = pixiv_get_ids_or_tags(pixiv_download_option)
                        if (illust_ids is not None):
                            run_pixiv_download(illust_id_arr=illust_ids)
                    elif (pixiv_download_option == "2"):
                        # Download from artist(s)/illustrator(s)
                        user_ids = pixiv_get_ids_or_tags(pixiv_download_option)
                        if (user_ids is not None):
                            run_pixiv_download(user_id_arr=user_ids)
                    else:
                        # Download using tag name(s)
                        tag_names = pixiv_get_ids_or_tags(pixiv_download_option)
                        if (tag_names is not None):
                            run_pixiv_download(tag_name_arr=tag_names)
                else:
                    break

        elif (user_action == "3"):
            # Download from Pixiv Fanbox post(s)
            nested_menu(website="pixiv_fanbox")

        elif (user_action == "4"):
            # Download Danbooru Posts
            danbooru_download_menu()

        elif (user_action == "5"):
            # Change Default Download Folder
            change_download_directory(configs=configs, print_message=True)
            configs = load_configs()

        elif (user_action == "6"):
            # Google Drive API key configurations
            if (drive_service is None):
                # Setup Google Drive API key
                temp_gdrive_service = None
                save_api_key = False
                while (True):
                    gdrive_api_key = get_input(
                        input_msg="Enter Google Drive API key (X to cancel, -h for guide): ",
                        regex=C.GOOGLE_API_KEY_INPUT_REGEX,
                        is_case_sensitive=True,
                        warning="Invalid Google Drive API key pattern. Please enter a valid Google Drive API key.\n"
                    )
                    if (gdrive_api_key in ("x", "X")):
                        break

                    if (gdrive_api_key == "-h"):
                        opened_guide = webbrowser.open(url=C.GDRIVE_API_KEY_GUIDE_PAGE, new=1)
                        if (opened_guide):
                            print_success(
                                "A new tab should have been opened, please follow the guide to get your Google Drive API key."
                            )
                        else:
                            print_warning(
                                f"Failed to open a new tab, please follow the guide here:\n{C.GDRIVE_API_KEY_GUIDE_PAGE}"
                            )
                        print()
                        continue

                    temp_gdrive_service = validate_gdrive_api_key(
                        gdrive_api_key, 
                        print_error=True
                    )
                    if (temp_gdrive_service is not None):
                        save_api_key = True
                        break

                if (save_api_key):
                    save_gdrive_api_key(api_key=gdrive_api_key)
                    drive_service = temp_gdrive_service
            else:
                # Remove Google Drive API key
                remove_drive_api_key = get_input(
                    input_msg="Are you sure you want to delete your saved Google Drive API Key? (y/N): ",
                    inputs=("y", "n"),
                    default="n"
                )
                if (remove_drive_api_key == "n"):
                    continue
                C.GDRIVE_API_KEY_PATH.unlink(missing_ok=True)
                drive_service = None
                print_success("Successfully deleted Google Drive API key.")

        elif (user_action == "7"):
            # Pixiv OAuth configurations
            if (pixiv_api is None):
                # Setup Pixiv OAuth
                temp_pixiv_api = PixivAPI()
                refresh_token = temp_pixiv_api.start_oauth_flow()
                if (refresh_token is not None):
                    pixiv_api = temp_pixiv_api
            else:
                # Remove Pixiv OAuth
                remove_pixiv_oauth = get_input(
                    input_msg="Are you sure you want to delete your saved Pixiv refresh token? (y/N): ",
                    inputs=("y", "n"),
                    default="n"
                )
                if (remove_pixiv_oauth == "n"):
                    continue
                C.PIXIV_REFRESH_TOKEN_PATH.unlink(missing_ok=True)
                pixiv_api = None
                print_success("Successfully deleted Pixiv refresh token.")

        elif (user_action == "8"):
            # Danbooru API key configurations
            if danbooru.username is None or danbooru.api_key is None:
                configure_danbooru_auth()
            else:
                remove_danbooru_auth = get_input(
                    input_msg="Are you sure you want to delete your saved Danbooru API key? (y/N): ",
                    inputs=("y", "n"),
                    default="n"
                )
                if (remove_danbooru_auth == "n"):
                    continue
                C.DANBOORU_AUTH_PATH.unlink(missing_ok=True)
                danbooru.username, danbooru.api_key = None, None
                danbooru.user_profile = danbooru.UserProfile(None, "Anonymous", 0, "Anonymous")
                print_success("Successfully deleted Pixiv refresh token.")

        elif (user_action == "9"):
            # Login
            fantia_logged_in = login_status.get("fantia", False)
            pixiv_fanbox_logged_in = login_status.get("pixiv_fanbox", False)
            if (fantia_logged_in and pixiv_fanbox_logged_in):
                print_warning("You are already logged in to both Fantia and Pixiv Fanbox.")
                continue

            if (not fantia_logged_in):
                fantia_login_result = login(
                    current_driver=driver,
                    website="fantia",
                    login_status=login_status
                )
            if (not pixiv_fanbox_logged_in):
                pixiv_fanbox_login_result = login(
                    current_driver=driver,
                    website="pixiv_fanbox",
                    login_status=login_status
                )
            save_cookies(*[fantia_login_result, pixiv_fanbox_login_result])

        elif (user_action == "10"):
            # logout
            fantia_logged_in = login_status.get("fantia", False)
            pixiv_fanbox_logged_in = login_status.get("pixiv_fanbox", False)
            if (not fantia_logged_in and not pixiv_fanbox_logged_in):
                print_warning("You are not logged in to either Fantia or Pixiv Fanbox.")
                continue

            if (fantia_logged_in):
                logout(driver=driver, website="fantia", login_status=login_status)
                delete_cookies("fantia")

            if (pixiv_fanbox_logged_in):
                logout(driver=driver, website="pixiv_fanbox", login_status=login_status)
                delete_cookies("pixiv_fanbox")

        else:
            # Report a bug
            opened_tab = webbrowser.open(C.ISSUE_PAGE, new=1)
            if (not opened_tab):
                print_warning(f"\nFailed to open web browser. Please visit the issue page manually and create an issue to report the bug at\n{C.ISSUE_PAGE}")
            else:
                print_success(f"\nA new tab has been opened in your web browser, please create an issue there to report the bug.")

def initialise() -> None:
    """Initialises the program and run the main program afterwards."""
    if (not C.DEBUG_MODE):
        sys.excepthook = exception_handler

    print(f"""
=========================================== {F.LIGHTBLUE_EX}CULTURED DOWNLOADER v{__version__ }{C.END} ===========================================
================================ {F.LIGHTBLUE_EX}https://github.com/KJHJason/Cultured-Downloader{C.END} =================================
======================================== {F.LIGHTBLUE_EX}Author: {__author__}, aka Dratornic{C.END} =========================================
=============================================== {F.LIGHTBLUE_EX}License: {__license__}{C.END} =================================================
{F.LIGHTYELLOW_EX}
Purpose: Allows you to download multiple images from Fantia or Pixiv Fanbox automatically.

Note:    Requires the user to login via this program for images that requires a membership.
         This program is not affiliated with Pixiv or Fantia.{C.END}
{F.RED}
Important:
Please read the term of use at https://github.com/KJHJason/Cultured-Downloader before using this program.{C.END}
""")
    with Spinner(
        message="Loading saved configs...",
        spinner_type="arc",
        colour="light_yellow",
        spinner_position="left",
        completion_msg="Successfully loaded saved configs!\n\n"
    ):
        configs = load_configs()

    # Ask before initialising the webdriver since
    # a change in the webdriver download path will
    # require the user to re-run the program.
    change_download_directory(configs=configs)

    # Check if the user has an active internet connection
    # before initialising the webdriver.
    if (not check_internet_connection()):
        print_danger("No internet connection detected. Please check your internet connection and try again.")
        return

    with get_driver(download_path=configs.download_directory) as driver:
        main_program(driver=driver, configs=configs)

def main() -> None:
    """Main function that will run the program."""
    try:
        initialise()
        print_warning("\nThe program will now shutdown...")
    except (KeyboardInterrupt, EOFError):
        print_danger("\n\nProgram terminated by user.")
    finally:
        input("Please press ENTER to quit.")

    delete_empty_and_old_logs()
    sys.exit(0)

if (__name__ == "__main__"):
    # import Python's standard libraries
    from argparse import ArgumentParser, BooleanOptionalAction
    parser = ArgumentParser(
        description="Cultured Downloader main program that lets you "\
                    "download multiple images from Fantia or Pixiv Fanbox automatically."
    )
    parser.add_argument(
        "-s", "--skip-update",
        action=BooleanOptionalAction,
        default=False,
        required=False,
        help="Skip the update check and run the program immediately."
    )
    args = parser.parse_args()

    if (not args.skip_update):
        # Import Third-party Libraries
        import httpx

        # check for latest version
        # if directly running this Python file.
        print_warning("Checking for latest version...")
        with httpx.Client(http2=True, headers=C.BASE_REQ_HEADERS) as client:
            for retry_counter in range(1, C.MAX_RETRIES + 1):
                try:
                    response = client.get(
                        "https://api.github.com/repos/KJHJason/Cultured-Downloader/releases/latest"
                    )
                    response.raise_for_status()
                except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.HTTPStatusError) as e:
                    if (retry_counter == C.MAX_RETRIES):
                        print_danger(f"Failed to check for latest version after {C.MAX_RETRIES} retries.")
                        if (isinstance(e, httpx.HTTPStatusError)):
                            if (e.response.status_code == 403):
                                print_danger("You might be rate limited by GitHub's API in which you can try again later in an hour time.")
                                print_danger("Alternatively, you can skip the update check by running the program with the --skip-update or -s flag.")
                            else:
                                print_danger(f"GitHub API returned an error with status code {e.response.status_code}...")
                        else:
                            print_danger("Please check your internet connection and try again.")

                        input("Please press ENTER to exit...")
                        sys.exit(1)

                    time.sleep(C.RETRY_DELAY)
                    continue
                else:
                    release_info = response.json()
                    latest_ver = release_info["tag_name"]
                    if (latest_ver != __version__):
                        print_danger(
                            f"New version {latest_ver} is available at " \
                            f"{release_info['html_url']}\n"
                        )
                    else:
                        print_success("You are running the latest version!\n")

                    break
    else:
        print_danger("Skipping update check...\n")

    main()