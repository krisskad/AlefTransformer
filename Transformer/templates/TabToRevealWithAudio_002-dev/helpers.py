from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, get_popup_mlo_from_text
from django.conf import settings
import os, shutil
import htmlentities


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


def image_xml(input_json_data, input_other_jsons_data, exiting_hashcode):
    """

    :param input_json_data: {
              "tabType": "image",
              "tabHeaderTxt": "text_108",
              "TabContentText": "text_036",
              "audio": "aud_008",
              "bgImage": "img_034"
            }
    :param input_other_jsons_data:
    :param exiting_hashcode:
    :return:
    """
    all_files = set()
    all_tags = []

    temp = []
    for _ in range(40):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    tabHeaderTxt = input_json_data.get("tabHeaderTxt", None)
    if tabHeaderTxt:
        tabHeaderTxt_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
    else:
        print("tabHeaderTxt Is not provided")
        tabHeaderTxt_text = ""

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                              xp:description="{htmlentities.encode(tabHeaderTxt_text)}" xp:fieldtype="folder"
                                              customclass="Normal">
        """
    )

    imageData = input_json_data.get("imageData", None)
    if imageData:
        imageData_src = input_json_data.get("src", None)
        if imageData_src:
            imageData_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageData_src]
            resp_img = copy_to_hashcode_dir(src_path=imageData_src, exiting_hashcode=exiting_hashcode)
            all_files.add(resp_img['relative_path'])
            exiting_hashcode.add(resp_img['hashcode'])
            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[7]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                        <alef_image xlink:label="{resp_img['hashcode']}" xp:name="alef_image"
                                    xp:description="" xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp_img['relative_path']}"
                                    width="1583" height="890"/>
                        </alef_image>
                    </alef_column>
                """
            )

    audio = input_json_data.get("audio", None)
    if audio:
        audio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio]
        resp = copy_to_hashcode_dir(src_path=audio_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="1" alignment="Center"
                         cellspan="1">
                <alef_audionew xlink:label="{temp[2]}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}"
                                    xp:name="alef_audiofile" xp:description=""
                                    audiocontrols="No" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
            </alef_column>
            """
        )
    else:
        print("Warning: Audio not found so ignoring audio tag")

    TabContentText = input_json_data.get("TabContentText", None)
    if TabContentText:
        TabContentText_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][TabContentText]

        popup_response = get_popup_mlo_from_text(
            text=TabContentText_text,
            input_other_jsons_data=input_other_jsons_data,
            all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            enable_question_statement=False
        )

        if popup_response:

            all_files = popup_response['all_files']
            exiting_hashcode = popup_response['exiting_hashcode']
            popup = "\n".join(popup_response['all_tags'])

            TabContentText_text_HtmlText = text_en_html_to_html_text(html_string=TabContentText_text)

            resp_text = write_html(
                text=TabContentText_text_HtmlText,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                        <alef_tooltip xlink:label="{temp[4]}" xp:name="alef_tooltip"
                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                """
            )
        else:

            resp_text = write_html(
                text=TabContentText_text,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                    </alef_column>
                """
            )

    else:
        print("tabHeaderTxt Is not provided so ignoring tag")

    bgImage = input_json_data.get("bgImage", None)
    if bgImage:
        bgImage_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][bgImage]
        resp = copy_to_hashcode_dir(src_path=bgImage_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[6]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                            xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}"
                            width="1583" height="890"/>
                </alef_image>
            </alef_column>
            """
        )

    all_tags.append(
        """
        </alef_section>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def button_with_popup(input_json_data, input_other_jsons_data, exiting_hashcode):
    pass