# import Python's standard libraries
from typing import Optional

# import third-party libraries
from pydantic import BaseModel

class DanbooruAuthSchema(BaseModel):
    """This class is used to validate the danbooru-auth.json file."""
    username: Optional[str] = None
    api_key: Optional[str] = None