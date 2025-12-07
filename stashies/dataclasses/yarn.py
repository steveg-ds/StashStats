from pydantic import Field, BaseModel, field_validator, ValidationInfo

import dash_bootstrap_components as dbc
from dash import html

from typing import Optional, Dict, Any, List, Union, ClassVar, Set

from .yarn_photos import YarnPhotos
from ..utils.model_config import MODEL_CONFIG


class Yarn(BaseModel):
    model_config = MODEL_CONFIG

    result_params: ClassVar[Set[str]] = Field(
        default={'discontinued', 'grams', 'yardage'}, init=False, repr=False
    )

    id: int = Field(alias="id")
    '''API Yarn ID'''

    name: str = Field(alias="name")
    '''Name of the yarn product'''

    discontinued: Optional[bool] = Field(...)
    '''Indicates if the yarn has been discontinued by the manufacturer'''

    grams: Optional[int] = Field(...)
    '''Weight of one complete skein/hank in grams'''

    yardage: Optional[int] = Field(...)
    '''Length of yarn contained in one skein/hank, measured in yards'''

    company: str = Field(..., alias="yarn_company_name")
    '''Name of the company that manufactures/distributes the yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if the yarn can be safely washed in a washing machine'''

    colorways: Optional[List[str]] = Field(default=None, init=False)

    photos: 'YarnPhotos' = Field(default_factory=YarnPhotos, alias='first_photo')
    '''Container for yarn photo URLs with multiple size variants.
    '''

    @field_validator('colorways', mode='before')
    def set_colorway_list(
        cls, v: Optional[List[Dict[str, Any]]]
    ) -> Union[List[str], None]:
        if v is not None:
            return [colorway['name'] for colorway in v]
        return v

    def create_card_display(self) -> dbc.Card:
        return dbc.Card(
            [
                dbc.CardImg(src=str(self.photos.thumbnail), top=True),
                dbc.CardBody(
                    [
                        html.H4(self.company, className="card-title"),
                        dbc.Row(dbc.Label(f"Yardage: {self.yardage}")),
                        dbc.Row(dbc.Label(f"Grams: {self.grams}")),
                        dbc.Row(
                            dbc.Label(
                                f"Discontinued: {'No!' if self.discontinued is False else 'Yes :('}"
                            )
                        ),
                        dbc.CardFooter(
                            [
                                dbc.Col(dbc.Button("Add to Stash", id=str(self.id))),
                            ]
                        ),
                    ]
                ),
            ],
        )
