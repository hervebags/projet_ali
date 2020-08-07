import infrastructure.ElasticDomain as elastic_domain
import interfaces.CanadienFoodFileResource as FoodResource
import json
import pandas as pd
import xlrd

from uuid import uuid4

from elasticsearch import Elasticsearch, helpers

import infrastructure.FoodIndexer as FoodIndexer
import infrastructure.RecipesIndexer as elastic_recette_gad
import interfaces.GuideAlimentaireCaResource as gac
import domaine.FoodScorer as FoodScorer
import infrastructure.ElasticDataFetcher as ElasticDataFetcher
import domaine.NutrientPortionConverter as NutrientPortionConverter
import domaine.FoodRecommender as FoodRecommender

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

    # Fetch the 13 main nutrients (plus potassium) and their values
    query_field_nutrients_groups = "nutrients.name.nutrient_group.nutrient_group_name.keyword"
    query_field_nutrients = "nutrients.name.nutrient_name.keyword"
    main_nutrients_and_their_values = ElasticDataFetcher.\
        fetch_main_nutrients_and_their_values(elastic_client,
                                              "nutrient_names",
                                              query_field_nutrients,
                                              query_string="céréale",
                                              number_of_items_to_return=300)

    foods_and_nutrients_in_reference_proportion = NutrientPortionConverter.\
        convert_to_reference_proportion(main_nutrients_and_their_values, reference_proportion=55)

    # Compute scores
    fiber_scores_computed = FoodScorer.compute_fiber_scores(foods_and_nutrients_in_reference_proportion)
    sugar_scores_computed = FoodScorer.compute_sugar_scores(foods_and_nutrients_in_reference_proportion)
    global_scores_computed = FoodScorer.compute_global_score(fiber_scores_computed, sugar_scores_computed)

    # Make recommendations
    scores_and_recommendations = FoodRecommender.make_recommendations(foods_and_nutrients_in_reference_proportion)

    # Display recommendation table
    nutrients_matrix, indices, nutrients_columns, fiber_scores, sugar_scores, global_scores, recommendations = \
        FoodRecommender.display_recommendation_table(
            foods_and_nutrients_in_reference_proportion,
            scores_and_recommendations)

    nutrients_data_frame = pd.DataFrame(nutrients_matrix, index=nutrients_columns, columns=indices)
    nutrients_data_frame = nutrients_data_frame.T

    # Add scores and recommendations to nutrients matrix
    nutrients_data_frame.insert(14, 'Fiber score', fiber_scores)
    nutrients_data_frame.insert(15, 'Sugar score', sugar_scores)
    nutrients_data_frame.insert(16, 'Global score', global_scores)
    nutrients_data_frame.insert(17, 'Recommendation', recommendations)

    print("Got here!")
