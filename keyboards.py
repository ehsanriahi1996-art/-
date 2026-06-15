from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def main_menu_employer():
    return ReplyKeyboardMarkup([
        ["📋 ثبت پروژه جدید", "📂 پروژه‌های من"],
        ["💰 وضعیت escrow", "👤 پروفایل من"],
    ], resize_keyboard=True)

def main_menu_freelancer():
    return ReplyKeyboardMarkup([
        ["🔍 مشاهده پروژه‌ها", "📨 پیشنهادهای من"],
        ["💬 پیام‌های من", "👤 پروفایل من"],
    ], resize_keyboard=True)

def role_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👔 کارفرما هستم", callback_data="role_employer")],
        [InlineKeyboardButton("💻 فریلنسر هستم", callback_data="role_freelancer")],
    ])

def project_list_keyboard(projects):
    buttons = []
    for p in projects:
        buttons.append([InlineKeyboardButton(
            f"📌 {p['title']} | {p['budget_min']:,}–{p['budget_max']:,} تومن",
            callback_data=f"project_{p['id']}"
        )])
    return InlineKeyboardMarkup(buttons)

def project_actions_keyboard(project_id, is_employer=False):
    buttons = [
        [InlineKeyboardButton("📨 پیشنهادها", callback_data=f"proposals_{project_id}")],
        [InlineKeyboardButton("💬 چت", callback_data=f"chat_{project_id}")],
    ]
    if not is_employer:
        buttons.insert(0, [InlineKeyboardButton("✍️ ارسال پیشنهاد", callback_data=f"propose_{project_id}")])
    return InlineKeyboardMarkup(buttons)

def proposal_actions_keyboard(proposal_id, project_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ قبول", callback_data=f"accept_{proposal_id}_{project_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{proposal_id}"),
        ],
        [InlineKeyboardButton("💬 چت با فریلنسر", callback_data=f"chat_{project_id}")],
    ])

def escrow_keyboard(project_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تایید تحویل و آزادسازی پول", callback_data=f"release_{project_id}")],
        [InlineKeyboardButton("⚠️ مشکل دارم", callback_data=f"dispute_{project_id}")],
    ])

def rating_keyboard(project_id, rated_id):
    buttons = []
    row = []
    for i in range(1, 6):
        row.append(InlineKeyboardButton(f"{'⭐'*i}", callback_data=f"rate_{project_id}_{rated_id}_{i}"))
    buttons.append(row)
    return InlineKeyboardMarkup(buttons)
