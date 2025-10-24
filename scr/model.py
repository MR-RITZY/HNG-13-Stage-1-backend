from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, DateTime, Boolean, JSON, func
from datetime import datetime


from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class StringRecord(Base):

    __tablename__ = "sting_record"

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    value: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    is_palindrome: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unique_characters: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    character_frequency_map: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), insert_default=func.now()
    )
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, DateTime, Boolean, JSON, func
from datetime import datetime


from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class StringRecord(Base):

    __tablename__ = "string_record_analysis"

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    value: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    is_palindrome: Mapped[bool] = mapped_column(Boolean, nullable=False)
    unique_characters: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    character_frequency_map: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), insert_default=func.now()
    )
