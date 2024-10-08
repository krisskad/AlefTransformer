import importlib
import glob
import pandas as pd
from django.conf import settings
from Transformer.helpers import read_json, zip_folder_contents, is_valid_xml, write_to_file, remove_char_from_keys, set_question_number
from Transformer.utils.write_main_xml_frame import write_mlo
from Transformer.utils.write_manifest_xml import write_imsmanifest_xml
import os, shutil
import platform


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
        print(f"Error: In template id : {template_id} --> {e}")
        # raise Exception(f"Error: In template id : {template_id} --> {e}")
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

    screen_number = 0
    for item in input_pages:
        screen_number = screen_number+1
        print(f"Screen Number: --> {screen_number}")

        template_id = item['pageData']['templateID']
        # if template_id != "TextwithImage_001":
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

def sanitizeXML(OUTPUT_DIR):
    if platform.system() == 'Windows':
        xml_files = glob.glob(os.path.join(OUTPUT_DIR,"**", "*.xml"),recursive=True)
        for xml_file in xml_files:
            # Read the content of the file
            with open(xml_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Replace backslashes with forward slashes
            content = content.replace('\\', '/')
            
            # Write the modified content back to the file
            with open(xml_file, 'w', encoding='utf-8') as file:
                file.write(content)

def iterative_process_data(all_dir_objs):

    try:
        customdnd_title = pd.read_csv(str(os.path.join(settings.BASE_DIR, 'media', 'customdnd_title.csv')))
    except:
        customdnd_title = pd.DataFrame()

    try:
        ela_types = pd.read_csv(str(os.path.join(settings.BASE_DIR, 'media', 'ela_template_types.csv')))
    except:
        ela_types = pd.DataFrame()

    try:
        ela_positions = pd.read_csv(str(os.path.join(settings.BASE_DIR, 'media', 'ela_thumbnail_imagetext_position.csv')))
    except:
        ela_positions = pd.DataFrame()

    resp_list = []
    for course_obj_dir_dict in all_dir_objs:
        print("#" * 20)
        # if course_obj_dir_dict["COURSE_ID"] != "CS_ELA9_L007_Discover":
        #     continue
        print(course_obj_dir_dict['COURSE_ID'])

        settings.INPUT_COMMON_DIR = course_obj_dir_dict['INPUT_COMMON_DIR']
        settings.INPUT_APP_DIR = course_obj_dir_dict['INPUT_APP_DIR']

        # print("Reading all input files")
        INPUT_STRUCTURE_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_STRUCTURE_JSON"]
        )
        INPUT_AUDIO_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_AUDIO_JSON"]
        )
        INPUT_VIDEO_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_VIDEO_JSON"]
        )
        INPUT_VIEW_JSON_DATA = read_json(
            file_path=course_obj_dir_dict["INPUT_VIEW_JSON"]
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

        # Iterate through the dictionary and replace 'non ansi' with 'ansi' in all values
        for key, value in INPUT_EN_TEXT_JSON_DATA.items():
            INPUT_EN_TEXT_JSON_DATA[key] = value.replace("’", "'") #
            # INPUT_EN_TEXT_JSON_DATA[key] = value.encode('ascii', 'ignore').decode('ascii')

        # Iterate through the dictionary and replace 'non ansi' with 'ansi' in all values
        for key, value in INPUT_COMMON_TEXT_JSON_DATA.items():
            INPUT_COMMON_TEXT_JSON_DATA[key] = value.replace("’", "'")
            # INPUT_COMMON_TEXT_JSON_DATA[key] = value.encode('ascii', 'ignore').decode('ascii')

        OTHER_JSON_DATA = {
            "INPUT_STRUCTURE_JSON_DATA": INPUT_STRUCTURE_JSON_DATA,
            "INPUT_AUDIO_JSON_DATA":INPUT_AUDIO_JSON_DATA,
            "INPUT_VIDEO_JSON_DATA":INPUT_VIDEO_JSON_DATA,
            "INPUT_VIEW_JSON_DATA":INPUT_VIEW_JSON_DATA,
            "INPUT_IMAGES_JSON_DATA":INPUT_IMAGES_JSON_DATA,
            "INPUT_EN_TEXT_JSON_DATA":INPUT_EN_TEXT_JSON_DATA,
            "INPUT_COMMON_GLOSSARY_JSON_DATA":INPUT_COMMON_GLOSSARY_JSON_DATA,
            "INPUT_COMMON_GLOSSARY_IMAGES_DATA":INPUT_COMMON_GLOSSARY_IMAGES_DATA,
            "INPUT_COMMON_TEMPLATE_IMAGES_DATA":INPUT_COMMON_TEMPLATE_IMAGES_DATA,
            "INPUT_COMMON_TEXT_JSON_DATA":INPUT_COMMON_TEXT_JSON_DATA,
            "OUTPUT_DIR":course_obj_dir_dict['OUTPUT_DIR'],
            "COURSE_ID":course_obj_dir_dict['COURSE_ID'],
            "CUSTOM_DND_TITLE":customdnd_title,
            "ELA_TEMPLATE_TYPE":ela_types,
            "ELA_TEXTBOX_POSITIONS":ela_positions
        }

        if "INPUT_APP_GLOSSARY_JSON" in course_obj_dir_dict:
            INPUT_APP_GLOSSARY_JSON_DATA = read_json(
                file_path=course_obj_dir_dict["INPUT_APP_GLOSSARY_JSON"]
            )

            OTHER_JSON_DATA["INPUT_APP_GLOSSARY_JSON_DATA"] = INPUT_APP_GLOSSARY_JSON_DATA

        # storing all hash strings
        GENERATED_HASH_CODES = set()

        # storing all relative hashcode file path like hashcode/filename
        ALL_MANIFEST_FILES = set()

        input_pages = INPUT_STRUCTURE_JSON_DATA.get('pages', [])
        input_pages = set_question_number(input_pages)

        MLO_TEMPLATES_OUTPUT_LIST = []

        STATUS = []
        screen_number = 0
        for item in input_pages:
            print("*"*10)
            screen_number = screen_number + 1
            print(f"Screen Number: --> {screen_number}")

            template_id = item['pageData']['templateID']
            item['screen_number'] = screen_number
            # if template_id == "TextwithImage_002":
            #     continue
            #
            # if screen_number != 5:
            #     continue
            if template_id == "DragAndDrop_002":
                print("Found DragAndDrop_002 --> Considering it as DragAndDrop_003")
                template_id = "DragAndDrop_003"

            response = call_package(
                template_id=template_id,
                page_data=item,
                other_json_data=OTHER_JSON_DATA,
                exiting_hashcode=GENERATED_HASH_CODES
            )
            if response:
                section = response.get('XML_STRING')
                hash_codes = response.get('GENERATED_HASH_CODES')
                manifest_files = response.get('MANIFEST_FILES')
                if response.get('STATUS', None):
                    STATUS.append(f"##### screen_number --> {screen_number} #########")
                    STATUS = STATUS + response.get('STATUS', None)
                if section:
                    MLO_TEMPLATES_OUTPUT_LIST.append(section)
                    GENERATED_HASH_CODES.update(hash_codes)
                    ALL_MANIFEST_FILES.update(manifest_files)
                else:
                    STATUS.append(f"##### screen_number --> {screen_number} #########")
                    STATUS.append(f"Note: No XML generated for screen_number {screen_number}: {template_id}")
                    print(f"Note: No xml code generated for Section: {template_id}")
            else:
                STATUS.append(f"##### screen_number --> {screen_number} #########")
                STATUS.append(f"Note: No response for screen_number {screen_number}: {template_id}")
                print(f"Note: No response for Section Template screen_number {screen_number}: {template_id}")

        all_sections = "\n".join(MLO_TEMPLATES_OUTPUT_LIST)
        mlo_response = write_mlo(
            lo_id=course_obj_dir_dict['COURSE_ID'],
            sections=all_sections,
            input_other_jsons_data=OTHER_JSON_DATA,
            exiting_hashcode=GENERATED_HASH_CODES
        )

        # is_mlo_valid = is_valid_xml(mlo_response['XM_STRING'])

        # if is_mlo_valid is True: # validate MLO file
        #     print("")
        # else:
        #     STATUS.append(f"Invalid MLO XML Error : {is_mlo_valid}")
        #     print(f"Invalid MLO XML : {is_mlo_valid}")

        GENERATED_HASH_CODES.update(mlo_response['GENERATED_HASH_CODES'])
        ALL_MANIFEST_FILES.update(mlo_response['MANIFEST_FILES'])

        write_imsmanifest_xml(
            all_manifest_files=ALL_MANIFEST_FILES,
            exiting_hashcode=GENERATED_HASH_CODES,
            input_other_jsons_data=OTHER_JSON_DATA,
        )

        print("Zipping output and moving it to output dir")

        sanitizeXML(settings.OUTPUT_DIR)

        zip_folder_contents(
            folder_path=str(settings.OUTPUT_DIR),
            zip_filename=str(os.path.join(course_obj_dir_dict['OUTPUT_DIR'],
                                          course_obj_dir_dict['COURSE_ID'] + ".zip"))
        )

        print(f"Removing temporary output {settings.OUTPUT_DIR}")
        shutil.rmtree(settings.OUTPUT_DIR)

        # print(STATUS)
        if STATUS:
            STATUS = list(set(STATUS))
            status_msg = "\n\n".join(STATUS)
            log_file_path = str(os.path.join(course_obj_dir_dict['OUTPUT_DIR'], f"{course_obj_dir_dict['COURSE_ID']}.txt"))
            write_to_file(file_path=log_file_path, content=status_msg)
            status = "Warning: please check the log"
        else:
            status = "successfully"
            status_msg = "successfully"
            log_file_path = ""

        resp_list.append(
            {
                "status": status,
                "message": status_msg,
                "course_name": course_obj_dir_dict['COURSE_ID'],
                "log_file":log_file_path
            }
        )
        print("#" * 20)

    return resp_list