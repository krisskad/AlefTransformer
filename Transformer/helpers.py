import glob
import random
import shutil
import random
import string
import os
import json
from django.conf import settings
from bs4 import BeautifulSoup

import os
import zipfile


def generate_unique_folder_name(existing_hashcode, prefix="L", k=27):
    """
    Generate a unique folder name starting with 'L' default and length of 27 characters.
    """
    k = k - 1
    while True:
        # Generate a random string
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=k))
        random_string = random_string.upper()
        # Combine with 'L'
        unique_folder_name = prefix + random_string

        # Check if the folder name is unique
        if unique_folder_name not in existing_hashcode:
            return unique_folder_name


def get_existing_folders(dest_folder):
    """
    Get a list of existing folder names in the destination folder.
    """
    existing_folders = set()
    for root, dirs, files in os.walk(dest_folder):
        existing_folders.update(dirs)
    return existing_folders


def read_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                return data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return {}
    else:
        print(f"Json file does not exist: {file_path}")
        return {}


def write_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # 'indent=4' adds indentation for readability, optional


def write_xml(file_path, xml_content):
    print("writing: ", file_path)
    xml_content = xml_content.replace("\n\n", "\n")
    with open(file_path, "w") as file:
        file.write(xml_content.strip())


def write_html(file_path, html_content):
    print("writing: ", file_path)
    html_content = html_content.replace("\n\n", "\n")
    with open(file_path, "w") as file:
        file.write(html_content.strip())


def generic_tag_creator(input_json_data, input_other_jsons_data, exiting_hashcode):
    all_files = set()
    all_tags = []

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    # Assigning values to variables
    src = input_json_data["pageData"]["args"]["src"]

    if src.startswith("vid"):
        src_path = input_other_jsons_data['INPUT_VIDEO_JSON_DATA'][src]
    elif src.startswith("img"):
        src_path = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][src]
    elif src.startswith("aud"):
        src_path = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][src]
    elif src.startswith("text"):
        src_path = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][src]
    else:
        print(f"input val not valid {src}")
        return ""


def zip_folder_contents(folder_path, zip_filename='output.zip'):
    os.chdir(folder_path)  # Change current directory to the folder to be zipped

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk("."):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(str(file_path), ".")
                zipf.write(str(file_path), arcname=rel_path)

    os.chdir(settings.BASE_DIR)  # Change back to the original directory if necessary


def extract_span_info(text):
    soup = BeautifulSoup(text, 'html.parser')
    spans = soup.find_all('span')

    if not spans:
        return text

    span_info = {}
    for span in spans:
        content = span.text.strip()
        span_info[content] = {
            'id': span.get('id'),
            'data-ref': span.get('data-ref')
        }

    return span_info


def text_en_html_to_html_text(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    spans_with_id = soup.find_all('span', id=True)

    for span in spans_with_id:
        strong_tag = soup.new_tag('strong')
        strong_tag.string = span.text
        span.replace_with(strong_tag)

    spans_with_data_ref = soup.find_all('span', {'data-ref': True})

    for span in spans_with_data_ref:
        del span['data-ref']
        del span['data-dir']

        span['class'] = 'jsx_tooltip'

    return str(soup)


def validate_paths(*paths):
    for path in paths:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return False
    return True


def get_input_dir_obj(INPUT_DIR, output_dir, INPUT_COMMON_DIR):
    all_courses_dir = glob.glob(os.path.join(INPUT_DIR, "*"))

    all_input_objects = []
    for each_course_dir in all_courses_dir:

        course_dir = os.path.basename(each_course_dir)
        if "common" in each_course_dir:
            print(f"Ignoring common folder from course dir: {course_dir}")
            continue

        # app
        INPUT_APP_DIR = os.path.join(INPUT_DIR, course_dir, 'app')
        # app json
        INPUT_STRUCTURE_JSON = os.path.join(INPUT_APP_DIR, "json", "structure.json")
        INPUT_AUDIO_JSON = os.path.join(INPUT_APP_DIR, "json", "audio.json")
        INPUT_EN_TEXT_JSON = os.path.join(INPUT_APP_DIR, "json", "en_text.json")
        INPUT_IMAGES_JSON = os.path.join(INPUT_APP_DIR, "json", "images.json")
        INPUT_VIDEO_JSON = os.path.join(INPUT_APP_DIR, "json", "video.json")
        # common
        INPUT_COMMON_GLOSSARY_JSON = os.path.join(INPUT_COMMON_DIR, "templates", "config", "glossary.json")
        INPUT_COMMON_GLOSSARY_IMAGES_JSON = os.path.join(INPUT_COMMON_DIR, "templates", "config",
                                                         "glossaryImages.json")
        INPUT_COMMON_TEMPLATE_IMAGES_JSON = os.path.join(INPUT_COMMON_DIR, "templates", "config",
                                                         "templateImages.json")
        INPUT_COMMON_TEXT_JSON = os.path.join(INPUT_COMMON_DIR, "templates", "config", "text.json")

        # Validate paths
        paths_exist = validate_paths(
            INPUT_STRUCTURE_JSON, INPUT_AUDIO_JSON, INPUT_EN_TEXT_JSON, INPUT_IMAGES_JSON, INPUT_VIDEO_JSON,
            INPUT_COMMON_GLOSSARY_JSON, INPUT_COMMON_GLOSSARY_IMAGES_JSON, INPUT_COMMON_TEMPLATE_IMAGES_JSON,
            INPUT_COMMON_TEXT_JSON
        )

        if paths_exist is False:
            print("Path does not exist")
            break
        all_input_objects.append(
            {
                "INPUT_APP_DIR": INPUT_APP_DIR,
                "INPUT_COMMON_DIR": INPUT_COMMON_DIR,
                "INPUT_STRUCTURE_JSON": INPUT_STRUCTURE_JSON,
                "INPUT_AUDIO_JSON": INPUT_AUDIO_JSON,
                "INPUT_EN_TEXT_JSON": INPUT_EN_TEXT_JSON,
                "INPUT_IMAGES_JSON": INPUT_IMAGES_JSON,
                "INPUT_VIDEO_JSON": INPUT_VIDEO_JSON,
                "INPUT_COMMON_GLOSSARY_JSON": INPUT_COMMON_GLOSSARY_JSON,
                "INPUT_COMMON_GLOSSARY_IMAGES_JSON": INPUT_COMMON_GLOSSARY_IMAGES_JSON,
                "INPUT_COMMON_TEMPLATE_IMAGES_JSON": INPUT_COMMON_TEMPLATE_IMAGES_JSON,
                "INPUT_COMMON_TEXT_JSON": INPUT_COMMON_TEXT_JSON,
                "COURSE_ID": course_dir,
                "COMMON_APP_DIR": INPUT_COMMON_DIR,
                "OUTPUT_DIR": output_dir
            }
        )

    return all_input_objects


def validate_inputs_dirs(input_dir, output_dir, common_dir):
    if input_dir is None or not isinstance(input_dir, str) or not os.path.isdir(input_dir):
        return {'error': 'Invalid or missing input directory'}

    if output_dir is None or not isinstance(output_dir, str) or not os.path.isdir(output_dir):
        return {'error': 'Invalid or missing output directory'}

    if common_dir is None or not isinstance(common_dir, str) or not os.path.isdir(common_dir):
        return {'error': 'Invalid or missing common directory'}

    all_input_obj = get_input_dir_obj(input_dir, output_dir, common_dir)

    return all_input_obj



