from scipy.stats import linregress


def compute_fiber_score(fiber_value_in_gram):
    """
    Calculer la pente de la droite de régression linéaire.
    Calculer l’ordonnée à l’origine d’une droite de régression linéaire.

    :param fiber_value_in_gram:
    :return:
    """
    x = [2, 6]
    y = [0.5, 0.9]
    x_y_lin_regression = linregress(x, y)
    slope = x_y_lin_regression.slope
    intercept = x_y_lin_regression.intercept

    if (slope * fiber_value_in_gram + intercept) > 1:
        fiber_score = 1
    else:
        if (slope * fiber_value_in_gram + intercept) < 0:
            fiber_score = 0
        else:
            fiber_score = slope * fiber_value_in_gram + intercept
    return fiber_score


def compute_fiber_scores(foods_and_nutrients_in_reference_proportion):
    """
    Calculer la pente de la droite de régression linéaire.
    Calculer l’ordonnée à l’origine d’une droite de régression linéaire.

    :return:
    """
    x = [2, 6]
    y = [0.5, 0.9]
    x_y_lin_regression = linregress(x, y)
    slope = x_y_lin_regression.slope
    intercept = x_y_lin_regression.intercept

    fiber_values_and_scores = []
    for food_index, food in enumerate(foods_and_nutrients_in_reference_proportion):
        fiber_values_and_scores.append({})
        food_description = foods_and_nutrients_in_reference_proportion[food_index].get('key')

        for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']['nutrient_names']['buckets']):
            if 'FIBRES ALIMENTAIRES TOTALES' in nutrient.values():
                fiber_value = nutrient.get('Total_nutrients_values').get('value')

        if (slope * fiber_value + intercept) > 1:
            fiber_score = 1
        else:
            if (slope * fiber_value + intercept) < 0:
                fiber_score = 0
            else:
                fiber_score = slope * fiber_value + intercept

        fiber_values_and_scores[food_index].update({"food_description": food_description, "fiber_score": fiber_score})

    return fiber_values_and_scores


def compute_sugar_score(sugar_value_in_gram):
    x = [8, 10]
    y = [0.9, 0.8]
    x_y_lin_regression = linregress(x, y)
    slope = x_y_lin_regression.slope
    intercept = x_y_lin_regression.intercept

    if (slope * sugar_value_in_gram + intercept) > 1:
        sugar_score = 1
    else:
        if (slope * sugar_value_in_gram + intercept) < 0:
            sugar_score = 0
        else:
            sugar_score = slope * sugar_value_in_gram + intercept
    return sugar_score


def compute_sugar_scores(foods_and_nutrients_in_reference_proportion):
    x = [8, 10]
    y = [0.9, 0.8]
    x_y_lin_regression = linregress(x, y)
    slope = x_y_lin_regression.slope
    intercept = x_y_lin_regression.intercept

    sugar_values_and_scores = []
    for food_index, food in enumerate(foods_and_nutrients_in_reference_proportion):
        sugar_values_and_scores.append({})
        food_description = foods_and_nutrients_in_reference_proportion[food_index].get('key')

        for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']['nutrient_names']['buckets']):
            if 'SUCRES TOTAUX' in nutrient.values():
                sugar_value = nutrient.get('Total_nutrients_values').get('value')

        if (slope * sugar_value + intercept) > 1:
            sugar_score = 1
        else:
            if (slope * sugar_value + intercept) < 0:
                sugar_score = 0
            else:
                sugar_score = slope * sugar_value + intercept

        sugar_values_and_scores[food_index].update({"food_description": food_description, "sugar_score": sugar_score})
    return sugar_values_and_scores


def compute_global_score(fiber_score, sugar_score):

    return fiber_score * 0.5 + sugar_score + 0.5


def compute_global_score(fiber_scores, sugar_scores):
    global_scores = []
    for score_index, (fiber_score, sugar_score) in enumerate(zip(fiber_scores, sugar_scores)):
        global_scores.append({})
        food_description = fiber_score.get('food_description')
        fiber_score_value = fiber_score.get('fiber_score')
        sugar_score_value = sugar_score.get('sugar_score')
        global_score_value = fiber_score_value * 0.5 + sugar_score_value * 0.5
        global_scores[score_index].update({"food_description": food_description,
                                           "fiber_score": fiber_score_value,
                                           "sugar_score": sugar_score_value,
                                           "global_score": global_score_value})
    return global_scores
