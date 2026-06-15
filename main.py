from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from config import *
from handlers.start import start, register_role, register_name, register_skills, register_bio
from handlers.project import (
    new_project, project_title, project_desc, project_budget_min,
    project_budget_max, project_deadline, browse_projects, show_project,
    start_proposal, proposal_price, proposal_time, proposal_desc,
    view_proposals, accept_proposal, reject_proposal
)
from handlers.chat import open_chat, send_chat_message, end_chat
from handlers.rating import release_escrow, handle_rating, rating_comment

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ─── Registration ConversationHandler ─────────────
    reg_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_ROLE: [CallbackQueryHandler(register_role, pattern="^role_")],
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
            REGISTER_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_skills)],
            REGISTER_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_bio)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # ─── Project ConversationHandler ──────────────────
    project_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📋 ثبت پروژه جدید$"), new_project),
            CallbackQueryHandler(start_proposal, pattern="^propose_"),
        ],
        states={
            PROJECT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_title)],
            PROJECT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_desc)],
            PROJECT_BUDGET_MIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_budget_min)],
            PROJECT_BUDGET_MAX: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_budget_max)],
            PROJECT_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_deadline)],
            PROPOSAL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, proposal_price)],
            PROPOSAL_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, proposal_time)],
            PROPOSAL_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, proposal_desc)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
    )

    # ─── Chat ConversationHandler ──────────────────────
    chat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(open_chat, pattern="^chat_")],
        states={
            CHAT_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_chat_message),
                CommandHandler("done", end_chat),
            ],
        },
        fallbacks=[CommandHandler("done", end_chat)],
    )

    # ─── Rating ConversationHandler ────────────────────
    rating_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_rating, pattern="^rate_")],
        states={
            RATING_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, rating_comment)],
        },
        fallbacks=[],
    )

    # ─── Add handlers ─────────────────────────────────
    app.add_handler(reg_conv)
    app.add_handler(project_conv)
    app.add_handler(chat_conv)
    app.add_handler(rating_conv)

    # Standalone callbacks
    app.add_handler(MessageHandler(filters.Regex("^🔍 مشاهده پروژه‌ها$"), browse_projects))
    app.add_handler(CallbackQueryHandler(show_project, pattern="^project_"))
    app.add_handler(CallbackQueryHandler(view_proposals, pattern="^proposals_"))
    app.add_handler(CallbackQueryHandler(accept_proposal, pattern="^accept_"))
    app.add_handler(CallbackQueryHandler(reject_proposal, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(release_escrow, pattern="^release_"))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
