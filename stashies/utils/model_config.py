from pydantic import ConfigDict

MODEL_CONFIG = ConfigDict(
    str_strip_whitespace=True,  # strip leading and trailing whitespace for str types.
    populate_by_name=True,  # an aliased field may be populated by its name as given by the model attribute, as well as the alias.
    validate_assignment=True,  # revalidate the data when the model is changed.
    arbitrary_types_allowed=True,  # allow arbitrary types for field types.
    validate_return=True,  # validate the return value from call validators.
    from_attributes=True,  # read data from arbitrary objects by looking at their attributes,
    defer_build=True,  # defer model validator and serializer construction until the first model validation.
    use_attribute_docstrings=True,  #  use docstrings for field descriptions.
    validate_by_alias=True,  #  aliased field may be populated by its alias (default)
    validate_by_name=True,  #  an aliased field may be populated by its name as given by the model attribute
)
