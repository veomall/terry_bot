import os
import json
from pathlib import Path
from dotenv import load_dotenv
from logger_setup import logger

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Constants
CHATS_DIR = Path("chats")
CHATS_DIR.mkdir(exist_ok=True)

# Load models configuration
def load_models_config():
    try:
        with open("models.json", "r", encoding="utf-8") as f:
            models_config = json.load(f)
        logger.info(f"Loaded {len(models_config['text'])} text models and {len(models_config['image'])} image models")
        return models_config
    except Exception as e:
        logger.error(f"Failed to load models configuration: {str(e)}")
        raise

# Load models configuration
MODELS_CONFIG = load_models_config() 