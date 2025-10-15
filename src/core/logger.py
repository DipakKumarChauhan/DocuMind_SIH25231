"""
Centralized logging configuration for DocuMind.
Uses loguru for structured, beautiful logs.
"""

import sys
from pathlib import Path

from loguru import logger

from src.core.config import settings


def setup_logger():
    """Configure logger with file and console handlers."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler with rotation
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info("Logger initialized successfully")
    return logger


# Initialize logger
app_logger = setup_logger()
