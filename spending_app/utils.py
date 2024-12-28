import json
from pydantic import BaseModel
from pydantic_core import ValidationError


def is_valid_input(schema: BaseModel, user_input: str) -> None:
    try:
        schema(value=user_input)
    except ValidationError as e:
        return False
    else:
        return True
