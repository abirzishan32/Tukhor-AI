from typing import Optional
from prisma import Prisma
from utils.logger import logger
import asyncio


class DatabaseManager:
    """Singleton database connection manager"""

    _instance: Optional["DatabaseManager"] = None
    _db: Optional[Prisma] = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def get_db(cls) -> Prisma:
        """Get database connection with proper connection management"""
        if cls._instance is None:
            cls._instance = cls()

        async with cls._lock:
            if cls._db is None:
                cls._db = Prisma()

            if not cls._db.is_connected():
                try:
                    await cls._db.connect()
                    logger.info("Database connected successfully")
                except Exception as e:
                    logger.error(f"Failed to connect to database: {str(e)}")
                    raise

            return cls._db

    @classmethod
    async def disconnect(cls):
        """Disconnect from database"""
        async with cls._lock:
            if cls._db and cls._db.is_connected():
                await cls._db.disconnect()
                logger.info("Database disconnected")
            cls._db = None

    @classmethod
    async def execute(cls, operation):
        """Execute database operation with automatic connection management"""
        db = await cls.get_db()
        try:
            return await operation(db)
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            # Try to reconnect on connection errors
            if "connection" in str(e).lower() or "query engine" in str(e).lower():
                logger.info("Attempting to reconnect to database...")
                await cls.disconnect()
                db = await cls.get_db()
                return await operation(db)
            raise


# Convenience function for getting database connection
async def get_db() -> Prisma:
    return await DatabaseManager.get_db()
