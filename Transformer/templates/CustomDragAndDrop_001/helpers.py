from collections import Counter


def group_items_by_position(sorted_combined, objects):
    grouped_items = {i: [] for i in range(len(objects))}
    sorted_items = []
    for item in sorted_combined:
        item_top = float(item['top'].replace('px', ''))
        item_left = float(item['left'].replace('px', ''))
        item_width = float(item['width'].replace('px', ''))
        item_height = float(item['height'].replace('px', ''))
        for i, obj in enumerate(objects):
            obj_top = float(obj['top'].replace('px', ''))
            obj_left = float(obj['left'].replace('px', ''))
            obj_width = float(obj['width'].replace('px', ''))
            obj_height = float(obj['height'].replace('px', ''))
            if (obj_top <= item_top <= obj_top + obj_height) and (obj_left <= item_left <= obj_left + obj_width) and \
                    (item_left + item_width <= obj_left + obj_width):
                grouped_items[i].append(item)
                sorted_items.append(item)
                break

    return {"grouped_items": grouped_items, "sorted_items": sorted_items}


def merge_and_sort_arrays(texts, styles):
    # Combine the texts and styles into a single list of dictionaries
    combined = []
    for i, text in enumerate(texts):
        combined_dict = {'text': text['text']}
        combined_dict.update(styles[i])
        combined.append(combined_dict)

    # Sort the combined list by the 'top' key
    sorted_combined = sorted(combined, key=lambda x: float(x['top'].replace('px', '')))
    # print(sorted_combined)
    return sorted_combined


def sort_by_left(data):
    # Sort the list of dictionaries by the "left" key
    sorted_data = sorted(data, key=lambda x: float(x["left"].replace("px", "")))
    return sorted_data


def find_most_common_left(objects):
    try:
        if len(objects) <= 2:
            most_common_left = sort_by_left(objects)

            return [most_common_left[0], ]
        else:
            left_counts = Counter(obj['left'] for obj in objects)
            most_common_left = left_counts.most_common(1)[0][0]

        final_obj = []
        for i in objects:
            if i["left"] == most_common_left:
                final_obj.append(i)
        return final_obj
    except Exception as e:
        print(f"Error in find_most_common_left: {e}")
        return objects


def group_by_top(objects):
    grouped = {}
    for obj in objects:
        top_value = int(float(obj["top"].replace("px", "")))

        if top_value + 2 in grouped:
            top_value = top_value + 2
        if top_value - 2 in grouped:
            top_value = top_value - 2

        if top_value in grouped:
            grouped[top_value].append(obj)
        else:
            grouped[top_value] = [obj]
    return grouped


