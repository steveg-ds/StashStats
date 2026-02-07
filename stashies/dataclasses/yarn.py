from pydantic import Field, BaseModel, field_validator, ValidationInfo, AliasChoices

import dash_bootstrap_components as dbc
from dash import dcc

from typing import Optional, Dict, Any, List, Union, ClassVar, Set

from .yarn_photos import YarnPhotos
from ..utils.model_config import MODEL_CONFIG


class Yarn(BaseModel):
    model_config = MODEL_CONFIG

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

    company: str = Field(
        ...,
        validation_alias=AliasChoices(
            "yarn_company_name", "company_name", "company", 'yarn_company'
        ),
    )
    '''Name of the company that manufactures/distributes the yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if the yarn can be safely washed in a washing machine'''

    colorways: Optional[List[str]] = Field(default=None, init=False)

    photos: 'YarnPhotos' = Field(
        default_factory=YarnPhotos,
        validation_alias=AliasChoices('first_photo', 'photos'),
    )
    '''Container for yarn photo URLs with multiple size variants.
    '''

    @field_validator('colorways', mode='before')
    def set_colorway_list(
        cls, v: Optional[List[Dict[str, Any]]]
    ) -> Union[List[str], None]:
        if v is not None:
            return list(set(sorted([colorway['name'] for colorway in v])))
        return v

    @field_validator('photos', mode='before')
    def convert_photo_list(
        cls, v: Union[List[Dict[str, Any]], Dict[str, Any]]
    ) -> 'YarnPhotos':
        if isinstance(v, list):
            from random import choice

            v = choice(v)
        return YarnPhotos(**v)

    @field_validator('company', mode='before')
    def get_company_name(cls, v: Union[Dict[str, Any], str]) -> str:
        if isinstance(v, dict):
            return v['name']
        return v

    def create_card_display(self) -> dbc.Card:
        return dbc.Card(
            [
                dbc.CardImg(
                    src=str(self.photos.small),
                    top=True,
                    style={"width": "75%", "margin": "0 auto", "display": "block"},
                ),
                dbc.CardBody(
                    [
                        dbc.Row(dbc.Label(f"Company: {self.company}")),
                        dbc.Row(dbc.Label(f"Yardage: {self.yardage}")),
                        dbc.Row(dbc.Label(f"Grams: {self.grams}")),
                        dbc.Row(
                            dbc.Label(
                                f"Discontinued: {'No!' if self.discontinued is False else 'Yes :('}"
                            )
                        ),
                        dbc.Col(
                            dbc.Button(
                                "Add to Stash",
                                id={
                                    "type": "search-result-button",
                                    "index": str(self.id),
                                },
                                className="mt-2",
                            )
                        ),
                    ]
                ),
            ],
            className="text-center",
        )

    def create_yarn_modal_body(self):
        return dbc.Container(
            [
                dbc.Row(
                    dbc.Col(
                        [
                            dbc.Row(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("Colorway:"),
                                        dbc.Select(
                                            id='yarn-modal-colorway-select',
                                            options=self.colorways,
                                            placeholder="Select Colorway",
                                            required=True,
                                        ),
                                    ]
                                ),
                                className="mb-3",  # Add spacing between rows
                                justify='center',
                            ),
                            dbc.Row(
                                dbc.InputGroup(
                                    [
                                        dbc.InputGroupText("# of Skeins:"),
                                        dbc.Input(
                                            type='number',
                                            min=0,
                                            max=50,
                                            step=1,
                                            value=0,
                                            id='yarn-modal-skein-select',
                                        ),
                                    ]
                                ),
                                justify='center',
                            ),
                            dbc.Row(
                                children=None,
                                id='yarn-modal-quantity-row',
                            ),  # TODO: create callback that multiplies num. skeins by grams and yardage
                        ],
                        width="auto",  # Use auto width to avoid full width
                    ),
                    className="h-100",  # Make row full height
                    justify='center',
                    align='center',
                ),
            ],
            fluid=True,
            className="h-100 d-flex align-items-center justify-content-center",  # Key classes for centering
        )
