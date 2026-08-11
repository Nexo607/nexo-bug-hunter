from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from ..core.config import settings
class Base(DeclarativeBase): pass
engine=create_async_engine(settings.database_url,future=True)
Session=async_sessionmaker(engine,expire_on_commit=False)
async def get_db():
    async with Session() as s: yield s
