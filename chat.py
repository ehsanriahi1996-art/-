from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_user, get_project, save_message, get_project_messages
from config import CHAT_MESSAGE

async def open_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    project_id = query.data.replace("chat_", "")
    p = get_project(project_id)
    user_id = query.from_user.id
    user = get_user(user_id)
    
    # determine receiver
    if user["role"] == "employer":
        receiver_id = p.get("selected_freelancer_id")
        if not receiver_id:
            await query.edit_message_text("⚠️ هنوز فریلنسری انتخاب نشده. اول پیشنهادها رو بررسی کن.")
            return ConversationHandler.END
    else:
        receiver_id = p["employer_id"]
    
    context.user_data["chat_project_id"] = project_id
    context.user_data["chat_receiver_id"] = receiver_id
    
    # show recent messages
    messages = get_project_messages(project_id)
    if messages:
        history = "\n".join([
            f"{'تو' if m['sender_id'] == user_id else '👤'}: {m['content']}"
            for m in messages[-10:]
        ])
        await query.edit_message_text(f"💬 تاریخچه چت:\n\n{history}\n\n✏️ پیامت رو بنویس:")
    else:
        await query.edit_message_text(f"💬 چت برای پروژه *{p['title']}* باز شد.\n\n✏️ پیامت رو بنویس:", parse_mode="Markdown")
    
    return CHAT_MESSAGE

async def send_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    project_id = context.user_data.get("chat_project_id")
    receiver_id = context.user_data.get("chat_receiver_id")
    
    if not project_id or not receiver_id:
        await update.message.reply_text("❌ خطا در چت. دوباره امتحان کن.")
        return ConversationHandler.END
    
    content = update.message.text.strip()
    sender = get_user(user_id)
    
    save_message(project_id, user_id, receiver_id, content)
    
    # forward to receiver
    p = get_project(project_id)
    try:
        await context.bot.send_message(
            chat_id=receiver_id,
            text=f"💬 پیام از {sender['full_name']} (پروژه: {p['title']}):\n\n{content}"
        )
    except:
        pass
    
    await update.message.reply_text("✅ پیام ارسال شد. ادامه بده یا /done برای خروج:")
    return CHAT_MESSAGE

async def end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 از چت خارج شدی.")
    context.user_data.pop("chat_project_id", None)
    context.user_data.pop("chat_receiver_id", None)
    return ConversationHandler.END
