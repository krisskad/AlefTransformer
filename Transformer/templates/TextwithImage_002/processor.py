from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong, get_teacher_note,
                                 remove_html_tags, mathml2latex_yarosh, remove_div_wrapper, remove_br_tags)
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

    try:
        view_ref = input_json_data["pageData"]['viewRef']
        view_obj = input_other_jsons_data["INPUT_VIEW_JSON_DATA"]["pages"][view_ref]
    except Exception as e:
        view_obj = {}
        print(f"Warning: view_ref not found please check view.json file : {e}")


    # Assigning values to variables
    # Extracting variables
    try:
        ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
        if "<math" in ques:
            ques = mathml2latex_yarosh(html_string=ques)
        else:
            ques = remove_html_tags(ques)
    except Exception as e:
        ques = ""
        print(f'Warning: TextwithImage_002 --> ques --> {e}')

    try:
        title_t = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    except Exception as e:
        title_t = ""

    text_list = [title_t]

    try:
        text_ids = input_json_data["pageData"]["args"]["textFieldData"]["textContent"]
        for text_id in text_ids:
            text_id_ref = text_id.get("text")
            text_list.append(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id_ref])
    except Exception as e:
        text_list = []
        print(f'Warning: The text content is also not found. The title will be left blank. {e}')

    html_tags_list = []
    teachers_note_xml = ""
    for idx, title in enumerate(text_list):
        try:
            title = remove_div_wrapper(title)
            title = remove_br_tags(title)
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

            try:
                if title_t:
                    if idx > 0:
                        extraTextsViewList = view_obj["pageData"]["args"]["extraTexts"][idx]
                        skip = False
                    else:
                        skip = True
                else:
                    extraTextsViewList = view_obj["pageData"]["args"]["extraTexts"][idx]
                    skip = False

                if not skip:
                    text_top = extraTextsViewList["top"]
                    text_left = extraTextsViewList["left"]
                    text_height = extraTextsViewList["height"]
                    text_width = extraTextsViewList["width"]
                    fontSize = extraTextsViewList["fontSize"]
                    color = extraTextsViewList["color"]

                    title = f"""
                    <span style="position: absolute; top: {text_top}; left: {text_left}; width: {text_width}; height: {text_height}; font-size: {fontSize}; color: {color};">
                        {title}
                    </span>
                    """

            except:
                pass

            text_resp = write_html(text=title, exiting_hashcode=exiting_hashcode, align=False)
            all_files.add(text_resp['relative_path'])
            exiting_hashcode.add(text_resp['hashcode'])

            text_html_tag = f"""
            <alef_html xlink:label="{text_resp['hashcode']}" xp:name="alef_html"
               xp:description="" xp:fieldtype="html"
               src="../../../{text_resp['relative_path']}"/>
            """

            html_tags_list.append(text_html_tag)

        except Exception as e:
            teachers_note_xml = ""
            html_tags_list = []
            print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")


    try:
        images = input_json_data["pageData"]["args"]["textFieldData"]["imageContent"]
    except Exception as e:
        raise Exception(f'Error: TextwithImage_002 --> images not found {e}')

    all_image_tags_list = []
    for idx, each_img in enumerate(images):
        try:
            img_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img['image']]
        except:
            print('Error: TextwithImage_002 --> image not found inside image list')
            continue

        try:
            extraImagesViewList = view_obj["pageData"]["args"]["extraImages"][idx]
            widthImg = int(float(extraImagesViewList["width"].replace("px", "")))
            heightImg = int(float(extraImagesViewList["height"].replace("px", "")))
            alignImg = ""

            # leftImg = int(float(extraImagesViewList["left"].replace("px", "")))
            #
            # alignImg = "Left"
            # if leftImg <= 400:
            #     alignImg = "Left"
            #
            # if 400 < leftImg <= 800:
            #     alignImg = "Center"
            #
            # if leftImg > 800:
            #     alignImg = "Right"

        except Exception as e:
            widthImg = 1644
            heightImg = 487
            alignImg = ""
            print(f"Warning: {e}")

        img_resp = copy_to_hashcode_dir(src_path=img_path, exiting_hashcode=exiting_hashcode)
        all_files.add(img_resp['relative_path'])
        exiting_hashcode.add(img_resp['hashcode'])

        all_image_tags_list.append(
            f"""
            <alef_image xlink:label="{img_resp['hashcode']}" xp:name="alef_image"
                        xp:description="" xp:fieldtype="image" alt="" customAlign="{alignImg}">
                <xp:img href="../../../{img_resp['relative_path']}" width="{widthImg}"
                        height="{heightImg}"/>
            </alef_image>
            """
        )
    all_image_tags = "\n".join(all_image_tags_list)

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)


    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
        resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        audio_tag = f"""
        <alef_audionew xlink:label="{temp[5]}" xp:name="alef_audionew"
                           xp:description="" xp:fieldtype="folder">
            <alef_audiofile xlink:label="{resp['hashcode']}"
                            xp:name="alef_audiofile" xp:description="" audiocontrols="Yes"
                            xp:fieldtype="file"
                            src="../../../{resp['relative_path']}"/>
        </alef_audionew>
        """

    except Exception as e:
        audio_tag = ""
        print(f'Warning: TextwithImage_002 --> src not found {e}')

    text_html_tags = "\n".join(html_tags_list)
    all_tags.append(
        f"""
    <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                              xp:description="{htmlentities.encode(ques)}" xp:fieldtype="folder" customclass="Text- Left">
        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                     xp:fieldtype="folder" width="auto" cellspan="1">
            {text_html_tags}
            {teachers_note_xml}
            {all_image_tags}
            {audio_tag}
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
