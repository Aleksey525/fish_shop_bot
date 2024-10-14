from telegram import InlineKeyboardButton


def create_menu_keyboard(products):
    product_buttons = [[InlineKeyboardButton(product['title'], callback_data=product['id'])] for product in products]
    cart_button = [InlineKeyboardButton('Моя корзина', callback_data='my_cart')]
    keyboard = product_buttons + [cart_button]
    return keyboard


def create_cart_keyboard(products):
    keyboard = [
        [InlineKeyboardButton(f"Удалить {i['title']}", callback_data=i['id'])] for
        product in products for i in product['products']]
    keyboard.append([InlineKeyboardButton('Оплатить', callback_data='payment')])
    keyboard.append([InlineKeyboardButton('В меню', callback_data='in_menu')])
    return keyboard


def create_product_keyboard(product_id):
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data='back')],
        [InlineKeyboardButton('Добавить в корзину', callback_data=product_id)],
        [InlineKeyboardButton('Моя корзина', callback_data='my_cart')]
    ]
    return keyboard
