from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_user, create_user
from utils.keyboards import role_keyboard, main_menu_employer, main_menu_freelancer
from config import REGISTER_ROLE, REGISTER_NAME, REGISTER_SKILLS, REGISTER_BIO

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if user:
        if user["role"] == "employer":
            await update.message.reply_text(
                f"👋 خوش برگشتی {user['full_name']}!\nچیکار می‌تونم برات بکنم؟",
                reply_markup=main_menu_employer()
            )
        else:
            await update.message.reply_text(
                f"👋 خوش برگشتی {user['full_name']}!\nچیکار می‌تونم برات بکنم؟",
                reply_markup=main_menu_freelancer()
            )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👋 به ربات فریلنسر خوش اومدی!\n\nاول بگو، تو چه نقشی داری؟",
        reply_markup=role_keyboard()
    )
    return REGISTER_ROLE

async def register_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    role = "employer" if query.data == "role_employer" else "freelancer"
    context.user_data["role"] = role
    
    await query.edit_message_text("✏️ اسم و فامیلت رو بنویس:")
    return REGISTER_NAME

async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    
    if context.user_data["role"] == "freelancer":
        await update.message.reply_text("🛠️ مهارت‌هاتو بنویس (با کاما جدا کن):\nمثال: طراحی سایت, پایتون, UI/UX")
        return REGISTER_SKILLS
    else:
        await update.message.reply_text("📝 یه معرفی کوتاه از خودت بنویس:")
        return REGISTER_BIO

async def register_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    skills = [s.strip() for s in update.message.text.split(",")]
    context.user_data["skills"] = skills
    await update.message.reply_text("📝 یه معرفی کوتاه از خودت بنویس:")
    return REGISTER_BIO

async def register_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bio = update.message.text.strip()
    role = context.user_data["role"]
    
    create_user(
        user_id=user.id,
        username=user.username or "",
        full_name=context.user_data["full_name"],
        role=role,
        skills=context.user_data.get("skills", []),
        bio=bio,
    )
    
    if role == "employer":
        await update.message.reply_text(
            "✅ ثبت‌نام موفق!\nحالا می‌تونی پروژه ثبت کنی.",
            reply_markup=main_menu_employer()
        )
    else:
        await update.message.reply_text(
            "✅ ثبت‌نام موفق!\nحالا می‌تونی پروژه‌ها رو ببینی و پیشنهاد بدی.",
            reply_markup=main_menu_freelancer()
        )
    
    return ConversationHandler.END
