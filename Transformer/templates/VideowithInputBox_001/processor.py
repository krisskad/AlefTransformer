from Transformer.helpers import (generate_unique_folder_name,
                                 text_en_html_to_html_text,get_teacher_note,
                                 get_popup_mlo_from_text, convert_html_to_strong)
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode, align=None):
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
        <!-- VideowithInputBox_001 -->

        """
    ]

    # Extracting variables
    # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
    try:
        src = input_other_jsons_data['INPUT_VIDEO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except:
        raise Exception("Error: VideowithInputBox_001 --> src audio not found")

    try:
        textFieldData = input_json_data["pageData"]["args"]["textFieldData"]
    except:
        raise Exception("Error: VideowithInputBox_001 --> textFieldData not found")

    try:
        from Transformer.helpers import calculate_video_duration
        asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src)
        seconds = calculate_video_duration(asset_abs_path)
        # print(asset_abs_path)
        seconds = seconds - 1
        seconds = f"00:00:{seconds}"
    except Exception as e:
        print("Error: ", e)
        seconds = "00:00:20"

    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    temp = []
    for _ in range(14):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
            <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                          xp:fieldtype="folder" customclass="Normal">
                <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                             xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_advancedvideo xlink:label="{temp[2]}" xp:name="alef_advancedvideo"
                                        xp:description="" xp:fieldtype="folder">
                        <alef_video xlink:label="{resp['hashcode']}" xp:name="alef_video"
                                    xp:description="" xp:fieldtype="movie">
                            <xp:mov xp:fieldtype="movie" alt="" xlink:label="{resp['hashcode']}"
                                    href="../../../{resp['relative_path']}" xp:description=""
                                    xp:name="alef_video"/>
                        </alef_video>
        """
    )

    qText = textFieldData.get("qText", None)
    qHtmlText = ""
    text = ""
    if qText:
        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qText]
        except:
            raise Exception("Error: VideowithInputBox_001 --> qText not found")


        try:
            teachers_note_xml = ""
            teacher_resp = get_teacher_note(
                text=text, all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                input_other_jsons_data=input_other_jsons_data
            )

            if teacher_resp:
                text = teacher_resp["remaining_text"]
                teachers_note_xml = teacher_resp["teachers_note_xml"]
                exiting_hashcode.update(teacher_resp["exiting_hashcode"])
                all_files.update(teacher_resp["all_files"])

        except Exception as e:
            teachers_note_xml = ""
            print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

        qHtmlText = text_en_html_to_html_text(html_string=text)
    else:
        teachers_note_xml = ""

    resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    popup_response = get_popup_mlo_from_text(
        text=text,
        input_other_jsons_data=input_other_jsons_data,
        all_files=all_files,
        exiting_hashcode=exiting_hashcode,
        enable_question_statement=False
    )

    if popup_response:
        all_files = popup_response['all_files']
        exiting_hashcode = popup_response['exiting_hashcode']
        popup = "\n".join(popup_response['all_tags'])
        all_tags.append(popup)

        all_tags.append(
            f"""
                        <alef_interactivesection xlink:label="{temp[3]}"
                                                 xp:name="alef_interactivesection" xp:description=""
                                                 xp:fieldtype="folder" alef_appearingtime="{seconds}">
                            <alef_section xlink:label="{temp[4]}" xp:name="alef_section"
                                          xp:description="" xp:fieldtype="folder" customclass="Normal">
                                <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                             xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                                    <alef_notebook xlink:label="{temp[6]}"
                                                   xp:name="alef_notebook" xp:description=""
                                                   xp:fieldtype="folder">
                                        <alef_questionstatement xlink:label="{temp[7]}"
                                                                xp:name="alef_questionstatement"
                                                                xp:description="" xp:fieldtype="folder">
                                            <alef_section_general xlink:label="{temp[8]}"
                                                                  xp:name="alef_section_general"
                                                                  xp:description="" xp:fieldtype="folder">
                                                <alef_column xlink:label="{temp[9]}"
                                                             xp:name="alef_column" xp:description=""
                                                             xp:fieldtype="folder" width="auto">
                                                    <alef_tooltip xlink:label="{temp[10]}"
                                                                  xp:name="alef_tooltip" xp:description=""
                                                                  xp:fieldtype="folder">
                                                        <alef_html xlink:label="{resp['hashcode']}"
                                                                   xp:name="alef_html" xp:description=""
                                                                   xp:fieldtype="html"
                                                                   src="../../../{resp['relative_path']}"/>
                                                        {popup}
                                                    </alef_tooltip>
                                                    {teachers_note_xml}
                                                </alef_column>
                                            </alef_section_general>
                                        </alef_questionstatement>
                                    </alef_notebook>
                                </alef_column>
                            </alef_section>
                        </alef_interactivesection>
                    </alef_advancedvideo>
                </alef_column>
            </alef_section>
            """
        )
    else:
        all_tags.append(
            f"""
                                <alef_interactivesection xlink:label="{temp[3]}"
                                                         xp:name="alef_interactivesection" xp:description=""
                                                         xp:fieldtype="folder" alef_appearingtime="{seconds}">
                                    <alef_section xlink:label="{temp[4]}" xp:name="alef_section"
                                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
                                        <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                                            <alef_notebook xlink:label="{temp[6]}"
                                                           xp:name="alef_notebook" xp:description=""
                                                           xp:fieldtype="folder">
                                                <alef_questionstatement xlink:label="{temp[7]}"
                                                                        xp:name="alef_questionstatement"
                                                                        xp:description="" xp:fieldtype="folder">
                                                    <alef_section_general xlink:label="{temp[8]}"
                                                                          xp:name="alef_section_general"
                                                                          xp:description="" xp:fieldtype="folder">
                                                        <alef_column xlink:label="{temp[9]}"
                                                                     xp:name="alef_column" xp:description=""
                                                                     xp:fieldtype="folder" width="auto">
                                                            <alef_html xlink:label="{resp['hashcode']}"
                                                                       xp:name="alef_html" xp:description=""
                                                                       xp:fieldtype="html"
                                                                       src="../../../{resp['relative_path']}"/>
                                                            {teachers_note_xml}
                                                        </alef_column>
                                                    </alef_section_general>
                                                </alef_questionstatement>
                                            </alef_notebook>
                                        </alef_column>
                                    </alef_section>
                                </alef_interactivesection>
                            </alef_advancedvideo>
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
    try:
        xml_output = create_mlo(
            input_json_data=page_data,
            input_other_jsons_data=other_json_data,
            exiting_hashcode=exiting_hashcode
        )
    except Exception as e:
        raise Exception(f"Error: {e} --> {page_data}")
    return xml_output
