from Transformer.helpers import (generate_unique_folder_name, get_teacher_note,
                                 mathml2latex_yarosh, convert_html_to_strong, remove_html_tags)
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
    STATUS = []

    all_tags = [
        """
        <!-- DragAndDrop_001 -->

        """
    ]
    # Extracting variables
    try:
        title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)


    try:
        teachers_note_xml = ""
        teacher_resp = get_teacher_note(
            text=title, all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            input_other_jsons_data=input_other_jsons_data
        )

        if teacher_resp:
            title = teacher_resp["remaining_text"]
            teachers_note_xml = teacher_resp["teachers_note_xml"]
            exiting_hashcode.update(teacher_resp["exiting_hashcode"])
            all_files.update(teacher_resp["all_files"])

    except Exception as e:
        teachers_note_xml = ""
        print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")


    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)
    # visibleElements = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
    #     input_json_data["pageData"]["args"]["visibleElements"]]
    try:
        dropItems = input_json_data["pageData"]["args"]["dropItems"]
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)
    try:
        dragItems = input_json_data["pageData"]["args"]["dragItems"]
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)
    if "<math" in title:
        title = mathml2latex_yarosh(html_string=title)

    resp = write_html(
        text=title,
        exiting_hashcode=exiting_hashcode
    )
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    temp = []
    for _ in range(11):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    if "<math" in title:
        clean_title = mathml2latex_yarosh(html_string=title)
    else:
        clean_title = remove_html_tags(title)

    all_tags.append(
        f"""
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                              xp:description="{htmlentities.encode(clean_title)}"
                              xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_categorization xlink:label="{temp[2]}" xp:name="alef_categorization"
                                             xp:description="" xp:fieldtype="folder"
                                             alef_categorizationtype="Normal" categorization_type="Text with Image"
                                             alef_shownumberofoptions="No" alef_limitanswer="No"
                                             alef_stickyoptions="No" alef_verticaloptions="No" invertoptions="No"
                                             submitattempts="2" validation="No" theme="Standard">
                            <alef_categorizationquestion xlink:label="{temp[3]}"
                                                         xp:name="alef_categorizationquestion" xp:description=""
                                                         xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[4]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{resp['relative_path']}"/>
                                        {teachers_note_xml}
                                    </alef_column>
                                </alef_section_general>
                            </alef_categorizationquestion>
        """
    )

    all_tags.append(
        f"""
        <alef_categories xlink:label="{temp[6]}" xp:name="alef_categories"
                                                 xp:description="" xp:fieldtype="folder">
        """
    )

    for each_cat in dropItems:
        try:
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_cat['title']]
            if "<math" in title:
                title = mathml2latex_yarosh(html_string=title)
            else:
                title = remove_html_tags(title)
        except:
            title = ""
            print('Error: DragAndDrop_001 --> title not found')

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)
        all_tags.append(
            f"""
                                    <alef_category xlink:label="{hashcode}" xp:name="alef_category"
                                               xp:description="{htmlentities.encode(title)}" xp:fieldtype="folder"> 
            """
        )

        for each_option in dragItems:

            if each_option['dropId'] == each_cat['dropId']:
                try:
                    image = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_option['image']]
                except Exception as e:
                    msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
                    STATUS.append(msg)
                    raise Exception(msg)
                resp = copy_to_hashcode_dir(src_path=image, exiting_hashcode=exiting_hashcode)
                all_files.add(resp['relative_path'])
                exiting_hashcode.add(resp['hashcode'])

                try:
                    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_option['text']]
                    if "<math" in text:
                        text = mathml2latex_yarosh(html_string=text)
                    else:
                        text = remove_html_tags(text)
                except:
                    text = ""
                    print('Error: DragAndDrop_001 --> text not found inside dragItems')

                temp2 = []
                for _ in range(10):
                    hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                    exiting_hashcode.add(hashcode_temp2)
                    temp2.append(hashcode_temp2)

                all_tags.append(
                    f"""
                                                <alef_option xlink:label="{temp2[0]}" xp:name="alef_option"
                                                             xp:description="" xp:fieldtype="folder" label="{htmlentities.encode(text)}">
                                                    <alef_optionvalue xlink:label="{temp2[1]}"
                                                                      xp:name="alef_optionvalue" xp:description=""
                                                                      xp:fieldtype="folder">
                                                        <alef_section_general xlink:label="{temp2[3]}"
                                                                              xp:name="alef_section_general" xp:description=""
                                                                              xp:fieldtype="folder">
                                                            <alef_column xlink:label="{temp2[4]}"
                                                                         xp:name="alef_column" xp:description=""
                                                                         xp:fieldtype="folder" width="auto">
                                                                <alef_image xlink:label="{resp['hashcode']}"
                                                                            xp:name="alef_image" xp:description=""
                                                                            xp:fieldtype="image" alt="">
                                                                    <xp:img href="../../../{resp['relative_path']}"
                                                                            width="301" height="155"/>
                                                                </alef_image>
                                                            </alef_column>
                                                        </alef_section_general>
                                                    </alef_optionvalue>
                                                </alef_option>
                    """
                )
        all_tags.append("</alef_category>")

    all_tags.append(
        """
        </alef_categories>
        """
    )

    from Transformer.helpers import get_xml_feedback, get_xml_hint
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
        exiting_hashcode.add(feedback_resp["GENERATED_HASH_CODES"])
        all_files.add(feedback_resp["MANIFEST_FILES"])
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
        exiting_hashcode.add(hint_resp["GENERATED_HASH_CODES"])
        all_files.add(hint_resp["MANIFEST_FILES"])
    except:
        pass

    all_tags.append("</alef_categorization>")

    try:
        resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_audionew xlink:label="{temp[8]}" xp:name="alef_audionew"
                           xp:description="" xp:fieldtype="folder">
                <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                src="../../../{resp['relative_path']}"/>
            </alef_audionew>
            """
        )
    except Exception as e:
        print(f"Warning: No Audio found {e}")


    all_tags.append(
        """
                </alef_column>
            </alef_section>
        """
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
