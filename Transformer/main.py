import importlib
from django.conf import settings
from Transformer.helpers import read_json, zip_folder_contents
from Transformer.utils.write_main_xml_frame import write_mlo
from Transformer.utils.write_manifest_xml import write_imsmanifest_xml
import os, shutil


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


def process_data(template_ids=None):
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
        # if template_id != "VideowithInputBox_001":
        #     continue

        if template_ids:
            if isinstance(template_ids, list):
                if not template_id in template_ids:
                    continue

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
        all_manifest_files=ALL_MANIFEST_FILES,
        exiting_hashcode=GENERATED_HASH_CODES

    )

    return True


def iterative_process_data(all_dir_objs):
    resp_list = []
    for course_obj_dir_dict in all_dir_objs:
        settings.INPUT_COMMON_DIR = course_obj_dir_dict['INPUT_COMMON_DIR']
        settings.INPUT_APP_DIR = course_obj_dir_dict['INPUT_APP_DIR']

        print("Reading all input files")
        INPUT_STRUCTURE_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_STRUCTURE_JSON"]
        )
        INPUT_AUDIO_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_AUDIO_JSON"]
        )
        INPUT_VIDEO_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_VIDEO_JSON"]
        )
        INPUT_IMAGES_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_IMAGES_JSON"]
        )
        INPUT_EN_TEXT_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_EN_TEXT_JSON"]
        )

        # Common
        INPUT_COMMON_GLOSSARY_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_COMMON_GLOSSARY_JSON"]
        )
        INPUT_COMMON_GLOSSARY_IMAGES_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_COMMON_GLOSSARY_IMAGES_JSON"]
        )
        INPUT_COMMON_TEMPLATE_IMAGES_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_COMMON_TEMPLATE_IMAGES_JSON"]
        )
        INPUT_COMMON_TEXT_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_COMMON_TEXT_JSON"]
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
            "INPUT_COMMON_TEXT_JSON_DATA":INPUT_COMMON_TEXT_JSON_DATA,
            "OUTPUT_DIR":course_obj_dir_dict['OUTPUT_DIR'],
            "COURSE_ID":course_obj_dir_dict['COURSE_ID']
        }

        # storing all hash strings
        GENERATED_HASH_CODES = set()

        # storing all relative hashcode file path like hashcode/filename
        ALL_MANIFEST_FILES = set()

        input_pages = INPUT_STRUCTURE_JSON_DATA.get('pages', [])

        MLO_TEMPLATES_OUTPUT_LIST = []
        for item in input_pages:
            template_id = item['pageData']['templateID']
            # if template_id != "DropDown_001":
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
            all_manifest_files=ALL_MANIFEST_FILES,
            exiting_hashcode=GENERATED_HASH_CODES

        )

        print("Zipping output and moving it to output dir")
        zip_folder_contents(
            folder_path=str(settings.OUTPUT_DIR),
            zip_filename=str(os.path.join(course_obj_dir_dict['OUTPUT_DIR'],
                                          course_obj_dir_dict['COURSE_ID'] + ".zip"))
        )

        print("Removing temporary output")
        # shutil.rmtree(settings.OUTPUT_DIR)

        resp_list.append(
            {
                "status": "successfully",
                "message": "successfully processed course1",
                "course_name": course_obj_dir_dict['COURSE_ID'],
                "log_file":""
            }
        )

    return resp_list