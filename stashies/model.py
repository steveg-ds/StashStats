from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Dict, Any, List, Union, Optional
from .base_req import Req
from .dataclasses import Yarn


@dataclass
class Model:
    req: 'Req' = Field(default_factory=Req)

    def search_yarn(
        self, query: str, sort: str = "best", page_size: int = 10
    ) -> Union[List['Yarn'], None]:
        ENDPOINT: str = "/yarns/search.json"

        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}

        data: Optional[Dict[str, Any]] = self.req.get_request(
            endpoint=ENDPOINT, params=params
        )
        if data is not None:
            return [Yarn(**yarn) for yarn in data['yarns']]
        return None
