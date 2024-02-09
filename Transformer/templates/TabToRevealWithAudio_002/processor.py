from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, get_popup_mlo_from_text
from django.conf import settings
import os, shutil
import htmlentities
from .helpers import *


def write_html(text, exiting_hashcode):

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

    if "templates" in src_path:
        asset_abs_path = os.path.join(settings.INPUT_COMMON_DIR, src_path)
    else:
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
    all_tags = []

    all_tags = [
        """
        <!-- TabToRevealWithAudio_002 -->

        """
    ]

    # Extracting variables
    textFieldData = input_json_data["pageData"]["args"]["textFieldData"]

    qText = textFieldData.get("qText", None)
    if qText:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qText]
    else:
        print("qText Not provided")
        text = ""

    temp1 = []
    for _ in range(3):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp1.append(hashcode_temp)
    all_tags.append(
        f"""
        <alef_section xlink:label="{temp1[0]}" xp:name="alef_section" xp:description=""
                              xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp1[1]}" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_presentation xlink:label="{temp1[2]}" xp:name="alef_presentation"
                                           xp:description="" xp:fieldtype="folder" type="Tabs" showtitle="false"
                                           tab_title="{htmlentities.decode(text)}" multipleopen="false" firstopen="false">
        """
    )

    # Iterate Array
    tabArray = input_json_data["pageData"]["args"]["tabArray"]

    for each_obj in tabArray:

        if "tabType" in each_obj:
            if each_obj["tabType"] == "image":
                img_xml = image(each_obj, input_other_jsons_data, exiting_hashcode)
                all_files.update(img_xml['MANIFEST_FILES'])
                exiting_hashcode.update(img_xml['GENERATED_HASH_CODES'])
                all_tags.append(img_xml['XML_STRING'])

            # if each_obj["tabType"] == "buttonWithPopup":
            #     button_with_popup_xml = button_with_popup(each_obj, input_other_jsons_data, exiting_hashcode)
            #     all_files.update(button_with_popup_xml['MANIFEST_FILES'])
            #     exiting_hashcode.update(button_with_popup_xml['GENERATED_HASH_CODES'])
            #     all_tags.append(button_with_popup_xml['XML_STRING'])

            if each_obj['tabType'] == "cards":
                flipcards_xml = flipcards(each_obj, input_other_jsons_data, exiting_hashcode)
                all_files.update(flipcards_xml['MANIFEST_FILES'])
                exiting_hashcode.update(flipcards_xml['GENERATED_HASH_CODES'])
                all_tags.append(flipcards_xml['XML_STRING'])

            # if each_obj['tabType'] == "video":
            #     video_xml = video(each_obj, input_other_jsons_data, exiting_hashcode)
            #     all_files.update(video_xml['MANIFEST_FILES'])
            #     exiting_hashcode.update(video_xml['GENERATED_HASH_CODES'])
            #     all_tags.append(video_xml['XML_STRING'])

    all_tags.append(
        """
                </alef_presentation>
            </alef_column>
        </alef_section>
        """
    )
    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def process_page_data(page_data, other_json_data, exiting_hashcode):
    # Custom processing for ClicktoRevealwithSubmit_001
    # Use page_data as needed

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    return xml_output
