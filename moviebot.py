import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.bot import DefaultBotProperties

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7569096698:AAGcdJjY70uu7N5481RH-OH30fLIlVwvHX8"

# Initialize bot and dispatcher using DefaultBotProperties for parse_mode="HTML"
bot = Bot(token=BOT_TOKEN, default_bot_properties=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Hardcoded mapping of channel IDs to movie keywords
MOVIE_CHANNEL_MAP = {
    "-1002309176330": [
        "rekhachithram",
        "construction",
        "interstellar",
        "mismatched",
        "operation",
        "romancham",
        "aavesham",
        "changer",
        "chhaava",
        "premalu",
        "singham",
        "animal",
        "devara",
        "bright",
        "dragon",
        "kaduva",
        "london",
        "movies",
        "mufasa",
        "pushpa",
        "catch",
        "kalki",
        "lucky",
        "movie",
        "marco",
        "mummy",
        "sanam",
        "2025",
        "deva",
        "fail",
        "home",
        "scam",
        "qalb",
        "your",
        "arm",
        "kgf",
        "mrs",
        "new",
        "rrr",
        "changer",
        "new",
        "jawaani",
        "pani"
    ],
    "-1002693696153": [
        "malayalam",
        "jathakam",
        "kathalan",
        "lucifer",
        "officer",
        "ponman"
    ],
    "-1002628543872": [
        "spiderman",
        "marvel",
        "thanos",
        "iron",
        "thor"
    ],
    "-1002478438004": [
        "bromance",
        "identity"
    ],
    "-1002607286522": [
        "empuraan",
        "empuran"
    ],
    "-1002469491741": [
        "mirzapur",
        "america",
        "endgame",
        "plankto",
        "alice",
        "moana"
    ],
    "-1002530496282": [
        "painkili"
    ],
    "-1002510009165": [
        "anpodu"
    ],
    "-1002550304596": [
        "baby",
        "officer",
        "duty"
    ]
}

# /start command handler
async def start_handler(message: types.Message):
    welcome_text = (
        "👋 <b>Welcome to the Movie Invite Bot!</b>\n\n"
        "🎬 Send me a movie name and I'll hook you up with a temporary join link.\n"
        "⏰ The link expires in 10 minutes.\n\n"
        "Enjoy the movie!"
    )
    await message.reply(welcome_text)

# Message handler that looks for movie keywords
async def movie_handler(message: types.Message):
    text = message.text.lower()
    # Iterate over each channel and its keyword list
    for channel_id, movies in MOVIE_CHANNEL_MAP.items():
        for movie in movies:
            if movie in text:
                logger.info(f"Keyword '{movie}' found in message: {text}")
                try:
                    # Calculate expiry timestamp (10 minutes from now)
                    expire_date = int(time.time()) + 600
                    # Create a temporary invite link (join request) for the specific channel
                    invite = await bot.create_chat_invite_link(
                        chat_id=int(channel_id),
                        expire_date=expire_date,
                        creates_join_request=True
                    )
                    keyboard = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="🎟️ Join Now", url=invite.invite_link)]
                        ]
                    )
                    response_text = (
                        f"🎥 <b>{movie.title()}</b>\n\n"
                        "Tap below to join (expires in 10 minutes)."
                    )
                    await message.reply(response_text, reply_markup=keyboard)
                    logger.info(f"Sent invite link for channel {channel_id} using keyword '{movie}'.")
                except TelegramBadRequest as e:
                    logger.error(f"Error creating invite link for channel {channel_id}: {e}")
                    await message.reply("😕 Something went wrong, try again later!")
                return  # Exit once the first matching movie has been handled
    # Optional: Log if no keyword was found
    logger.info("No matching movie keyword found in the message.")

async def main():
    dp.message.register(start_handler, Command("start"))
    dp.message.register(movie_handler)
    logger.info("Bot is starting... Listening for messages!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped. Bye!")
