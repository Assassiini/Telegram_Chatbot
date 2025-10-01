import asyncio
import os
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# --- Setup ---
# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client (v1.x syntax)
# It automatically uses the OPENAI_API_KEY from your .env file
client = OpenAI()

# Get Telegram token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- In-memory storage for conversation history ---
# Using a dictionary to store history for each user separately
user_history = {}
model_name = "gpt-3.5-turbo"

# --- Dispatcher and Bot Initialization ---
dp = Dispatcher()

# --- HANDLER FUNCTIONS ---
@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    """
    This handler replies to /start and /help commands.
    """
    help_text = (
        "Hi! I'm a Telegram bot powered by OpenAI. Here are the commands:\n"
        "/start or /help - Show this help menu\n"
        "/clear - Clear your conversation history\n\n"
        "Just type any message to chat with me!"
    )
    await message.answer(help_text)

@dp.message(Command(commands=['clear']))
async def clear_history(message: types.Message):
    """
    This handler clears the user's conversation history.
    """
    user_id = message.from_user.id
    user_history[user_id] = []
    await message.answer("I've cleared our past conversation history.")

@dp.message()
async def handle_chat(message: types.Message):
    """
    This handler processes the user's input and generates a response using the OpenAI API.
    """
    user_id = message.from_user.id
    user_input = message.text

    # Get or create the user's history
    if user_id not in user_history:
        user_history[user_id] = []

    # Add the user's message to their history
    user_history[user_id].append({"role": "user", "content": user_input})

    logging.info(f"User {user_id} said: {user_input}")

    try:
        # Create the API call using the user's history
        response = client.chat.completions.create(
            model=model_name,
            messages=user_history[user_id]
        )
        
        bot_response = response.choices[0].message.content
        
        # Add the bot's response to the history
        user_history[user_id].append({"role": "assistant", "content": bot_response})
        
        logging.info(f"Bot response to {user_id}: {bot_response}")
        await message.answer(bot_response)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.answer("Sorry, I'm having trouble connecting to the AI model right now.")

# --- Bot Startup ---
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.info("Starting bot...")
    asyncio.run(main())