import json
import telebot

# Your Telegram Bot Token
TOKEN = "7569096698:AAGcdJjY70uu7N5481RH-OH30fLIlVwvHX8"
bot = telebot.TeleBot(TOKEN)

# Load movies data
with open("movies.json", "r", encoding="utf-8") as file:
    movies_data = json.load(file)

# Convert keyword-based movies.json into an optimized format
keyword_to_links = {}
for link, keywords in movies_data["movies"].items():
    for keyword in keywords:
        keyword = keyword.lower()
        if keyword not in keyword_to_links:
            keyword_to_links[keyword] = []
        keyword_to_links[keyword].append(link)

@bot.message_handler(func=lambda message: True)
def send_movie_link(message):
    words = message.text.lower().split()  # Split user message into words
    found_links = set()  # Store unique links

    for word in words:
        if word in keyword_to_links:
            found_links.update(keyword_to_links[word])  # Add matching links

    if found_links:
        response = "\n".join(found_links)
        bot.reply_to(message, response)  # Send matching links
    else:
        pass  # Ignore irrelevant messages

# Start the bot
bot.polling()
