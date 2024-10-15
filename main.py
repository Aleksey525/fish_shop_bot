from environs import Env
from io import BytesIO
import requests
import redis
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler


from auxiliary_functions import get_products_from_cart, get_cart_document_id
from keyboards import create_menu_keyboard, create_cart_keyboard, create_product_keyboard


def start(update: Update, context: CallbackContext) -> str:
    products = context.bot_data['products']
    keyboard = create_menu_keyboard(products)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Выберите товар:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_description(update: Update, context: CallbackContext) -> str:
    strapi_token = context.bot_data['strapi_token']
    strapi_carts_url = 'http://127.0.0.1:1337/api/carts'
    strapi_cart_products_url = 'http://127.0.0.1:1337/api/cart-products'
    headers = {'Authorization': f'Bearer {strapi_token}'}
    chat_id = update.callback_query.message.chat_id
    query = update.callback_query
    query.answer()
    products = context.bot_data['products']
    keyboard = create_menu_keyboard(products)
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.data == 'my_cart':
        cart_document_id = get_cart_document_id(strapi_carts_url, chat_id, headers)
        product_titles, products = get_products_from_cart(headers, cart_document_id)
        current_products = products[0]['products']

        if not current_products:
            products = context.bot_data['products']
            keyboard = create_menu_keyboard(products)
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'В корзине ничего нет, добавьте товары'
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            return 'HANDLE_MENU'
        else:
            keyboard = create_cart_keyboard(products)
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = "\n\n".join(product_titles)
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            return 'HANDLE_CART'

    if query.data == 'back':
        context.bot.delete_message(chat_id=chat_id,
                           message_id=update.callback_query.message.message_id)
        context.bot.send_message(chat_id=chat_id, text='МЕНЮ', reply_markup=reply_markup)
        return 'HANDLE_MENU'

    if query.data:
        product_id = int(update.callback_query.data)
        products = context.bot_data['products']
        selected_product = next((product for product in products if product['id'] == product_id), None)
        cart_url = f'{strapi_carts_url}?filters[tg_id][$eq]={chat_id}&populate=*'
        cart_response = requests.get(cart_url, headers=headers)
        cart_response.raise_for_status()
        cart_data = cart_response.json()['data']

        if not cart_data:
            new_cart_data = {
                "data": {
                    "tg_id": str(chat_id)
                }
            }
            new_cart_response = requests.post(strapi_carts_url, headers=headers, json=new_cart_data)
            new_cart_response.raise_for_status()
            cart_id = new_cart_response.json()['data']['id']
            cart_document_id = new_cart_response.json()['data']['documentId']
            cart_product_data = {
                "data": {
                    "cart": cart_id,
                    "products": selected_product['id']
                }
            }

            create_product_response = requests.post(strapi_cart_products_url, headers=headers, json=cart_product_data)
            create_product_response.raise_for_status()
            cart_product_document_id = create_product_response.json()['data']['documentId']

            update_cart_data = {
                "data": {
                    "tg_id": str(chat_id),
                    "cart_products": {
                        "connect": [{'documentId': cart_product_document_id}]
                    }
                }
            }
            update_cart_response = requests.put(f'{strapi_carts_url}/{cart_document_id}', headers=headers,
                                                json=update_cart_data)
            update_cart_response.raise_for_status()
        else:
            cart_products = cart_data[0]['cart_products']
            cart_document_id = cart_data[0]['documentId']
            cart_product_document_id = cart_products[0]['documentId']
            update_cart_product_data = {
                "data": {
                    "products": {
                        'connect': [{'id': selected_product['id']}]
                    }
                }
            }
            update_cart_product_response = requests.put(f'{strapi_cart_products_url}/{cart_product_document_id}',
                                                        headers=headers, json=update_cart_product_data)
            update_cart_product_response.raise_for_status()

            update_cart_data = {
                "data": {
                    "tg_id": str(chat_id),
                    "cart_products": {
                        "connect": [{'documentId': cart_product_document_id}]
                    }
                }
            }
            update_cart_response = requests.put(f'{strapi_carts_url}/{cart_document_id}', headers=headers,
                                                json=update_cart_data)
            update_cart_response.raise_for_status()

        return 'HANDLE_DESCRIPTION'


