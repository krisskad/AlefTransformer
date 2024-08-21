from Transformer.helpers import (generate_unique_folder_name,
                                 text_en_html_to_html_text, get_teacher_note,
                                 get_popup_mlo_from_text, convert_html_to_strong, get_xml_hint,
                                 get_xml_feedback, mathml2latex_yarosh)
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
    STATUS = []
    all_files = set()
    all_tags = [
        """
        <!-- AudiowithInputBox_001 -->

        """
    ]
    # Extracting variables
    # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
    try:
        textFieldData = input_json_data["pageData"]["args"]["textFieldData"]
    except:
        msg = f"Error: AudiowithInputBox_001 --> textFieldData not found in input structure"
        STATUS.append(msg)
        raise Exception(msg)

    mediaBoxData = input_json_data["pageData"]["args"].get("mediaBoxData", None)

    qText = textFieldData.get("qText", None)


    try:
        teachers_note_xml = ""
        teacher_resp = get_teacher_note(
            text=qText, all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            input_other_jsons_data=input_other_jsons_data
        )

        if teacher_resp:
            qText = teacher_resp["remaining_text"]
            teachers_note_xml = teacher_resp["teachers_note_xml"]
            exiting_hashcode.update(teacher_resp["exiting_hashcode"])
            all_files.update(teacher_resp["all_files"])

    except Exception as e:
        teachers_note_xml = ""
        print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

    qHtmlText = ""
    text = ""
    if qText:
        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qText]

            if "<math" in text:
                text = mathml2latex_yarosh(html_string=text)

            qHtmlText = text_en_html_to_html_text(html_string=text)
        except:
            msg = f"Error: AudiowithInputBox_001 --> {qText} not found in en text"
            STATUS.append(msg)
            raise Exception(msg)
    else:
        msg = f"Error: AudiowithInputBox_001 --> qText not found in structure.json"
        STATUS.append(msg)
        raise Exception(msg)
    resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode, align=None)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    temp = []
    for _ in range(25):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    if mediaBoxData:
        customclass = "Input Box"
    else:
        customclass = "Text- Left"

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[12]}" xp:name="alef_section" xp:description=""
                      xp:fieldtype="folder" customclass="{customclass}">
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

    popup_response = get_popup_mlo_from_text(
        text=text,
        input_other_jsons_data=input_other_jsons_data,
        all_files=all_files,
        exiting_hashcode=exiting_hashcode
    )

    if popup_response:
        all_files = popup_response['all_files']
        exiting_hashcode = popup_response['exiting_hashcode']
        all_tags = all_tags + popup_response['all_tags']

    all_tags.append(
        f"""
                        </alef_tooltip>
                        {teachers_note_xml}
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        </alef_notebook>
        """
    )

    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except:
        msg = "Error: AudiowithInputBox_001 --> src not found for audio"
        STATUS.append(msg)
        raise Exception(msg)
    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    all_tags.append(
        f"""
        <alef_audionew xlink:label="{temp[19]}" xp:name="alef_audionew"
                       xp:description="" xp:fieldtype="folder">
            <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                            xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                            src="../../../{resp['relative_path']}"/>
        </alef_audionew>
        """
    )

    all_tags.append(
        "</alef_column>"
    )
    if "mediaBoxData" in input_json_data["pageData"]["args"]:
        try:
            img_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][
                input_json_data["pageData"]["args"]['mediaBoxData']["src"]]
        except:
            msg = "Error: AudiowithInputBox_001 --> src not found within mediaBoxData"
            STATUS.append(msg)
            raise Exception(msg)

        resp = copy_to_hashcode_dir(src_path=img_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[20]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description=""
                            xp:fieldtype="image" alt="" customWidth="600" customAlign="Center">
                    <xp:img href="../../../{resp['relative_path']}" width="891"
                            height="890"/>
                </alef_image>
            </alef_column>
            """
        )
    else:
        try:
            img_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][
                input_json_data["pageData"]["args"]['background']["src"]]
        except:
            msg = "Error: AudiowithInputBox_001 --> background src not found"
            STATUS.append(msg)
            raise Exception(msg)

        resp = copy_to_hashcode_dir(src_path=img_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            
            <alef_column xlink:label="{temp[21]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description=""
                            xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}" width="1920" height="1080"/>
                </alef_image>
            </alef_column>
            """
        )



    try:
        feedback = input_json_data["pageData"]["args"].get("feedback", None)
        # get feedback xml
        feedback_resp = get_xml_feedback(
            feedback=feedback,
            exiting_hashcode=exiting_hashcode,
            all_files=all_files,
            input_other_jsons_data=input_other_jsons_data
        )
        all_tags.append(feedback_resp["XML_STRING"])
        exiting_hashcode.update(feedback_resp["GENERATED_HASH_CODES"])
        all_files.update(feedback_resp["MANIFEST_FILES"])
    except:
        pass

    try:
        hint = input_json_data["pageData"]["args"].get("hint", None)
        # get feedback xml
        hint_resp = get_xml_hint(
            hint=hint,
            exiting_hashcode=exiting_hashcode,
            all_files=all_files,
            input_other_jsons_data=input_other_jsons_data
        )
        all_tags.append(hint_resp["XML_STRING"])
        exiting_hashcode.update(hint_resp["GENERATED_HASH_CODES"])
        all_files.update(hint_resp["MANIFEST_FILES"])
    except:
        pass

    all_tags.append(
        "</alef_section>"
    )
    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files,
        "STATUS":STATUS
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
