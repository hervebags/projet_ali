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


def fetch_main_nutrients_and_their_values(elastic_client, query_field_name, query_field_path, query_string="céréale",
                                          number_of_items_to_return=5):
    """
    Il y a 13 nutrits principaux d'après .....

    :param elastic_client:
    :param query_field_name:
    :param query_field_path:
    :param query_string:
    :param number_of_items_to_return:
    :return:
    """
    query_body = prepare_query_body(query_field_name, query_field_path, query_string=query_string,
                                    number_of_items_to_return=number_of_items_to_return)

    res = elastic_client.search(index="foods_enriched",
                                body=query_body, size=10,
                                track_total_hits=True)
    nutrients_with_their_values_json = res['aggregations']['Food_desc_aggr']['buckets']

    return nutrients_with_their_values_json