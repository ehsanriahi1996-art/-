from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import *
from utils.keyboards import *
from config import *

# ─── Employer: Create Project ─────────────────────────
async def new_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user or user["role"] != "employer":
        await update.message.reply_text("❌ فقط کارفرماها می‌تونن پروژه ثبت کنن.")
        return ConversationHandler.END
    
    await update.message.reply_text("📋 عنوان پروژه رو بنویس:")
    return PROJECT_TITLE

async def project_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["project_title"] = update.message.text.strip()
    await update.message.reply_text("📝 توضیحات کامل پروژه رو بنویس:")
    return PROJECT_DESC

async def project_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["project_desc"] = update.message.text.strip()
    await update.message.reply_text("💰 حداقل بودجه (تومن) رو بنویس:\nمثال: 500000")
    return PROJECT_BUDGET_MIN

async def project_budget_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.replace(",", "").strip())
        context.user_data["budget_min"] = amount
        await update.message.reply_text("💰 حداکثر بودجه (تومن) رو بنویس:")
        return PROJECT_BUDGET_MAX
    except:
        await update.message.reply_text("❌ فقط عدد وارد کن:")
        return PROJECT_BUDGET_MIN

async def project_budget_max(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text.replace(",", "").strip())
        if amount < context.user_data["budget_min"]:
            await update.message.reply_text("❌ حداکثر باید بیشتر از حداقل باشه:")
            return PROJECT_BUDGET_MAX
        context.user_data["budget_max"] = amount
        await update.message.reply_text("📅 مهلت انجام (روز) رو بنویس:\nمثال: 14")
        return PROJECT_DEADLINE
    except:
        await update.message.reply_text("❌ فقط عدد وارد کن:")
        return PROJECT_BUDGET_MAX

async def project_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text.strip())
        uid = update.effective_user.id
        p = create_project(
            employer_id=uid,
            title=context.user_data["project_title"],
            description=context.user_data["project_desc"],
            budget_min=context.user_data["budget_min"],
            budget_max=context.user_data["budget_max"],
            deadline_days=days,
        )
        await update.message.reply_text(
            f"✅ پروژه ثبت شد!\n\n"
            f"📌 {p['title']}\n"
            f"💰 {p['budget_min']:,} – {p['budget_max']:,} تومن\n"
            f"📅 مهلت: {days} روز",
            reply_markup=main_menu_employer()
        )
        return ConversationHandler.END
    except:
        await update.message.reply_text("❌ فقط عدد وارد کن:")
        return PROJECT_DEADLINE

# ─── Freelancer: Browse Projects ─────────────────────
async def browse_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    projects = get_open_projects()
    if not projects:
        await update.message.reply_text("📭 هنوز پروژه‌ای ثبت نشده.")
        return
    
    await update.message.reply_text(
        f"🔍 {len(projects)} پروژه باز پیدا شد:",
        reply_markup=project_list_keyboard(projects)
    )

async def show_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    project_id = query.data.replace("project_", "")
    p = get_project(project_id)
    if not p:
        await query.edit_message_text("❌ پروژه پیدا نشد.")
        return
    
    user_id = query.from_user.id
    user = get_user(user_id)
    is_employer = user and user["role"] == "employer" and p["employer_id"] == user_id
    
    text = (
        f"📌 *{p['title']}*\n\n"
        f"📝 {p['description']}\n\n"
        f"💰 بودجه: {p['budget_min']:,} – {p['budget_max']:,} تومن\n"
        f"📅 مهلت: {p['deadline_days']} روز\n"
        f"👔 کارفرما: {p['users']['full_name']}\n"
        f"📊 وضعیت: {p['status']}"
    )
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=project_actions_keyboard(project_id, is_employer)
    )

# ─── Freelancer: Submit Proposal ─────────────────────
async def start_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    project_id = query.data.replace("propose_", "")
    context.user_data["proposal_project_id"] = project_id
    
    p = get_project(project_id)
    await query.edit_message_text(
        f"✍️ ارسال پیشنهاد برای: *{p['title']}*\n\n"
        f"💰 بودجه کارفرما: {p['budget_min']:,} – {p['budget_max']:,} تومن\n\n"
        f"قیمت پیشنهادی خودت رو بنویس (تومن):",
        parse_mode="Markdown"
    )
    return PROPOSAL_PRICE

