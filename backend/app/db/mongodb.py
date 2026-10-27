"""
Async MongoDB client connection management using Motor.
Provides database access, collection retrieval, and index initialization for EvalForge.
"""

from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


mongodb_manager = MongoDBManager()


async def connect_to_mongo():
    """Initializes Motor MongoDB client and sets up collection indexes."""
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    mongodb_manager.client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=2000
    )
    mongodb_manager.db = mongodb_manager.client[settings.DATABASE_NAME]

    # Initialize indexes asynchronously
    try:
        # Datasets collection
        datasets_col = mongodb_manager.db["eval_datasets"]
        await datasets_col.create_index("dataset_id", unique=True)
        await datasets_col.create_index("name")
        await datasets_col.create_index("domain")
        await datasets_col.create_index("created_at")

        # Test cases collection
        cases_col = mongodb_manager.db["test_cases"]
        await cases_col.create_index("test_case_id", unique=True)
        await cases_col.create_index("dataset_id")
        await cases_col.create_index("test_type")
        await cases_col.create_index("difficulty")
        await cases_col.create_index([("dataset_id", 1), ("test_type", 1)])

        # Synthetic generator jobs
        jobs_col = mongodb_manager.db["generator_jobs"]
        await jobs_col.create_index("job_id", unique=True)
        await jobs_col.create_index("dataset_id")
        await jobs_col.create_index("status")

        # Benchmark runs collection
        runs_col = mongodb_manager.db["benchmark_runs"]
        await runs_col.create_index("run_id", unique=True)
        await runs_col.create_index("dataset_id")
        await runs_col.create_index("target_model")
        await runs_col.create_index("status")
        await runs_col.create_index("created_at")

        # Evaluation results collection
        results_col = mongodb_manager.db["eval_results"]
        await results_col.create_index("result_id", unique=True)
        await results_col.create_index("run_id")
        await results_col.create_index("test_case_id")
        await results_col.create_index("verdict")
        await results_col.create_index([("run_id", 1), ("verdict", 1)])

        logger.info("✓ EvalForge MongoDB collections and indexes initialized successfully.")
    except Exception as e:
        logger.warning(f"Notice: MongoDB index initialization deferred or skipped: {e}")


async def close_mongo_connection():
    """Closes MongoDB connection on application shutdown."""
    if mongodb_manager.client:
        logger.info("Closing MongoDB connection...")
        mongodb_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    """Dependency helper to access current MongoDB database instance."""
    return mongodb_manager.db
