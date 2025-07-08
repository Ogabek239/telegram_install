import os
from dotenv import load_dotenv
import logging
import instaloader
import shutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# .env faylni yuklash
load_dotenv()
BOT_TOKEN = os.getenv("token")

# Log sozlamasi
logging.basicConfig(level=logging.INFO)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Salom! Instagram'dan video yuborishim uchun post yoki reel linkni yuboring.")

# Video yuklab beruvchi funksiya
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Bu Instagram linki emas.")
        return

    await update.message.reply_text("⏳ Video yuklab olinmoqda...")

    try:
        # Instaloader sozlamasi
        loader = instaloader.Instaloader(
            download_videos=True,
            save_metadata=False,
            dirname_pattern="video"
        )

        # Instagram sessiyani yuklash (cookie orqali)
        loader.load_session_from_file("vision_samarqand")

        # Shortcode ajratish
        if "/reel/" in url:
            shortcode = url.split("/reel/")[-1].split("/")[0]
        elif "/p/" in url:
            shortcode = url.split("/p/")[-1].split("/")[0]
        else:
            await update.message.reply_text("❌ Faqat post yoki reel link yuboring.")
            return

        # Postni yuklash
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target="video")

        # Video faylni topish
        video_path = None
        if os.path.exists("video"):
            for file in os.listdir("video"):
                if file.endswith(".mp4"):
                    video_path = os.path.join("video", file)
                    break

        # Video yuborish
        if video_path:
            with open(video_path, 'rb') as f:
                await update.message.reply_video(f)
        else:
            await update.message.reply_text("❌ Video topilmadi.")

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi:\n{e}")

    # Tozalash
    if os.path.exists("video"):
        shutil.rmtree("video", ignore_errors=True)

# Botni ishga tushurish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("✅ Bot ishga tushdi.")
    app.run_polling()

if __name__ == "__main__":
    main()
