import pickle
import datetime
import traceback
from logger_setup import logger
from config import CHATS_DIR, MODELS_CONFIG

# User sessions storage
user_sessions = {}

class UserSession:
    def __init__(self):
        self.history = []
        self.current_model = None
        self.provider = None
        self.system_prompt = None
        self.is_image_mode = False
        self.last_image = None
        self.interface_language = "ru"  # По умолчанию русский язык интерфейса
        # Добавляем переменную для отслеживания генерации изображений в групповом чате
        self.group_image_generated = False
    
    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        logger.debug(f"Added message with role '{role}', content length: {len(content) if content else 0}")
    
    def clear_history(self):
        logger.debug(f"Clearing history of {len(self.history)} messages")
        self.history = []
        if self.system_prompt:
            self.add_message("system", self.system_prompt)
        self.last_image = None
    
    def set_model(self, model_name, model_type="text"):
        config = MODELS_CONFIG["text"] if model_type == "text" else MODELS_CONFIG["image"]
        if model_name in config:
            self.current_model = model_name
            if model_type == "text":
                self.provider = config[model_name]["provider"]
            else:
                self.provider = config[model_name]["provider"]
            self.is_image_mode = (model_type == "image")
            # Сбрасываем флаг генерации изображения в групповом чате при выборе модели
            self.group_image_generated = False
            logger.info(f"Model set to {model_name} ({self.provider}), image mode: {self.is_image_mode}")
            return True
        
        logger.warning(f"Attempted to set unknown model: {model_name} of type {model_type}")
        return False
    
    def reset_image_model_in_group(self):
        """Сбрасывает модель генерации изображений в групповом чате."""
        if self.is_image_mode:
            self.current_model = None
            self.provider = None
            self.group_image_generated = False
            logger.info("Reset image model in group chat")
            return True
        return False
    
    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
        logger.info(f"System prompt set: {prompt[:50]}...")
        # Clear history and add system prompt
        self.clear_history()
    
    def supports_vision(self):
        if self.current_model and not self.is_image_mode:
            return MODELS_CONFIG["text"][self.current_model].get("vision", False)
        return False
    
    def set_interface_language(self, language_code):
        """Устанавливает язык интерфейса для пользователя."""
        if language_code in ["ru", "en", "de", "fr", "es", "it"]:
            self.interface_language = language_code
            logger.info(f"Interface language set to {language_code}")
            return True
        logger.warning(f"Attempted to set unknown language: {language_code}")
        return False
    
    def get_interface_language(self):
        """Возвращает текущий язык интерфейса пользователя."""
        return self.interface_language


def save_user_session(user_id):
    """Сохраняет сессию пользователя в файл."""
    if user_id not in user_sessions:
        logger.warning(f"Attempt to save non-existent session for user {user_id}")
        return False
    
    session = user_sessions[user_id]
    
    # Skip saving if history is empty
    if not session.history:
        logger.debug(f"Skipping save for user {user_id} - empty history")
        return False
    
    try:
        chat_file = CHATS_DIR / f"user_{user_id}.pickle"
        
        # Create a serializable representation of the session
        session_data = {
            "history": session.history,
            "current_model": session.current_model,
            "provider": session.provider,
            "system_prompt": session.system_prompt,
            "is_image_mode": session.is_image_mode,
            "last_interaction": datetime.datetime.now().isoformat(),
            "interface_language": session.interface_language,
            "group_image_generated": session.group_image_generated,
        }
        
        with open(chat_file, "wb") as f:
            pickle.dump(session_data, f)
        
        logger.debug(f"Saved session for user {user_id} with {len(session.history)} messages")
        return True
    except Exception as e:
        logger.error(f"Error saving session for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False


def load_user_session(user_id):
    """Загружает сессию пользователя из файла."""
    chat_file = CHATS_DIR / f"user_{user_id}.pickle"
    
    if not chat_file.exists():
        logger.debug(f"No saved session found for user {user_id}")
        return None
    
    try:
        with open(chat_file, "rb") as f:
            session_data = pickle.load(f)
        
        logger.info(f"Loaded session for user {user_id} with {len(session_data['history'])} messages")
        
        # Create and populate session object
        session = UserSession()
        session.history = session_data["history"]
        session.current_model = session_data["current_model"]
        session.provider = session_data["provider"]
        session.system_prompt = session_data["system_prompt"]
        session.is_image_mode = session_data["is_image_mode"]
        
        # Load interface language if available
        if "interface_language" in session_data:
            session.interface_language = session_data["interface_language"]
            
        # Load group_image_generated flag if available
        if "group_image_generated" in session_data:
            session.group_image_generated = session_data["group_image_generated"]
        
        logger.debug(f"User {user_id} last interaction: {session_data.get('last_interaction', 'unknown')}")
        return session
    except Exception as e:
        logger.error(f"Error loading session for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None


def get_or_create_session(user_id):
    """Получает существующую или создает новую сессию для пользователя."""
    if user_id not in user_sessions:
        # Try to load previous session
        loaded_session = load_user_session(user_id)
        if loaded_session:
            user_sessions[user_id] = loaded_session
            logger.info(f"Loaded previous session for user {user_id}")
        else:
            user_sessions[user_id] = UserSession()
            logger.info(f"Created new session for user {user_id}")
    
    return user_sessions[user_id] 