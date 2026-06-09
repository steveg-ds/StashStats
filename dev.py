import os
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from typing import Optional, Dict, Any, ClassVar
from pydantic.dataclasses import dataclass

from stashies import Req


if __name__ == "__main__":
    load_dotenv()
    req = Req(
        API_USERNAME=os.getenv("API_USERNAME") or "",
        API_KEY=os.getenv("API_KEY") or ""
    )
    print(req.get_request(endpoint='current_user.json'))