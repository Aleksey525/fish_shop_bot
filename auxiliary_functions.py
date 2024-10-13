import requests


def get_products_from_cart(headers):
    strapi_carts_url = 'http://127.0.0.1:1337/api/carts'
    params = {
        'populate[cart_products][populate]': 'products',
    }
    response = requests.get(strapi_carts_url, headers=headers, params=params)
    products = response.json()['data'][0]['cart_products']
    product_titles = []
    for product in products:
        fish_title = (product['products'][0]['title'])
        product_titles.append(fish_title)
    return product_titles, products