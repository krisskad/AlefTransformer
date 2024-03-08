from Transformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh,
                                 text_en_html_to_html_text,
                                 get_popup_mlo_from_text,
                                 convert_html_to_strong,
                                 remove_html_tags
                                 )
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
        <!-- Carousel_002 -->

        """
    ]

    # Extracting variables
    # title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    # src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    # description = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["description"]]

    try:
        slides = input_json_data["pageData"]["args"]["slides"]
    except:
        raise Exception('Error: Carousel_002 --> slides not found')

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                                  xp:fieldtype="folder" customclass="Normal">
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_presentation xlink:label="{temp[2]}" xp:name="alef_presentation"
                                   xp:description="" xp:fieldtype="folder" type="Image Carousel"
                                   showtitle="false" multipleopen="false" firstopen="false">
        """
    )

    for slide in slides:
        image_id = slide.get("image")
        text_id = slide.get("text")
        title_id = slide.get("title")
        description = slide.get("description")
        audio_id = slide.get("audio")

        try:
            audio = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio_id]
        except:
            raise Exception('Error: Carousel_002 --> audio not found inside slide')

        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
            text = remove_html_tags(text)

        except:
            text = ""
            print('Warning: Carousel_002 --> text not found inside slide')

            # raise Exception('Error: Carousel_002 --> text not found inside slide')

        try:
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title_id]
            title = remove_html_tags(title)
        except:
            # raise Exception('Error: Carousel_002 --> title not found inside slide')
            print('Warning: Carousel_002 --> title not found inside slide')
            title = ""

        try:
            description = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][description]
        except:
            raise Exception('Error: Carousel_002 --> description not found inside slide')

        try:
            image_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][image_id]
        except:
            raise Exception('Error: Carousel_002 --> image not found inside slide')

        if "<math" in title:
            title = mathml2latex_yarosh(html_string=title)

        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)

        if "<math" in description:
            description = mathml2latex_yarosh(html_string=description)

        HtmlText = text_en_html_to_html_text(html_string=description)

        resp_desc = write_html(
            text=HtmlText,
            exiting_hashcode=exiting_hashcode,
            align='center'
        )
        all_files.add(resp_desc['relative_path'])
        exiting_hashcode.add(resp_desc['hashcode'])
        # if "stain" in description:
        #     print(description)

        popup_response = get_popup_mlo_from_text(
            text=description,
            input_other_jsons_data=input_other_jsons_data,
            all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            enable_question_statement=False
        )

        resp_image = copy_to_hashcode_dir(
            src_path=image_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp_image['relative_path'])
        exiting_hashcode.add(resp_image['hashcode'])

        resp_audio = copy_to_hashcode_dir(
            src_path=audio,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp_audio['relative_path'])
        exiting_hashcode.add(resp_audio['hashcode'])

        temp2 = []
        for _ in range(10):
            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp2)
            temp2.append(hashcode_temp2)

        if popup_response:
            all_files = popup_response['all_files']
            exiting_hashcode = popup_response['exiting_hashcode']
            popup = "\n".join(popup_response['all_tags'])

            all_tags.append(
                f"""
                <alef_section xlink:label="{temp2[2]}" xp:name="alef_section"
                                                  xp:description="{htmlentities.encode(title)}" xp:fieldtype="folder"
                                                  customclass="Normal">
                    <alef_column xlink:label="{temp2[0]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_audionew xlink:label="{temp2[1]}" xp:name="alef_audionew"
                                       xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{resp_audio['hashcode']}"
                                            xp:name="alef_audiofile" xp:description=""
                                            audiocontrols="No" xp:fieldtype="file"
                                            src="../../../{resp_audio['relative_path']}"/>
                        </alef_audionew>
                        <alef_tooltip xlink:label="{temp2[3]}" xp:name="alef_tooltip"
                                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_desc['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                        <alef_image xlink:label="{resp_image['hashcode']}" xp:name="alef_image"
                                    xp:description="{htmlentities.encode(text)}"
                                    xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp_image['relative_path']}"
                                    width="1575" height="890"/>
                        </alef_image>
                    </alef_column>
                </alef_section>
                """
            )
        else:
            all_tags.append(
                f"""
                <alef_section xlink:label="{temp2[2]}" xp:name="alef_section"
                                                  xp:description="{htmlentities.encode(title)}" xp:fieldtype="folder"
                                                  customclass="Normal">
                    <alef_column xlink:label="{temp2[0]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_audionew xlink:label="{temp2[1]}" xp:name="alef_audionew"
                                       xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{resp_audio['hashcode']}"
                                            xp:name="alef_audiofile" xp:description=""
                                            audiocontrols="No" xp:fieldtype="file"
                                            src="../../../{resp_audio['relative_path']}"/>
                        </alef_audionew>
                        <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                   xp:description="" xp:fieldtype="html"
                                   src="../../../{resp_desc['relative_path']}"/>
                        <alef_image xlink:label="{resp_image['hashcode']}" xp:name="alef_image"
                                    xp:description="{htmlentities.encode(text)}"
                                    xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp_image['relative_path']}"
                                    width="1575" height="890"/>
                        </alef_image>
                    </alef_column>
                </alef_section>
                """
            )

    all_tags.append(
        """
                </alef_presentation>
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
