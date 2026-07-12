import os
import logging
import tempfile
import sys
from pathlib import Path
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

# User preferences (simple in-memory storage)
user_preferences = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋\n\n"
        "I'm a Text-to-Speech bot. Send me any text and I'll convert it to speech!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/lang - Change language\n"
        "/help - Get help\n\n"
        "Just send me any text message and I'll reply with an audio file."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "🤖 How to use this bot:\n\n"
        "1. Simply send me any text message\n"
        "2. I'll convert it to speech and send you an audio file\n"
        "3. Use /lang to change the language\n\n"
        "Supported languages: English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi\n\n"
        "Default language: English"
    )

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu."""
    keyboard = []
    row = []
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Select your preferred language:",
        reply_markup=reply_markup
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    user_preferences[user_id] = {'lang': lang_code}
    
    await query.edit_message_text(
        f"✅ Language set to: {LANGUAGES[lang_code]}\n\n"
        f"Now send me any text to convert to speech!"
    )

async def text_to_speech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert text to speech and send audio."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Check if text is too long
    if len(text) > 5000:
        await update.message.reply_text(
            "⚠️ Text is too long! Please send text under 5000 characters."
        )
        return
    
    # Get user's language preference
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    
    # Send typing action
    await update.message.chat.send_action(action="record_voice")
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        # Convert text to speech
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(temp_path)
        
        # Send audio file
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"🔊 Text-to-Speech (Language: {LANGUAGES[lang]})",
                title="TTS Audio",
                performer="TTS Bot"
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error in text_to_speech: {e}")
        await update.message.reply_text(
            "❌ Sorry, an error occurred while converting text to speech. Please try again."
        )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text(
        "🎤 I can only convert text messages to speech. Please send me a text message!"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    # Get token from environment variable with better error handling
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.info("Please set TELEGRAM_BOT_TOKEN in your Railway environment variables")
        sys.exit(1)  # Exit with error code
    
    logger.info("✅ Bot token found, starting bot...")
    
    try:
        # Create application
        application = Application.builder().token(token).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("lang", language_menu))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
        
        # Add message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_to_speech))
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        logger.info("🚀 Bot is starting...")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
