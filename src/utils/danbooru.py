# import third-party libraries
from tabulate import tabulate
from colorama import init as colorama_init, Fore, Style
import httpx, asyncio, aiofiles

# import Python's standard libraries
from typing import Iterable, Literal, Union, Optional, Generator
from pathlib import Path
from time import perf_counter_ns
from json import JSONDecodeError

# import local files
if (__package__ is None or __package__ == ""):
    from constants import CONSTANTS
    from spinner import Spinner
    from functional import get_input, print_success, print_warning, print_danger, load_configs
    from user_data import load_danbooru_auth, save_danbooru_auth
    from errors import TooManyRequests, ApiKeyError
else:
    from .constants import CONSTANTS
    from .spinner import Spinner
    from .functional import get_input, print_success, print_warning, print_danger, load_configs
    from .user_data import load_danbooru_auth, save_danbooru_auth
    from .errors import TooManyRequests, ApiKeyError

# -------- Danbooru Data Objects --------
class Post():
    def __init__(self, id:int, data:dict, detailed:bool = False) -> None:
        if "bad_id" in data.get("tag_string_meta"):
            self.source = None
        elif data.get("pixiv_id") is not None:
            self.source = f"https://www.pixiv.net/en/artworks/{data.get('pixiv_id')}" # If pixiv source
        else:
            self.source = data.get("source")
            if self.source == "":
                self.source = None

        self.id = id
        self.md5 = data.get("md5")
        self.tag_string_general = set(data.get("tag_string_general").split())
        self.is_banned = data.get("is_banned")

        if detailed:
            characters = data.get("tag_string_character")
            if characters == "":
                self.characters = f"{Fore.LIGHTYELLOW_EX}N.A.{Style.RESET_ALL}"
            else:
                characters = characters.split()
                self.characters = [character.replace("_", " ").title() for character in characters[:3]]
                if len(characters) > 3:
                    self.characters.append(f"{Fore.LIGHTYELLOW_EX}And {len(characters) - 3} more...{Style.RESET_ALL}")
                self.characters = "\n".join(self.characters)
            
            artists = data.get("tag_string_artist")
            if artists == "":
                self.artists = f"{Fore.LIGHTYELLOW_EX}N.A.{Style.RESET_ALL}"
            else:
                artists = artists.split()
                self.artists = [artist.replace("_", " ").title() for artist in artists[:3]]
                if len(artists) > 3:
                    self.artists.append(f"{Fore.LIGHTYELLOW_EX}And {len(artists) - 3} more...{Style.RESET_ALL}")
                self.artists = "\n".join(self.artists)

            copyrights = data.get("tag_string_copyright")
            if copyrights == "":
                self.copyrights = f"{Fore.LIGHTYELLOW_EX}N.A.{Style.RESET_ALL}"
            else:
                copyrights = copyrights.split()
                self.copyrights = [copyright.replace("_", " ").title() for copyright in copyrights[:3]]
                if len(copyrights) > 3:
                    self.copyrights.append(f"{Fore.LIGHTYELLOW_EX}And {len(copyrights) - 3} more...{Style.RESET_ALL}")
                self.copyrights = "\n".join(self.copyrights)

        if image_size == "small": # This makes sense don't think too much about it.
            self.file_url = data.get("large_file_url")
        elif image_size == "large": # Both have the same value in the event the image is small.
            self.file_url = data.get("file_url")

    def __str__(self):
        try:
            return tabulate(
                tabular_data = [(self.id, self.artists, self.characters, self.copyrights)],
                headers = ("Post", "Artist(s)", "Character(s)", "Copyright(s)"),
                tablefmt = "simple_grid",
                disable_numparse = True,
            )
        except AttributeError:
            raise AttributeError("\"detailed\" variable must be set to \"True\"!")

    def check_valid(self) -> Optional[str]:
        source = ""
        if self.is_banned:
            if self.source is not None:
                source = f"The image can be downloaded manually from '{self.source}'."
                message = f"{Fore.YELLOW}Post {self.id} has been banned from Danbooru. {source}{Style.RESET_ALL}"
        elif self.tag_string_general.intersection({"loli", "shota", "toddlercon"}):
            if self.source is not None:
                source = f"The image can be downloaded manually from '{self.source}'."
            message = f"{Fore.YELLOW}Post {self.id} is Danbooru Gold exclusive only. {source}{Style.RESET_ALL}"
        else:
            message = None
        return message

    async def save(self) -> None:
        message = self.check_valid()
        if message is not None:
            print_warning(message)
            return
        
        filepath = directory.joinpath(f"Post_{self.id}.{self.file_url.rsplit('.', 1)[-1]}")
        if filepath.is_file():
            print_warning(f"File \"{filepath.name}\" already exists.")

        async with httpx.AsyncClient() as client:
            await download_async_group(self.file_url, client, filepath)

