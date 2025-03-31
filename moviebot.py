import json
import asyncio
import os
import time
import logging
from aiogram import Dispatcher, types
from aiogram.client.bot import Bot, DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the JSON file name
JSON_FILE = "movies.json"

# Check if the JSON file exists; if not, create a default structure
if not os.path.exists(JSON_FILE):
    default_data = {
        "123456789": ["movie1", "movie2"],
        "987654321": ["movie3", "movie4", "movie5"]
    }  # Replace these channel IDs with your actual channel IDs
    with open(JSON_FILE, "w") as file:
        json.dump(default_data, file, indent=4)
    logger.info(f"Created default '{JSON_FILE}' file with sample data.")

# Load movie-channel mapping from JSON file
with open(JSON_FILE, "r") as file:
    MOVIE_CHANNEL_MAP = json.load(file)
logger.info(f"Loaded movie-channel mapping from '{JSON_FILE}': {json.dumps(MOVIE_CHANNEL_MAP, indent=4)}")

# Bot token (using your provided token)
BOT_TOKEN = "7569096698:AAGcdJjY70uu7N5481RH-OH30fLIlVwvHX8"

# Initialize bot with default properties for parse_mode HTML.
# NOTE: If you are NOT behind a proxy, remove the `proxy` parameter.
bot = Bot(
    token=BOT_TOKEN,
    proxy="http://your.proxy.address:port",  # Replace with your proxy URL or remove if not needed.
    default_bot_properties=DefaultBotProperties(parse_mode="HTML")
)

# Initialize Dispatcher
dp = Dispatcher()

# Function to revoke an invite link after a delay
async def revoke_link_after_delay(chat_id: int, invite_link: str, delay: int):
    await asyncio.sleep(delay)
    logger.info(f"Revoking invite link: {invite_link} for chat {chat_id}")
    try:
        await bot.revoke_chat_invite_link(chat_id, invite_link)
    except TelegramBadRequest as e:
        logger.error(f"Failed to revoke link {invite_link} for chat {chat_id}: {e}")

# Function to generate a temporary invite link (as join request link) and schedule its revocation.
async def create_temp_invite(chat_id: int, duration: int = 600) -> str:
    expire_date = int(time.time()) + duration  # Compute Unix timestamp for expiry
    logger.info(f"Creating temporary join request link for channel ID {chat_id} that expires at {expire_date}...")
    invite = await bot.create_chat_invite_link(
        chat_id,
        expire_date=expire_date,
        creates_join_request=True
    )
    logger.info(f"Invite link created: {invite.invite_link}")
    # Schedule revocation in the background
    asyncio.create_task(revoke_link_after_delay(chat_id, invite.invite_link, duration))
    return invite.invite_link

# Handler for /start command
async def start_handler(message: types.Message):
    start_message = (
        "👋 <b>Welcome to the Movie Invite Bot!</b>\n\n"
        "🎬 Just drop a movie name in your message and I'll hook you up with a temporary join link.\n"
        "⏰ Remember: The link expires in <i>10 minutes</i> and requires admin approval.\n\n"
        "Have fun and enjoy the show! 🍿"
    )
    await message.reply(start_message, parse_mode="HTML")

# Message handler: Checks incoming messages for any movie keywords.
async def filter_and_respond(message: types.Message):
    text = message.text.lower()
    for channel_id, movies in MOVIE_CHANNEL_MAP.items():
        for movie in movies:
            if movie in text:
                logger.info(f"Detected '{movie}' in message from {message.from_user.first_name}.")
                try:
                    invite_link = await create_temp_invite(int(channel_id))
                except TelegramBadRequest as e:
                    logger.error(f"Error creating invite link for channel {channel_id}: {e}")
                    await message.reply("😕 Oops, something went wrong with the link. Try again later!", parse_mode="HTML")
                    return
                # Create an inline keyboard button for the invite link
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🎟️ Join Now", url=invite_link)]
                ])
                # Updated response text with humor and Gen Z vibes
                response_text = (
                    f"🎥 <b>{movie.title()}</b>\n\n"
                    "Tap the button below \n\n"
                    "⏳JOIN FAST : it expires in 10 minutes."
                )
                await message.reply(response_text, reply_markup=keyboard, parse_mode="HTML")
                return  # Stop after sending one invite link

async def main():
    # Register handlers using proper filters
    dp.message.register(start_handler, Command("start"))
    dp.message.register(filter_and_respond)

    logger.info("Bot is starting... Listening for messages!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped. Bye!")
