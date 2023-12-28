import importlib
from django.conf import settings
from Transformer.helpers import read_json
from Transformer.utils.write_main_xml_frame import write_mlo
from Transformer.utils.write_manifest_xml import write_imsmanifest_xml


def call_package(template_id, page_data, other_json_data, exiting_hashcode):
    try:
        package_name = f"Transformer.templates.{template_id}.processor"
        module = importlib.import_module(package_name)
        print(f"Package Imported : {template_id}")
        return module.process_page_data(page_data, other_json_data, exiting_hashcode)
    except ModuleNotFoundError:
        print(f"No package found for templateID: {template_id}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_data():
    # App
    INPUT_STRUCTURE_JSON_DATA = read_json(
        file_path=settings.INPUT_STRUCTURE_JSON
    )
    INPUT_AUDIO_JSON_DATA = read_json(
        file_path=settings.INPUT_AUDIO_JSON
    )
    INPUT_VIDEO_JSON_DATA = read_json(
        file_path=settings.INPUT_VIDEO_JSON
    )
    INPUT_IMAGES_JSON_DATA = read_json(
        file_path=settings.INPUT_IMAGES_JSON
    )
    INPUT_EN_TEXT_JSON_DATA = read_json(
        file_path=settings.INPUT_EN_TEXT_JSON
    )

    # Common
    INPUT_COMMON_GLOSSARY_JSON_DATA = read_json(
        file_path=settings.INPUT_COMMON_GLOSSARY_JSON
    )
    INPUT_COMMON_GLOSSARY_IMAGES_DATA = read_json(
        file_path=settings.INPUT_COMMON_GLOSSARY_IMAGES_JSON
    )
    INPUT_COMMON_TEMPLATE_IMAGES_DATA = read_json(
        file_path=settings.INPUT_COMMON_TEMPLATE_IMAGES_JSON
    )
    INPUT_COMMON_TEXT_JSON_DATA = read_json(
        file_path=settings.INPUT_COMMON_TEXT_JSON
    )

    OTHER_JSON_DATA = {
        "INPUT_STRUCTURE_JSON_DATA": INPUT_STRUCTURE_JSON_DATA,
        "INPUT_AUDIO_JSON_DATA":INPUT_AUDIO_JSON_DATA,
        "INPUT_VIDEO_JSON_DATA":INPUT_VIDEO_JSON_DATA,
        "INPUT_IMAGES_JSON_DATA":INPUT_IMAGES_JSON_DATA,
        "INPUT_EN_TEXT_JSON_DATA":INPUT_EN_TEXT_JSON_DATA,
        "INPUT_COMMON_GLOSSARY_JSON_DATA":INPUT_COMMON_GLOSSARY_JSON_DATA,
        "INPUT_COMMON_GLOSSARY_IMAGES_DATA":INPUT_COMMON_GLOSSARY_IMAGES_DATA,
        "INPUT_COMMON_TEMPLATE_IMAGES_DATA":INPUT_COMMON_TEMPLATE_IMAGES_DATA,
        "INPUT_COMMON_TEXT_JSON_DATA":INPUT_COMMON_TEXT_JSON_DATA
    }

    # storing all hash strings
    GENERATED_HASH_CODES = set()

    # storing all relative hashcode file path like hashcode/filename
    ALL_MANIFEST_FILES = set()

    input_pages = INPUT_STRUCTURE_JSON_DATA.get('pages', [])

    MLO_TEMPLATES_OUTPUT_LIST = []
    for item in input_pages:
        template_id = item['pageData']['templateID']
        # if template_id != "Video_001":
        #     continue

        response = call_package(
            template_id=template_id,
            page_data=item,
            other_json_data=OTHER_JSON_DATA,
            exiting_hashcode=GENERATED_HASH_CODES
        )
        if response:
            section = response['XML_STRING']
            hash_codes = response['GENERATED_HASH_CODES']
            manifest_files = response['MANIFEST_FILES']
            if section:
                MLO_TEMPLATES_OUTPUT_LIST.append(section)
                GENERATED_HASH_CODES.update(hash_codes)
                ALL_MANIFEST_FILES.update(manifest_files)

    mlo_response = write_mlo(
        sections=MLO_TEMPLATES_OUTPUT_LIST,
        input_other_jsons_data=OTHER_JSON_DATA,
        exiting_hashcode=GENERATED_HASH_CODES
    )

    GENERATED_HASH_CODES.update(mlo_response['GENERATED_HASH_CODES'])
    ALL_MANIFEST_FILES.update(mlo_response['MANIFEST_FILES'])

    write_imsmanifest_xml(
        all_manifest_files=ALL_MANIFEST_FILES
    )

    return True