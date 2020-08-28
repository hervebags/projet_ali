def suggest_the_best_combination_for_recipe_using_fcen(a_gac_recipe_with_its_recommendations):
    total_score = 0
    for item in a_gac_recipe_with_its_recommendations['hits']['hits'][0]['_source']['ingrédients']:
        print('Ingrédient: ', item['ingrédient'])
        print('Aliment recommendé: ', item['recommendations'][0]['food_description'])
        print('Fiber score: ', item['recommendations'][0]['fiber_score'])
        print('Sugar score: ', item['recommendations'][0]['sugar_score'])
        print('Global score: ', item['recommendations'][0]['global_score'])
        total_score += item['recommendations'][0]['global_score']
        print('------------------------------------')

    print('Recipe score:', total_score)

