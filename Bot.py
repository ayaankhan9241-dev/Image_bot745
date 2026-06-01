import os
import asyncio
import random
import logging
from telegram import Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

user_data = {}

# ✂️ Split prompts
def split_prompts(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

# ✨ Enhance prompt
def enhance_prompt(prompt, seed):
    base = "same face, same character, consistent person, cinematic lighting, ultra detailed, 4k, pixar style"
    return f"{prompt}, {base}, seed:{seed}"

# 🖼️ Generate URL (FREE)
def generate_url(prompt):
    safe_prompt = prompt.replace(" ", "%20")
    return f"https://image.pollinations.ai/prompt/{safe_prompt}"

# ⚡ Parallel processing
async def process(prompts, seed):
    loop = asyncio.get_event_loop()
    tasks = []

    for p in prompts:
        enhanced = enhance_prompt(p, seed)
        tasks.append(loop.run_in_executor(None, generate_url, enhanced))

    return await asyncio.gather(*tasks)

# 📸 Handle photo (reference face)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    seed = random.randint(1, 999999)

    user_data[user_id] = {
        "seed": seed
    }

    await update.message.reply_text(
        f"✅ Character locked (FREE MODE)\nSeed: {seed}"
    )

# 🧠 Handle prompts
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        await update.message.reply_text("❗ Pehle ek photo bhejo")
        return

    prompts = split_prompts(update.message.text)

    await update.message.reply_text(f"🎬 Generating {len(prompts)} images...")

    results = await process(prompts, user_data[user_id]["seed"])

    media = [InputMediaPhoto(url) for url in results]

    for i in range(0, len(media), 10):
        await update.message.reply_media_group(media[i:i+10])

# ▶️ Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 FREE AI BOT\n\n1. Photo bhejo\n2. Prompts bhejo (blank line se separate)"
    )

# 🚀 Main
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ FREE BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
