from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Dict, Any, List, Union, Optional
from .base_req import Req
from .dataclasses import Yarn


@dataclass
class Model:
    req: 'Req' = Field(default_factory=Req)

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
    ) -> Union[List['Yarn'], None]:

        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}

        data: Optional[Dict[str, Any]] = self.req.get_request(
            endpoint="/yarns/search.json", params=params
        )
        if data is not None:
            yarns = [Yarn(**yarn) for yarn in data['yarns']]
            return yarns
        return None

    def search_colorways(self, yarn_id: int) -> Union[List[str], None]:

        params = {"include": "colorways"}

        try:
            data: Optional[Dict[str, Any]] = self.req.get_request(
                endpoint=f"yarns/{yarn_id}.json", params=params
            )
            if data is not None:

                return [colorway['name'] for colorway in data['colorways']]
        except Exception as e:
            print(e)
        return None