def group_text_by_area(texts, styles, objects, drop_items_positions, drop_items_ids, input_other_jsons_data,
                       title_text):
    # Example usage:
    # texts = [
    #         { "text": "CS_extraTxt_2" },
    #         { "text": "CS_extraTxt_4" },
    #         { "text": "CS_extraTxt_6" },
    #         { "text": "CS_extraTxt_8" },
    #         { "text": "CS_extraTxt_5" },
    #         { "text": "CS_extraTxt_9" },
    #         { "text": "CS_extraTxt_10" },
    #         { "text": "CS_extraTxt_3" },
    #         { "text": "CS_extraTxt_7" },
    #         { "text": "CS_extraTxt_1" }
    #       ]
    #
    # styles = [
    #         {
    #           "left": "214.35px",
    #           "top": "295.4px",
    #           "width": "278.15px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "214.35px",
    #           "top": "423.40000000000003px",
    #           "width": "419.55px",
    #           "height": "47.05px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "214.35px",
    #           "top": "548.4px",
    #           "width": "471.7px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "214.35px",
    #           "top": "675px",
    #           "width": "361.25px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "1035.4px",
    #           "top": "421.95px",
    #           "width": "13.4px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "978.6px",
    #           "top": "675px",
    #           "width": "13.4px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "1313.9px",
    #           "top": "238.15px",
    #           "width": "401.8px",
    #           "height": "90px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "894.5px",
    #           "top": "295.4px",
    #           "width": "13.4px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "1085.4px",
    #           "top": "548.4px",
    #           "width": "13.4px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         },
    #         {
    #           "left": "282.6px",
    #           "top": "196.6px",
    #           "width": "852.9px",
    #           "height": "46px",
    #           "fontSize": "35px",
    #           "color": "#000000",
    #           "fontFamily": "Roboto-Regular"
    #         }
    #       ]
    #
    # objects = [
    #         {
    #           "left": "173.8px",
    #           "top": "276.4px",
    #           "width": "1070.5px",
    #           "height": "84px"
    #         },
    #         {
    #           "left": "173.8px",
    #           "top": "402.9px",
    #           "width": "1070.5px",
    #           "height": "84px"
    #         },
    #         {
    #           "left": "173.8px",
    #           "top": "529.4px",
    #           "width": "1070.5px",
    #           "height": "84px"
    #         },
    #         {
    #           "left": "173.8px",
    #           "top": "656px",
    #           "width": "1070.5px",
    #           "height": "84px"
    #         },
    #         {
    #           "left": "1285.35px",
    #           "top": "199px",
    #           "width": "458.95px",
    #           "height": "541px"
    #         }
    #       ]
    #
    # drop_items = [
    #         { "left": "509.8px", "top": "290.4px" },
    #         { "left": "650.8px", "top": "416.9px" },
    #         { "left": "700.45px", "top": "543.4px" },
    #         { "left": "591.95px", "top": "670px" }
    #       ]

    most_common_left = find_most_common_left(objects)
    sorted_combined = merge_and_sort_arrays(texts, styles)
    response = group_items_by_position(sorted_combined, most_common_left)
    grouped_items = response["grouped_items"]
    sorted_items = response["sorted_items"]

    if title_text:
        main_title = title_text
    else:
        if len(sorted_combined) > len(sorted_items):
            # there is title present
            titles = []
            instructions = []
            for each_check in sorted_combined:
                if not each_check in sorted_items:
                    if "text" in each_check:
                        en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_check["text"]]
                        if int(float(each_check["left"].replace("px", ""))) >= 1300:
                            instructions.append(instructions)
                        else:
                            if int(float(each_check["top"].replace("px", ""))) <= 200:
                                titles.append(en_text)

            main_title = " ".join(titles)
            instructions_text = " ".join(instructions)
        else:
            main_title = title_text
            instructions_text = ""

    final_group = {}
    for key, items in grouped_items.items():
        group_of_tops = group_by_top(items)
        for top_key, top_items in group_of_tops.items():
            group_of_tops[top_key] = sort_by_left(top_items)

        final_group[key] = group_of_tops

    final = {}
    for group_key, group_val in final_group.items():
        drop_box_obj = drop_items_positions[group_key]
        drop_box_top = int(float(drop_box_obj["top"].replace("px", ""))) + 5
        group = {}
        for each_y_key, each_y_value in group_val.items():
            if drop_box_top in range(int(each_y_key) - 5, int(each_y_key) + 5):
                each_y_value.append(drop_box_obj)
                each_y_sorted = sort_by_left(each_y_value)
                group[each_y_key] = each_y_sorted

        final[group_key] = group

    final_text = []

    for key, val in final.items():
        try:
            drop_id = drop_items_ids[key].get("dropId")
        except Exception as e:
            drop_id = key
            print(f"Error: {e}")

        temp_text = []
        for k, v in val.items():
            for j in v:
                if "text" in j:
                    en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][j["text"]]
                    temp_text.append(en_text)
                else:
                    temp_text.append(f"""<span class="dragndrop">{drop_id}</span>""")

        final_text.append(" ".join(temp_text))

    text = "<hr>".join(final_text)

    if main_title:
        final_html_text = f"""<strong>{main_title}</strong><br>{text}"""
    else:
        final_html_text = text

    return final_html_text