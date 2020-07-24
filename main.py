import infrastructure.Elastic_domain as elastic_domain
import interfaces.CanadienFoodFileResource as FoodResource


from elasticsearch import Elasticsearch, helpers

import infrastructure.FoodIndexer as FoodIndexer
import infrastructure.elastic_recette_gad as elastic_recette_gad
import interfaces.guidealimentaireca as gac
""" NB: You must start ElasticSearch before using this code """


""" All endpoint URLs """
base = "https://food-nutrition.canada.ca/api/"

#Canadian Nutrient (CNF) API
#CNF_FOOD_URL = base + "canadian-nutrient-file/food/?lang=fr&type=json&id=1256"
# A food cannot be further decomposed into ingredients.    --------------------------------------------------
#CNF_FOOD_URL = base + "canadian-nutrient-file/food/?lang=fr&type=json"
#CNF_NUTRIENT_NAME_URL = base + "canadian-nutrient-file/nutrientname/?lang=fr&type=json"
#CNF_NUTRIENT_GROUP_URL = base + "canadian-nutrient-file/nutrientgroup/?lang=fr&type=json"
#CNF_NUTRIENT_SOURCE_URL = base + "canadian-nutrient-file/nutrientsource/?lang=fr&type=json"
#CNF_NUTRIENT_AMOUNT_URL = base + "canadian-nutrient-file/nutrientamount/?type=json&lang=fr&id=1256"
#Identify the nutrient amount per 100 grams for a food. ----------------------------------------------------
#CNF_NUTRIENT_AMOUNT_URL = base + "canadian-nutrient-file/nutrientamount/?type=json&lang=fr"
#CNF_SERVING_SIZE_URL = base + "canadian-nutrient-file/servingsize/?type=json&lang=fr"
#CNF_REFUSE_AMOUNT_URL = base + "canadian-nutrient-file/refuseamount/?lang=fr&type=json"
#CNF_YIELD_AMOUNT_URL = base + "canadian-nutrient-file/yieldamount/?lang=fr&type=json"

#food_resource = FoodResource.CanadienFoodFileResource()
#foodIndexer = FoodIndexer.FoodIndexer()

if __name__ == "__main__":
    elastic_client = Elasticsearch(hosts=[elastic_domain.domain_address])
    """
    # Test health
    #  r = elastic_client.cluster.health(wait_for_status='yellow', request_timeout=1)
    # print(f"Status of '{r['cluster_name']}': {r['status']}")

    # Get resources as lists of jsons
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

    # Index the resources gotten
    # foodIndexer.index_documents(nutrient_name_jsons, elastic_client, "nutrient_names")
    #foodIndexer.index_documents(nutrient_source_jsons, elastic_client, "nutrient_sources")
    #foodIndexer.index_documents(nutrient_group_jsons, elastic_client, "nutrient_groups")
    #foodIndexer.index_documents(nutrient_amount_jsons, elastic_client, "nutrient_amounts")
    #foodIndexer.index_documents(food_jsons, elastic_client, "foods")
    """
    gac.find_data_GCA()
    elastic_recette_gad.index_documents_gac(elastic_client,"index_final")

    print("Got here")

