from datetime import datetime
import requests

from elasticsearch import Elasticsearch, helpers
from itertools import chain, islice
from json import dumps
from time import sleep
from uuid import uuid4

import infrastructure.ElasticDomain as elastic_domain
import os, uuid


def prepare_index_creation_body_for_gac_fcen_integration():
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "Catégories": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "cuisson": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "image": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "ingrédients": {
                    "type": "nested",
                    "properties": {
                        "ingrédient": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "recommendations": {
                            "type": "nested",
                            "properties": {
                                "fiber_score": {
                                    "type": "long"
                                },
                                "food_description": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "global_score": {
                                    "type": "long"
                                },
                                "sugar_score": {
                                    "type": "float"
                                }
                            }
                        },
                        "valeur": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "link": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "portion": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "préparation": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "temps": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "titre": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "truc": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                }
            }
        }
    }

    return mapping


class FoodIndexer:
    def __init__(self):
        pass

    def bulk_json_data(self, json_list, _index):
        for doc in json_list:
            if '{"index"' not in doc:
                yield {
                    "_index": _index,
                    "_id": doc['food_code'],
                    "_source": doc
                }

    def generate_data(self, json_list, index: str):
        for doc in json_list:
            #id = doc['food_code'] + '00' + doc['nutrient_name_id'] # --------------------------------------------------
            id = str(uuid4())
            if '{"index"' not in doc:
                yield {
                    "_index": index,
                    "_id": id,
                    "_source": doc
                }

    def generate_data_for_suggestor(self, json_list, index: str):
        for doc in json_list:
            id = str(uuid4())
            doc["food_description_suggest"] = doc["food_description"]
            if '{"index"' not in doc:
                yield {
                    "_index": index,
                    "_id": id,
                    "_source": doc
                }

    def generate_data_for_gac_fcen_matcher(self, recipes_jsons, recommendations_for_recipes, index: str):
        for doc,recommendations_for_one_recipe in zip(recipes_jsons, recommendations_for_recipes):
            doc.pop('_index')
            doc.pop('_type')
            doc.pop('_id')
            doc.pop('_score')
            doc = doc['_source']
            id = str(uuid4())

            for recommendation, (key, ingredient) in zip(recommendations_for_one_recipe, enumerate(doc['ingrédients'])):
                doc['ingrédients'][key].update({'recommendations': recommendation})

            if '{"index"' not in doc:
                yield {
                    "_index": index,
                    "_id": id,
                    "_source": doc
                }

    # pre-slice generator by chunks
    def chunks(self, iterable, chunk_size: int = 10): # ----------------------------------------------------------------
        iterator = iter(iterable)
        for first in iterator:
            yield chain([first], islice(iterator, chunk_size - 1))

    def index_documents(self, json_list, elastic_client, index_name):
        # Variables
        bulk_size = 1000

        # Create index
        print(f"Deleting index '{index_name}'...")
        elastic_client.indices.delete(index=index_name, ignore=[400, 404])
        print(f"Creating index '{index_name}'...")
        elastic_client.indices.create(index=index_name, ignore=400)

        # Prepare actions to be executed by the bulk helper
        print("Generating data...")
        data = self.generate_data(json_list, index_name)

        # Send data
        print("Sending...")
        cpt = 0
        for chunk in self.chunks(data, bulk_size):
            try:
                print(f"Bulk {cpt + 1}: size {bulk_size}")
                res = helpers.bulk(elastic_client, chunk,
                                   chunk_size=bulk_size,
                                   request_timeout=120)
                #assert res[0] == bulk_size --------------------------------------------------
            except Exception as e:
                print("ERROR:", e)
            cpt += 1

        # wait a bit
        sleep(2)

        # print result total
        #r = elastic_client.indices.stats(index=[index_name], metric="docs", level="indices")["indices"][index_name]
        #print("Data recorded...")
        #print(dumps(r, indent=2))

        # get one record
        """
        print("Example...")
        r = elastic_client.search(index=index_name)
        print(dumps(r['hits']['hits'][0], indent=2))
        """

    def index_generator_data(self, data_generator, elastic_client, index_name):
        # Variables
        bulk_size = 1000

        # Create index
        #print(f"Deleting index '{index_name}'...")
        #elastic_client.indices.delete(index=index_name, ignore=[400, 404])
        #print(f"Creating index '{index_name}'...")
        #elastic_client.indices.create(index=index_name, ignore=400)

        # Send data
        print("Sending...")
        cpt = 0
        for chunk in self.chunks(data_generator, bulk_size):
            try:
                print(f"Bulk {cpt + 1}: size {bulk_size}")
                res = helpers.bulk(elastic_client, chunk,
                                   chunk_size=bulk_size,
                                   request_timeout=120)
            except Exception as e:
                print("ERROR:", e)
            cpt += 1

        # wait a bit
        sleep(2)

    def index_gac_with_recommended_foods(self, recipes_jsons, recommendations_for_recipes, elastic_client, index_name):
        # Variables
        bulk_size = 10

        # Create index
        print(f"Deleting index '{index_name}'...")
        elastic_client.indices.delete(index=index_name, ignore=[400, 404])
        print(f"Creating index '{index_name}'...")
        index_creation_body = prepare_index_creation_body_for_gac_fcen_integration()
        index_creation_response = elastic_client.indices.create(index=index_name, body=index_creation_body,ignore=400)
        if 'acknowledged' in index_creation_response:
            if index_creation_response['acknowledged']:
                print("INDEX MAPPING SUCCESS FOR INDEX:", index_creation_response['index'])

        # Prepare actions to be executed by the bulk helper
        print("Generating data...")
        data = self.generate_data_for_gac_fcen_matcher(recipes_jsons=recipes_jsons,
                                                       recommendations_for_recipes=recommendations_for_recipes,
                                                       index=index_name)

        # Send data
        print("Sending...")
        cpt = 0
        for chunk in self.chunks(data, bulk_size):
            try:
                print(f"Bulk {cpt + 1}: size {bulk_size}")
                res = helpers.bulk(elastic_client, chunk,
                                   chunk_size=bulk_size,
                                   request_timeout=120)
                #assert res[0] == bulk_size --------------------------------------------------
            except Exception as e:
                print("ERROR:", e)
            cpt += 1

        # wait a bit
        sleep(2)

    def test_indexing(self, foods_with_nutrients_amounts, elastic_client):
        bulk_size = 10

        for food in foods_with_nutrients_amounts:
            #index_name = 'food_' + food['food_code'] # ----------------------------------------------------------------
            index_name = 'food_' + str(uuid4())
            # Create index
            print(f"Deleting index '{index_name}'...")
            elastic_client.indices.delete(index=index_name, ignore=[400, 404])
            print(f"Creating index '{index_name}'...")
            elastic_client.indices.create(index=index_name, ignore=400)

            # Prepare actions to be executed by the bulk helper
            print("Generating data...")
            data = self.generate_data(food, index_name)

            # Send data
            print("Sending...")
            cpt = 0
            for chunk in self.chunks(data, bulk_size):
                try:
                    print(f"Bulk {cpt + 1}: size {bulk_size}")
                    res = helpers.bulk(elastic_client, chunk,
                                       chunk_size=bulk_size,
                                       request_timeout=120)
                    assert res[0] == bulk_size
                except Exception as e:
                    print("ERROR:", e)
                cpt += 1

            # wait a bit
            sleep(2)

    def index_all_nutrient_amounts(self, nutrients_amounts_jsons, elastic_client):
        index_creation_result = elastic_client.indices.create(index="nutrient_amounts2", ignore=400)
        print("nutrient_amounts Index_creation_result: ", index_creation_result)
        print()

        try:
            # make the bulk call, and get a response
            response = helpers.bulk(elastic_client, self.bulk_json_data(nutrients_amounts_jsons, "nutrient_amounts"))
            print("\nRESPONSE:", response)
            print()
        except Exception as e:
            print("\nERROR:", e)

