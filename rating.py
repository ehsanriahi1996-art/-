from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_user, get_project, create_rating, update_escrow_status
from utils.keyboards import rating_keyboard
from config import RATING_SCORE, RATING_COMMENT

async def release_escrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    project_id = query.data.replace("release_", "")
    p = get_project(project_id)
    
    update_escrow_status(project_id, "released")
    
    # notify freelancer
    await context.bot.send_message(
        chat_id=p["selected_freelancer_id"],
        text="💰 پرداخت آزاد شد! پول به حسابت واریز میشه.\n\nلطفاً به کارفرما امتیاز بده:",
        reply_markup=rating_keyboard(project_id, p["employer_id"])
    )
    
    # ask employer to rate
    await query.edit_message_text(
        "✅ پرداخت آزاد شد!\n\nلطفاً به فریلنسر امتیاز بده:",
        reply_markup=rating_keyboard(project_id, p["selected_freelancer_id"])
    )

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, project_id, rated_id, score = query.data.split("_")
    context.user_data["rating_project_id"] = project_id
    context.user_data["rating_rated_id"] = int(rated_id)
    context.user_data["rating_score"] = int(score)
    
    stars = "⭐" * int(score)
    await query.edit_message_text(f"امتیاز: {stars}\n\nیه نظر کوتاه بنویس:")
    return RATING_COMMENT

async def rating_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    comment = update.message.text.strip()
    
    create_rating(
        project_id=context.user_data["rating_project_id"],
        rater_id=user_id,
        rated_id=context.user_data["rating_rated_id"],
        score=context.user_data["rating_score"],
        comment=comment,
    )
    
    await update.message.reply_text("✅ ممنون! نظرت ثبت شد.")
    return ConversationHandler.END
