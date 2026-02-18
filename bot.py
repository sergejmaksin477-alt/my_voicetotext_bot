import os
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["8319299806:AAHfKdzaUTZnhOZ_TlQPqoIBNToqQrjm6d8"]
GROQ_API_KEY = os.environ["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"]

async def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                data={"model": "whisper-large-v3-turbo", "response_format": "text"},
                files={"file": ("audio.ogg", f, "audio/ogg")},
            )
    response.raise_for_status()
    return response.text.strip()

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ Транскрибирую...")
    
    voice = update.message.voice or update.message.audio
    tg_file = await context.bot.get_file(voice.file_id)
    
    file_path = f"/tmp/{voice.file_id}.ogg"
    await tg_file.download_to_drive(file_path)
    
    try:
        text = await transcribe_audio(file_path)
        await msg.edit_text(f"📝 {text}")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")
    finally:
        os.remove(file_path)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))

if __name__ == "__main__":
    app.run_polling()
```

**`requirements.txt`**
```
python-telegram-bot==21.6
httpx==0.27.0
```

**`Procfile`** (нужен для Railway)
```
worker: python bot.py