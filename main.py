import infrastructure.ElasticDomain as elastic_domain
import interfaces.CanadienFoodFileResource as FoodResource
import json
import xlrd

from uuid import uuid4

from elasticsearch import Elasticsearch, helpers
from scipy.stats import linregress

import infrastructure.FoodIndexer as FoodIndexer
import infrastructure.RecipesIndexer as elastic_recette_gad
import interfaces.GuideAlimentaireCaResource as gac

""" NB: You must start ElasticSearch before using this code """

""" All endpoint URLs """
base = "https://food-nutrition.canada.ca/api/"

# Canadian Nutrient (CNF) API
CNF_FOOD_URL = base + "canadian-nutrient-file/food/?lang=fr&type=json&id=1256"
CNF_FOOD_URL = base + "canadian-nutrient-file/food/?lang=fr&type=json"
CNF_NUTRIENT_NAME_URL = base + "canadian-nutrient-file/nutrientname/?lang=fr&type=json"
CNF_NUTRIENT_GROUP_URL = base + "canadian-nutrient-file/nutrientgroup/?lang=fr&type=json"
CNF_NUTRIENT_SOURCE_URL = base + "canadian-nutrient-file/nutrientsource/?lang=fr&type=json"
CNF_NUTRIENT_AMOUNT_URL = base + "canadian-nutrient-file/nutrientamount/?type=json&lang=fr&id=1256"
CNF_NUTRIENT_AMOUNT_URL = base + "canadian-nutrient-file/nutrientamount/?type=json&lang=fr"
CNF_SERVING_SIZE_URL = base + "canadian-nutrient-file/servingsize/?type=json&lang=fr"
CNF_REFUSE_AMOUNT_URL = base + "canadian-nutrient-file/refuseamount/?lang=fr&type=json"
CNF_YIELD_AMOUNT_URL = base + "canadian-nutrient-file/yieldamount/?lang=fr&type=json"

food_resource = FoodResource.CanadienFoodFileResource()
foodIndexer = FoodIndexer.FoodIndexer()