class Pool():
    def __init__(self, id:int, data:dict) -> None:
        self.id = id
        self.name = data.get("name").replace("_", " ").title()
        self.posts = data.get("post_ids")
        self.post_count = len(self.posts)

    def __str__(self) -> str:
        return tabulate(
            tabular_data = [(self.id, self.post_count, self.name)],
            headers = ("Pool", "Posts", "Name"),
            tablefmt = "simple_grid",
            disable_numparse = True,
            maxcolwidths = [None, None, 75]
        )

    async def save(self, mode:str, limit:int, direction:str, pivot:int) -> None:
        if mode == "id":
            if direction == ">":
                posts = sorted(filter(lambda id: id > pivot, self.posts))[:limit]
            elif direction == "<":
                posts = sorted(filter(lambda id: id < pivot, self.posts))[-limit:]

        elif mode == "order":
            if direction == ">":
                posts = self.posts[pivot: limit + pivot]
            elif direction == "<":
                posts = self.posts[max(0, pivot - limit): pivot]

        now = perf_counter_ns()
        complete = 0
        spinner_message = f"Downloading images.. {{complete}}/{len(posts)} ({{percent}}%)"

        folder = directory.joinpath(self.name)
        if folder.is_dir():
            print_warning(f"Folder \"{folder.name}\" already exists.")
        folder.mkdir(parents=True, exist_ok=True)

        messages = []
        with Spinner(spinner_message.format(complete=0, percent=0), colour="yellow", spinner_position="left", spinner_type="material", completion_msg="Done", cancelled_msg="Cancelled\n") as spinner:
            async with httpx.AsyncClient() as client:
                try:
                    for async_group in generate_async_group(posts):
                        data = await asyncio.gather(*(fetch_async_group(
                                    client = client, 
                                    post_id = post) 
                                for post in async_group))
                        
                        valid = []
                        for index, id in enumerate(async_group):
                            response = data[index]
                            message = verify_response(id, "post", response)
                            if message is not None:
                                messages.append(message)
                            else:
                                post = Post(id, response.json())
                                message = post.check_valid()
                                messages.append(message) if message is not None else valid.append(post)
                                
                        if mode == "id": # Post_<id>
                            await asyncio.gather(*(download_async_group(
                                    url = post.file_url, 
                                    client = client, 
                                    filepath = folder.joinpath(f"Post_{post.id}.{post.file_url.rsplit('.', 1)[-1]}"))
                                for post in valid))

                        elif mode == "order": # Page_<num>
                            await asyncio.gather(*(download_async_group(
                                    url = post.file_url, 
                                    client = client, 
                                    filepath = folder.joinpath(f"Page_{complete+index+1}.{post.file_url.rsplit('.', 1)[-1]}"))
                                for index, post in enumerate(valid)))

                        complete += len(async_group)
                        spinner.message = spinner_message.format(complete=complete, percent=round(complete/self.post_count*100, 2))

                except TooManyRequests as error:
                    spinner.stop(error=True)
                    print_danger(error)
                except KeyboardInterrupt:
                    spinner.stop(manually_stopped=True)
            
        print(f"\n[Process complete in {round((perf_counter_ns() - now)/1000000000, 2)}s]")
        if messages:
            if get_input("Some images were not downloaded. See more information? (Y/n):", inputs=("y", "n"), default="y") == "y":
                print(*messages, sep="\n")

