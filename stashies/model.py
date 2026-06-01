from pydantic.dataclasses import dataclass
from pydantic import Field, ValidationError
from typing import Dict, Any, List, Union, Optional
from .base_req import Req
from .base import Base
from .dataclasses import Yarn


@dataclass
class Model(Base):
    # TODO: eventually I should set up redis/ memory caching to reduce API hits
    REQ: 'Req' = Field(default_factory=Req)

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
    ) -> Union[List['Yarn'], None]:

        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}

        data: Optional[Dict[str, Any]] = self.REQ.get_request(
            endpoint="yarns/search.json", params=params
        )

        if data is not None:
            yarns = [Yarn(**yarn) for yarn in data['yarns']]
            return yarns
        return None

    def create_stash(self, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        import os
        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/create.json"
        return self.REQ.post_request(endpoint=endpoint, data=stash_data)

    def get_full_yarn(self, yarn_id: Union[str, int]) -> Optional['Yarn']:

        try:
            result = self.REQ.get_request(
                endpoint=f"yarns/{yarn_id}.json", params={'include': 'colorways'}
            )
            if result is not None:
                yarn = Yarn(**result['yarn'])
                yarn.colorways = result['colorways']

                return yarn

            return None
        except ValidationError as e:
            self.LOGGER.error(e)
        except Exception as e:
            self.LOGGER.error(e)
