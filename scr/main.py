from fastapi import FastAPI, Depends, status, Query
from contextlib import asynccontextmanager, AsyncExitStack
from typing import Annotated, Optional

from scr.db import db_lifepan
from scr.log import info_log 
from scr.schema import InsertString, ReturnString, ReturnStringList
from scr.string_service import StringAnalysis, get_string_analysis
from scr.exc import (
    StringAlreadyExistsException,
    register_exc,
    StringNotFoundException,
    UnparsableNaturalLanguageException,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    info_log.info("Setting up start-ups")
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(db_lifepan())
        info_log.info("Start-ups Successfully Completed -- App is live now")
        yield
        info_log.info("Shutting down and cleaning up resources")


app = FastAPI(lifespan=lifespan)
register_exc(app)


string_analysis = Annotated[StringAnalysis, Depends(get_string_analysis)]


@app.get("/strings/filter-by-natural-language", response_model=ReturnStringList)
async def get_string_by_nl(
    string_analysis: string_analysis,
    query: str = Query(..., description="Natural language query"),
):
    string = await string_analysis.get_strings_from_natural_lang(query.lower())
    if not string:
        raise UnparsableNaturalLanguageException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unable to parse natural language query -- "
                "Bad query or String with such description doesn't in the system",
            ),
        )
    return ReturnStringList(
    return_list=[ReturnString(orm_string=s) for s in string])


@app.get("/strings", response_model= ReturnStringList)
async def get_string(
    string_analysis: string_analysis,
    length: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    min_word_count: Optional[int] = None,
    max_word_count: Optional[int] = None,
    character_count: Optional[str] = None,
    min_character_count: Optional[str] = None,
    max_character_count: Optional[str] = None,
    contains_character: Optional[str] = None,
    startswith: Optional[str] = None,
    endswith: Optional[str] = None,
    unique_characters: Optional[int] = None,
    is_palindrome: Optional[bool] = None,
):

    conditions = {
        "length": length,
        "min_length": min_length,
        "max_length": max_length,
        "word_count": word_count,
        "min_word_count": min_word_count,
        "max_word_count": max_word_count,
        "character_count": character_count,
        "min_character_count": min_character_count,
        "max_character_count": max_character_count,
        "contains_character": contains_character,
        "startswith": startswith,
        "endswith": endswith,
        "unique_characters": unique_characters,
        "is_palindrome": is_palindrome,
    }

    string = await string_analysis.get_strings_by_condition(conditions)
    if not string:
        raise StringNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "String Not Found. " "Register string to database by POST /strings"
            ),
        )
    return ReturnStringList(
    return_list=[ReturnString(orm_string=s) for s in string]
)


@app.get("/strings/{string_value}")
async def get_string(string_value: str, string_analysis: string_analysis):
    string = await string_analysis.get_string_by_value(string_value.lower())
    if not string:
        raise StringNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "String Not Found. " "Register string to database by POST /strings"
            ),
        )
    return ReturnString(orm_string=string)

@app.post("/strings", status_code=status.HTTP_201_CREATED, response_model=ReturnString)
async def insert_new_string(strings: InsertString, string_analysis: string_analysis):
    result = await string_analysis.insert_string(strings.string.lower())
    if not result:
        raise StringAlreadyExistsException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String Already Exists. Retrieve string from GET /strings/string_value",
        )
    return ReturnString(orm_string=result)


@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_string(string_value: str, string_analysis: string_analysis):
    rowcount = await string_analysis.delete_strings_by_value(string_value.lower())
    if not rowcount:
        raise StringNotFoundException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Can't Be Deleted -- String doesn't exists in system",
        )
    return {}


