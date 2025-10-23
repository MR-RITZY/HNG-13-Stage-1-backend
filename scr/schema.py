from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class InsertString(BaseModel):
    string: str

    @field_validator("string")
    def lower_string(cls, value:str):
        return value.lower()


class ORMString(BaseModel):
    id: str
    value: str
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    character_frequency_map: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReturnString(BaseModel):
    orm_string: ORMString = Field(exclude=True)
    id: Optional[str] = None
    value: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def compute_output(self):
        orm = self.orm_string
        self.id = orm.id
        self.value = orm.value
        self.properties = {
            "length": orm.length,
            "is_palindrome": orm.is_palindrome,
            "unique_characters": orm.unique_characters,
            "word_count": orm.word_count,
            "sha256_hash": orm.id,
            "character_frequency_map": orm.character_frequency_map,
        }
        self.created_at = orm.created_at
        return self
    
class ReturnStringList(BaseModel):
    return_list: List[ReturnString]
    
    model_config = ConfigDict(from_attributes=True)
