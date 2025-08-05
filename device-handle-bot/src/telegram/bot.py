# Telegram bot with inline buttons: Lock / Unlock
from __future__ import annotations
from typing import Final
from datetime import datetime
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)
from src.config import settings
from src.kafka.producer import ControlProducer

# Build inline keyboard (two actions)
def main_keyboard(target_label: str) -> InlineKeyboardMarkup:
    """Return the main inline keyboard."""
    buttons = [
        [
            InlineKeyboardButton(text="🔒 Bloquear", callback_data="lock"),
            InlineKeyboardButton(text="🔓 Desbloquear", callback_data="unlock"),
        ],
    ]
    footer = [
        [InlineKeyboardButton(text=f"🎯 Destino: {target_label}", callback_data="noop")]
    ]
    return InlineKeyboardMarkup(buttons + footer)

def user_allowed(user_id: int) -> bool:
    """Check if user is in allowlist (if provided)."""
    if not settings.allowed_user_ids:
        return True
    return user_id in settings.allowed_user_ids

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show welcome and keyboard."""
    user = update.effective_user
    if not user_allowed(user.id):
        await update.message.reply_text("⛔ No autorizado.")
        return

    target = settings.machine_target
    title  = settings.bot_title
    msg = (
        f"<b>{title}</b>\n"
        f"Control de equipos (Kafka)\n"
        f"Selecciona una acción:"
    )
    await update.message.reply_text(
        msg,
        reply_markup=main_keyboard(target_label=target),
        parse_mode=ParseMode.HTML
    )

async def on_press(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle lock/unlock button presses."""
    q = update.callback_query
    await q.answer()

    user = update.effective_user
    if not user_allowed(user.id):
        await q.edit_message_text("⛔ No autorizado.")
        return

    action = q.data
    if action not in ("lock", "unlock", "noop"):
        await q.edit_message_text("Acción desconocida.")
        return
    if action == "noop":
        return

    # Send control event to Kafka
    producer: ControlProducer = context.bot_data["producer"]
    actor = f"telegram:{user.id}"
    producer.send_control(action=action, target=settings.machine_target, actor=actor)

    # Feedback to user (keep keyboard)
    status = "🔒 Bloqueo enviado" if action == "lock" else "🔓 Desbloqueo enviado"
    time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    text = (
        f"<b>{settings.bot_title}</b>\n"
        f"{status}\n"
        f"🎯 Destino: <code>{settings.machine_target}</code>\n"
        f"🕑 {time_str}"
    )
    await q.edit_message_text(
        text,
        reply_markup=main_keyboard(target_label=settings.machine_target),
        parse_mode=ParseMode.HTML
    )

def build_app() -> Application:
    """Wire Telegram app with Kafka producer in bot_data."""
    app = ApplicationBuilder().token(settings.bot_token).build()
    # Store a singleton producer in bot_data
    app.bot_data["producer"] = ControlProducer()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_press))

    return app
