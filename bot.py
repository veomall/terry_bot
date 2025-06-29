from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from logger_setup import logger
from config import TOKEN
from bot_handlers import (
    start, 
    help_command, 
    new_chat, 
    image_mode, 
    handle_model_selection,
    handle_system_prompt_choice,
    handle_photo,
    handle_message,
    setup_commands,
    translate
)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("newchat", new_chat))
    application.add_handler(CommandHandler("image", image_mode))
    application.add_handler(CommandHandler("translate", translate))
    
    # Add callback query handlers
    application.add_handler(CallbackQueryHandler(handle_model_selection, pattern="^model:"))
    application.add_handler(CallbackQueryHandler(handle_system_prompt_choice, pattern="^systemprompt:"))
    
    # Add message handler for photos
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Add message handler for text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Setup menu commands when bot starts
    application.post_init = setup_commands

    logger.info("Starting bot...")
    # Run the bot until the user presses Ctrl-C
    application.run_polling()
    logger.info("Bot stopped")

if __name__ == "__main__":
    main()