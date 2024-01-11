from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, extract_span_info
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
    all_tags = [
        """
        <!-- AudiowithInputBox_001 -->

        """
    ]
    # Extracting variables
    # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
    textFieldData = input_json_data["pageData"]["args"]["textFieldData"]

    qText = textFieldData.get("qText", None)
    qHtmlText = ""
    text = ""
    if qText:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qText]
        qHtmlText = text_en_html_to_html_text(html_string=text)

    resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    temp = []
    for _ in range(40):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[12]}" xp:name="alef_section" xp:description=""
                      xp:fieldtype="folder" customclass="Text- Left">
            <alef_column xlink:label="{temp[13]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_notebook xlink:label="{temp[14]}" xp:name="alef_notebook"
                               xp:description="" xp:fieldtype="folder">
                    <alef_questionstatement xlink:label="{temp[15]}"
                                            xp:name="alef_questionstatement" xp:description=""
                                            xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[16]}"
                                              xp:name="alef_section_general" xp:description=""
                                              xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[17]}" xp:name="alef_column"
                                         xp:description="" xp:fieldtype="folder" width="auto">
                                <alef_tooltip xlink:label="{temp[18]}"
                                              xp:name="alef_tooltip" xp:description=""
                                              xp:fieldtype="folder">
                                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                               xp:description="" xp:fieldtype="html"
                                               src="../../../{resp['relative_path']}"/>
        """
    )

    # get span info
    span_info = extract_span_info(text=text)

    for span_content, span_attr_obj in span_info.items():
        data_ref = span_attr_obj["data-ref"]
        if data_ref is None:
            continue
        deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]

        front_img = deck_oj['front']['img']
        front_content_list = deck_oj['front']['content']
        front_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][front_])
                                  for front_ in front_content_list])
        front_text_resp = write_html(text=front_text, exiting_hashcode=exiting_hashcode)
        all_files.add(front_text_resp['relative_path'])
        exiting_hashcode.add(front_text_resp['hashcode'])

        back_img = deck_oj['back']['img']
        back_content_list = deck_oj['back']['content']
        back_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][back_])
                                 for back_ in back_content_list])
        back_text_resp = write_html(text=back_text, exiting_hashcode=exiting_hashcode)
        all_files.add(back_text_resp['relative_path'])
        exiting_hashcode.add(back_text_resp['hashcode'])

        front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]
        back_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][back_img]

        front_img_path_resp = copy_to_hashcode_dir(src_path=front_img_path, exiting_hashcode=exiting_hashcode)
        all_files.add(front_img_path_resp['relative_path'])
        exiting_hashcode.add(front_img_path_resp['hashcode'])

        back_img_path_resp = copy_to_hashcode_dir(src_path=back_img_path, exiting_hashcode=exiting_hashcode)
        all_files.add(back_img_path_resp['relative_path'])
        exiting_hashcode.add(back_img_path_resp['hashcode'])

        all_tags.append(
            f"""
            <alef_popupvalue xlink:label="{temp[0]}"
                             xp:name="alef_popupvalue" xp:description=""
                             xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp[1]}"
                                      xp:name="alef_section_general"
                                      xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="{temp[2]}"
                                 xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto">
                        <alef_flipcards xlink:label="{temp[3]}"
                                        xp:name="alef_flipcards" xp:description=""
                                        xp:fieldtype="folder" customtype="Flipcard"
                                        height="500" multipleopen="false"
                                        flipdirection="Right">
                            <alef_flipcard xlink:label="{temp[7]}"
                                           xp:name="alef_flipcard" xp:description=""
                                           xp:fieldtype="folder" centered="true">
                                <alef_section
                                        xlink:label="{temp[8]}"
                                        xp:name="alef_section" xp:description=""
                                        xp:fieldtype="folder" customclass="Normal">
                                    <alef_column
                                            xlink:label="{temp[9]}"
                                            xp:name="alef_column" xp:description=""
                                            xp:fieldtype="folder" width="auto"
                                            cellspan="1">
                                        <alef_html
                                                xlink:label="{front_text_resp['hashcode']}"
                                                xp:name="alef_html"
                                                xp:description=""
                                                xp:fieldtype="html"
                                                src="../../../{front_text_resp['relative_path']}"/>
                                        <alef_image
                                                xlink:label="{front_img_path_resp['hashcode']}"
                                                xp:name="alef_image"
                                                xp:description=""
                                                xp:fieldtype="image" alt="">
                                            <xp:img href="../../../{front_img_path_resp['relative_path']}"
                                                    width="1136" height="890"/>
                                        </alef_image>
                                    </alef_column>
                                </alef_section>
                                <alef_section
                                        xlink:label="{temp[10]}"
                                        xp:name="alef_section" xp:description=""
                                        xp:fieldtype="folder" customclass="Normal">
                                    <alef_column
                                            xlink:label="{temp[11]}"
                                            xp:name="alef_column" xp:description=""
                                            xp:fieldtype="folder" width="auto"
                                            cellspan="1">
                                        <alef_html
                                                xlink:label="{back_text_resp['hashcode']}"
                                                xp:name="alef_html"
                                                xp:description=""
                                                xp:fieldtype="html"
                                                src="../../../{back_text_resp['relative_path']}"/>
                                        <alef_image
                                                xlink:label="{back_img_path_resp['hashcode']}"
                                                xp:name="alef_image"
                                                xp:description=""
                                                xp:fieldtype="image" alt="">
                                            <xp:img href="../../../{back_img_path_resp['relative_path']}"
                                                    width="1396" height="890"/>
                                        </alef_image>
                                    </alef_column>
                                </alef_section>
                            </alef_flipcard>
                        </alef_flipcards>
                    </alef_column>
                </alef_section_general>
            </alef_popupvalue>
            """
        )

    all_tags.append(
        """
                        </alef_tooltip>
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        </alef_notebook>
        """
    )

    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    all_tags.append(
        f"""
        <alef_audionew xlink:label="{temp[22]}" xp:name="alef_audionew"
                       xp:description="" xp:fieldtype="folder">
            <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                            xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                            src="../../../{resp['relative_path']}"/>
        </alef_audionew>
        """
    )

    if "mediaBoxData" in input_json_data["pageData"]["args"]:
        img_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][
            input_json_data["pageData"]["args"]['mediaBoxData']["src"]]
    else:
        img_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][
            input_json_data["pageData"]["args"]['background']["src"]]

    resp = copy_to_hashcode_dir(src_path=img_src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    all_tags.append(
        f"""
        </alef_column>
            <alef_column xlink:label="{temp[23]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description=""
                            xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}" width="1920" height="1080"/>
                </alef_image>
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
