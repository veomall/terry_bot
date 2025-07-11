"""
Модуль с текстами интерфейса бота на разных языках.
"""

TRANSLATIONS = {
    # Русский (по умолчанию)
    "ru": {
        # Команды и описания
        "cmd_newchat": "Начать новый текстовый разговор",
        "cmd_image": "Генерация изображений",
        "cmd_translate": "Перевод текста",
        "cmd_language": "Изменить язык интерфейса",
        "cmd_help": "Показать справку",
        
        # Приветствия и общие фразы
        "welcome": "Привет! Я Terry - сборник моделей AI. Используй /newchat для начала нового разговора с текстовыми моделями или /image для генерации изображений.",
        "error_occurred": "Произошла ошибка: {}",
        
        # Выбор модели
        "select_text_model": "Выберите текстовую модель для разговора:",
        "select_image_model": "Выберите модель для генерации изображений:",
        "model_selected": "Выбрана модель: {}",
        "send_image_prompt": "Отправьте текстовый запрос для генерации изображения.",
        
        # Групповой чат
        "select_model_for_next_image": "Для создания ещё одного изображения в групповом чате, пожалуйста, снова выберите модель используя команду /image",
        
        # Системный промпт
        "system_prompt_question": "Хотите задать системный промпт?{}",
        "set_system_prompt": "Задать системный промпт",
        "no_system_prompt": "Без системного промпта",
        "send_system_prompt": "Пожалуйста, отправьте свой системный промпт в следующем сообщении.",
        "system_prompt_set": "Системный промпт установлен. Новый чат создан с моделью {}.\nОтправьте сообщение, чтобы начать разговор.",
        "chat_created_no_prompt": "Новый чат создан с моделью {}.\nСистемный промпт не установлен. Отправьте сообщение, чтобы начать разговор.",
        
        # Vision и обработка изображений
        "vision_capability": "\n\nЭта модель поддерживает анализ изображений. Вы можете отправлять фото вместе с вопросами.",
        "no_vision_support": "Текущая модель не поддерживает анализ изображений. Выберите другую модель с поддержкой vision.",
        "image_received": "Изображение получено. Теперь задайте вопрос или опишите, что вы хотите узнать об этом изображении.",
        "no_image_found": "Не найдено изображение для анализа. Пожалуйста, отправьте изображение вместе с вопросом.",
        "image_error": "Произошла ошибка при анализе изображения: {}",
        "generated_with": "Сгенерировано с помощью {}",
        
        # Перевод
        "translation_mode_activated": "🌐 Перевод\n\nПожалуйста, укажите язык, на который нужно перевести текст (например, 'английский', 'немецкий', 'французский' и т.д.).",
        "translation_language_selected": "Язык перевода: {}.\n\nТеперь отправьте текст, который нужно перевести.",
        "translation_result": "Перевод на {}:\n\n{}",
        "translation_error": "Произошла ошибка при переводе: {}",
        
        # Выбор языка интерфейса
        "language_selection": "Выберите язык интерфейса бота:",
        "language_set": "Язык интерфейса изменен на {}",
        
        # Справка
        "help_title": "*🤖 Terry*\n\n",
        "help_features": "• Общение с различными AI моделями\n• Генерация изображений\n• Анализ изображений (для поддерживаемых моделей)\n• Перевод текста\n\n",
        "help_instructions": "1️⃣ Выберите модель через /newchat (для текста) или /image (для картинок)\n2️⃣ При выборе текстовой модели вы можете задать системный промпт или продолжить без него\n3️⃣ Отправляйте сообщения для общения с выбранной моделью\n4️⃣ Для моделей с поддержкой vision 👁 можно отправлять изображения с вопросами\n5️⃣ Используйте /translate для перевода текста\n6️⃣ Используйте /language для изменения языка интерфейса",
        "current_model_vision": "\n✅ Эта модель поддерживает анализ изображений. Отправьте фото с вопросом.",
        
        # Ошибки
        "select_model_first": "Пожалуйста, выберите модель с помощью команды /newchat перед началом разговора.",
        
        # Названия языков для отображения
        "language_name_ru": "Русский",
        "language_name_en": "Английский",
        "language_name_be": "Беларусский",
    },
    
    # English
    "en": {
        # Commands and descriptions
        "cmd_newchat": "Start a new text conversation",
        "cmd_image": "Generate images",
        "cmd_translate": "Translate text",
        "cmd_language": "Change interface language",
        "cmd_help": "Show help",
        
        # Greetings and common phrases
        "welcome": "Hello! I'm Terry - a collection of AI models. Use /newchat to start a new conversation with text models or /image to generate images.",
        "error_occurred": "An error occurred: {}",
        
        # Model selection
        "select_text_model": "Choose a text model for conversation:",
        "select_image_model": "Choose a model for image generation:",
        "model_selected": "Selected model: {}",
        "send_image_prompt": "Send a text prompt for image generation.",
        
        # Group chat
        "select_model_for_next_image": "To create another image in a group chat, please select a model again using the /image command",
        
        # System prompt
        "system_prompt_question": "Do you want to set a system prompt?{}",
        "set_system_prompt": "Set system prompt",
        "no_system_prompt": "No system prompt",
        "send_system_prompt": "Please send your system prompt in the next message.",
        "system_prompt_set": "System prompt set. New chat created with model {}.\nSend a message to start the conversation.",
        "chat_created_no_prompt": "New chat created with model {}.\nNo system prompt set. Send a message to start the conversation.",
        
        # Vision and image processing
        "vision_capability": "\n\nThis model supports image analysis. You can send photos with questions.",
        "no_vision_support": "The current model doesn't support image analysis. Choose another model with vision support.",
        "image_received": "Image received. Now ask a question or describe what you want to know about this image.",
        "no_image_found": "No image found for analysis. Please send an image with your question.",
        "image_error": "An error occurred while analyzing the image: {}",
        "generated_with": "Generated with {}",
        
        # Translation
        "translation_mode_activated": "🌐 Translation\n\nPlease specify the language to translate to (for example, 'English', 'German', 'French', etc.).",
        "translation_language_selected": "Translation language: {}.\n\nNow send the text you want to translate.",
        "translation_result": "Translation to {}:\n\n{}",
        "translation_error": "An error occurred during translation: {}",
        
        # Interface language selection
        "language_selection": "Select the bot's interface language:",
        "language_set": "Interface language changed to {}",
        
        # Help
        "help_title": "*🤖 Terry*\n\n",
        "help_features": "• Communication with various AI models\n• Image generation\n• Image analysis (for supported models)\n• Text translation\n",
        "help_instructions": "1️⃣ Choose a model via /newchat (for text) or /image (for images)\n2️⃣ When choosing a text model, you can set a system prompt or continue without it\n3️⃣ Send messages to interact with the selected model\n4️⃣ For models with vision 👁 support, you can send images with questions\n5️⃣ Use /translate to translate text\n6️⃣ Use /language to change the interface language",
        "current_model_vision": "\n✅ This model supports image analysis. Send a photo with a question.",
        
        # Errors
        "select_model_first": "Please select a model using the /newchat command before starting a conversation.",
        
        # Language names for display
        "language_name_ru": "Russian",
        "language_name_en": "English",
        "language_name_be": "Belarusian",
    },
    
    # Belarusian
    "be": {
        # Commands and descriptions
        "cmd_newchat": "Пачаць новую размову",
        "cmd_image": "Стварыць выявы",
        "cmd_translate": "Перакласьці тэкст",
        "cmd_language": "Зьмяніць мову інтэрфэйсу",
        "cmd_help": "Паказаць даведку",

        # Greetings and common phrases
        "welcome": "Прывітаньне! Я Terry - склад мадэляў AI. Выкарыстоўвайце /newchat для пачатку новай размовы з тэкставымі мадэлямі або /image для стварэньня выявы.",
        "error_occurred": "Адбылася памылка: {}",

        # Model selection
        "select_text_model": "Выберыце тэкставую мадэль для размовы:",
        "select_image_model": "Выберыце мадэль для стварэньня выявы:",
        "model_selected": "Выбраная мадэль: {}",
        "send_image_prompt": "Адпраўце тэкставы запыт для стварэньня выявы.",
        
        # Group chat
        "select_model_for_next_image": "Для стварэньня яшчэ аднаго выявы ў групавым чаце, калі ласка, зноў выберыце мадэль выкарыстоўваючы каманду /image",
        
        # System prompt
        "system_prompt_question": "Хочаце задаць сыстэмны прампт?{}",
        "set_system_prompt": "Задаць сыстэмны прампт",
        "no_system_prompt": "Без сыстэмнага прампту",
        "send_system_prompt": "Адпраўце свой сыстэмны прампт у наступным паведамленьні.",
        "system_prompt_set": "Сыстэмны прампт усталяваны. Новая размова створаная з мадэльлю {}.\nАдпраўце паведамленьне, каб пачаць размову.",
        "chat_created_no_prompt": "Новая размова створаная з мадэльлю {}.\nСыстэмны прампт не ўсталяваны. Адпраўце паведамленьне, каб пачаць размову.",
        
        # Vision and image processing
        "vision_capability": "\n\nГэтая мадэль падтрымлівае аналіз выявы. Вы можаце адправіць фота з пытаньнем.",
        "no_vision_support": "Гэтая мадэль не падтрымлівае аналіз выявы. Выберыце іншую мадэль з падтрымкай vision.",
        "image_received": "Выява атрыманая. Задайце пытаньне або апішыце, што вы хочаце ведаць пра гэтую выяву.",
        "no_image_found": "Выява ня знойдзеная для аналізу. Адпраўце выяву з пытаньнем.",
        "image_error": "Адбылася памылка пры аналізе выявы: {}",
        "generated_with": "Створана з дапамогай {}",
        
        # Translation
        "translation_mode_activated": "🌐 Пераклад\n\nКалі ласка, укажыце мову, на якую вы хочаце перакласьці (напрыклад, 'ангельская', 'нямецкая', 'француская' і г.д.).",
        "translation_language_selected": "Мова перакладу: {}.\n\nЦяпер адпраўце тэкст, які вы хочаце перакласьці.",
        "translation_result": "Пераклад на {}:\n\n{}",
        "translation_error": "Адбылася памылка пры перакладзе: {}",
        
        # Interface language selection
        "language_selection": "Выберыце мову інтэрфэйсу бота:",
        "language_set": "Мова інтэрфэйсу зьмененая на {}",
        
        # Help
        "help_title": "*🤖 Terry*\n\n",
        "help_features": "• Размова з рознымі AI мадэлямі\n• Стварэньне выявы\n• Аналіз выявы (для падтрымоўваных мадэляў)\n• Пераклад тэксту\n",
        "help_instructions": "1️⃣ Выберыце мадэль праз /newchat (для тэксту) або /image (для выявы)\n2️⃣ Пры выбары тэкставай мадэлі вы можаце задаць сыстэмны прампт або працягнуць безь яго\n3️⃣ Адпраўляйце паведамленьні для размовы з выбранай мадэльлю\n4️⃣ Для мадэляў з падтрымкай vision 👁 можна адправіць выявы з пытаньнем\n5️⃣ Выкарыстоўвайце /translate для перакладу тэксту\n6️⃣ Выкарыстоўвайце /language для зьмены мовы інтэрфэйсу",
        "current_model_vision": "\n✅ Гэтая мадэль падтрымлівае аналіз выявы. Адпраўце фота з пытаньнем.",
        
        # Errors
        "select_model_first": "Выберыце мадэль праз /newchat перад пачаткам размовы.",
        
        # Language names for display
        "language_name_ru": "Расейская",
        "language_name_en": "Ангельская",
        "language_name_be": "Беларуская"
    },
}

def get_text(key, lang="ru", *args, **kwargs):
    """
    Возвращает переведенный текст по ключу для указанного языка.
    Если перевод не найден, возвращает текст на русском языке.
    Поддерживает форматирование строк через args и kwargs.
    """
    # Проверяем, что язык существует, иначе используем русский
    if lang not in TRANSLATIONS:
        lang = "ru"
    
    # Получаем перевод для указанного языка или для русского, если перевод не найден
    text = TRANSLATIONS[lang].get(key) or TRANSLATIONS["ru"].get(key) or key
    
    # Если есть аргументы для форматирования, применяем их
    if args or kwargs:
        try:
            text = text.format(*args, **kwargs)
        except Exception:
            # В случае ошибки форматирования возвращаем исходный текст
            pass
    
    return text 