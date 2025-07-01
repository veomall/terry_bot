import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ContextTypes

from logger_setup import logger
from config import MODELS_CONFIG
from session import user_sessions, save_user_session, get_or_create_session, UserSession
from ai_client import get_ai_response, generate_image
from translations import get_text, TRANSLATIONS

async def setup_commands(application):
    """Настраивает меню команд в Telegram боте."""
    commands = [
        BotCommand("newchat", "Начать новый текстовый разговор"),
        BotCommand("image", "Генерация изображений"),
        BotCommand("translate", "Перевод текста"),
        BotCommand("language", "Изменить язык интерфейса"),
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
    lang = session.get_interface_language()
    
    await update.message.reply_text(get_text("welcome", lang))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a more informative help message when the command /help is issued."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested help")
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Get current model info if available
    current_model_info = ""
    if user_id in user_sessions and user_sessions[user_id].current_model:
        session = user_sessions[user_id]
        model_type = "image" if session.is_image_mode else "text"
        if model_type in MODELS_CONFIG and session.current_model in MODELS_CONFIG[model_type]:
            display_name = MODELS_CONFIG[model_type][session.current_model].get("display_name", session.current_model)
            current_model_info = get_text("current_model", lang, display_name)
            
            # Add vision capability info
            if not session.is_image_mode and session.supports_vision():
                current_model_info += get_text("current_model_vision", lang)
    
    help_text = (
        get_text("help_title", lang) +
        get_text("help_features", lang) +
        get_text("help_instructions", lang) +
        current_model_info
    )
    
    await update.message.reply_text(help_text, parse_mode="Markdown")
    logger.debug(f"Sent detailed help message to user {user_id}")

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new chat session and ask user to choose a model."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started new chat")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Create buttons for text models
    keyboard = []
    for model_id, model_info in MODELS_CONFIG["text"].items():
        display_name = model_info.get("display_name", model_id)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"model:text:{model_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("select_text_model", lang), reply_markup=reply_markup)
    logger.debug(f"Sent model selection menu to user {user_id}")

