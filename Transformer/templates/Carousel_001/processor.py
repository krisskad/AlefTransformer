from Transformer.helpers import generate_unique_folder_name, mathml2latex_yarosh, text_en_html_to_html_text, get_popup_mlo_from_text
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

    # Extracting variables
    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    # src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    description = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["description"]]

    slides = input_json_data["pageData"]["args"]["slides"]

    if "<math" in title:
        title = mathml2latex_yarosh(html_string=title)

    if "<math" in description:
        description = mathml2latex_yarosh(html_string=description)

    HtmlText = text_en_html_to_html_text(html_string=description)

    content = f"<strong>{title}</strong><br><br>{HtmlText}"
    resp = write_html(
        text=content,
        exiting_hashcode=exiting_hashcode,
        align='center'
    )
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    popup_response = get_popup_mlo_from_text(
        text=description,
        input_other_jsons_data=input_other_jsons_data,
        all_files=all_files,
        exiting_hashcode=exiting_hashcode,
        enable_question_statement=True
    )

    temp = []
    for _ in range(11):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    if popup_response:
        all_files = popup_response['all_files']
        exiting_hashcode = popup_response['exiting_hashcode']
        popup = "\n".join(popup_response['all_tags'])

        all_tags.append(
            f"""
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                                  xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_tooltip xlink:label="{temp[2]}" xp:name="alef_tooltip"
                                          xp:description="" xp:fieldtype="folder">
                                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{resp['relative_path']}"/>
                                {popup}
                            </alef_tooltip>
            """
        )
    else:
        all_tags.append(
            f"""
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                                  xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp['relative_path']}"/>
            """
        )

    all_tags.append(
        f"""
        <alef_presentation xlink:label="{temp[3]}" xp:name="alef_presentation"
                               xp:description="" xp:fieldtype="folder" type="Image Carousel"
                               showtitle="false" multipleopen="false" firstopen="false">
        """
    )

    for slide in slides:
        image_id = slide.get("image")
        text_id = slide.get("text")

        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
        image_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][image_id]

        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)

        resp = copy_to_hashcode_dir(
            src_path=image_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        temp2 = []
        for _ in range(2):
            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp2)
            temp2.append(hashcode_temp2)

        all_tags.append(
            f"""
                <alef_section xlink:label="{temp2[0]}" xp:name="alef_section"
                              xp:description="" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp2[1]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                    xp:description="{htmlentities.encode(text)}"
                                    xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp['relative_path']}"
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

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    return xml_output
