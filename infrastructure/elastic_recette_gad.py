import json
from time import sleep
from uuid import uuid4
from elasticsearch import Elasticsearch, helpers


es = Elasticsearch(hosts="localhost:9200")
elastic_client = Elasticsearch()

data_json = None
with open('data.txt', encoding='utf8') as json_file:
    data_json = json.load(json_file)

def generate_data(json_list, index: str):
    for doc in json_list:
            #id = doc['food_code'] + '00' + doc['nutrient_name_id'] # --------------------------------------------------
            id = str(uuid4())
            if '{"index"' not in doc:
                yield {
                    "_index": index,
                    "_id": id,
                    "_source": doc
                }


def index_documents_gac(elastic_client,json_list, index_name):
    # Create index
    print(f"Deleting index '{index_name}'...")
    elastic_client.indices.delete(index=index_name, ignore=[400, 404])
    print(f"Creating index '{index_name}'...")
    elastic_client.indices.create(index=index_name, ignore=400)

    # Prepare actions to be executed by the bulk helper


    data = generate_data(json_list, index_name)
    helpers.bulk(elastic_client, data,
                 chunk_size=1000,
                 request_timeout=120)






