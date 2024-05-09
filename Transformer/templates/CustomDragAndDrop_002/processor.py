from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong, get_teacher_note,
                                 write_html_mlo, mathml2latex_yarosh, get_xml_feedback, get_xml_hint)
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
        <!-- CustomDragAndDrop_001 -->

        """
    ]

    # Extracting variables
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    submitCount = input_json_data["pageData"]["args"].get("submitCount", 2)
    shuffle = input_json_data["pageData"]["args"]["shuffle"]
    dragItems = input_json_data["pageData"]["args"]["dragItems"]
    dropItems = input_json_data["pageData"]["args"]["dropItems"]

    temp = []
    for _ in range(5):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_draganddrop xlink:label="{temp[2]}" xp:name="alef_draganddrop" xp:description="" xp:fieldtype="folder" submitattempts="{submitCount}" validation="Yes" autowidth="false" optionwidth="No" invertoptions="No" stickyoptions="No">
                    <alef_draganddropitem xlink:label="{temp[3]}" xp:name="alef_draganddropitem" xp:description="" xp:fieldtype="folder">
        """
    )

    try:
        try:
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
                input_json_data["pageData"]["args"]["title"]['text']]
        except Exception as e:
            print(f"title text not found --> Now taking extra text as title")

            try:
                extra_text_list = input_json_data["pageData"]["args"]["extraTexts"]
                if len(extra_text_list) == 1:
                    text_id = extra_text_list[0]["text"]
                    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
                else:
                    extra_text_list = input_json_data["pageData"]["args"]["extraTexts"]
                    all_text = []
                    for i in extra_text_list:
                        text_id = i["text"]
                        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
                        all_text.append(text)
                    title = " ".join(all_text)
            except Exception as e:
                print(f"Error: text not found --> {e}")

        temp2 = []
        for _ in range(5):
            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp2)
            temp2.append(hashcode_temp2)

        resp = write_html(text=title, exiting_hashcode=exiting_hashcode, align=None)
        exiting_hashcode.add(resp['hashcode'])
        all_files.add(resp['relative_path'])
        all_tags.append(
            f"""
            <alef_questionstatement xlink:label="{temp2[0]}" xp:name="alef_questionstatement" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp2[1]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="{temp2[2]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}"/>
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
            """
        )
    except Exception as e:
        print(f"Warning: CustomDragAndDrop_001 --> question statement not found {e}")



    try:
        map_link = dict()
        options = []
        map_link_list = []
        for index, each_option in enumerate(dragItems):
            dropId = each_option.get("dropId")
            dropId = int(dropId)+1

            temp4 = []
            for _ in range(5):
                hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp2)
                temp4.append(hashcode_temp2)

            text_id = each_option.get("text", None)
            image_id = each_option.get("image", None)

            tag = ""
            if text_id:
                en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
                resp = write_html(
                    text=en_text,
                    exiting_hashcode=exiting_hashcode
                )
                exiting_hashcode.add(resp['hashcode'])
                all_files.add(resp['relative_path'])
                tag = f"""
                 <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}"/>
                """

            if image_id:
                image_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][image_id]
                resp = copy_to_hashcode_dir(
                    src_path=image_src,
                    exiting_hashcode=exiting_hashcode
                )
                exiting_hashcode.add(resp['hashcode'])
                all_files.add(resp['relative_path'])
                tag = f"""
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}" width="500" height="281"/>
                </alef_image>
                """

            map_link[dropId] = temp4[0]
            # print(index)
            view_ref = input_json_data["pageData"]['viewRef']
            view_obj = input_other_jsons_data["INPUT_VIEW_JSON_DATA"]["pages"][view_ref]
            dropItem_list = view_obj["pageData"]["args"]["dropItems"][index]

            top_pos = dropItem_list['top'].replace("px", "")
            left_pos = dropItem_list['left'].replace("px", "")

            minus = 50
            top_pos = top_pos - minus

            map_link_list.append(
                f"""
                 <maplink xlink:name="New Link" name="New Link" type="internal" targetid="{temp4[0]}" ShowMode="" left="{left_pos}" top="{top_pos}"/>
                """
            )
            options.append(
                f"""
                <alef_option xlink:label="{temp4[0]}" xp:name="alef_option" xp:description="{dropId}" xp:fieldtype="folder">
                    <alef_optionvalue xlink:label="{temp4[1]}" xp:name="alef_optionvalue" xp:description="" xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp4[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="{temp4[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                {tag}
                            </alef_column>
                        </alef_section_general>
                    </alef_optionvalue>
                </alef_option>
                """
            )

    except Exception as e:
        map_link_list = []
        options = []
        print(f"Error while creating options: {e}")

    screen_number = input_json_data['screen_number']
    image_name = f"{input_other_jsons_data['COURSE_ID']}_{str(screen_number)}.png"

    image_path = os.path.join('A1_CustomDND', image_name)
    # if os.path.isfile(image_path):
    #     print("Valid File")
    # else:
    #     image_path = os.path.join('B1_CustomDND', image_name)

    # print(image_path)
    try:

        map_link_join = "\n".join(map_link_list)

        resp = copy_to_hashcode_dir(src_path=image_path, exiting_hashcode=exiting_hashcode)
        exiting_hashcode.add(resp['hashcode'])
        all_files.add(resp['relative_path'])
        all_tags.append(
            f"""
            <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                <xp:img href="../../../{resp['relative_path']}" width="1466" height="600">
                    {map_link_join}
                </xp:img>
            </alef_image>
            """
        )
    except Exception as e:
        print(f"Warning: {e}")

    options_join = "\n".join(options)
    all_tags.append(
        options_join
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

    all_tags.append(
        """
                    </alef_draganddropitem>
                </alef_draganddrop>
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
