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

    aud_id = input_json_data['pageData']['args']['src']
    text_id = input_json_data['pageData']['args']['ques']
    textContent = input_json_data['pageData']['args']['ques']['textFieldData']['textContent']['text']

    aud_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]
    text_src = input_other_jsons_data['INPUT_TEXT_EN_JSON_DATA'][text_id]

    all_tags.append(
        f"""
        <alef_section xlink:label="L4L6DE7DWZG4EVNZKI5UL6TQ5EA" xp:name="alef_section"
                                  xp:description="{htmlentities.encode(text_src)}" xp:fieldtype="folder"
                                  customclass="Text with Images">
						<alef_column xlink:label="L3CN72MEF57OUHIZ5H3DFL3C4LY" xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
							<alef_html xlink:label="LHDY5O2SJIWPUZEUAOWGXRH4I2M" xp:name="alef_html" xp:description=""
                                       xp:fieldtype="html"
                                       src="../../../LHDY5O2SJIWPUZEUAOWGXRH4I2M/emptyHtmlModel.html"/>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES":exiting_hashcode,
        "MANIFEST_FILES":all_files
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
