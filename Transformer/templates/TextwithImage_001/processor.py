from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, get_popup_mlo_from_text
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode, align=None):

    if align:
        template = f"""
        <html>
        <head>
            <title></title>
        </head>
        <body style="font-family:Helvetica, 'Helvetica Neue', Arial !important; font-size:13px;">
            <div style="text-align:center">{text}</div>
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
        <!-- TextwithImage_001 -->

        """
    ]

    # Assigning values to variables
    aud_id = input_json_data["pageData"]["args"]["src"]
    ques_id = input_json_data["pageData"]["args"]["ques"]
    text_id = input_json_data["pageData"]["args"]["textFieldData"]["textContent"]["text"]
    # align = input_json_data["pageData"]["args"]["textFieldData"]["textContent"].get("type", None)

    imageContent_list = input_json_data["pageData"]["args"]["textFieldData"]["imageContent"]

    if len(imageContent_list)>1:
        align = True
    else:
        align = False

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)
    # aud_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]
    ques_src = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][ques_id]
    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]

    HtmlText = text_en_html_to_html_text(html_string=text)

    resp = write_html(
        text=HtmlText,
        exiting_hashcode=exiting_hashcode,
        align=align
    )
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    popup_response = get_popup_mlo_from_text(
        text=text,
        input_other_jsons_data=input_other_jsons_data,
        all_files=all_files,
        exiting_hashcode=exiting_hashcode,
        enable_question_statement=True
    )
    hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode1)
    hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode2)
    hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode3)
    if popup_response:
        all_files = popup_response['all_files']
        exiting_hashcode = popup_response['exiting_hashcode']
        popup = "\n".join(popup_response['all_tags'])

        class_id = "Text with Images"
        if not len(imageContent_list)>1:
            class_id = "Text- Left"
        all_tags.append(
            f"""
            <alef_section xlink:label="{hashcode1}" xp:name="alef_section"
                                      xp:description="{htmlentities.encode(ques_src)}" xp:fieldtype="folder"
                                      customclass="{class_id}">
                <alef_column xlink:label="{hashcode2}" xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_tooltip xlink:label="{hashcode3}" xp:name="alef_tooltip"
                                          xp:description="" xp:fieldtype="folder">
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description=""
                                               xp:fieldtype="html"
                                               src="../../../{resp['relative_path']}"/>
                        {popup}
                    </alef_tooltip>
            """
        )

        src_audio_path = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]
        resp = copy_to_hashcode_dir(
            src_path=src_audio_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode4)

        all_tags.append(
            f"""
                            <alef_audionew xlink:label="{hashcode4}" xp:name="alef_audionew"
                                           xp:description="" xp:fieldtype="folder">
                                <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                                xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                                src="../../../{resp['relative_path']}"/>
                            </alef_audionew>
                        </alef_column>
            """
        )

    else:
        class_id = "Text with Images"
        if not len(imageContent_list)>1:
            class_id = "Text- Left"
        all_tags.append(
            f"""
            <alef_section xlink:label="{hashcode1}" xp:name="alef_section"
                                      xp:description="{htmlentities.encode(ques_src)}" xp:fieldtype="folder"
                                      customclass="{class_id}">
                <alef_column xlink:label="{hashcode2}" xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description=""
                                           xp:fieldtype="html"
                                           src="../../../{resp['relative_path']}"/>
            """
        )


    # image columns
    if len(imageContent_list)>1:
        hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode3)

        all_tags.append(
            f"""
            <alef_section xlink:label="{hashcode3}" xp:name="alef_section"
                                              xp:description="" xp:fieldtype="folder" customclass="Normal">
            """
        )
        for each_img in imageContent_list:
            # print(each_img)
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)

            src_image_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img['image']]
            resp = copy_to_hashcode_dir(
                src_path=src_image_path,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            src_en_text = ""
            if "label" in each_img:
                src_en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_img['label']]

            hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode1)

            all_tags.append(
                f"""
                    <alef_column xlink:label="{hashcode1}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                                        xp:description="" xp:fieldtype="image" alt="{htmlentities.encode(src_en_text)}">
                            <xp:img href="../../../{resp['relative_path']}" width="891"
                                                        height="890"/>
                        </alef_image>
                    </alef_column>
                """
            )

        all_tags.append(
            """
            </alef_section>
            """
        )
    else:
        for each_img in imageContent_list:
            # print(each_img)
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)

            src_image_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img['image']]
            resp = copy_to_hashcode_dir(
                src_path=src_image_path,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            src_en_text = ""
            if "label" in each_img:
                src_en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_img['label']]

            hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode1)

            all_tags.append(
                f"""
                    <alef_column xlink:label="{hashcode1}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                                        xp:description="" xp:fieldtype="image" alt="{htmlentities.encode(src_en_text)}">
                            <xp:img href="../../../{resp['relative_path']}" width="688"
                                                        height="890"/>
                        </alef_image>
                    </alef_column>
                """
            )

    if len(imageContent_list)>1:
        src_audio_path = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]
        resp = copy_to_hashcode_dir(
            src_path=src_audio_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode4)

        all_tags.append(
            f"""
                            <alef_audionew xlink:label="{hashcode4}" xp:name="alef_audionew"
                                           xp:description="" xp:fieldtype="folder">
                                <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                                xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                                src="../../../{resp['relative_path']}"/>
                            </alef_audionew>
                        </alef_column>
                    </alef_section>
            """
        )
    else:
        all_tags.append(
            """</alef_section>"""
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
