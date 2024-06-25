from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong, get_teacher_note,
                                 remove_html_tags, mathml2latex_yarosh)
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

    asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)
    destination_src_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_path)))
    shutil.copy2(str(asset_abs_path), str(destination_src_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_path)))

    response = {
        "relative_path":relative_path,
        "hashcode": hashcode,
    }

    return response


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = [
        """
        <!-- TextwithImage_002 -->

        """
    ]
    # Assigning values to variables
    # Extracting variables
    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except:
        raise Exception('Error: TextwithImage_002 --> src not found')

    try:
        ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
        if "<math" in ques:
            ques = mathml2latex_yarosh(html_string=ques)
        else:
            ques = remove_html_tags(ques)

    except:
        ques = ""
        print('Error: TextwithImage_002 --> ques not found')

    try:
        title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    except Exception as e:
        print(f'Error: Unable to find the title in title field of structure.json. Trying to find the title in textContent in structure.json... {e}')
        try:
            text_ids = input_json_data["pageData"]["args"]["textFieldData"]["textContent"]
            text_list = []
            for text_id in text_ids:
                text_id_ref = text_id.get("text")
                text_list.append(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id_ref])
            # print(text_list)
            title = "<br>".join(text_list)
        except Exception as e:
            title = ""
            print(f'Warning: The text content is also not found. The title will be left blank. {e}')

    try:

        if "<math" in title:
            title = mathml2latex_yarosh(html_string=title)

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
        images = input_json_data["pageData"]["args"]["textFieldData"]["imageContent"]
    except:
        raise Exception('Error: TextwithImage_002 --> images not found')

    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    text_resp = write_html(text=title, exiting_hashcode=exiting_hashcode, align=True)
    all_files.add(text_resp['relative_path'])
    exiting_hashcode.add(text_resp['hashcode'])

    all_image_tags_list = []
    for each_img in images:
        try:
            img_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img['image']]
        except:
            print('Error: TextwithImage_002 --> image not found inside image list')
            continue
        img_resp = copy_to_hashcode_dir(src_path=img_path, exiting_hashcode=exiting_hashcode)
        all_files.add(img_resp['relative_path'])
        exiting_hashcode.add(img_resp['hashcode'])

        all_image_tags_list.append(
            f"""
            <alef_image xlink:label="{img_resp['hashcode']}" xp:name="alef_image"
                        xp:description="" xp:fieldtype="image" alt="" customAlign="Center">
                <xp:img href="../../../{img_resp['relative_path']}" width="1644"
                        height="487"/>
            </alef_image>
            """
        )
    all_image_tags = "\n".join(all_image_tags_list)

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
    <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                              xp:description="{htmlentities.encode(ques)}" xp:fieldtype="folder" customclass="Text- Left">
        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                     xp:fieldtype="folder" width="auto" cellspan="1">
            <alef_html xlink:label="{text_resp['hashcode']}" xp:name="alef_html"
                       xp:description="" xp:fieldtype="html"
                       src="../../../{text_resp['relative_path']}"/>
            {teachers_note_xml}
            {all_image_tags}
            <alef_audionew xlink:label="{temp[5]}" xp:name="alef_audionew"
                           xp:description="" xp:fieldtype="folder">
                <alef_audiofile xlink:label="{resp['hashcode']}"
                                xp:name="alef_audiofile" xp:description="" audiocontrols="Yes"
                                xp:fieldtype="file"
                                src="../../../{resp['relative_path']}"/>
            </alef_audionew>
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
        raise Exception(f"Error: {e}")
    return xml_output