def prepare_query_body(query_field_name, query_field_path, query_string="céréale", number_of_items_to_return=5):
    query_body = {
        "aggs": {
            "Food_desc_aggr": {
                "terms": {
                    "field": "food_description.keyword",
                    "size": number_of_items_to_return
                },
                "aggs": {
                    "nutrients_nested_aggregation": {
                        "nested": {
                            "path": "nutrients"
                        },
                        "aggs": {
                            query_field_name: {
                                # Must be aggregation name ---------------------------------------------
                                "terms": {
                                    "field": query_field_path,
                                    "include": [
                                        "LIPIDES TOTAUX",
                                        "ACIDES GRAS SATURÉS TOTAUX",
                                        "ACIDES GRAS TRANS TOTAUX",
                                        "CHOLESTEROL",
                                        "SODIUM",
                                        "GLUCIDES TOTAUX (PAR DIFFÉRENCE)",
                                        "FIBRES ALIMENTAIRES TOTALES",
                                        "SUCRES TOTAUX",
                                        "PROTÉINES",
                                        "ÉQUIVALENTS D'ACTIVITÉ DU RÉTINOL",
                                        "VITAMINE C",
                                        "CALCIUM",
                                        "FER",
                                        "POTASSIUM"
                                    ],
                                    "size": 20
                                },
                                "aggs": {
                                    "Total_nutrients_values": {
                                        "sum": {
                                            "field": "nutrients.nutrient_value"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "query": {
            "match": {
                "food_description": query_string
            }
        }
    }
    return query_body


def fetch_main_nutrients_and_their_values(query_field_name, query_field_path, query_string="céréale",
                                          number_of_items_to_return=5):
    """
    Il y a 13 nutrits principaux d'après .....

    :param query_field_name:
    :param query_field_path:
    :param query_string:
    :param number_of_items_to_return:
    :return:
    """
    query_body = prepare_query_body(query_field_name, query_field_path, query_string="céréale",
                                    number_of_items_to_return=5)

    res = elastic_client.search(index="foods_enriched",
                                body=query_body, size=10,
                                track_total_hits=True)
    nutrients_with_their_values_json = res['aggregations']['Food_desc_aggr']['buckets']

    return nutrients_with_their_values_json


def convert_to_reference_proportion(nutrients_with_their_values_json, reference_proportion=55):
    """

    :param nutrients_with_their_values_json:
    :param reference_proportion: in gram
    :return:
    """
    fcen_portion = 100  # 100 g
    foods_with_nutrients_in_reference_proportion = nutrients_with_their_values_json.copy()

    for food_index, food in enumerate(foods_with_nutrients_in_reference_proportion):
        for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']['nutrient_names']['buckets']):
            nutrient_in_reference_proportion =\
                nutrient['Total_nutrients_values']['value'] * reference_proportion / fcen_portion

            foods_with_nutrients_in_reference_proportion[food_index].get('nutrients_nested_aggregation')\
                .get('nutrient_names').get('buckets')[nutrient_index].get('Total_nutrients_values')\
                .update({'value': nutrient_in_reference_proportion})
        # print()
    return foods_with_nutrients_in_reference_proportion


def compute_fiber_score(fiber_value_in_gram):
    """
    Calculer la pente de la droite de régression linéaire.
    Calculer l’ordonnée à l’origine d’une droite de régression linéaire.

    :param nutrients_with_their_values_json:
    :param fiber_value_in_gram:
    :return:
    """
    x = [2, 6]
    y = [0.5, 0.9]
    x_y_lin_regression = linregress(x, y)
    slope = x_y_lin_regression.slope
    intercept = x_y_lin_regression.intercept

    fiber_score = 0
    if (slope * fiber_value_in_gram + intercept) > 1:
        fiber_score = 1
    else:
        if (slope * fiber_value_in_gram + intercept) < 0:
            fiber_score = 0
        else:
            fiber_score = slope * fiber_value_in_gram + intercept
    return fiber_score


def compute_sugar_score():
    pass


def compute_global_score():
    pass


def get_recommandation_bon_choix_ou_meilleur_choix():
    pass


if __name__ == "__main__":
    elastic_client = Elasticsearch(hosts=[elastic_domain.domain_address])

    # Test health
    r = elastic_client.cluster.health(wait_for_status='yellow', request_timeout=1)
    print(f"Status of '{r['cluster_name']}': {r['status']}")

    # Get resources as lists of jsons
    """
    print("Fetching nutrient names ...")
    #nutrient_name_response, nutrient_name_jsons = food_resource.get_all_json_document(CNF_NUTRIENT_NAME_URL)
    #print(str(nutrient_name_jsons ))
    print("Fetching nutrient sources ...")
    #nutrient_source_response, nutrient_source_jsons = food_resource.get_all_json_document(CNF_NUTRIENT_SOURCE_URL)
    print("Fetching nutrient groups ...")
    # nutrient_group_response, nutrient_group_jsons = food_resource.get_all_json_document(CNF_NUTRIENT_GROUP_URL)
    print("Fetching nutrient amounts ...")
    # nutrient_amount_response, nutrient_amount_jsons = food_resource.get_all_json_document(CNF_NUTRIENT_AMOUNT_URL)
    print("Fetching foods ...")
    #ici ----------------
    print('matching ici')
    food_response, food_jsons = food_resource.get_all_json_document(CNF_FOOD_URL)
    print("Fetching serving sizes ...")
    serving_size_response, serving_size_jsons = food_resource.get_all_json_document(CNF_SERVING_SIZE_URL)
    print("Fetching refuse amounts ...")
    refuse_amount_response, refuse_amount_jsons = food_resource.get_all_json_document(CNF_REFUSE_AMOUNT_URL)
    print("Fetching yield amounts ...")
    yield_amount_response, yield_amount_jsons = food_resource.get_all_json_document(CNF_YIELD_AMOUNT_URL)
    """

    # print("Fetching GAC data ...")
    # gac.find_data_GCA()

    # Index the resources gotten
    # foodIndexer.index_documents(nutrient_name_jsons, elastic_client, "nutrient_names")
    # foodIndexer.index_documents(nutrient_source_jsons, elastic_client, "nutrient_sources")
    # foodIndexer.index_documents(nutrient_group_jsons, elastic_client, "nutrient_groups")
    # foodIndexer.index_documents(nutrient_amount_jsons, elastic_client, "nutrient_amounts")
    # foodIndexer.index_documents(food_jsons, elastic_client, "foods")
    # foodIndexer.index_documents(serving_size_jsons, elastic_client, "serving_size")
    # foodIndexer.index_documents(refuse_amount_jsons, elastic_client, "refuse_amount")
    # foodIndexer.index_documents(yield_amount_jsons, elastic_client, "yield_amount")

    # elastic_recette_gad.index_documents_gac(elastic_client,"gac")

    # Fetch the 13 main nutrients and their values
    query_field_nutrients_groups = "nutrients.name.nutrient_group.nutrient_group_name.keyword"
    query_field_nutrients = "nutrients.name.nutrient_name.keyword"
    main_nutrients_and_their_values = fetch_main_nutrients_and_their_values("nutrient_names",
                                                                            query_field_nutrients,
                                                                            query_string="céréale",
                                                                            number_of_items_to_return=5)
    foods_and_nutrients_in_reference_proportion = convert_to_reference_proportion(main_nutrients_and_their_values,
                                                                                  reference_proportion=55)

    print("fiber score is: ", compute_fiber_score(4))

    print("Got here!")
