import csv
from time import sleep

import requests


class ProductScraper:
    def __init__(self):
        """
        Инициализация класса ProductScraper.
        Устанавливает заголовки запроса, используемые для имитации браузера.
        """

        Accept = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        )
        User_Agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        self.headers = {
            'Accept': Accept,

            'User-Agent': User_Agent

        }

    def get_json(self, url):
        """
        Отправляет GET-запрос к указанному URL и возвращает JSON-ответ.

        Args:
        url (str): URL, к которому отправляется запрос.

        Returns:
        dict or None: JSON-ответ, если запрос успешен (статус 200), иначе None.
        """
        s = requests.Session()
        response = s.get(url=url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Ошибка при получении данных: {response.status_code}")
            return None

    def product(self, json_data):
        """
        Извлекает список продуктов из JSON-данных.

        Args:
        json_data (dict): JSON-ответ, содержащий данные о продуктах.

        Returns:
        list or None: Список продуктов, если данные доступны, иначе None.
        """

        if json_data:
            return json_data['data']['products']['products']

    def card_product(self, response):
        """
        Извлекает детальную информацию о продукте из JSON-ответа.

        Args:
        response (dict): JSON-ответ, содержащий детальную информацию о продукте.

        Returns:
        dict: Словарь с информацией о продукте.
        """

        description = response['data']['productDescription'][0]['content']
        instructions = response['data']['productDescription'][1]['content']
        if '<br>' in description:
            description = description.replace('<br>', '')
        if '<br>' in instructions:
            instructions = instructions.replace('<br>', '')

        name = response['data']['productDescription'][0]['title']

        regular_price = response['data']['variants'][0]['price']['regular']['amount']

        if 'discount' in response['data']['variants'][0]['price']:
            discount_price = response['data']['variants'][0]['price']['discount']['amount']
        else:
            discount_price = "нет скидки"

        if len(response['data']['productDescription']) > 3 and 'subtitle' in response['data']['productDescription'][3]:
            brand_country = response['data']['productDescription'][3]['subtitle']
        else:
            brand_country = "Страна не указана"

        product_data = {
            'описание': description,
            'инструкция по применению': instructions,
            'наименование': name,
            'цена': regular_price,
            'цена со скидкой': discount_price,
            'страна бренда': brand_country
        }

        return product_data

    def scrape_products(self):
        """
        Метод для скрапинга продуктов с сайта и сохранения данных в CSV-файл.

        Этот метод выполняет скрапинг продуктов, начиная с первой страницы, и продолжает до тех пор,
        пока данные по продуктам доступны. Каждый продукт обрабатывается и сохраняется в CSV-файл.
        """
        i = 1
        page_count = 0
        number_goods = 0
        with open('product_data.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = ['ссылка', 'рейтинг пользователей', 'описание', 'инструкция по применению', 'наименование',
                          'страна бренда', 'цена', 'цена со скидкой']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            while True:

                url = (
                    f'https://goldapple.ru/front/api/catalog/plp?categoryId'
                    f'=1000000007&cityId=c2deb16a-0330-4f05-821f-1d09c93331e6&geoPolygons'
                    f'=EKB-000000316&geoPolygons[]=EKB-000000319&geoPolygons[]='
                    f'=EKB-000000319&geoPolygons[]=EKB-000000318&geoPolygons[]='
                    f'EKB-000000320&pageNumber={i}'
                )
                json_data = self.get_json(url)

                if json_data is None:
                    break

                products = self.product(json_data)
                if not products:
                    break

                page_count += 1
                print(f"Обрабатавается страница №{page_count}")

                for product_ in products:
                    sleep(2)
                    url_ = product_['url']
                    id = product_['itemId']
                    rating = product_['reviews']['rating'] if 'reviews' in product_ and product_[
                        'reviews'] else "Данных о рейтинге нет"

                    item_json = self.get_json(
                        url=f'https://goldapple.ru/front/api/catalog/product-card?'
                            f'itemId={id}&cityId=c2deb16a-0330-4f05-821f-1d09c93331e6&'
                            f'geoPolygons[]=EKB-000000316&geoPolygons[]=EKB-000000319&'
                            f'geoPolygons[]=EKB-000000318&geoPolygons[]=EKB-000000320&'
                            f'customerGroupId=0'
                    )

                    if item_json is not None:
                        card_product_data = self.card_product(item_json)
                        card_product_data['ссылка'] = f"https://goldapple.ru{url_}"
                        card_product_data['рейтинг пользователей'] = rating
                        writer.writerow(card_product_data)

                    number_goods += 1
                    print(f"Обрабатавается товар №{number_goods}")

                i += 1

            print("Страницы закончились.")
            print(f"Всего спаршно: {number_goods} товаров")