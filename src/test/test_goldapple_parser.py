import unittest
from unittest.mock import Mock, patch

from src.goldapple_parser import ProductScraper


class TestProductScraper(unittest.TestCase):

    @patch('requests.Session.get')
    def test_get_json_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': {'products': {'products': [{}, {}]}}}
        mock_get.return_value = mock_response

        scraper = ProductScraper()
        json_data = scraper.get_json('https://example.com')

        self.assertIsNotNone(json_data)
        self.assertEqual(len(json_data['data']['products']['products']), 2)

    @patch('requests.Session.get')
    def test_get_json_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        scraper = ProductScraper()
        json_data = scraper.get_json('https://example.com')

        self.assertIsNone(json_data)

    def test_product_extraction(self):
        scraper = ProductScraper()
        json_data = {'data': {'products': {'products': [{'name': 'Product1'}, {'name': 'Product2'}]}}}
        products = scraper.product(json_data)

        self.assertIsNotNone(products)
        self.assertEqual(len(products), 2)

    def test_card_product_extraction_extra_keys(self):
        scraper = ProductScraper()
        example_response = {
            'data': {
                'productDescription': [
                    {'title': 'Product Title', 'content': 'Product Description'},
                    {'title': 'Instructions', 'content': 'Product Instructions'},
                    {'title': 'Other Info', 'content': 'Other Info'},
                    {'subtitle': 'Brand Country', 'extra_key': 'extra_value'}
                ],
                'variants': [
                    {'price': {'regular': {'amount': 100}, 'discount': {'amount': 80}, 'extra_key': 'extra_value'}}
                ],
                'extra_key': 'extra_value'
            }
        }
        product_data = scraper.card_product(example_response)
        self.assertEqual(product_data['описание'], 'Product Description')
        self.assertEqual(product_data['инструкция по применению'], 'Product Instructions')
        self.assertEqual(product_data['наименование'], 'Product Title')
        self.assertEqual(product_data['цена'], 100)
        self.assertEqual(product_data['цена со скидкой'], 80)
        self.assertEqual(product_data['страна бренда'], 'Brand Country')

    def test_card_product_extraction_all_keys(self):
        scraper = ProductScraper()
        example_response = {
            'data': {
                'productDescription': [
                    {'title': 'Product Title', 'content': 'Product Description'},
                    {'title': 'Instructions', 'content': 'Product Instructions'},
                    {'title': 'Other Info', 'content': 'Other Info'},
                    {'subtitle': 'Brand Country'}
                ],
                'variants': [
                    {'price': {'regular': {'amount': 100}, 'discount': {'amount': 80}}}
                ]
            }
        }
        product_data = scraper.card_product(example_response)
        self.assertEqual(product_data['описание'], 'Product Description')
        self.assertEqual(product_data['инструкция по применению'], 'Product Instructions')
        self.assertEqual(product_data['наименование'], 'Product Title')
        self.assertEqual(product_data['цена'], 100)
        self.assertEqual(product_data['цена со скидкой'], 80)
        self.assertEqual(product_data['страна бренда'], 'Brand Country')

    def test_card_product_extraction(self):
        scraper = ProductScraper()
        example_response = {
            'data': {
                'productDescription': [
                    {'title': 'Product Title', 'content': 'Product Description'},
                    {'title': 'Instructions', 'content': 'Product Instructions'},
                    {'title': 'Other Info', 'content': 'Other Info'},
                ],
                'variants': [
                    {'price': {'regular': {'amount': 100}, 'discount': {'amount': 80}}}
                ]
            }
        }
        product_data = scraper.card_product(example_response)
        self.assertEqual(product_data['наименование'], 'Product Title')
        self.assertEqual(product_data['описание'], 'Product Description')
        self.assertEqual(product_data['цена'], 100)
        self.assertEqual(product_data['цена со скидкой'], 80)

    def test_wrong_data_types_in_json(self):
        scraper = ProductScraper()
        wrong_types_json_data = {
            'data': {
                'products': {
                    'products': [
                        {'name': 123},
                        {'name': 'Product 2'}
                    ]
                }
            }
        }
        products = scraper.product(wrong_types_json_data)
        self.assertEqual(len(products), 2)

    def test_extra_keys_in_json(self):
        scraper = ProductScraper()
        extra_keys_json_data = {
            'data': {
                'products': {
                    'products': [
                        {'name': 'Product 1'},
                        {'name': 'Product 2'}
                    ],
                    'extra_key': 'extra_value'
                }
            }
        }
        products = scraper.product(extra_keys_json_data)
        self.assertEqual(len(products), 2)

    def test_invalid_product_data(self):
        scraper = ProductScraper()
        invalid_json_data = {
            'data': {
                'products': {
                    'products': [
                        {'name': 'Product 1'},
                        {'product_name': 'Product 2'}
                    ]
                }
            }
        }
        products = scraper.product(invalid_json_data)
        self.assertEqual(len(products), 2)

    def test_empty_json_response(self):
        scraper = ProductScraper()
        empty_json_data = {}
        products = scraper.product(empty_json_data)
        self.assertEqual(len(products) if products is not None else 0, 0)

    def test_empty_json(self):
        scraper = ProductScraper()
        empty_json_data = {}
        products = scraper.product(empty_json_data)
        self.assertIsNone(products)

    def test_card_product(self):
        scraper = ProductScraper()
        mock_response = {
            'data': {
                'productDescription': [
                    {'title': 'Test Product', 'content': 'This is a test description.'},
                    {'title': 'Instructions', 'content': 'This is a test instruction.'}
                ],
                'variants': [
                    {
                        'price': {
                            'regular': {'amount': '100'},
                            'discount': {'amount': '80'}
                        }
                    }
                ]
            }
        }

        product_data = scraper.card_product(mock_response)

        expected_product_data = {
            'описание': 'This is a test description.',
            'инструкция по применению': 'This is a test instruction.',
            'наименование': 'Test Product',
            'цена': '100',
            'цена со скидкой': '80',
            'страна бренда': 'Страна не указана'
        }

        self.assertEqual(product_data, expected_product_data)


if __name__ == '__main__':
    unittest.main()
