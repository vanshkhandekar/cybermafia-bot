import telebot
import re
import requests
import os
from bs4 import BeautifulSoup

# 🪄 Tumhara real bot token yahan hardcoded:
BOT_TOKEN = "5924901610:AAEihZbSgRgx3U2dP88hTGspYkBqJ7D46oU"  # <-- Tumhara token

bot = telebot.TeleBot(BOT_TOKEN)

TERABOX_REGEX = r'(https?://[^\s]+terabox\.com/s/[^\s]+)'

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 
    """👋 **Welcome to Cyber Mafia's Bot!** ❤️

Send me any TeraBox video link (even multiple links at once) — I’ll fetch and deliver them directly to you as video or audio.  

If you face any issues or need help, feel free to DM me anytime.  
I’m always here to assist you. ⚡

Enjoy using the bot and thanks for trusting Cyber Mafia! 🔥
""", parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def handle_links(message):
    links = re.findall(TERABOX_REGEX, message.text)
    if not links:
        bot.reply_to(message, "❌ No valid TeraBox links found. Please send correct link(s).")
        return

    bot.send_message(message.chat.id, f"⏳ Processing {len(links)} link(s)...")

    for link in links:
        try:
            bot.send_message(message.chat.id, f"🔍 Fetching video from: {link}")
            real_url = get_real_download_link(link)

            # Ask user: audio or video?
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(
                telebot.types.InlineKeyboardButton("🎵 Audio", callback_data=f"audio|{real_url}"),
                telebot.types.InlineKeyboardButton("🎥 Video", callback_data=f"video|{real_url}")
            )
            bot.send_message(message.chat.id, "Choose format:", reply_markup=markup)

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Failed to process: {link}\nReason: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    choice, url = call.data.split("|")
    try:
        file_path = download_temp_file(url)
        caption = f"✅ Here’s your {choice} from Cyber Mafia’s Bot"

        if choice == "audio":
            bot.send_audio(call.message.chat.id, audio=open(file_path, 'rb'), caption=caption)
        else:
            bot.send_document(call.message.chat.id, open(file_path, 'rb'), caption=caption)

        os.remove(file_path)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Failed to send file.\nReason: {e}")

def get_real_download_link(link):
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(link, headers=headers, timeout=10)
    if r.status_code != 200:
        raise Exception("Failed to open page")

    soup = BeautifulSoup(r.text, 'html.pa
