from Transformer.helpers import generate_unique_folder_name
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode):

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
        <!-- InputBox_001 -->

        """
    ]

    # Extracting variables
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    extraTexts = input_json_data["pageData"]["args"]["extraTexts"]

    all_tags.append(
        f"""
            <alef_section xlink:label="LF2FLE6WGMPNERKHN4SZDNMAWUI" xp:name="alef_section"
                          xp:description="{extraTexts[0].get('text')}" xp:fieldtype="folder" customclass="Normal">
                <alef_column xlink:label="LHEZOCGPV3DEUDEBZYZZ4YETQWM" xp:name="alef_column" xp:description=""
                             xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_predefined_graphorganizer xlink:label="LK7B4YVMKPMUEDBWLO7QKEBUMJI"
                                                    xp:name="alef_predefined_graphorganizer" xp:description=""
                                                    xp:fieldtype="folder" type="{extraTexts[0].get('text')}">
        """
    )

    for each_obj in extraTexts[1:]:
        resp = write_html(text=each_obj['text'], exiting_hashcode=exiting_hashcode)
        exiting_hashcode.add(resp['hashcode'])
        all_files.add(resp['relative_path'])

        all_tags.append(
            f"""
            <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
               xp:description="" xp:fieldtype="html"
               src="../../../{resp['relative_path']}"/>
            """
        )

    all_tags.append(
        """
                </alef_predefined_graphorganizer>
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
