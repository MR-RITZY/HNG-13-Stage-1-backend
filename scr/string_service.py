from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import Depends
from hashlib import sha256
from collections import Counter
from lark import Lark

from scr.db import get_db
from scr.model import StringRecord
from scr.string_analysis import filter_query_by_conditions
from scr.lark_transformer import NLTransformer
from scr.lang_analysis import preprocess_query
from scr.lark_lang import lang
from scr.lang_analysis import build_filters
from scr.log import error_log  
import traceback

db = Annotated[AsyncSession, Depends(get_db)]

parser = Lark(lang, start="start", parser="earley")
transformer = NLTransformer()


class StringAnalysis:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def insert_string(self, string: str):

        string_data = {
            "id": sha256(string.encode()).hexdigest(),
            "value": string,
            "length": len("".join(string.split(" "))),
            "is_palindrome": (string.lower() == string[::-1].lower()),
            "unique_characters": len(set(list(string))),
            "word_count": len(string.split(" ")),
            "character_frequency_map": dict(Counter(string)),
        }

        try:
            string_model = StringRecord(**string_data)
            self.db.add(string_model)
            await self.db.commit()
            await self.db.refresh(string_model)
            return string_model
        except IntegrityError as e:
            await self.db.rollback()
            print(f"IntegrityError: {str(e)}")
            return None

    async def get_string_by_value(self, value: str):
        result = await self.db.scalars(
            select(StringRecord).where(StringRecord.value == value)
        )
        return result.first()

    async def get_strings_by_condition(self, conditions: dict):
        result = await self.db.scalars(
            select(StringRecord).where(*filter_query_by_conditions(conditions))
        )
        return result.all()

    
    async def delete_strings_by_value(self, value: str):
        result = await self.db.execute(
            delete(StringRecord).where(StringRecord.value==value)
        )
        self.db.commit()
        return result.rowcount
    
    async def get_strings_from_natural_lang(self, query: str):
    
        try:
            cleaned = preprocess_query(query)
            
            tree = parser.parse(cleaned)
            parsed = transformer.transform(tree)
            
            filters = build_filters(parsed, StringRecord)
            
            stmt = select(StringRecord)
            if filters:
                stmt = stmt.where(*filters)
            
            results = await self.db.scalars(stmt)
            return results.all()
            
        except Exception as e:
            print(f"Error parsing query: {e}")
            print(f"Cleaned query: {cleaned if 'cleaned' in locals() else query}")
            traceback.print_exc()
            return None

async def get_string_analysis(db:db):
        return StringAnalysis(db)