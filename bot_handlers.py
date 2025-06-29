import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ContextTypes

from logger_setup import logger
from config import MODELS_CONFIG
from session import user_sessions, save_user_session, get_or_create_session, UserSession
from ai_client import get_ai_response, generate_image

async def setup_commands(application):
    """Настраивает меню команд в Telegram боте."""
    commands = [
        BotCommand("newchat", "Начать новый текстовый разговор"),
        BotCommand("image", "Генерация изображений"),
        BotCommand("translate", "Перевод текста"),
        BotCommand("help", "Показать справку"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands menu has been set up")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    logger.info(f"User {user_id} (@{username}) started the bot")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    
    await update.message.reply_text(
        "Привет! Я Terry - сборник моделей AI. Используй /newchat для начала нового разговора с текстовыми моделями или /image для генерации изображений."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a more informative help message when the command /help is issued."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested help")
    
    # Get current model info if available
    current_model_info = ""
    if user_id in user_sessions and user_sessions[user_id].current_model:
        session = user_sessions[user_id]
        model_type = "image" if session.is_image_mode else "text"
        if model_type in MODELS_CONFIG and session.current_model in MODELS_CONFIG[model_type]:
            display_name = MODELS_CONFIG[model_type][session.current_model].get("display_name", session.current_model)
            current_model_info = f"\n\n🤖 *Текущая модель*: {display_name}"
            
            # Add vision capability info
            if not session.is_image_mode and session.supports_vision():
                current_model_info += "\n✅ Эта модель поддерживает анализ изображений. Отправьте фото с вопросом."
    
    help_text = (
        "*🤖 Terry*\n\n"
        "• Общение с различными AI моделями\n"
        "• Генерация изображений\n"
        "• Анализ изображений (для поддерживаемых моделей)\n"
        
        "1️⃣ Выберите модель через /newchat (для текста) или /image (для картинок)\n"
        "2️⃣ При выборе текстовой модели вы можете задать системный промпт или продолжить без него\n"
        "3️⃣ Отправляйте сообщения для общения с выбранной моделью\n"
        "4️⃣ Для моделей с поддержкой vision 👁 можно отправлять изображения с вопросами\n\n"
        f"{current_model_info}"
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.debug(f"Sent detailed help message to user {user_id}")

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session and ask user to choose a model."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started new chat")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    
    # Create buttons for text models
    keyboard = []
    for model_id, model_info in MODELS_CONFIG["text"].items():
        display_name = model_info.get("display_name", model_id)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"model:text:{model_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите текстовую модель для разговора:", reply_markup=reply_markup)
    logger.debug(f"Sent model selection menu to user {user_id}")

async def image_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to image generation mode and ask user to choose a model."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} switched to image mode")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    
    # Create buttons for image models
    keyboard = []
    for model_id, model_info in MODELS_CONFIG["image"].items():
        display_name = model_info.get("display_name", model_id)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"model:image:{model_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите модель для генерации изображений:", reply_markup=reply_markup)
    logger.debug(f"Sent image model selection menu to user {user_id}")

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle model selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    logger.info(f"User {user_id} selected model from callback: {callback_data}")
    
    # Extract model type and name from callback data
    _, model_type, model_name = callback_data.split(":", 2)
    
    # Set the model for the user session
    user_sessions[user_id].set_model(model_name, model_type)
    
    if model_type == "image":
        user_sessions[user_id].clear_history()
        provider = MODELS_CONFIG['image'][model_name]['provider']
        display_name = MODELS_CONFIG['image'][model_name].get('display_name', model_name)
        await query.edit_message_text(
            f"Выбрана модель: {display_name}\n\n"
            f"Отправьте текстовый запрос для генерации изображения."
        )
        logger.debug(f"User {user_id} selected image model {model_name}")
        save_user_session(user_id)
        return
    
    # For text models, ask about system prompt
    keyboard = [
        [InlineKeyboardButton("Задать системный промпт", callback_data="systemprompt:custom")],
        [InlineKeyboardButton("Без системного промпта", callback_data="systemprompt:none")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    vision_info = ""
    if MODELS_CONFIG["text"][model_name].get("vision", False):
        vision_info = "\n\nЭта модель поддерживает анализ изображений. Вы можете отправлять фото вместе с вопросами."
    
    display_name = MODELS_CONFIG["text"][model_name].get("display_name", model_name)
    await query.edit_message_text(
        f"Выбрана модель: {display_name}\n\n"
        f"Хотите задать системный промпт?{vision_info}",
        reply_markup=reply_markup
    )
    logger.debug(f"User {user_id} selected text model {model_name} and was shown prompt selection")
    save_user_session(user_id)

async def handle_system_prompt_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user's choice about system prompt."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    logger.info(f"User {user_id} selected prompt type: {callback_data}")
    
    _, choice = callback_data.split(":", 1)
    
    if choice == "custom":
        # User wants to set a custom system prompt
        await query.edit_message_text(
            "Пожалуйста, отправьте свой системный промпт в следующем сообщении."
        )
        context.user_data["awaiting_system_prompt"] = True
        logger.debug(f"User {user_id} is setting a custom prompt")
    
    else:  # none
        # User doesn't want a system prompt
        user_sessions[user_id].system_prompt = None
        user_sessions[user_id].clear_history()
        display_name = MODELS_CONFIG["text"][user_sessions[user_id].current_model].get("display_name", user_sessions[user_id].current_model)
        await query.edit_message_text(
            f"Новый чат создан с моделью {display_name}.\n"
            f"Системный промпт не установлен. Отправьте сообщение, чтобы начать разговор."
        )
        logger.debug(f"User {user_id} chose not to set a system prompt")
    
    save_user_session(user_id)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photos sent by users."""
    user_id = update.effective_user.id
    photo_id = update.message.photo[-1].file_id
    logger.info(f"User {user_id} sent a photo: {photo_id}")
    
    # Check if user has an active session
    session = get_or_create_session(user_id)
    
    # Check if model supports vision
    if not session.supports_vision():
        await update.message.reply_text(
            "Текущая модель не поддерживает анализ изображений. Выберите другую модель с поддержкой vision."
        )
        logger.warning(f"User {user_id} tried to use vision with non-supporting model: {session.current_model}")
        return
    
    # Get the photo file
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Store image for future use
    session.last_image = photo_bytes
    logger.debug(f"Downloaded image of size {len(photo_bytes)} bytes")
    
    # Get caption or ask for a question
    caption = update.message.caption
    
    if caption:
        # If there's a caption, process it as a question about the image
        logger.info(f"User {user_id} sent image with caption: {caption}")
        await handle_image_question(update, context, caption, photo_bytes)
    else:
        await update.message.reply_text(
            "Изображение получено. Теперь задайте вопрос или опишите, что вы хотите узнать об этом изображении."
        )
        context.user_data["awaiting_image_question"] = True
        logger.debug(f"User {user_id} uploaded image without caption, awaiting question")
    
    save_user_session(user_id)

async def handle_image_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question=None, image_bytes=None) -> None:
    """Process a question about an image."""
    user_id = update.effective_user.id
    message = update.message
    
    # If question is not provided, use the message text
    if question is None:
        question = message.text
    
    # If image is not provided, use the last image
    if image_bytes is None:
        image_bytes = user_sessions[user_id].last_image
        
        if image_bytes is None:
            await message.reply_text("Не найдено изображение для анализа. Пожалуйста, отправьте изображение вместе с вопросом.")
            logger.warning(f"User {user_id} tried to ask about an image, but no image was found")
            return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=user_id, action="typing")
    
    try:
        # Add user message to history
        user_sessions[user_id].add_message("user", question)
        
        # Get response from the model
        model = user_sessions[user_id].current_model
        provider_name = user_sessions[user_id].provider
        history = user_sessions[user_id].history
        
        logger.info(f"User {user_id} asked about image: '{question}' using {model} ({provider_name})")
        
        # Send request to g4f with image
        response = await get_ai_response(provider_name, model, history, image_bytes)
        
        # Add assistant response to history
        user_sessions[user_id].add_message("assistant", response)
        
        # Save updated session
        save_user_session(user_id)
        
        # Send the response to the user
        await message.reply_text(response)
        logger.info(f"Sent image analysis response to user {user_id}, response length: {len(response)}")
        
    except Exception as e:
        logger.error(f"Error analyzing image for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        await message.reply_text(f"Произошла ошибка при анализе изображения: {str(e)}")
    
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start translation mode."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} initiated translation mode")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    
    # Set translation mode
    context.user_data["awaiting_target_language"] = True
    
    await update.message.reply_text(
        "🌐 Режим перевода активирован.\n\n"
        "Пожалуйста, укажите язык, на который нужно перевести текст (например, 'английский', 'немецкий', 'французский' и т.д.)."
    )
    logger.debug(f"User {user_id} was asked to specify target language")

async def handle_target_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle target language selection for translation."""
    user_id = update.effective_user.id
    target_language = update.message.text
    
    logger.info(f"User {user_id} selected translation target language: {target_language}")
    
    # Store the target language
    context.user_data["translation_target_language"] = target_language
    context.user_data["awaiting_target_language"] = False
    context.user_data["awaiting_translation_text"] = True
    
    await update.message.reply_text(
        f"Язык перевода: {target_language}.\n\n"
        f"Теперь отправьте текст, который нужно перевести."
    )
    logger.debug(f"User {user_id} was asked to provide text for translation")

async def handle_translation_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text for translation."""
    user_id = update.effective_user.id
    text_to_translate = update.message.text
    target_language = context.user_data.get("translation_target_language")
    
    logger.info(f"User {user_id} sent text for translation to {target_language}: '{text_to_translate[:50]}...'")
    
    # Clear translation mode
    context.user_data["awaiting_translation_text"] = False
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=user_id, action="typing")
    
    try:
        # Create a prompt for translation
        translate_prompt = f"Переведи следующий текст на {target_language}. Верни только переведенный текст без объяснений и комментариев:\n\n{text_to_translate}"
        
        # Create temporary session for translation
        temp_session = UserSession()
        temp_session.set_model("gpt-4o", "text")
        temp_session.add_message("user", translate_prompt)
        
        # Get response from the model
        logger.info(f"Requesting translation for user {user_id} to {target_language}")
        response = await get_ai_response(temp_session.provider, temp_session.current_model, temp_session.history)
        
        # Send the translation
        await update.message.reply_text(
            f"Перевод на {target_language}:\n\n{response}"
        )
        logger.info(f"Translation sent to user {user_id}, response length: {len(response)}")
        
    except Exception as e:
        logger.error(f"Error during translation for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        await update.message.reply_text(f"Произошла ошибка при переводе: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"User {user_id} sent message: '{message_text[:30]}...' ({len(message_text)} chars)")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    
    # If we're waiting for a system prompt
    if context.user_data.get("awaiting_system_prompt", False):
        # Set the system prompt
        session.set_system_prompt(message_text)
        context.user_data["awaiting_system_prompt"] = False
        display_name = MODELS_CONFIG["text"][session.current_model].get("display_name", session.current_model)
        await update.message.reply_text(
            f"Системный промпт установлен. Новый чат создан с моделью {display_name}.\n"
            f"Отправьте сообщение, чтобы начать разговор."
        )
        logger.debug(f"User {user_id} set custom system prompt: '{message_text[:50]}...'")
        save_user_session(user_id)
        return
    
    # If we're waiting for a target language for translation
    if context.user_data.get("awaiting_target_language", False):
        await handle_target_language(update, context)
        return
    
    # If we're waiting for text to translate
    if context.user_data.get("awaiting_translation_text", False):
        await handle_translation_text(update, context)
        return
    
    # If we're waiting for a question about an image
    if context.user_data.get("awaiting_image_question", False):
        context.user_data["awaiting_image_question"] = False
        logger.debug(f"User {user_id} asked question about previously uploaded image")
        await handle_image_question(update, context)
        return
    
    # Check if model is selected
    if not session.current_model:
        await update.message.reply_text(
            "Пожалуйста, выберите модель с помощью команды /newchat перед началом разговора."
        )
        logger.warning(f"User {user_id} tried to chat without selecting a model first")
        return
    
    # Show typing indicator or upload photo indicator
    action = "upload_photo" if session.is_image_mode else "typing"
    await context.bot.send_chat_action(chat_id=user_id, action=action)
    
    try:
        if session.is_image_mode:
            # Handle image generation
            provider_name = session.provider
            model = session.current_model
            
            logger.info(f"User {user_id} requested image generation with prompt: '{message_text[:50]}...'")
            
            # Generate image
            image_url = await generate_image(provider_name, model, message_text)
            
            # Send the image
            await update.message.reply_photo(photo=image_url, caption=f"Сгенерировано с помощью {model}")
            logger.info(f"Generated and sent image to user {user_id}")
            
        else:
            # Handle text conversation
            # Add user message to history
            session.add_message("user", message_text)
            
            # Get response from the model
            model = session.current_model
            provider_name = session.provider
            history = session.history
            
            logger.info(f"Getting AI response for user {user_id} using {model} ({provider_name})")
            
            # Send request to g4f
            response = await get_ai_response(provider_name, model, history)
            
            # Add assistant response to history
            session.add_message("assistant", response)
            
            # Send the response to the user
            await update.message.reply_text(response)
            logger.info(f"Sent AI response to user {user_id}, response length: {len(response)}")
        
        # Save session after successful response
        save_user_session(user_id)
    
    except Exception as e:
        logger.error(f"Error in handle_message for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        await update.message.reply_text(f"Произошла ошибка: {str(e)}") 