def handle_menu(update: Update, context: CallbackContext) -> str:
    strapi_url = 'http://127.0.0.1:1337/'
    strapi_carts_url = 'http://127.0.0.1:1337/api/carts/'
    strapi_token = context.bot_data['strapi_token']
    headers = {'Authorization': f'Bearer {strapi_token}'}
    query = update.callback_query
    query.answer()
    chat_id = update.callback_query.message.chat_id

    if query.data == 'my_cart':
        cart_document_id = get_cart_document_id(strapi_carts_url, chat_id, headers)
        product_titles, products = get_products_from_cart(headers, cart_document_id)
        current_products = products[0]['products']

        if not current_products:
            products = context.bot_data['products']
            keyboard = create_menu_keyboard(products)
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = 'В корзине ничего нет, добавьте товары'
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            return 'HANDLE_MENU'
        else:
            keyboard = create_cart_keyboard(products)
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = "\n\n".join(product_titles)
            context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            return 'HANDLE_CART'

    product_id = int(query.data)
    products = context.bot_data['products']
    selected_product = next((product for product in products if product['id'] == product_id), None)
    image_url = selected_product['picture'][0]['formats']['medium']['url']
    full_image_url = f'{strapi_url}{image_url}'
    response = requests.get(full_image_url)
    response.raise_for_status()
    image_data = BytesIO(response.content)

    keyboard = create_product_keyboard(product_id)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.delete_message(chat_id=chat_id,
                       message_id=update.callback_query.message.message_id)
    if selected_product:
        context.bot.send_photo(chat_id=chat_id, photo=image_data, caption=f"{selected_product['title']} ({selected_product['price']} руб. за кг)"
                                     f"\n\n{selected_product['description']}", reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'


def handle_users_reply(update: Update, context: CallbackContext) -> None:
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
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
        print(f"State updated to {next_state}")
    except Exception as err:
        print(err)


def handle_cart(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    chat_id = update.callback_query.message.chat_id

    if query.data == 'in_menu':
        products = context.bot_data['products']
        keyboard = create_menu_keyboard(products)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text='Выберите товар:', reply_markup=reply_markup)
        return 'HANDLE_MENU'

    if query.data == 'payment':
        context.bot.send_message(chat_id=chat_id, text='Напишите ваш email:')
        return 'WAITING_EMAIL'

    if query.data:
        product_id = query.data
        strapi_token = context.bot_data['strapi_token']
        headers = {'Authorization': f'Bearer {strapi_token}'}
        strapi_carts_url = 'http://127.0.0.1:1337/api/carts'
        strapi_cart_product_url = 'http://127.0.0.1:1337/api/cart-products'
        cart_document_id = get_cart_document_id(strapi_carts_url, chat_id, headers)
        cart_url = f'{strapi_carts_url}/{cart_document_id}'
        params = {
            'populate': '*',
        }
        response = requests.get(cart_url, headers=headers, params=params)
        response.raise_for_status()
        cart_product_document_id = response.json()['data']['cart_products'][0]['documentId']
        cart_product_url = f"{strapi_cart_product_url}/{cart_product_document_id}"

        updated_data = {
            'data': {
            "products": {
                'disconnect': [{'id': product_id}]

                }
            }
        }

        update_cart_products_response = requests.put(cart_product_url, headers=headers, json=updated_data)
        update_cart_products_response.raise_for_status()

        return 'HANDLE_CART'


def waiting_email(update: Update, context: CallbackContext) -> str:
    strapi_clients_url = 'http://127.0.0.1:1337/api/clients'
    strapi_token = context.bot_data['strapi_token']
    user_email = update.message.text
    headers = {'Authorization': f'Bearer {strapi_token}'}
    chat_id = update.message.chat_id
    new_client_data = {
        "data": {
            "tg_id": str(chat_id),
            'email': user_email
        }
    }

    new_client_response = requests.post(strapi_clients_url, headers=headers, json=new_client_data)
    new_client_response.raise_for_status()

    return 'WAITING_EMAIL'


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