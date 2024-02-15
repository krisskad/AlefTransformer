from Transformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh, remove_html_tags, convert_html_to_strong)
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
    all_tags = []

    all_tags = [
        """
        <!-- DragAndDrop_003 -->

        """
    ]

    # Extracting variables
    try:
        title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    except:
        raise Exception('Error: DragAndDrop_003 --> title not found')

    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except:
        raise Exception('Error: DragAndDrop_003 --> src not found')

    # submit = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["submit"]]
    try:
        submitCount = input_json_data["pageData"]["args"]["submitCount"]
    except:
        submitCount = 3
        print('Error: DragAndDrop_003 --> submitCount not found')

    # showAnswer = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["showAnswer"]]
    try:
        feedback = input_json_data["pageData"]["args"]["feedback"]
    except:
        raise Exception('Error: DragAndDrop_003 --> feedback not found')

    # feedBackAudio = input_json_data["pageData"]["args"]["feedBackAudio"]
    try:
        hint = input_json_data["pageData"]["args"]["hint"]
    except:
        raise Exception('Error: DragAndDrop_003 --> hint not found')

    # visibleElements = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
    #     input_json_data["pageData"]["args"]["visibleElements"]]
    try:
        dropItems = input_json_data["pageData"]["args"]["dropItems"]
    except:
        raise Exception('Error: DragAndDrop_003 --> dropItems not found')

    try:
        dragItems = input_json_data["pageData"]["args"]["dragItems"]
    except:
        raise Exception('Error: DragAndDrop_003 --> dragItems not found')

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
                                             submitattempts="{submitCount}" validation="Yes" theme="Standard">
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
        hashcode_temp1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp1)
        try:
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_cat['title']]
            title = remove_html_tags(title)
        except:
            title = ""
            print('Error: DragAndDrop_003 --> title not found in dropItems')

        if "<math" in title:
            title = mathml2latex_yarosh(html_string=title)

        all_tags.append(
            f"""
                                    <alef_category xlink:label="{hashcode_temp1}" xp:name="alef_category"
                                               xp:description="{htmlentities.encode(title)}" xp:fieldtype="folder"> 
            """
        )

        for each_option in dragItems:

            temp1 = []
            for _ in range(11):
                hashcode_temp1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp1)
                temp1.append(hashcode_temp1)
            try:
                image = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_option['image']]
            except:
                raise Exception('Error: DragAndDrop_003 --> image not found in dragItems')

            resp = copy_to_hashcode_dir(src_path=image, exiting_hashcode=exiting_hashcode)
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            try:
                text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_option['text']]
                text = remove_html_tags(text)
            except:
                text = ""
                print('Error: DragAndDrop_003 --> text not found in dragItems')

            if "<math" in text:
                text = mathml2latex_yarosh(html_string=text)

            if each_option['dropId'] == each_cat['dropId']:
                all_tags.append(
                    f"""
                                                <alef_option xlink:label="{temp1[0]}" xp:name="alef_option"
                                                             xp:description="" xp:fieldtype="folder" label="{htmlentities.encode(text)}">
                                                    <alef_optionvalue xlink:label="{temp1[1]}"
                                                                      xp:name="alef_optionvalue" xp:description=""
                                                                      xp:fieldtype="folder">
                                                        <alef_section_general xlink:label="{temp1[2]}"
                                                                              xp:name="alef_section_general" xp:description=""
                                                                              xp:fieldtype="folder">
                                                            <alef_column xlink:label="{temp1[3]}"
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

    # add all hint, feedback, etc
    count = 1
    for key, val in feedback.items():
        if count > 2:
            break
        base_key = key.split("_")[0]
        try:
            text_val = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
        except:
            print('warning: DragAndDrop_003 --> text missing in feedback')
            continue

        if "<math" in text_val:
            text_val = mathml2latex_yarosh(html_string=text_val)

        resp = write_html(
            text=text_val,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        temp2 = []
        for _ in range(4):
            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp2)
            temp2.append(hashcode_temp2)

        all_tags.append(
            f"""
                            <alef_{base_key}feedback xlink:label="{temp2[0]}"
                                                  xp:name="alef_{base_key}feedback" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp2[1]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp2[2]}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{resp['relative_path']}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_{base_key}feedback>
            
            """
        )
        count = count + 1

    # add all hint, feedback, etc
    for key, val in hint.items():
        try:
            text_val = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
        except:
            print('warning: DragAndDrop_003 --> text missing in hint')
            continue

        if "<math" in text_val:
            text_val = mathml2latex_yarosh(html_string=text_val)

        resp = write_html(
            text=text_val,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        temp3 = []
        for _ in range(4):
            hashcode_temp3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp3)
            temp3.append(hashcode_temp3)

        all_tags.append(
            f"""
                            <alef_hint xlink:label="{temp3[0]}" xp:name="alef_hint"
                                       xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp3[1]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp3[2]}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{resp['relative_path']}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_hint>

            """
        )

    all_tags.append("</alef_categorization>")

    try:
        resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        hashcode_temp4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp4)
        all_tags.append(
            f"""
                            <alef_audionew xlink:label="{hashcode_temp4}" xp:name="alef_audionew"
                                           xp:description="" xp:fieldtype="folder">
                                <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                                xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                                src="../../../{resp['relative_path']}"/>
                            </alef_audionew>
            """
        )
    except:
        print('warning: DragAndDrop_003 --> audio missing')

    all_tags.append(
        """
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
        xml_output = {
            "XML_STRING": "",
            "GENERATED_HASH_CODES": set(),
            "MANIFEST_FILES": set(),
            "STATUS": [f"Error : {e}", ]
        }
    return xml_output