async def image_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to image generation mode and ask user to choose a model."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} switched to image mode")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Create buttons for image models
    keyboard = []
    for model_id, model_info in MODELS_CONFIG["image"].items():
        display_name = model_info.get("display_name", model_id)
        keyboard.append([InlineKeyboardButton(display_name, callback_data=f"model:image:{model_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("select_image_model", lang), reply_markup=reply_markup)
    logger.debug(f"Sent image model selection menu to user {user_id}")

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language change command."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested language change")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    current_lang = session.get_interface_language()
    
    # Create buttons for language selection
    keyboard = []
    for lang_code in ["ru", "en", "be"]:
        # Get language name in user's current language
        lang_name_key = f"language_name_{lang_code}"
        lang_name = get_text(lang_name_key, current_lang)
        
        # Add visual indicator for currently selected language
        button_text = f"✓ {lang_name}" if lang_code == current_lang else lang_name
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"lang:{lang_code}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("language_selection", current_lang), reply_markup=reply_markup)
    logger.debug(f"Sent language selection menu to user {user_id}")

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle interface language selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    logger.info(f"User {user_id} selected language from callback: {callback_data}")
    
    # Extract language code from callback data
    _, lang_code = callback_data.split(":", 1)
    
    # Get user session and set language
    session = get_or_create_session(user_id)
    session.set_interface_language(lang_code)
    save_user_session(user_id)
    
    # Get language name for the selected language
    lang_name_key = f"language_name_{lang_code}"
    lang_name = get_text(lang_name_key, lang_code)
    
    # Confirm language change in the new selected language
    await query.edit_message_text(get_text("language_set", lang_code, lang_name))
    logger.debug(f"User {user_id} changed interface language to {lang_code}")

async def handle_model_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle model selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    callback_data = query.data
    logger.info(f"User {user_id} selected model from callback: {callback_data}")
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Extract model type and name from callback data
    _, model_type, model_name = callback_data.split(":", 2)
    
    # Set the model for the user session
    user_sessions[user_id].set_model(model_name, model_type)
    
    if model_type == "image":
        user_sessions[user_id].clear_history()
        provider = MODELS_CONFIG['image'][model_name]['provider']
        display_name = MODELS_CONFIG['image'][model_name].get('display_name', model_name)
        await query.edit_message_text(
            f"{get_text('model_selected', lang, display_name)}\n\n"
            f"{get_text('send_image_prompt', lang)}"
        )
        logger.debug(f"User {user_id} selected image model {model_name}")
        save_user_session(user_id)
        return
    
    # For text models, ask about system prompt
    keyboard = [
        [InlineKeyboardButton(get_text("set_system_prompt", lang), callback_data="systemprompt:custom")],
        [InlineKeyboardButton(get_text("no_system_prompt", lang), callback_data="systemprompt:none")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    vision_info = ""
    if MODELS_CONFIG["text"][model_name].get("vision", False):
        vision_info = get_text("vision_capability", lang)
    
    display_name = MODELS_CONFIG["text"][model_name].get("display_name", model_name)
    await query.edit_message_text(
        f"{get_text('model_selected', lang, display_name)}\n\n"
        f"{get_text('system_prompt_question', lang, vision_info)}",
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
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    _, choice = callback_data.split(":", 1)
    
    if choice == "custom":
        # User wants to set a custom system prompt
        await query.edit_message_text(get_text("send_system_prompt", lang))
        context.user_data["awaiting_system_prompt"] = True
        logger.debug(f"User {user_id} is setting a custom prompt")
    
    else:  # none
        # User doesn't want a system prompt
        user_sessions[user_id].system_prompt = None
        user_sessions[user_id].clear_history()
        display_name = MODELS_CONFIG["text"][user_sessions[user_id].current_model].get("display_name", user_sessions[user_id].current_model)
        await query.edit_message_text(get_text("chat_created_no_prompt", lang, display_name))
        logger.debug(f"User {user_id} chose not to set a system prompt")
    
    save_user_session(user_id)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photos sent by users."""
    user_id = update.effective_user.id
    photo_id = update.message.photo[-1].file_id
    logger.info(f"User {user_id} sent a photo: {photo_id}")
    
    # Check if user has an active session
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Check if model supports vision
    if not session.supports_vision():
        await update.message.reply_text(get_text("no_vision_support", lang))
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
        await update.message.reply_text(get_text("image_received", lang))
        context.user_data["awaiting_image_question"] = True
        logger.debug(f"User {user_id} uploaded image without caption, awaiting question")
    
    save_user_session(user_id)

async def handle_image_question(update: Update, context: ContextTypes.DEFAULT_TYPE, question=None, image_bytes=None) -> None:
    """Process a question about an image."""
    user_id = update.effective_user.id
    message = update.message
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # If question is not provided, use the message text
    if question is None:
        question = message.text
    
    # If image is not provided, use the last image
    if image_bytes is None:
        image_bytes = user_sessions[user_id].last_image
        
        if image_bytes is None:
            await message.reply_text(get_text("no_image_found", lang))
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
        await message.reply_text(get_text("image_error", lang, str(e)))

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start translation mode."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} initiated translation mode")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # Set translation mode
    context.user_data["awaiting_target_language"] = True
    
    await update.message.reply_text(get_text("translation_mode_activated", lang))
    logger.debug(f"User {user_id} was asked to specify target language")

async def handle_target_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle target language selection for translation."""
    user_id = update.effective_user.id
    target_language = update.message.text
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    logger.info(f"User {user_id} selected translation target language: {target_language}")
    
    # Store the target language
    context.user_data["translation_target_language"] = target_language
    context.user_data["awaiting_target_language"] = False
    context.user_data["awaiting_translation_text"] = True
    
    await update.message.reply_text(get_text("translation_language_selected", lang, target_language))
    logger.debug(f"User {user_id} was asked to provide text for translation")

async def handle_translation_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text for translation."""
    user_id = update.effective_user.id
    text_to_translate = update.message.text
    target_language = context.user_data.get("translation_target_language")
    
    # Get user session for language
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
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
        await update.message.reply_text(get_text("translation_result", lang, target_language, response))
        logger.info(f"Translation sent to user {user_id}, response length: {len(response)}")
        
    except Exception as e:
        logger.error(f"Error during translation for user {user_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        await update.message.reply_text(get_text("translation_error", lang, str(e)))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    logger.info(f"User {user_id} sent message: '{message_text[:30]}...' ({len(message_text)} chars)")
    
    # Initialize user session
    session = get_or_create_session(user_id)
    lang = session.get_interface_language()
    
    # If we're waiting for a system prompt
    if context.user_data.get("awaiting_system_prompt", False):
        # Set the system prompt
        session.set_system_prompt(message_text)
        context.user_data["awaiting_system_prompt"] = False
        display_name = MODELS_CONFIG["text"][session.current_model].get("display_name", session.current_model)
        await update.message.reply_text(get_text("system_prompt_set", lang, display_name))
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
        await update.message.reply_text(get_text("select_model_first", lang))
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
            await update.message.reply_photo(
                photo=image_url, 
                caption=get_text("generated_with", lang, model)
            )
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
        await update.message.reply_text(get_text("error_occurred", lang, str(e))) 