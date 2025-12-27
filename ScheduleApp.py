import config
from ScheduleClient import ScheduleClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

ENTER_GROUP, SELECT_SCHEDULE_TYPE, SELECT_DAY, SELECT_WEEK = range(4) # States of the bot

# Keyboards
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

# App class
class ScheduleApp:
    def __init__(self):
        self.__token = config.TOKEN
        self.__sc = ScheduleClient('https://digital.etu.ru/api')
        self.__conv_handler = ConversationHandler( # Handles transition between states
            entry_points=[CommandHandler('start', self.start)], # Write /start to enter
            states={
                ENTER_GROUP: [MessageHandler(filters.TEXT, self.enter_group)],
                SELECT_SCHEDULE_TYPE: [CallbackQueryHandler(self.select_schedule_type)],
                SELECT_WEEK: [CallbackQueryHandler(self.select_week)],
                SELECT_DAY: [CallbackQueryHandler(self.select_day)]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
    
    async def start(self, update: Update, context): # Entry
        await update.message.reply_text('Введите номер группы:')
        return ENTER_GROUP
    async def restart(self, update: Update, context): # Начало
        await update.callback_query.edit_message_text('Выберите какое расписание вам нужно:', reply_markup=select_schedule_type_keyboard)
        return SELECT_SCHEDULE_TYPE
    async def enter_group(self, update: Update, context):
        try:
            context.user_data['group'] = int(update.message.text)
        except:
            await update.message.reply_text('Неверный ввод, попробуйте еще раз:')
            return ENTER_GROUP

        await update.message.reply_text('Выберите какое расписание вам нужно:', reply_markup=select_schedule_type_keyboard)
        return SELECT_SCHEDULE_TYPE

    async def select_schedule_type(self, update: Update, context):
        query = update.callback_query
        await query.answer()

        if query.data == 'schedule_day':
            await query.edit_message_text('Выберите день:', reply_markup=select_day_keyboard)
            return SELECT_DAY
        elif query.data == 'schedule_week':
            await query.edit_message_text('Выберите неделю:', reply_markup=select_week_keyboard)
            return SELECT_WEEK
        else:
            return await self.restart(update, context)

    async def select_day(self, update: Update, context):
        query = update.callback_query
        await query.answer()

        if query.data == 'day_today':
            await query.edit_message_text('*Типо расписание на сегодня*')
        elif query.data == 'day_tomorrow':
            await query.edit_message_text('*Типо расписание на завтра*')
        else:
            return await self.restart(update, context)
    async def select_week(self, update: Update, context):
        query = update.callback_query
        await query.answer()

        response = ''
        if query.data == 'week_odd':
            response = 'Расписание на нечетную неделю:\n\n' + self.__sc.request_schedule_week(context.user_data['group'], 1)
        elif query.data == 'week_even':
            response = 'Расписание на четную неделю:\n\n' + self.__sc.request_schedule_week(context.user_data['group'], 2)
        else:
            return await self.restart(update, context)
        await query.edit_message_text(response, reply_markup=select_week_keyboard)
    async def run(self): # Run bot handling
        application = (
            ApplicationBuilder()
            .token(self.__token)
            .read_timeout(10)
            .write_timeout(10)
            .build()
        )

        application.add_handler(self.__conv_handler)
        application.run_polling()