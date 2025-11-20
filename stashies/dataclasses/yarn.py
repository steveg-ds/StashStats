from pydantic import Field, BaseModel, field_validator, ValidationInfo

from typing import Optional, Dict, Any

from .yarn_photos import YarnPhotos


class Yarn(BaseModel):
    """
    Represents a yarn product in the Ravelry API.

    This Pydantic model defines the structure and validation for yarn data,
    including basic properties, physical characteristics, company information,
    and associated photos.

    - Attributes:
        - id (int): Unique identifier for the yarn (not shown in string representation)
        - name (str): Commercial name of the yarn product
        - discontinued (Optional[bool]): Flag indicating if the yarn is no longer produced
        - grams (Optional[int]): Weight of one skein in grams
        - yardage (Optional[int]): Length of one skein in yards
        - yarn_company (str): Name of the manufacturing company
        - machine_washable (Optional[bool]): Indicates if yarn can be machine washed
        - photos (Optional[YarnPhotos]): Dataclass for yarn photo URLs with multiple sizes

    - Field Aliases:
        - 'yarn_company' maps from 'yarn_company_name' in source data
        - 'photos' maps from 'first_photo' in source data
    Validation:
        Includes a field validator for 'photos' that automatically injects the yarn ID
        into the photos data before validation, ensuring photo objects reference their parent yarn.
    """

    id: int = Field(alias="id", repr=False)
    '''Unique identifier for the yarn (not included in string representation)'''

    name: str = Field(alias="name")
    '''Commercial name of the yarn product'''

    discontinued: Optional[bool] = Field(...)
    '''Indicates if the yarn has been discontinued by the manufacturer'''

    grams: Optional[int] = Field(...)
    '''Weight of one complete skein/hank in grams'''

    yardage: Optional[int] = Field(...)
    '''Length of yarn contained in one skein/hank, measured in yards'''

    yarn_company: str = Field(..., alias="yarn_company_name")
    '''Name of the company that manufactures/distributes the yarn'''

    machine_washable: Optional[bool] = Field(...)
    '''Indicates if the yarn can be safely washed in a washing machine'''

    photos: Optional['YarnPhotos'] = Field(..., alias='first_photo')
    '''Container for yarn photo URLs with multiple size variants.
       Contains URLS for square, medium, thumbnail, and small photo sizes.
       Automatically populated from the 'first_photo' field in source data.
    '''

    @field_validator('photos', mode='before')
    def set_yarn_id(cls, v: Dict[str, Any], info: ValidationInfo) -> Any:
        """
        Field validator that injects the yarn ID into photos data before validation.

        This ensures that when YarnPhotos objects are created, they have access to
        their parent yarn's ID for reference or additional processing.

        Args:
            v: The photos data dictionary from source data
            info: ValidationInfo object containing context about the validation

        Returns:
            The modified photos data with yarn_id included, or original data if None

        Note:
            Runs in 'before' mode to modify data before YarnPhotos validation occurs
        """
        if v is not None:
            v['yarn_id'] = info.data['id']

        return v
