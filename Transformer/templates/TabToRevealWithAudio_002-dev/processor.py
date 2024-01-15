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


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = []

    # Extracting variables
    # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
    textFieldData = input_json_data["pageData"]["args"]["textFieldData"]

    qText = textFieldData.get("qText", None)
    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qText]

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
        temp2 = []
        for _ in range(40):
            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp)
            temp2.append(hashcode_temp)

        if "tabType" in each_obj:
            if each_obj["tabType"] == "image":
                tabHeaderTxt = each_obj.get("tabHeaderTxt")
                if tabHeaderTxt:
                    tabHeaderTxt = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
                else:
                    print("No tab header text found. Assigned it as blank string")
                    tabHeaderTxt = ""

                all_tags.append(
                    f"""
                            <alef_section xlink:label="{temp2[0]}" xp:name="alef_section"
                              xp:description="{htmlentities.encode(tabHeaderTxt)}" xp:fieldtype="folder"
                              customclass="Normal">
                    """
                )

                audio = each_obj.get("audio")
                if audio:
                    audio = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio]
                    resp = copy_to_hashcode_dir(
                        src_path=audio,
                        exiting_hashcode=exiting_hashcode
                    )
                    all_files.add(resp['relative_path'])
                    exiting_hashcode.add(resp['hashcode'])

                    all_tags.append(
                        f"""
                            <alef_column xlink:label="{temp2[1]}" xp:name="alef_column"
                                         xp:description="" xp:fieldtype="folder" width="1" alignment="Center"
                                         cellspan="1">
                                <alef_audionew xlink:label="{temp2[2]}" xp:name="alef_audionew"
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
                    print("No tab audio found. Ignoring the tag")

                TabContentText = each_obj.get("TabContentText")
                if TabContentText:
                    all_tags.append(
                        f"""
                            <alef_column xlink:label="{temp2[3]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                        """
                    )
                    TabContentText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][TabContentText]
                    qHtmlText = text_en_html_to_html_text(html_string=TabContentText)
                    qHtmlText_resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
                    all_files.add(qHtmlText_resp['relative_path'])
                    exiting_hashcode.add(qHtmlText_resp['hashcode'])

                    popup_resp = get_popup_mlo_from_text(
                        text=TabContentText,
                        exiting_hashcode=exiting_hashcode,
                        all_files=all_files,
                        input_other_jsons_data=input_other_jsons_data
                    )
                    if popup_resp:
                        exiting_hashcode = popup_resp['exiting_hashcode']
                        all_files = popup_resp['all_files']
                        popups = "\n".join(popup_resp['all_tags'])

                        all_tags.append(
                            f"""

                                    <alef_tooltip xlink:label="{temp1[4]}" xp:name="alef_tooltip"
                                                  xp:description="" xp:fieldtype="folder">
                                        <alef_questionstatement xlink:label="{temp2[5]}"
                                                                xp:name="alef_questionstatement" xp:description=""
                                                                xp:fieldtype="folder">
                                            <alef_section_general xlink:label="{temp2[6]}"
                                                                  xp:name="alef_section_general" xp:description=""
                                                                  xp:fieldtype="folder">
                                                <alef_column xlink:label="{temp2[7]}"
                                                             xp:name="alef_column" xp:description=""
                                                             xp:fieldtype="folder" width="auto"/>
                                            </alef_section_general>
                                        </alef_questionstatement>
                                        <alef_html xlink:label="{qHtmlText_resp['hashcode']}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{qHtmlText_resp['relative_path']}"/>
                                        {popups}
                                    </alef_tooltip>
                                </alef_column>
                            """
                        )

                    else:
                        all_tags.append(
                            f"""
                                <alef_questionstatement xlink:label="{temp2[5]}"
                                                        xp:name="alef_questionstatement" xp:description=""
                                                        xp:fieldtype="folder">
                                    <alef_section_general xlink:label="{temp2[6]}"
                                                          xp:name="alef_section_general" xp:description=""
                                                          xp:fieldtype="folder">
                                        <alef_column xlink:label="{temp2[7]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto"/>
                                    </alef_section_general>
                                </alef_questionstatement>
                                <alef_html xlink:label="{qHtmlText_resp['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{qHtmlText_resp['relative_path']}"/>
                            </alef_column>
                            """
                        )

                else:
                    print("No TabContentText found. Ignoring...")


                bgImage = each_obj.get("bgImage")
                if bgImage:
                    bgImage = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][bgImage]
                else:
                    print("No tab bgImage text found. Assigned it as blank string")
                    bgImage = ""

            if each_obj["tabType"] == "image":
                # tabHeaderTxt = each_obj["tabHeaderTxt"]
                TabContentText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_obj["TabContentText"]]
                # audio = each_obj["audio"]
                if "bgImage" in each_obj:
                    Image = each_obj["bgImage"]

                qHtmlText = text_en_html_to_html_text(html_string=TabContentText)

                qHtmlText_resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
                all_files.add(qHtmlText_resp['relative_path'])
                exiting_hashcode.add(qHtmlText_resp['hashcode'])

                popup_resp = get_popup_mlo_from_text(
                    text=TabContentText,
                    exiting_hashcode=exiting_hashcode,
                    all_files=all_files,
                    input_other_jsons_data=input_other_jsons_data
                )
                popups = ""
                if popup_resp:
                    exiting_hashcode = popup_resp['exiting_hashcode']
                    all_files = popup_resp['all_files']
                    popups = "\n".join(popup_resp['all_tags'])

                temp1 = []
                for _ in range(10):
                    hashcode_temp1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                    exiting_hashcode.add(hashcode_temp1)
                    temp1.append(hashcode_temp1)

                all_tags.append(
                    f"""
                        <alef_column xlink:label="{temp1[0]}" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                     cellspan="1">
                            <alef_tooltip xlink:label="{temp1[1]}" xp:name="alef_tooltip"
                                          xp:description="" xp:fieldtype="folder">
                                <alef_html xlink:label="{qHtmlText_resp['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{qHtmlText_resp['relative_path']}"/>
                                {popups}
                            </alef_tooltip>
                        </alef_column>
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
