import logging
import os
from datetime import datetime
from rich.logging import RichHandler
from dotenv import load_dotenv

load_dotenv()

def setup_logger():
    """
    Sets up the logger for the application.\n
    Creates a directory for logs if it doesn't exist and configures the logger to log to both a file and the console.
    """
    # Create a directory for logs if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up the logger
    logger = logging.getLogger("JobFIT")
    logger.setLevel(logging.DEBUG) 

    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a file handler for logging to a file
    log_file = os.path.join(log_dir, f"jobfit_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # Create a console handler for logging to the console
    rich_handler = RichHandler(rich_tracebacks=True, markup=True)
    rich_handler.setLevel(logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO)
    rich_format = logging.Formatter("%(message)s") 
    rich_handler.setFormatter(rich_format)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(rich_handler)

    # Set the logging level for specific libraries to WARNING
    # This reduces the verbosity of third-party libraries
    for lib in ["openai", "httpx", "httpcore", "urllib3", "requests", "websocket", "websockets", "matplotlib"]:
        logging.getLogger(lib).setLevel(logging.WARNING)

    return logger