async def proposal_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = int(update.message.text.replace(",", "").strip())
        context.user_data["proposal_price"] = price
        await update.message.reply_text("📅 زمان تحویل پیشنهادی (روز):")
        return PROPOSAL_TIME
    except:
        await update.message.reply_text("❌ فقط عدد وارد کن:")
        return PROPOSAL_PRICE

async def proposal_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        days = int(update.message.text.strip())
        context.user_data["proposal_days"] = days
        await update.message.reply_text(
            "💬 توضیح بده چرا تو برای این پروژه مناسبی؟\n"
            "(تجربه، نمونه‌کار، رویکردت رو بنویس)"
        )
        return PROPOSAL_DESC
    except:
        await update.message.reply_text("❌ فقط عدد وارد کن:")
        return PROPOSAL_TIME

async def proposal_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    desc = update.message.text.strip()
    
    proposal = create_proposal(
        project_id=context.user_data["proposal_project_id"],
        freelancer_id=user_id,
        price=context.user_data["proposal_price"],
        delivery_days=context.user_data["proposal_days"],
        description=desc,
    )
    
    # notify employer
    p = get_project(context.user_data["proposal_project_id"])
    freelancer = get_user(user_id)
    
    try:
        await context.bot.send_message(
            chat_id=p["employer_id"],
            text=(
                f"🔔 پیشنهاد جدید برای پروژه *{p['title']}*\n\n"
                f"👤 فریلنسر: {freelancer['full_name']}\n"
                f"💰 قیمت: {proposal['price']:,} تومن\n"
                f"📅 زمان تحویل: {proposal['delivery_days']} روز\n\n"
                f"💬 {desc}"
            ),
            parse_mode="Markdown",
            reply_markup=proposal_actions_keyboard(proposal["id"], p["id"])
        )
    except:
        pass
    
    await update.message.reply_text(
        "✅ پیشنهادت ارسال شد! کارفرما بررسی می‌کنه.\n"
        "می‌تونی از طریق همین ربات با کارفرما چت کنی.",
        reply_markup=main_menu_freelancer()
    )
    return ConversationHandler.END

# ─── Employer: View Proposals ─────────────────────────
async def view_proposals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    project_id = query.data.replace("proposals_", "")
    proposals = get_project_proposals(project_id)
    
    if not proposals:
        await query.edit_message_text("📭 هنوز پیشنهادی نرسیده.")
        return
    
    for prop in proposals:
        stars = "⭐" * int(prop["users"]["rating"] or 0)
        text = (
            f"👤 {prop['users']['full_name']} {stars}\n"
            f"💰 {prop['price']:,} تومن\n"
            f"📅 {prop['delivery_days']} روز\n\n"
            f"💬 {prop['description']}"
        )
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=text,
            reply_markup=proposal_actions_keyboard(prop["id"], project_id)
        )

async def accept_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    _, proposal_id, project_id = query.data.split("_", 2)
    prop = get_proposal(proposal_id)
    
    update_proposal_status(proposal_id, "accepted")
    update_project_status(project_id, "in_progress", prop["freelancer_id"])
    
    # notify freelancer
    p = get_project(project_id)
    await context.bot.send_message(
        chat_id=prop["freelancer_id"],
        text=(
            f"🎉 پیشنهادت قبول شد!\n\n"
            f"📌 پروژه: *{p['title']}*\n"
            f"💰 مبلغ: {prop['price']:,} تومن\n\n"
            f"کارفرما پرداخت امن رو انجام میده و بعد شروع کن."
        ),
        parse_mode="Markdown"
    )
    
    await query.edit_message_text(
        f"✅ پیشنهاد قبول شد!\nحالا لینک پرداخت escrow رو برای کارفرما ارسال کن.",
        reply_markup=escrow_keyboard(project_id)
    )

async def reject_proposal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    proposal_id = query.data.replace("reject_", "")
    update_proposal_status(proposal_id, "rejected")
    await query.edit_message_text("❌ پیشنهاد رد شد.")
