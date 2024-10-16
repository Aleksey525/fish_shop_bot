import requests


def get_products_from_cart(strapi_carts_url, headers, document_id):
    cart_url = f'{strapi_carts_url}{document_id}'
    params = {
        'populate[cart_products][populate]': 'products',
    }
    response = requests.get(cart_url, headers=headers, params=params)
    response.raise_for_status()
    products = response.json()['data']['cart_products']
    product_titles = [current_product['title'] for product in products for current_product in product['products']]
    return product_titles, products


def get_cart_document_id(strapi_carts_url, chat_id, headers):
    params = {
        'filters[tg_id][$eq]': chat_id,
        'populate': '*'
    }
    cart_response = requests.get(strapi_carts_url, headers=headers, params=params)
    cart_response.raise_for_status()
    cart_data = cart_response.json()['data']
    cart_document_id = cart_data[0]['documentId']
    return cart_document_id