from src.telegram.bot import build_app

if __name__ == "__main__":
    app = build_app()
    print("[i] Telegram control bot is running. Press Ctrl+C to stop.")
    app.run_polling(close_loop=False)
