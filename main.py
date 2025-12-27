import logging
import config
from ScheduleClient import ScheduleClient
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

ENTER_GROUP, SELECT_SCHEDULE_TYPE, SELECT_DAY, SELECT_WEEK = range(4)

sc = ScheduleClient('https://digital.etu.ru/api')

select_schedule_type_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='На неделю', callback_data='schedule_week'),
        InlineKeyboardButton(text='На конкретный день', callback_data='schedule_day'),
    ],
])
select_week_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Нечетная неделя', callback_data='week_odd'),
        InlineKeyboardButton(text='Четная неделя', callback_data='week_even'),
        InlineKeyboardButton(text='В начало', callback_data='main'),
    ],
])
select_day_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(text='Сегодня', callback_data='day_today'),
        InlineKeyboardButton(text='Завтра', callback_data='day_tomorrow'),
        InlineKeyboardButton(text='В начало', callback_data='main'),
    ],
])

async def start(update: Update, context):
    await update.message.reply_text('Введите номер группы:')
    return ENTER_GROUP
async def restart(update: Update, context):
    await update.callback_query.edit_message_text('Выберите какое расписание вам нужно:', reply_markup=select_schedule_type_keyboard)
    return SELECT_SCHEDULE_TYPE
async def enter_group(update: Update, context):
    try:
        context.user_data['group'] = int(update.message.text)
    except:
        await update.message.reply_text('Неверный ввод, попробуйте еще раз:')
        return ENTER_GROUP

    await update.message.reply_text('Выберите какое расписание вам нужно:', reply_markup=select_schedule_type_keyboard)
    return SELECT_SCHEDULE_TYPE

async def select_schedule_type(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'schedule_day':
        await query.edit_message_text('Выберите день:', reply_markup=select_day_keyboard)
        return SELECT_DAY
    elif query.data == 'schedule_week':
        await query.edit_message_text('Выберите неделю:', reply_markup=select_week_keyboard)
        return SELECT_WEEK
    else:
        return await restart(update, context)

async def select_day(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'day_today':
        await query.edit_message_text('*Типо расписание на сегодня*')
    elif query.data == 'day_tomorrow':
        await query.edit_message_text('*Типо расписание на завтра*')
    else:
        return await restart(update, context)
async def select_week(update: Update, context):
    query = update.callback_query
    await query.answer()

    response = ''
    if query.data == 'week_odd':
        response = 'Расписание на нечетную неделю:\n\n' + sc.request_schedule_week(context.user_data['group'], 1)
    elif query.data == 'week_even':
        response = 'Расписание на четную неделю:\n\n' + sc.request_schedule_week(context.user_data['group'], 2)
    else:
        return await restart(update, context)
    await query.edit_message_text(response, reply_markup=select_week_keyboard)

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        ENTER_GROUP: [MessageHandler(filters.TEXT, enter_group)],
        SELECT_SCHEDULE_TYPE: [CallbackQueryHandler(select_schedule_type)],
        SELECT_WEEK: [CallbackQueryHandler(select_week)],
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
        .build()
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()