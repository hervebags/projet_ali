# -*- coding: utf-8 -*-

import json
# import pandas as pd
import requests

from requests.exceptions import HTTPError

"""
If you wanna insert large data and you care efficiency at the same time, you
can use helpers.streaming_bulk or helpers.parallel_bulk to speed up your
operations.
"""


class CanadienFoodFileResource:
    def __init__(self):
        pass

    def get_all_json_document(self, url):
        response = requests.get(url)
        try:
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')
            pass

        json_documents = response.json()

        return response, json_documents

    def get_all_foods(self, url):
        # Try id = 1256
        response = requests.get(url)
        try:
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')
            pass

        foods_jsons = response.json()

        return response, foods_jsons

    def get_all_foods_with_nutrients(self, foods_url, nutrients_url):
        """
        Todo:
        Add error checking

        :param foods_url:
        :param nutrients_url:
        :return:
        """
        for food in requests.get(foods_url).json():
            nutrient_amounts = requests.get(f"{nutrients_url}&id={food['food_code']}").json()
            yield {**food, 'nutrient_amounts': nutrient_amounts}

    def get_nutrient_group_by_id(self, url):
        response = requests.get(url)

        return response

    def get_nutrient_source_by_id(self, url):
        response = requests.get(url)

        return response

    def get_nutrient_amounts_for_food_code(self, url, food_code):
        food_code_url = url + "&id=" + str(food_code)

        response = requests.get(food_code_url)
        try:
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')
            pass

        nutrient_amounts_jsons = response.json()

        return response, nutrient_amounts_jsons

    def get_all_nutrient_amounts(self, url):
        response = requests.get(url)
        try:
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print('Success!')

        nutrient_amounts_jsons = response.json()

        return response, nutrient_amounts_jsons

    def get_serving_size_by_food_id(self, url):
        response = requests.get(url)

        return response

    def get_refuse_amount_by_food_id(self, url):
        response = requests.get(url)

        return response

    def get_yield_amount_by_food_id(self, url):
        response = requests.get(url)

        return response
