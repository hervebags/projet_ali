from domaine import FoodScorer


# def make_recommendation(food):
#     """
#     bon_choix_ou_meilleur_choix
#
#     :return:
#     """
#
#     pass


def make_recommendations(foods_and_nutrients_in_reference_proportion):
    """
    bon_choix_ou_meilleur_choix

    :return:
    """
    fiber_scores = FoodScorer.compute_all_fiber_scores(foods_and_nutrients_in_reference_proportion)
    sugar_scores = FoodScorer.compute_sugar_scores(foods_and_nutrients_in_reference_proportion)
    global_scores = FoodScorer.compute_global_score(fiber_scores, sugar_scores)

    # Show text
    for score_index, global_score in enumerate(global_scores):
        if(global_score.get('fiber_score') >= 0.7) and (global_score.get('sugar_score') >= 0.7):
            global_scores[score_index].update({'recommendation': 'Meilleur choix'})
        elif(global_score.get('fiber_score') >= 0.4) and (global_score.get('sugar_score') >= 0.4):
            global_scores[score_index].update({'recommendation': 'Bon choix'})
        else:
            global_scores[score_index].update({'recommendation': 'Pas recommandé'})

    return global_scores


def display_recommendation_table(foods_and_nutrients_in_reference_proportion, food_scores_and_recommendations):
    # Create Pandas series
    indices = []  # food_descriptions
    for food_index, food in enumerate(foods_and_nutrients_in_reference_proportion):
        indices.append(food.get('key'))

    nutrient_names = {"lipids_satures": 'ACIDES GRAS SATURÉS TOTAUX',
                      "lipides_trans": 'ACIDES GRAS TRANS TOTAUX',
                      "calcium": 'CALCIUM',
                      "cholesterol": 'CHOLESTEROL',
                      "fer": 'FER',
                      "fibres": 'FIBRES ALIMENTAIRES TOTALES',
                      "glucides": 'GLUCIDES TOTAUX (PAR DIFFÉRENCE)',
                      "lipides": 'LIPIDES TOTAUX',
                      "potassium": 'POTASSIUM',
                      "proteines": 'PROTÉINES',
                      "sodium": 'SODIUM',
                      "sucres": 'SUCRES TOTAUX',
                      "vitamine_c": 'VITAMINE C',
                      "vitamine_a": "ÉQUIVALENTS D'ACTIVITÉ DU RÉTINOL"}

    all_found_nutrients = []
    nutrients_columns = []
    for nutrient_name_index, (nutrient_name_actual_name, nutrient_fcen_name) in enumerate(nutrient_names.items()):
        nutrient_list = []
        nutrients_columns.append(nutrient_name_actual_name)

        # Get one column at a time
        for food_index, food in enumerate(foods_and_nutrients_in_reference_proportion):
            found_nutrient_names = []
            for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']
                                                      ['nutrient_names']
                                                      ['buckets']):
                found_nutrient_names.append(nutrient.get('key'))

            if nutrient_fcen_name in found_nutrient_names:
                for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']
                                                          ['nutrient_names']
                                                          ['buckets']):
                    if nutrient.get('key') == nutrient_fcen_name:
                        nutrient_list.append(food['nutrients_nested_aggregation']
                                             ['nutrient_names']
                                             ['buckets'][nutrient_index].get('Total_nutrients_values').get('value'))
                        break
            else:
                nutrient_list.append(0)

        all_found_nutrients.append(nutrient_list)

    fiber_scores = []
    sugar_scores = []
    global_scores = []
    recommendations = []
    for food_score_index, food_score in enumerate(food_scores_and_recommendations):
        fiber_scores.append(food_score.get('fiber_score'))
        sugar_scores.append(food_score.get('sugar_score'))
        global_scores.append(food_score.get('global_score'))
        recommendations.append(food_score.get('recommendation'))

    return all_found_nutrients, indices, nutrients_columns, fiber_scores, sugar_scores, global_scores, recommendations


def display_recommendation_graph():
    pass


# def make_recommendation(score):
#     """
#     bon_choix_ou_meilleur_choix
#
#     :return:
#     """
#     pass


# def make_recommendation(scores):
#     """
#     bon_choix_ou_meilleur_choix
#
#     :return:
#     """
#     pass

def recommend_food_for_a_gac_recipe(ingredients):
    pass
