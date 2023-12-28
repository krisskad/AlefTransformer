from Transformer.helpers import generate_unique_folder_name
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, destination_file_path):
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

    with open(destination_file_path, "w") as file:
        file.write(template.strip())


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = []

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    # Assigning values to variables
    aud_id = input_json_data["pageData"]["args"]["src"]
    ques_id = input_json_data["pageData"]["args"]["ques"]
    text_id = input_json_data["pageData"]["args"]["textFieldData"]["textContent"]["text"]
    imageContent_list = input_json_data["pageData"]["args"]["textFieldData"]["imageContent"]

    aud_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]
    ques_src = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][ques_id]
    text_src = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
    write_html(destination_file_path=path_to_html, text=text_src)

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_path)

    hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode1)
    hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode2)

    all_tags.append(
        f"""
        <alef_section xlink:label="{hashcode1}" xp:name="alef_section"
                                  xp:description="{htmlentities.encode(ques_src)}" xp:fieldtype="folder"
                                  customclass="Text with Images">
            <alef_column xlink:label="{hashcode2}" xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_html xlink:label="{hashcode}" xp:name="alef_html" xp:description=""
                                       xp:fieldtype="html"
                                       src="../../../{relative_path}"/>
        """
    )

    hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode3)

    all_tags.append(
        f"""
        <alef_section xlink:label="{hashcode3}" xp:name="alef_section"
                                          xp:description="" xp:fieldtype="folder" customclass="Normal">
        """
    )

    # image columns
    for each_img in imageContent_list:
        # print(each_img)
        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        src_image_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img['image']]
        src_en_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_img['label']]

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        src_image_abs_path = os.path.join(settings.INPUT_APP_DIR, src_image_path)
        destination_image_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_image_path)))
        shutil.copy2(str(src_image_abs_path), str(destination_image_path))

        relative_path = os.path.join(hashcode, str(os.path.basename(src_image_path)))
        all_files.add(relative_path)

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)

        all_tags.append(
            f"""
                <alef_column xlink:label="{hashcode1}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_image xlink:label="{hashcode}" xp:name="alef_image"
                                                    xp:description="" xp:fieldtype="image" alt="{htmlentities.encode(src_en_text)}">
                        <xp:img href="../../../{relative_path}" width="688"
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

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    src_audio_path = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    src_audio_abs_path = os.path.join(settings.INPUT_APP_DIR, src_audio_path)
    destination_audio_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_audio_path)))
    shutil.copy2(str(src_audio_abs_path), str(destination_audio_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_audio_path)))
    all_files.add(relative_path)

    hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode4)

    all_tags.append(
        f"""
                        <alef_audionew xlink:label="{hashcode4}" xp:name="alef_audionew"
                                       xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{hashcode}" xp:name="alef_audiofile"
                                            xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                            src="../../../{relative_path}"/>
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

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    return xml_output
