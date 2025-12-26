import logging
import config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ENTER_GROUP, SELECT_SCHEDULE_TYPE, SELECT_DAY = range(3)

select_schedule_type_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="На неделю", callback_data="schedule_week"),
        InlineKeyboardButton(text="На конкретный день", callback_data="schedule_day"),
    ],
])
select_day_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text="Сегодня", callback_data="day_today"),
        InlineKeyboardButton(text="Завтра", callback_data="day_tomorrow"),
    ],
])

async def start(update: Update, context):
    await update.message.reply_text("Введите номер группы:")
    return ENTER_GROUP

async def enter_group(update: Update, context):
    context.user_data['group'] = int(update.message.text)
    await update.message.reply_text("Выберите какое расписание вам нужно:", reply_markup=select_schedule_type_keyboard)
    return SELECT_SCHEDULE_TYPE

async def select_schedule_type(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "schedule_day":
        await query.edit_message_text("Выберите день:", reply_markup=select_day_keyboard)
        return SELECT_DAY
    elif query.data == "schedule_week":
        await query.edit_message_text("*Типо расписание на неделю*")
    return ConversationHandler.END

async def select_day(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "day_today":
        await query.edit_message_text("*Типо расписание на сегодня*")
    elif query.data == "day_tomorrow":
        await query.edit_message_text("*Типо расписание на завтра*")

    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ENTER_GROUP: [MessageHandler(filters.TEXT, enter_group)],
        SELECT_SCHEDULE_TYPE: [CallbackQueryHandler(select_schedule_type)],
        SELECT_DAY: [CallbackQueryHandler(select_day)]
    },
    fallbacks=[CommandHandler('start', start)]
)

def main():
    application = (
        ApplicationBuilder()
        .token(config.TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()