class Artist():
    def __init__(self, id:int, data:dict):
        self.id = id
        self.name = data.get("name")

        self.group = data.get("group_name").replace("_", " ").title()
        if self.group == "":
            self.group = f"{Fore.LIGHTYELLOW_EX}N.A.{Style.RESET_ALL}"

        aliases = data.get("other_names")
        self.alias = [alias.replace("_", " ").title() for alias in aliases[:3]]
        if len(aliases) > 3:
            self.alias.append(f"{Fore.LIGHTYELLOW_EX}And {len(aliases) - 3} more...{Style.RESET_ALL}")
        self.alias = "\n".join(self.alias)

        self.is_banned = data.get("banned")

    def __str__(self):
        return tabulate(
            tabular_data=[(self.id, self.name.replace("_", " ").title(), self.group, self.alias)],
            headers = ("ID", "Name", "Group", "Alias"),
            tablefmt = "simple_grid",
            disable_numparse = True
        )

    async def save(self, limit:int, direction:str, pivot:int) -> None:
        response = httpx.get(
            url = "https://danbooru.donmai.us/posts.json", auth = get_auth(),
            params = {
                "limit": limit,
                "tags": self.name,
                "page": ("a" if direction == ">" else "b") + str(pivot) # b<id>, a<id>
            })

        message = verify_response(self.id, "artist", response)
        if message is not None:
            print(message)
            return

        folder = directory.joinpath(self.name)
        if folder.is_dir():
            print_warning(f"Folder \"{folder.name}\" already exists.")
        folder.mkdir(parents=True, exist_ok=True)

        messages = {"gold": 0, "banned": 0, "source":[]}
        now = perf_counter_ns()
        complete = 0
        spinner_message = f"Downloading images.. {{complete}}/{len(response.json())} ({{percent}}%)"

        with Spinner(spinner_message.format(complete=0, percent=0), colour="yellow", spinner_position="left", spinner_type="material", completion_msg="Done", cancelled_msg="Cancelled\n") as spinner:
            async with httpx.AsyncClient() as client:
                # try:
                    for async_group in generate_async_group(response.json()):
                        valid = []
                        for data in async_group:
                            if data.get("id") is None:
                                if data.get("pixiv_id") is not None:
                                    messages.get("source").append(f"https://www.pixiv.net/en/artworks/{data.get('pixiv_id')}") # If pixiv source
                                elif "bad_id" not in data.get("tag_string_meta"):
                                    messages.get("source").append(data.get("source"))

                                if self.is_banned:
                                    messages["banned"] += 1
                                elif set(data.get("tag_string_general")).intersection({"loli", "shota", "toddlercon"}):
                                    messages["gold"] += 1   
                            else:
                                valid.append(Post(data.get("id"), data))

                            await asyncio.gather(*(download_async_group(
                                url = post.file_url, 
                                client = client, 
                                filepath = folder.joinpath(f"Post_{post.id}.{post.file_url.rsplit('.', 1)[-1]}"))
                            for post in valid))

                        complete += len(async_group)
                        spinner.message = spinner_message.format(complete=complete, percent=round(complete/limit*100, 2))

                # except TooManyRequests as error:
                #     spinner.stop(error=True)
                #     print_danger(error)
                #     for task in asyncio.all_tasks():
                #         task.cancel()
                # except KeyboardInterrupt:
                #     spinner.stop(manually_stopped=True)
                #     for task in asyncio.all_tasks():
                #         task.cancel()
                #     print("Cancelling")
            
        print(f"\n[Process complete in {round((perf_counter_ns() - now)/1000000000, 2)}s]")
        if messages.get("gold") + messages.get("banned") != 0:
            sources = '\n- '.join(messages.get('source'))
            if get_input("Some images were not downloaded. See more information? (Y/n):", inputs=("y", "n"), default="y") == "y":
                print(f"""\
Danbooru Gold Exclusive: {Fore.LIGHTYELLOW_EX}{messages.get('gold')}{Style.RESET_ALL}\t\
Banned: {Fore.LIGHTYELLOW_EX}{messages.get('banned')}{Style.RESET_ALL}
The following images can be manually downloaded:
-{sources}""")       

# ---------- Helper Functions ----------
def fetch_resource(id:int, type:str) -> httpx.Response:
    if type not in {"post", "pool", "artist"}:
        raise Exception("Type variable can only be \"post\", \"pool\" or \"artist\"!")
    
    response = httpx.get(url = f"https://danbooru.donmai.us/{type}s/{id}.json", auth = get_auth())
    return response

def verify_response(id:int, type:str, response:httpx.Response) -> Optional[str]:
    if response.status_code > 399:
        if response.status_code == 401:
            message = f"{Fore.LIGHTRED_EX}Error with API key/username, please re-configure.{Style.RESET_ALL}"
        elif response.status_code == 403:
            message = f"{Fore.LIGHTRED_EX}API key does not have the necessary permissions, please re-configure.{Style.RESET_ALL}"
        if response.status_code == 404:
            message = f"{Fore.LIGHTRED_EX}{type.capitalize()} {id} was not found.{Style.RESET_ALL}"
        else:
            try:
                data = response.json()
                message = f"{Fore.LIGHTRED_EX} Error {response.status_code}: {data.get('message')} [{data.get('error')}]{Style.RESET_ALL}"
            except JSONDecodeError:
                message = f"{Fore.LIGHTRED_EX}Error {response.status_code}: Unknown error{Style.RESET_ALL}"
    else:
        message = None
    return message

