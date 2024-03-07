from Transformer.helpers import generate_unique_folder_name, convert_html_to_strong
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, destination_file_path):
    text = convert_html_to_strong(html_str=text)

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
    all_tags = [
        """
        <!-- Video_001 -->

        """
    ]

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    # Assigning values to variables
    try:
        src = input_json_data["pageData"]["args"]["src"]
    except:
        raise Exception("Error: Video_001 --> src video not found")

    if src.startswith("vid"):
        src_path = input_other_jsons_data['INPUT_VIDEO_JSON_DATA'][src]
    else:
        print(f"input val not valid {src}")
        return ""

    asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)
    destination_src_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_path)))
    shutil.copy2(str(asset_abs_path), str(destination_src_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_path)))
    all_files.add(relative_path)

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
                        <alef_advancedvideo xlink:label="{temp[2]}" xp:name="alef_advancedvideo"
                                            xp:description="" xp:fieldtype="folder">
                            <alef_video xlink:label="{hashcode}" xp:name="alef_video"
                                        xp:description="" xp:fieldtype="movie">
                                <xp:mov xp:fieldtype="movie" alt="" xlink:label="{hashcode}"
                                        href="../../../{relative_path}" xp:description=""
                                        xp:name="alef_video"/>
                            </alef_video>
                        </alef_advancedvideo>
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
