from elasticsearch import Elasticsearch, helpers


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
            "bool": {
                "must": [
                    {
                        "match": {
                            "food_description": query_string
                        }
                    },
                    {
                        "bool": {
                            "must_not": [
                                {
                                    "match": {
                                        "food_description": "bébé"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    return query_body


def prepare_food_enriched_data_fetcher_query_body():
    query_body = {
        "query": {
            "match_all": {}
        }
    }
    return query_body


def prepare_sugar_score_query_body():
    # "size": 100,

    query_body = {
        "query": {
            "match": {
                "food_description": "céréale"
            }
        },
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "lang": "painless",
                    "source": """
            float [] x_values = new float[]{8.0F, 10.0F};
            float [] y_values = new float[]{0.9F, 0.8F};

            float x_avg = (x_values[0] + x_values[1]) / 2;
            float y_avg = (y_values[0] + y_values[1]) / 2;

            float slope_numerator = 0;
            float slope_denominator = 0;
            for(int i=0; i<2; i++){
              slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
              slope_denominator += Math.pow((x_values[i] - x_avg), 2);
            }
            float slope = slope_numerator / slope_denominator;

            float intercept = y_avg - slope * x_avg;

            if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
              return -1;
            } else {
              double sugar_value = doc['nutrients2.nu269'].value;
              if ((slope * sugar_value + intercept) > 1) {
                return 1;
              } else {
                if ((slope * sugar_value + intercept) < 0) {
                  return 0;
                } else {
                  return slope * sugar_value + intercept;
                }
              }
            }
          """
                },
                "order": "desc"
            }
        },
        "_source": {
            "includes": [
                "food_code",
                "food_description"
            ]
        }
    }

    return query_body


def prepare_query_body_for_all_scores():
    """
    Sort by global_score

    :return:
    """
    query_body = {
        "query": {
            "match": {
                "food_description": "céréale"
            }
        },
        "_source": {
            "includes": [
                "food_code",
                "food_description"
            ]
        },
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "lang": "painless",
                    "source": """
              float [] x_values = new float[]{2.0F, 6.0F};
              float [] y_values = new float[]{0.5F, 0.9F};

              float x_avg = (x_values[0] + x_values[1]) / 2;
              float y_avg = (y_values[0] + y_values[1]) / 2;

              float slope_numerator = 0;
              float slope_denominator = 0;
              for(int i=0; i<2; i++){
                slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                slope_denominator += Math.pow((x_values[i] - x_avg), 2);
              }
              float slope = slope_numerator / slope_denominator;
              float intercept = y_avg - slope * x_avg;

              double fiber_score = 0;
              if (!doc.containsKey('nutrients2.nu291') || doc['nutrients2.nu291'].empty) {
                return 0;
              } else {
                double fiber_value = doc['nutrients2.nu291'].value;
                if ((slope * fiber_value + intercept) > 1) {
                  fiber_score = 1;
                } else {
                  if ((slope * fiber_value + intercept) < 0) {
                    fiber_score =  0;
                  } else {
                    fiber_score = slope * fiber_value + intercept;
                  }
                }


              x_values = new float[]{8.0F, 10.0F};
              y_values = new float[]{0.9F, 0.8F};

              x_avg = (x_values[0] + x_values[1]) / 2;
              y_avg = (y_values[0] + y_values[1]) / 2;

              slope_numerator = 0;
              slope_denominator = 0;
              for(int i=0; i<2; i++){
                slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                slope_denominator += Math.pow((x_values[i] - x_avg), 2);
              }
              slope = slope_numerator / slope_denominator;

              intercept = y_avg - slope * x_avg;

              double sugar_score = 0;
              if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
                return 0;
              } else {
                double sugar_value = doc['nutrients2.nu269'].value;
                if ((slope * sugar_value + intercept) > 1) {
                  sugar_score = 1;
                } else {
                  if ((slope * sugar_value + intercept) < 0) {
                    sugar_score =  0;
                  } else {
                    sugar_score =  slope * sugar_value + intercept;
                  }
                }
              }
                return (fiber_score * 0.5 + sugar_score* 0.5);
              }
          """
                },
                "order": "desc"
            }
        },
        "script_fields": {
            "fiber_score": {
                "script": {
                    "lang": "painless",
                    "source": """
              float [] x_values = new float[]{2.0F, 6.0F};
              float [] y_values = new float[]{0.5F, 0.9F};

              float x_avg = (x_values[0] + x_values[1]) / 2;
              float y_avg = (y_values[0] + y_values[1]) / 2;

              float slope_numerator = 0;
              float slope_denominator = 0;
              for(int i=0; i<2; i++){
                slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                slope_denominator += Math.pow((x_values[i] - x_avg), 2);
              }
              float slope = slope_numerator / slope_denominator;

              float intercept = y_avg - slope * x_avg;
              if (!doc.containsKey('nutrients2.nu291') || doc['nutrients2.nu291'].empty) {
                return 0;
              } else {
                double fiber_value = doc['nutrients2.nu291'].value;
                if ((slope * fiber_value + intercept) > 1) {
                  return 1;
                } else {
                  if ((slope * fiber_value + intercept) < 0) {
                    return 0;
                  } else {
                    return slope * fiber_value + intercept;
                  }
                }
              }
            """
                }
            },
            "sugar_score": {
                "script": {
                    "lang": "painless",
                    "source": """
              float [] x_values = new float[]{8.0F, 10.0F};
              float [] y_values = new float[]{0.9F, 0.8F};

              float x_avg = (x_values[0] + x_values[1]) / 2;
              float y_avg = (y_values[0] + y_values[1]) / 2;

              float slope_numerator = 0;
              float slope_denominator = 0;
              for(int i=0; i<2; i++){
                slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                slope_denominator += Math.pow((x_values[i] - x_avg), 2);
              }
              float slope = slope_numerator / slope_denominator;

              float intercept = y_avg - slope * x_avg;

              if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
                return 0;
              } else {
                double sugar_value = doc['nutrients2.nu269'].value;
                if ((slope * sugar_value + intercept) > 1) {
                  return 1;
                } else {
                  if ((slope * sugar_value + intercept) < 0) {
                    return 0;
                  } else {
                    return slope * sugar_value + intercept;
                  }
                }
              }
            """
                }
            }
        }
    }

    return query_body


def prepare_query_body_for_gag():
    query_body = {
        "query": {
            "match_all": {}
        }
    }

    return query_body


def prepare_query_body_for_gac_ingredients(food_description=""):
    query_body = {
        "query": {
            "match": {
                "food_description": food_description
            }
        },
        "_source": {
            "includes": [
                "food_code",
                "food_description"
            ]
        },
        "sort": {
            "_script": {
                "type": "number",
                "script": {
                    "lang": "painless",
                    "source": """
                  float [] x_values = new float[]{2.0F, 6.0F};
                  float [] y_values = new float[]{0.5F, 0.9F};

                  float x_avg = (x_values[0] + x_values[1]) / 2;
                  float y_avg = (y_values[0] + y_values[1]) / 2;

                  float slope_numerator = 0;
                  float slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  float slope = slope_numerator / slope_denominator;
                  float intercept = y_avg - slope * x_avg;

                  double fiber_score = 0;
                  if (!doc.containsKey('nutrients2.nu291') || doc['nutrients2.nu291'].empty) {
                    return 0;
                  } else {
                    double fiber_value = doc['nutrients2.nu291'].value;
                    if ((slope * fiber_value + intercept) > 1) {
                      fiber_score = 1;
                    } else {
                      if ((slope * fiber_value + intercept) < 0) {
                        fiber_score =  0;
                      } else {
                        fiber_score = slope * fiber_value + intercept;
                      }
                    }


                  x_values = new float[]{8.0F, 10.0F};
                  y_values = new float[]{0.9F, 0.8F};

                  x_avg = (x_values[0] + x_values[1]) / 2;
                  y_avg = (y_values[0] + y_values[1]) / 2;

                  slope_numerator = 0;
                  slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  slope = slope_numerator / slope_denominator;

                  intercept = y_avg - slope * x_avg;

                  double sugar_score = 0;
                  if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
                    return 0;
                  } else {
                    double sugar_value = doc['nutrients2.nu269'].value;
                    if ((slope * sugar_value + intercept) > 1) {
                      sugar_score = 1;
                    } else {
                      if ((slope * sugar_value + intercept) < 0) {
                        sugar_score =  0;
                      } else {
                        sugar_score =  slope * sugar_value + intercept;
                      }
                    }
                  }
                    return (fiber_score * 0.5 + sugar_score* 0.5);
                  }
              """
                },
                "order": "desc"
            }
        },
        "script_fields": {
            "fiber_score": {
                "script": {
                    "lang": "painless",
                    "source": """
                  float [] x_values = new float[]{2.0F, 6.0F};
                  float [] y_values = new float[]{0.5F, 0.9F};

                  float x_avg = (x_values[0] + x_values[1]) / 2;
                  float y_avg = (y_values[0] + y_values[1]) / 2;

                  float slope_numerator = 0;
                  float slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  float slope = slope_numerator / slope_denominator;

                  float intercept = y_avg - slope * x_avg;
                  if (!doc.containsKey('nutrients2.nu291') || doc['nutrients2.nu291'].empty) {
                    return 0;
                  } else {
                    double fiber_value = doc['nutrients2.nu291'].value;
                    if ((slope * fiber_value + intercept) > 1) {
                      return 1;
                    } else {
                      if ((slope * fiber_value + intercept) < 0) {
                        return 0;
                      } else {
                        return slope * fiber_value + intercept;
                      }
                    }
                  }
                """
                }
            },
            "sugar_score": {
                "script": {
                    "lang": "painless",
                    "source": """
                  float [] x_values = new float[]{8.0F, 10.0F};
                  float [] y_values = new float[]{0.9F, 0.8F};

                  float x_avg = (x_values[0] + x_values[1]) / 2;
                  float y_avg = (y_values[0] + y_values[1]) / 2;

                  float slope_numerator = 0;
                  float slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  float slope = slope_numerator / slope_denominator;

                  float intercept = y_avg - slope * x_avg;

                  if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
                    return 0;
                  } else {
                    double sugar_value = doc['nutrients2.nu269'].value;
                    if ((slope * sugar_value + intercept) > 1) {
                      return 1;
                    } else {
                      if ((slope * sugar_value + intercept) < 0) {
                        return 0;
                      } else {
                        return slope * sugar_value + intercept;
                      }
                    }
                  }
                """
                }
            },
            "global_score": {
                "script": {
                    "lang": "painless",
                    "source": """
                          float [] x_values = new float[]{2.0F, 6.0F};
                  float [] y_values = new float[]{0.5F, 0.9F};

                  float x_avg = (x_values[0] + x_values[1]) / 2;
                  float y_avg = (y_values[0] + y_values[1]) / 2;

                  float slope_numerator = 0;
                  float slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  float slope = slope_numerator / slope_denominator;
                  float intercept = y_avg - slope * x_avg;

                  double fiber_score = 0;
                  if (!doc.containsKey('nutrients2.nu291') || doc['nutrients2.nu291'].empty) {
                    return 0;
                  } else {
                    double fiber_value = doc['nutrients2.nu291'].value;
                    if ((slope * fiber_value + intercept) > 1) {
                      fiber_score = 1;
                    } else {
                      if ((slope * fiber_value + intercept) < 0) {
                        fiber_score =  0;
                      } else {
                        fiber_score = slope * fiber_value + intercept;
                      }
                    }


                  x_values = new float[]{8.0F, 10.0F};
                  y_values = new float[]{0.9F, 0.8F};

                  x_avg = (x_values[0] + x_values[1]) / 2;
                  y_avg = (y_values[0] + y_values[1]) / 2;

                  slope_numerator = 0;
                  slope_denominator = 0;
                  for(int i=0; i<2; i++){
                    slope_numerator += (x_values[i] - x_avg) * (y_values[i] - y_avg);
                    slope_denominator += Math.pow((x_values[i] - x_avg), 2);
                  }
                  slope = slope_numerator / slope_denominator;

                  intercept = y_avg - slope * x_avg;

                  double sugar_score = 0;
                  if (!doc.containsKey('nutrients2.nu269') || doc['nutrients2.nu269'].empty) {
                    return 0;
                  } else {
                    double sugar_value = doc['nutrients2.nu269'].value;
                    if ((slope * sugar_value + intercept) > 1) {
                      sugar_score = 1;
                    } else {
                      if ((slope * sugar_value + intercept) < 0) {
                        sugar_score =  0;
                      } else {
                        sugar_score =  slope * sugar_value + intercept;
                      }
                    }
                  }
                    return (fiber_score * 0.5 + sugar_score* 0.5);
                  }
                        """
                }
            }
        }
    }

    return query_body


def prepare_query_body_for_fetching_a_recipe_with_its_recommendations(recipe_name):
    query_body = {
        "query": {
            "match": {
                "titre.keyword": recipe_name
            }
        }
    }

    return query_body


def fetch_main_nutrients_and_their_values(elastic_client, query_field_name, query_field_path, index="foods_enriched",
                                          query_string="céréale", number_of_items_to_return=5):
    """
    Il y a 13 nutrits principaux d'après .....

    :param elastic_client:
    :param query_field_name:
    :param query_field_path:
    :param index:
    :param query_string:
    :param number_of_items_to_return:
    :return:
    """
    query_body = prepare_query_body(query_field_name, query_field_path, query_string=query_string,
                                    number_of_items_to_return=number_of_items_to_return)

    res = elastic_client.search(index=index,
                                body=query_body, size=10,
                                track_total_hits=True)
    nutrients_with_their_values_json = res['aggregations']['Food_desc_aggr']['buckets']

    return nutrients_with_their_values_json


def fetch_food_enriched(elastic_client, index="foods_enriched", size=10):
    query_body = prepare_food_enriched_data_fetcher_query_body()

    # res = elastic_client.search(index=index,
    #                             body=query_body, size=size,
    #                             track_total_hits=True)
    
    res = helpers.scan(elastic_client, query=query_body, scroll='5m', preserve_order=True, size=size)
    return res


def fetch_sorted_sugar_scores(elastic_client, index="foods_enriched", size=10):
    query_body = prepare_sugar_score_query_body()

    res = elastic_client.search(index=index,
                                body=query_body, size=size,
                                track_total_hits=True)

    return res


def fetch_fiber_score():
    pass


def fetch_global_score():
    pass


def fetch_all_scores(elastic_client, index="foods_enriched", size=10):
    query_body = prepare_query_body_for_all_scores()

    res = elastic_client.search(index=index,
                                body=query_body, size=size,
                                track_total_hits=True)
    return res


def fetch_gac_data(elastic_client, index="gac", size=10):
    query_body = prepare_query_body_for_gag()

    res = elastic_client.search(index=index,
                                body=query_body, size=size,
                                track_total_hits=True)
    return res


def fetch_matching_foods_for_recipes(elastic_client, gac_recipes, index="foods_enriched", size=10):
    recommendations_for_all_recipes = list()
    for recipe in gac_recipes:
        ingredients = recipe['_source']['ingrédients']

        recommendations_for_all_ingredients = list()
        for ingredient in ingredients:
            query_body = prepare_query_body_for_gac_ingredients(ingredient['ingrédient'])
            res = elastic_client.search(index=index,
                                        body=query_body, size=size,
                                        track_total_hits=True)

            recommendations_for_one_ingredient = list()
            for food in res['hits']['hits']:
                recommendation = dict()
                recommendation['food_description'] = food['_source']['food_description']
                recommendation['fiber_score'] = food['fields']['fiber_score'][0]
                recommendation['sugar_score'] = food['fields']['sugar_score'][0]
                recommendation['global_score'] = food['fields']['global_score'][0]
                recommendations_for_one_ingredient.append(recommendation)
            recommendations_for_all_ingredients.append(recommendations_for_one_ingredient)
        recommendations_for_all_recipes.append(recommendations_for_all_ingredients)

    return recommendations_for_all_recipes


def fetch_matching_foods_for_ingredient(elastic_client, ingredient, index="foods_enriched", size=10):
    query_body = prepare_query_body_for_gac_ingredients(ingredient['ingrédient'])
    res = elastic_client.search(index=index,
                                body=query_body, size=size,
                                track_total_hits=True)

    # print("Ingrédient: " + ingredient['ingrédient'])
    # print("-------------------------- Matching food: --------------------------------")
    # for food in res['hits']['hits']:
    #     print(food['_source']['food_description'])
    #     if food['fields']['fiber_score'][0] is not None:
    #         print("Fiber score = " + str(food['fields']['fiber_score'][0]))
    #     if food['fields']['sugar_score'][0] is not None:
    #         print("Sugar score = " + str(food['fields']['sugar_score'][0]))
    #     if food['fields']['global_score'][0] != -1:
    #         print("Global score = " + str(food['fields']['global_score'][0]))
    #     else:
    #         print("Pas de score global")
    #     print()
    # print("\n\n")

    return res['hits']['hits']


def fetch_a_recipe_with_its_recommendations(elastic_client, recipe_name, index="gac_with_recommendations", size=1):
    query_body = prepare_query_body_for_fetching_a_recipe_with_its_recommendations(recipe_name)
    res = elastic_client.search(index=index,
                                body=query_body, filter_path=['hits.hits._source.ingrédients.ingrédient',
                                                              'hits.hits._source.ingrédients.recommendations'
                                                              ],
                                size=size)

    return res
