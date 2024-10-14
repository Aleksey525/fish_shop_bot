import requests


def get_products_from_cart(headers, document_id):
    strapi_carts_url = 'http://127.0.0.1:1337/api/carts'
    cart_url = f'{strapi_carts_url}/{document_id}'
    params = {
        'populate[cart_products][populate]': 'products',
    }
    response = requests.get(cart_url, headers=headers, params=params)
    products = response.json()['data']['cart_products']
    product_titles = [current_product['title'] for product in products for current_product in product['products']]
    return product_titles, products


def get_cart_id(strapi_carts_url, chat_id, headers):
    cart_url = f'{strapi_carts_url}?filters[tg_id][$eq]={chat_id}&populate=*'
    cart_response = requests.get(cart_url, headers=headers)
    cart_data = cart_response.json()['data']
    cart_id = cart_data[0]['id']
    return cart_id


def get_cart_document_id(strapi_carts_url, chat_id, headers):
    cart_url = f'{strapi_carts_url}?filters[tg_id][$eq]={chat_id}&populate=*'
    cart_response = requests.get(cart_url, headers=headers)
    cart_data = cart_response.json()['data']
    cart_document_id = cart_data[0]['documentId']
    return cart_document_id