def generate_async_group(post_ids:Iterable[int]) -> Generator[int, None, None]:
    start, length = 0, len(post_ids)

    for limit, step in group_generation:
        end = (length + 1) if limit is None else (start + limit)
        
        for index in range(start, end, step):
                yield post_ids[index: min(end, index+step)]

        if limit is None or length <= limit:
            return
        start += limit

def legacy_generate_async_group(post_ids:Iterable[int], length:int=3) -> Generator[int, None, None]:
    if length > 5:
        print(f"{Fore.YELLOW}Warning: An async group of larger than 5 (e.g. 10) may result in '429: Too Many Requests' for large pools.{Fore.RESET}")
    for index in range(0, len(post_ids), length):
        yield post_ids[index: index+length]

async def fetch_async_group(client:httpx.AsyncClient, post_id:int) -> dict:
    response = await client.get(f"https://danbooru.donmai.us/posts/{post_id}.json")
    if response.status_code == 429:
        raise TooManyRequests("The server is unable to handle the large number of posts queries; please try again later.")
    return response

async def download_async_group(url:Union[str, Path], client:httpx.AsyncClient, filepath:Union[str, Path]) -> None:
    async with client.stream("GET", url) as response, aiofiles.open(filepath, "wb") as file:
        async for chunk in response.aiter_bytes(CONSTANTS.CHUNK_SIZE):
            await file.write(chunk)

def get_auth():
    if username is None or api_key is None:
        return None
    else:
        return (username, api_key)

# --------- User Data Management ---------
class UserProfile():
    # Default values from: https://danbooru.donmai.us/profile.json
    def __init__(self, id:Optional[int]=None, name:str="Anonymous", level:int=0, level_string:str="Anonymous"):
        self.id = id
        self.name = name
        self.level = level
        self.level_string = level_string

    def __str__(self):
        username = "Guest" if self.name == "Anonymous" else self.name
        user_level = "Not logged in" if self.level_string == "Anonymous" else self.level_string
        return f"Danbooru: {username} ({user_level})"

    def __repr__(self):
        return tabulate(
            tabular_data = [(self.id, self.name, f"{self.level_string} [{self.level}]")],
            headers = ("User ID", "Username", "Level"),
            tablefmt = "simple_grid",
            disable_numparse = True
        )

def get_user_data(username:Optional[str]=None, api_key:Optional[str]=None) -> UserProfile:
    if username is None or api_key is None:
        auth = get_auth()
    else:
        auth = (username, api_key)

    response = httpx.get(url = "https://danbooru.donmai.us/profile.json", auth = auth)
    message = verify_response(username, "User", response)

    if message is not None:
        raise ValueError(message)
    else:
        data = response.json()
        return UserProfile(data.get("id"), data.get("name"), data.get("level"), data.get("level_string"))

# ------ Initialise global values ------
username:Optional[str] = None
api_key:Optional[str] = None
image_size:Literal["large", "small"] = "large"
directory:Path = Path(load_configs().download_directory)
group_generation:tuple[tuple[Optional[int], int]] = ((50, 10), (50, 5), (400, 4), (None, 3))
user_profile:UserProfile = UserProfile(None, "Anonymous", 0, "Anonymous") # Default values for non-users

def auto_init():
    global username, api_key, user_profile

    user_data = load_danbooru_auth()
    if user_data is not None:
        username = user_data.get("username")
        api_key = user_data.get("api_key")
    else: # Something wrong, use default configurations
        username, api_key = None, None

    try:
        user_profile = get_user_data()
    except ValueError as error:
        # print_danger(error)
        user_profile = UserProfile(None, "Anonymous", 0, "Anonymous")

colorama_init()

__all__ = ["api_key", "username", "user_profile", "directory", "image_size", "fetch_resource", 
        "generate_async_group", "fetch_async_group", "download_async_group",
        "Post", "Pool", "Artist"]

if __name__ == "__main__":
    # print(load_danbooru_auth())
    print(user_profile)
    print(repr(user_profile))