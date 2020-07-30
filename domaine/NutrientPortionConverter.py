def convert_to_reference_proportion(nutrients_with_their_values_json, reference_proportion=55):
    """

    :param nutrients_with_their_values_json:
    :param reference_proportion: in gram
    :return:
    """
    fcen_portion = 100  # 100 g
    foods_with_nutrients_in_reference_proportion = nutrients_with_their_values_json.copy()

    for food_index, food in enumerate(foods_with_nutrients_in_reference_proportion):
        for nutrient_index, nutrient in enumerate(food['nutrients_nested_aggregation']['nutrient_names']['buckets']):
            nutrient_in_reference_proportion =\
                nutrient['Total_nutrients_values']['value'] * reference_proportion / fcen_portion

            foods_with_nutrients_in_reference_proportion[food_index].get('nutrients_nested_aggregation')\
                .get('nutrient_names').get('buckets')[nutrient_index].get('Total_nutrients_values')\
                .update({'value': nutrient_in_reference_proportion})
        # print()
    return foods_with_nutrients_in_reference_proportion