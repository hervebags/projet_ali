def enrich_recipes_data_with_nutrient_values(recipes_json, elastic_client):
    food_description = recipes_json[0]['ingrédients'][0]['ingrédient']

    query = {
        "query": {
            "match": {
                "food_description": food_description
            }
        }
    }
    res_foods_enriched_query = elastic_client.search(index="foods_enriched",
                                body=query, size=10,
                                track_total_hits=True)

    body = {
        "processors": [
            {
                "set": {
                    "field": "recommended_foods",
                    "value": res_foods_enriched_query['hits']['hits']
                }
            }
        ]
    }
    pipeline_id = str(uuid4())
    res_pipeline = elastic_client.put_pipeline(id, body)

    # elastic_client.update_by_query(index="gac", pipeline=pipeline_id)
