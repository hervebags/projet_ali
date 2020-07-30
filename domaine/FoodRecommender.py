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
    fiber_scores = FoodScorer.compute_fiber_scores(foods_and_nutrients_in_reference_proportion)
    sugar_scores = FoodScorer.compute_sugar_scores(foods_and_nutrients_in_reference_proportion)
    global_scores = FoodScorer.compute_global_score(fiber_scores, sugar_scores)

    # Show text
    for score_index, global_score in enumerate(global_scores):
        if(global_score.get('fiber_score') >= 0.7) and (global_score.get('sugar_score') >= 0.7):
            global_scores[score_index].update({'recommendation': 'Meilleur choix'})
        elif(global_score.get('fiber_score') >= 0.6) and (global_score.get('sugar_score') >= 0.6):
            global_scores[score_index].update({'recommendation': 'Bon choix'})
        else:
            global_scores[score_index].update({'recommendation': 'Pas recommandé'})

    return global_scores


def display_recommendation_table():
    pass


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