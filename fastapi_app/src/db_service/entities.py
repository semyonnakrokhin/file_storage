import datetime
from typing import Optional

from sqlalchemy import BigInteger, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# from fastapi_app.src.database import Base


class Base(DeclarativeBase):
    pass


class FileOrm(Base):
    __tablename__ = "file_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    tag: Mapped[Optional[str]]
    size: Mapped[int] = mapped_column(BigInteger)
    mime_type: Mapped[str]
    modification_time: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.datetime.utcnow
    )

    _table_args__ = (UniqueConstraint("name", "mime_type", name="uq_name_mimetype"),)

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.id}, {self.name}, {self.tag}, {self.mime_type})"
        )

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if key != "_sa_instance_state"
        }
