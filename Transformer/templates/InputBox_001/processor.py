from Transformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh,
                                 text_en_html_to_html_text,
                                 get_popup_mlo_from_text, convert_html_to_strong)
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode, align=None):
    try:
        from Transformer.helpers import assing_class_for_color
        text = assing_class_for_color(text)
    except:
        pass
    text = convert_html_to_strong(html_str=text)

    if align:
        template = f"""
        <html>
        <head>
            <title></title>
        </head>
        <body style="font-family:Helvetica, 'Helvetica Neue', Arial !important; font-size:13px;">
            <div style="text-align:{align}">{text}</div>
        </body>
        </html>
        """
    else:
        template = f"""
        <html>
        <head>
            <title></title>
        </head>
        <body style="font-family:Helvetica, 'Helvetica Neue', Arial !important; font-size:13px;">
            {text}
        </body>
        </html>
        """

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")

    with open(path_to_html, "w") as file:
        file.write(template.strip())

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")

    response = {
        "relative_path": relative_path,
        "hashcode": hashcode,
    }

    return response


def copy_to_hashcode_dir(src_path: str, exiting_hashcode: set):
    """
    :param src_path: example images/01.png
    :param exiting_hashcode: example
    :return:
    """

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)
    destination_src_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_path)))
    shutil.copy2(str(asset_abs_path), str(destination_src_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_path)))

    response = {
        "relative_path": relative_path,
        "hashcode": hashcode,
    }

    return response



def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = [
        """
        <!-- InputBox_001 -->
        """
    ]

    src = input_json_data["pageData"]["args"].get("src", None)
    inputBoxes = input_json_data["pageData"]["args"].get("inputBoxes", [])
    extraTexts = input_json_data["pageData"]["args"].get("extraTexts", [])

    buttonsPos = input_json_data["pageData"]["args"].get("buttonsPos", "") # Burger Writing GO
    bookPopUpButton = input_json_data["pageData"]["args"].get("bookPopUpButton", "") # Plot Diagram

    template_type = ""
    if buttonsPos:
        template_type = "Burger Writing GO"

    if bookPopUpButton:
        template_type = "Plot Diagram"

    if not template_type:
        raise Exception("No template identity found : please check input structure.json and note which type of template is this?")

    view_ref = input_json_data["pageData"]['viewRef']
    extraTextViewsorted_data = []

    try:
        view_obj = input_other_jsons_data["INPUT_VIEW_JSON_DATA"]["pages"][view_ref]
        extra_text_css_list = view_obj["pageData"]["args"]["extraTexts"]
        extraTextView = []
        for i, j in zip(extra_text_css_list, extraTexts):
            i["text"] = j["text"]
            extraTextView.append(i)

        # Define a custom key function to extract the integer value from the "top" key
        def sort_by_top(item):
            return int(float(item["top"].replace("px", "")))

        # Sort the data using the custom key function
        extraTextViewsorted_data = sorted(extraTextView, key=sort_by_top)

    except Exception as e:
        print(f"Error: {e}")

    title = ""
    if len(inputBoxes) < len(extraTexts):
        # there are more input and less text (There are title) remove title from text
        try:
            titleobj = extraTextViewsorted_data[0]
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][titleobj["text"]]
            extraTextViewsorted_data.pop(0)
        except Exception as e:
            print(f"Error : {e}")

    html_list = []
    try:
        if inputBoxes:
            for idx, hml_obj in enumerate(extraTextViewsorted_data):
                text_obj = extraTextViewsorted_data[idx]
                text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_obj["text"]]

                if text:
                    resp = write_html(
                        text=text,
                        exiting_hashcode=exiting_hashcode
                    )
                    exiting_hashcode.add(resp['hashcode'])
                    all_files.add(resp['relative_path'])

                    html_xml = f"""
                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                    """
                    html_list.append(html_xml)
    except Exception as e:
        print(e)

    temp = []
    for _ in range(5):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    html_join = "\n".join(html_list)
    all_tags.append(f"""
    <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description="{title}" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
            <alef_predefined_graphorganizer xlink:label="{temp[2]}" xp:name="alef_predefined_graphorganizer" xp:description="" xp:fieldtype="folder" type="{template_type}">
                {html_join}
            </alef_predefined_graphorganizer>
        </alef_column>
    </alef_section>
    """)

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def process_page_data(page_data, other_json_data, exiting_hashcode):
    # Custom processing for ClicktoRevealwithSubmit_001
    # Use page_data as needed
    try:
        xml_output = create_mlo(
            input_json_data=page_data,
            input_other_jsons_data=other_json_data,
            exiting_hashcode=exiting_hashcode
        )
    except Exception as e:
        raise Exception(f"Error: {e} --> {page_data}")
    return xml_output
