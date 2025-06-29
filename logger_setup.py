import logging
import datetime
from pathlib import Path

# Configure logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"bot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create a logger
logger = logging.getLogger("ai_bot")
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
file_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')
console_format = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
file_handler.setFormatter(file_format)
console_handler.setFormatter(console_format)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info(f"Starting bot with log file: {log_file}") 