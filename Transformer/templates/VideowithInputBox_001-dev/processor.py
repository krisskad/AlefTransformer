from Transformer.helpers import generate_unique_folder_name
from django.conf import settings
import os, shutil
from bs4 import BeautifulSoup


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

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    src_video_id = input_json_data['pageData']['args']['src']
    src_video_path = input_other_jsons_data['INPUT_VIDEO_JSON_DATA'][src_video_id]
    video_src_file_path = str(os.path.join(settings.INPUT_APP_DIR, src_video_path))

    # create folder
    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    destination_file_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_video_path)))

    relative_file = os.path.join(hashcode, str(os.path.basename(src_video_path)))
    all_files.add(relative_file)
    shutil.copy2(video_src_file_path, destination_file_path)

    all_tags = [f"""
    <alef_section xlink:label="LSGD7QMA6HX7UXNS6SDM6O63WMI" xp:name="alef_section" xp:description=""
                                      xp:fieldtype="folder" customclass="Normal">
                            <alef_column xlink:label="LJRCSAKECTQ3ERKSZGJE2YIQNPQ" xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto" cellspan="1">
                                <alef_advancedvideo xlink:label="LS3DTK36ZJPTUDJQPXACNUAGCSU" xp:name="alef_advancedvideo"
                                                    xp:description="" xp:fieldtype="folder">
                                    <alef_video xlink:label="{hashcode}" xp:name="alef_video"
                                                xp:description="" xp:fieldtype="movie">
                                        <xp:mov xp:fieldtype="movie" alt="" xlink:label="{hashcode}"
                                                href="../../../{relative_file}" xp:description=""
                                                xp:name="alef_video"/>
                                    </alef_video>
    """]

    qtext_id = input_json_data['pageData']['args']['textFieldData']['qText']
    placeHolderText_id = input_json_data['pageData']['args']['textFieldData']['placeHolderText']
    btnText_id = input_json_data['pageData']['args']['textFieldData']['btnText']

    qText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][qtext_id]

    soup = BeautifulSoup(qText, 'html.parser')
    span_tags = soup.find_all('span')
    tag_list = []
    for tag in span_tags:
        if 'id' in tag.attrs:  # Check if the tag has an 'id' attribute
            tag_id = tag['id']  # Extract the value of the 'id' attribute

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
