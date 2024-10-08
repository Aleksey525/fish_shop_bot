from environs import Env
from io import BytesIO
import requests
import redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler


def start(update, context):
    print('start')
    products = context.bot_data['products']
    keyboard = [[InlineKeyboardButton(product['title'], callback_data=int(product['id']))] for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет!', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_description(update, context):
    products = context.bot_data['products']
    keyboard = [[InlineKeyboardButton(product['title'], callback_data=int(product['id']))] for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)
    chat_id = update.callback_query.message.chat_id
    query = update.callback_query
    query.answer()
    if query.data == 'back':
        context.bot.delete_message(chat_id=chat_id,
                           message_id=update.callback_query.message.message_id)
        context.bot.send_message(chat_id=chat_id, text='МЕНЮ', reply_markup=reply_markup)
        return 'HANDLE_MENU'
    if query.data == 'add_to_cart':
        strapi_token = context.bot_data['strapi_token']
        strapi_url = 'http://127.0.0.1:1337/api/carts'
        headers = {'Authorization': f'Bearer {strapi_token}'}
        cart_data = {
            'data': {
                'tg_id': str(chat_id),
            }
        }
        response = requests.post(strapi_url, headers=headers, json=cart_data)
        return 'HANDLE_DESCRIPTION'


def handle_menu(update: Update, context: CallbackContext) -> str:
    strapi_url = 'http://127.0.0.1:1337/'
    query = update.callback_query
    query.answer()
    chat_id = update.callback_query.message.chat_id
    product_id = int(query.data)
    products = context.bot_data['products']
    selected_product = next((product for product in products if product['id'] == product_id), None)
    image_url = selected_product['picture'][0]['formats']['medium']['url']
    full_image_url = f'{strapi_url}{image_url}'
    response = requests.get(full_image_url)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='back')],
        [InlineKeyboardButton('Добавить в корзину', callback_data='add_to_cart')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(chat_id=chat_id,
                       message_id=update.callback_query.message.message_id)
    if selected_product:
        context.bot.send_photo(chat_id=chat_id, photo=image_data, caption=f"{selected_product['title']} ({selected_product['price']} руб. за кг)"
                                     f"\n\n{selected_product['description']}", reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'


def handle_users_reply(update, context):
    db = context.bot_data['redis_connection']
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
        print(f"State updated to {next_state}")
    except Exception as err:
        print(err)


def main():
    env = Env()
    env.read_env()
    token = env.str('TG_BOT_TOKEN')
    redis_host = env.str('REDIS_HOST')
    redis_port = env.int('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    strapi_token = env('STRAPI_TOKEN')
    url = 'http://127.0.0.1:1337/api/products'
    params = {
        'populate': '*',
    }
    headers = {'Authorization': f'Bearer {strapi_token}'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    products = response.json()['data']
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['products'] = products
    redis_connection = redis.Redis(host=redis_host, port=redis_port,
                                   password=redis_password, db=0)
    dispatcher.bot_data['redis_connection'] = redis_connection
    dispatcher.bot_data['strapi_token'] = strapi_token

    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()