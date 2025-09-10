import sys
import os
from loguru import logger
from app.environment import environment
# Remove default handler
logger.remove()

# Configure loguru logger
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
    enqueue=True,
    serialize=environment.ENVIRONMENT != "dev"
)

# Add file logging for production
if os.environ.get("ENVIRONMENT") == "production":
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
    )


# Create a custom logger instance
def get_logger(name: str = None):
    """Get a logger instance with the specified name"""
    if name:
        return logger.bind(name=name)
    return logger


# Export the main logger
__all__ = ["logger", "get_logger"]
