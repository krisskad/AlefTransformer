import htmlentities
import os
from Transformer.helpers import generate_unique_folder_name, write_xml
import shutil
from django.conf import settings


def write_mlo(sections, input_other_jsons_data, exiting_hashcode):
    all_files = set()
    all_tags = [
        """<?xml version="1.0" encoding="utf-8"?>""",
        """<alef_mlo xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xp="http://www.giuntilabs.com/exact/xp_v1d0" xlink:label="LT7KP3OIZ2WREPBI2GM7LDEXRZU" xp:name="mlo" xp:description="MITR Reveal and Inspire Widgets" href="mlo.html" xp:version="3.1" xp:editortype="webeditor" xml:space="preserve" xml:class="" webeditorsafe="true" xp:deliverytype="SCORM" direction="LTR" sequence="000">"""
    ]

    head = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['head']]
    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['title']]
    subtitle = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['subtitle']]
    goalText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['goalText']]

    image_thumb_hashcode = ""
    relative_file = ""
    for key, val in input_other_jsons_data['INPUT_IMAGES_JSON_DATA'].items():
        if "launchPage.png" in val:
            image_thumb_hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(image_thumb_hashcode)
            image_thumb_destination_file_path = str(
                os.path.join(settings.OUTPUT_DIR, image_thumb_hashcode, os.path.basename(val)))

            image_thumb_src_file_path = str(os.path.join(settings.INPUT_APP_DIR, 'images', os.path.basename(val)))

            # Create the unique folder if it doesn't exist
            relative_file = os.path.join(image_thumb_hashcode, "launchPage.png")
            all_files.add(relative_file)

            # create folder
            path_to_hashcode = os.path.join(settings.OUTPUT_DIR, image_thumb_hashcode)
            os.makedirs(path_to_hashcode, exist_ok=True)

            shutil.copy2(image_thumb_src_file_path, image_thumb_destination_file_path)

    all_tags.append(
        f"""
        <alef_page xlink:label="L3LHLS7DTRTJUNCWSZX3M3LWYTA" xp:name="alef_page" xp:description="{htmlentities.encode(head)}" xp:fieldtype="folder" unittitle="{htmlentities.encode(title)} | {htmlentities.encode(subtitle)}" view="Normal" direction="LTR" allowautoplay="false" style="Style 1" customizationid="Custom_R&amp;I" width="1440" height="810" fixeddimension="No" includetoolkit="No" sequence="000">
        <alef_section xlink:label="LQ4IMNKPTQHQE7AX3D5FGM4JWME" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="LWWHJYSORL7KENOW64SWOKJ5WBQ" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
        <alef_presentation xlink:label="LIJI7RDHJDESULCGOSP6YH5EFBI" xp:name="alef_presentation" xp:description="" xp:fieldtype="folder" type="Carousel" ela_title1="{htmlentities.encode(title)}" ela_title2="{htmlentities.encode(subtitle)}" lessonObjective="{htmlentities.encode(subtitle)}" showtitle="false" multipleopen="false" firstopen="false">
        <alef_section xlink:label="LWUQ7OPC4ESGENIZOZLXH4RQVCA" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="LQAFGRAHGOWUUPHQGMY2IWFZWKU" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1" />
        </alef_section>
        <alef_image xlink:label="{image_thumb_hashcode}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
        <xp:img href="../../../{relative_file}" width="1920" height="1080" />
        </alef_image>
        """,
    )

    all_sections = "\n".join(sections)

    all_tags.append(all_sections)

    all_tags.append(
        """
        </alef_presentation>
        </alef_column>
        </alef_section>
        </alef_page>
        </alef_mlo>
        """
    )

    xml_content = "\n".join(all_tags)

    # create folder
    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(image_thumb_hashcode)

    path_to_hashcode = str(os.path.join(settings.OUTPUT_DIR, "1", "mlo", hashcode))
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_xml = os.path.join(path_to_hashcode, 'mlo.xml')
    lo_xml_filepath = os.path.join(settings.OUTPUT_DIR, '1', f'lo_{hashcode}.xpl.xml')

    all_files.add(os.path.join(hashcode, 'mlo.xml'))
    all_files.add(os.path.join("1", f'lo_{hashcode}.xpl.xml'))

    write_xml(
        file_path=path_to_xml,
        xml_content=xml_content
    )

    write_xml(
        file_path=lo_xml_filepath,
        xml_content=xml_content
    )

    response = {
        "MANIFEST_FILES":all_files,
        "GENERATED_HASH_CODES":exiting_hashcode
    }

    return response

