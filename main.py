import json
import logging
import threading
import telebot
from telebot import types

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram Bot Token (keeping it the same)
TOKEN = "7569096698:AAGcdJjY70uu7N5481RH-OH30fLIlVwvHX8"
bot = telebot.TeleBot(TOKEN)

# Load movies data with error handling
try:
    with open("movies.json", "r", encoding="utf-8") as file:
        movies_data = json.load(file)
except Exception as e:
    logger.error(f"Failed to load movies.json: {e}")
    movies_data = {"movies": {}}

# Convert keyword-based movies.json into an optimized format
keyword_to_links = {}
for link, keywords in movies_data.get("movies", {}).items():
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower not in keyword_to_links:
            keyword_to_links[keyword_lower] = []
        keyword_to_links[keyword_lower].append(link)

# Handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
         "👋 𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙏𝙃𝙀 𝙈𝙊𝙑𝙄𝙀 𝙄𝙉𝙑𝙄𝙏𝙀 𝘽𝙊𝙏\n\n"
        "🎬 Send me a movie name and I'll hook you up with a temporary join link.\n"
        "⏰ The link expires in 10 minutes.\n\n"
        "Enjoy the movie!"
    )
    bot.send_message(message.chat.id, welcome_text)

# Function to delete a message after a delay
def delete_message_later(chat_id, message_id, delay=1200):
    """Delete a message after the specified delay (in seconds)."""
    def delete_msg():
        try:
            bot.delete_message(chat_id, message_id)
            logger.info(f"Deleted message {message_id} from chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to delete message {message_id}: {e}")
    timer = threading.Timer(delay, delete_msg)
    timer.start()

# General message handler for movie link requests
@bot.message_handler(func=lambda message: True)
def send_movie_link(message):
    # Split the message into individual words and filter out words not in our JSON
    words = message.text.lower().split()
    valid_keywords = [word for word in words if word in keyword_to_links]

    if not valid_keywords:
        # No valid keywords found; ignore the message.
        logger.info("No valid keywords found in the message; ignoring.")
        return

    # Use the first valid keyword found
    movie_found = valid_keywords[0]
    logger.info(f"Keyword '{movie_found}' found in message: {message.text}")

    try:
        # Get the dynamic join link from the JSON mapping (choosing the first if multiple exist)
        matching_links = keyword_to_links.get(movie_found)
        join_link = matching_links[0] if matching_links else None
        if not join_link:
            bot.reply_to(message, "😕 Oops, couldn't find a link for that keyword!")
            return

        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text="🎟️ Join Now", url=join_link)
        keyboard.add(button)
        response_text = (
            f"🎥 <b>{movie_found.title()} UPLOADED HERE</b>\n\n"
            "Tap below to join (expires in 10 minutes).\n\n"
            "REQUEST WILL BE ACCEPTED WITHIN 5 MINUTES"
        )
        reply = bot.reply_to(message, response_text, parse_mode="HTML", reply_markup=keyboard)
        logger.info(f"Sent join link for keyword '{movie_found}'.")
        # Schedule deletion of the reply message in 5 minutes (300 seconds)
        delete_message_later(message.chat.id, reply.message_id, delay=300)
    except Exception as e:
        logger.error(f"Error sending join link: {e}")
        bot.reply_to(message, "😕 Something went wrong, try again later!")

if __name__ == "__main__":
    logger.info("Bot polling has started...")
    bot.polling()
