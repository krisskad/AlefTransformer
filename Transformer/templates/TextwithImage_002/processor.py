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
    all_tags = []

    # Assigning values to variables
    # Extracting variables
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    images = input_json_data["pageData"]["args"]["textFieldData"]["imageContent"]

    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])


    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
    write_html(text=title, destination_file_path=path_to_html)

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")

    all_image_tags_list = []
    for each_img in images:
        img_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_img]
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

    all_tags.append(
        f"""
    <alef_section xlink:label="L3K4XYFNVTJTUBO4TEQK2KXHRSQ" xp:name="alef_section"
                              xp:description="{htmlentities.encode(ques)}" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="LCZLORRV75HOUTHTWT37A5I6JUQ" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_section xlink:label="LDT2SP3TM33IUPNCF7WAOHOPUI4" xp:name="alef_section"
                                      xp:description="" xp:fieldtype="folder" customclass="Normal">
                            <alef_column xlink:label="LRL766D37GBFUDKE4GWXV7D6PKI" xp:name="alef_column"
                                         xp:description="" xp:fieldtype="folder" width="12" cellspan="1">
                                <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{relative_path}"/>
                                {all_image_tags}
                                <alef_audionew xlink:label="LYFPVNQZMPTKEPOB2OVPZ5YZSSU" xp:name="alef_audionew"
                                               xp:description="" xp:fieldtype="folder">
                                    <alef_audiofile xlink:label="{resp['hashcode']}"
                                                    xp:name="alef_audiofile" xp:description="" audiocontrols="Yes"
                                                    xp:fieldtype="file"
                                                    src="../../../{resp['relative_path']}"/>
                                </alef_audionew>
                            </alef_column>
                        </alef_section>
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
