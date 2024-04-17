import glob
# import random
import shutil
import random
import string
# import os
import json
from django.conf import settings
from bs4 import BeautifulSoup
# import traceback
import os
import zipfile
from lxml import etree
import xml.etree.ElementTree as ET
import re


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
        with open(file_path, 'r', encoding='utf-8') as file:
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
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)  # 'indent=4' adds indentation for readability, optional


def write_xml(file_path, xml_content):
    print("writing: ", file_path)
    xml_content = xml_content.replace("\n\n", "\n")
    with open(file_path, "w", encoding='utf-8') as file:
        file.write(xml_content.strip())


def write_html(file_path, html_content):
    print("writing: ", file_path)
    html_content = html_content.replace("\n\n", "\n")
    with open(file_path, "w", encoding='utf-8') as file:
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
    if "data-ref" in text or "id=" in text:
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
    else:
        span_info = ''
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
        INPUT_VIEW_JSON = os.path.join(INPUT_APP_DIR, "json", "view.json")

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
            INPUT_VIEW_JSON,
            INPUT_COMMON_GLOSSARY_JSON, INPUT_COMMON_GLOSSARY_IMAGES_JSON, INPUT_COMMON_TEMPLATE_IMAGES_JSON,
            INPUT_COMMON_TEXT_JSON
        )

        if paths_exist is False:
            print("Path does not exist")
            break

        path_obj = {
                "INPUT_APP_DIR": INPUT_APP_DIR,
                "INPUT_COMMON_DIR": INPUT_COMMON_DIR,
                "INPUT_STRUCTURE_JSON": INPUT_STRUCTURE_JSON,
                "INPUT_AUDIO_JSON": INPUT_AUDIO_JSON,
                "INPUT_EN_TEXT_JSON": INPUT_EN_TEXT_JSON,
                "INPUT_IMAGES_JSON": INPUT_IMAGES_JSON,
                "INPUT_VIDEO_JSON": INPUT_VIDEO_JSON,
                "INPUT_VIEW_JSON": INPUT_VIEW_JSON,
                "INPUT_COMMON_GLOSSARY_JSON": INPUT_COMMON_GLOSSARY_JSON,
                "INPUT_COMMON_GLOSSARY_IMAGES_JSON": INPUT_COMMON_GLOSSARY_IMAGES_JSON,
                "INPUT_COMMON_TEMPLATE_IMAGES_JSON": INPUT_COMMON_TEMPLATE_IMAGES_JSON,
                "INPUT_COMMON_TEXT_JSON": INPUT_COMMON_TEXT_JSON,
                "COURSE_ID": course_dir,
                "COMMON_APP_DIR": INPUT_COMMON_DIR,
                "OUTPUT_DIR": output_dir
            }

        INPUT_APP_GLOSSARY_JSON = os.path.join(INPUT_APP_DIR, "json", "glossary.json")

        if os.path.exists(INPUT_APP_GLOSSARY_JSON):
            path_obj["INPUT_APP_GLOSSARY_JSON"] = INPUT_APP_GLOSSARY_JSON

        all_input_objects.append(
            path_obj
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


def mathml2latex_yarosh_old(html_string: str):
    """ MathML to LaTeX conversion with XSLT from krishna kadam"""
    xslt_file = os.path.join(settings.BASE_DIR, 'Transformer', 'assets', 'LaTex', 'mmltex.xsl')
    dom = etree.fromstring(html_string)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    newdom = str(newdom).replace("$", "")
    newdom = f"\({newdom}\)"
    output = f"""<span class="math-tex">{str(newdom)}</span>"""
    return output


def mathml2latex_yarosh(html_string: str):
    """ MathML to LaTeX conversion with XSLT from krishna kadam"""
    xslt_file = os.path.join(settings.BASE_DIR, 'Transformer', 'assets', 'LaTex', 'mmltex.xsl')

    # Extract MathML elements from HTML string
    soup = BeautifulSoup(html_string, 'html.parser')
    mathml_elements = soup.find_all('math')

    # Convert MathML elements to LaTeX one by one
    for mathml_element in mathml_elements:
        dom = etree.fromstring(str(mathml_element))
        xslt = etree.parse(xslt_file)
        transform = etree.XSLT(xslt)
        newdom = transform(dom)
        newdom = str(newdom).replace("$", "")
        newdom = f"\({newdom}\)"
        latex_output = f"""<span class="math-tex">{str(newdom)}</span>"""

        html_string = html_string.replace(str(mathml_element), latex_output)

    return html_string


def write_html_mlo(text, exiting_hashcode, align="center"):
    text = convert_html_to_strong(html_str=text)

    if align:
        template = f"""
        <html>
        <head>
            <title></title>
        </head>
        <body style="font-family:Helvetica, 'Helvetica Neue', Arial !important; font-size:13px;">
            <div style="text-align:{align}">{text}</div>
        </body>
        </html>
        """
    else:
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



def add_space_after_span(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    for span_tag in soup.find_all('span'):
        # Add a space after each span tag
        span_tag.insert_after(' ')
    return str(soup)


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

    if "templates" in src_path:
        asset_abs_path = os.path.join(settings.INPUT_COMMON_DIR, src_path)
    else:
        asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)

    destination_src_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_path)))
    shutil.copy2(str(asset_abs_path), str(destination_src_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_path)))

    response = {
        "relative_path": relative_path,
        "hashcode": hashcode,
    }

    return response


def remove_br(html_string):
    # Define the regular expression pattern
    pattern = re.compile(r'(?<![.:])\s*<br>')  # Match <br> not preceded by period or colon, allowing spaces

    # Replace <br> with an empty string
    cleaned_html = re.sub(pattern, '', html_string)

    return cleaned_html


def get_popup_mlo_from_text(text: str, input_other_jsons_data: dict, all_files: set, exiting_hashcode: set,
                            enable_question_statement=None):
    if text:
        all_tags = []
        question_statement = ""
        if enable_question_statement:
            temp1 = []
            for _ in range(3):
                hashcode_temp1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp1)
                temp1.append(hashcode_temp1)
            question_statement = f"""
            <alef_questionstatement xlink:label="{temp1[0]}"
                                    xp:name="alef_questionstatement"
                                    xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp1[1]}"
                                      xp:name="alef_section_general"
                                      xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="{temp1[2]}"
                                 xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto"/>
                </alef_section_general>
            </alef_questionstatement>
            """

        # get span info
        span_info = extract_span_info(text=text)
        if isinstance(span_info, str):
            return ''
        for span_content, span_attr_obj in span_info.items():

            temp = []
            for _ in range(15):
                hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp)
                temp.append(hashcode_temp)

            data_ref = span_attr_obj["data-ref"]
            if data_ref is None:
                continue

            try:
                look_into_app = False
                deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]
            except Exception as e:
                look_into_app = True
                print(f"While creating popup card {data_ref} not found in INPUT_COMMON_GLOSSARY_JSON_DATA")
                print("Looking into INPUT_APP_GLOSSARY_JSON_DATA")
                deck_oj = input_other_jsons_data["INPUT_APP_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]

            if "front" in deck_oj:
                front_content_list = deck_oj['front'].get('content', None)
                if look_into_app:
                    front_text = "<hr>".join([str(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][front_])
                                              for front_ in front_content_list])
                else:
                    front_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][front_])
                                              for front_ in front_content_list])

                front_text = assign_class_html(html_str=front_text, search_term="color", class_id='orangeText')
                front_text_resp = write_html_mlo(text=front_text, exiting_hashcode=exiting_hashcode)
                all_files.add(front_text_resp['relative_path'])
                exiting_hashcode.add(front_text_resp['hashcode'])

                front_img = deck_oj.get('front', None).get('img', None)
                if front_img:
                    if look_into_app:
                        front_img_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][front_img]
                    else:
                        front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]

                    try:
                        front_img_path_resp = copy_to_hashcode_dir(src_path=front_img_path,
                                                                   exiting_hashcode=exiting_hashcode)
                        all_files.add(front_img_path_resp['relative_path'])
                        exiting_hashcode.add(front_img_path_resp['hashcode'])
                        front_img_tag = f"""
                        <alef_image
                                xlink:label="{front_img_path_resp['hashcode']}"
                                xp:name="alef_image"
                                xp:description=""
                                xp:fieldtype="image" alt="">
                            <xp:img href="../../../{front_img_path_resp['relative_path']}"
                                    width="1136" height="890"/>
                        </alef_image>
                        """
                    except Exception as e:
                        print(f"Warning: {e}")
                        front_img_tag = ""
                else:
                    print(f"Warning: Front image not found in popup values --> {deck_oj.get('front', None)}")
                    front_img_tag = ""

                front_section = f"""
                <alef_section
                        xlink:label="{temp[8]}"
                        xp:name="alef_section" xp:description=""
                        xp:fieldtype="folder" customclass="Normal">
                    <alef_column
                            xlink:label="{temp[9]}"
                            xp:name="alef_column" xp:description=""
                            xp:fieldtype="folder" width="auto"
                            cellspan="1">
                        <alef_html
                                xlink:label="{front_text_resp['hashcode']}"
                                xp:name="alef_html"
                                xp:description=""
                                xp:fieldtype="html"
                                src="../../../{front_text_resp['relative_path']}"/>
                        {front_img_tag}
                    </alef_column>
                </alef_section>
                """
            else:
                print("Warning: Front key is not present in glossary.json the popup values")
                front_text_resp = {"hashcode":"", "front_text_resp":""}
                front_img_tag = ""
                front_section = ""

            if "back" in deck_oj:

                back_content_list = deck_oj['back']['content']

                if look_into_app:
                    back_text = "<hr>".join([str(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][back_])
                                             for back_ in back_content_list])
                else:
                    back_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][back_])
                                             for back_ in back_content_list])
                back_text = assign_class_html(html_str=back_text, search_term="color", class_id='orangeText')
                back_text_resp = write_html_mlo(text=back_text, exiting_hashcode=exiting_hashcode)
                all_files.add(back_text_resp['relative_path'])
                exiting_hashcode.add(back_text_resp['hashcode'])

                back_img = deck_oj.get('back', None).get('img', None)
                if back_img:
                    if look_into_app:
                        back_img_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][back_img]
                    else:
                        back_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][back_img]

                    try:
                        back_img_path_resp = copy_to_hashcode_dir(src_path=back_img_path, exiting_hashcode=exiting_hashcode)
                        all_files.add(back_img_path_resp['relative_path'])
                        exiting_hashcode.add(back_img_path_resp['hashcode'])
                        back_img_tag = f"""
                        <alef_image
                                xlink:label="{back_img_path_resp['hashcode']}"
                                xp:name="alef_image"
                                xp:description=""
                                xp:fieldtype="image" alt="">
                            <xp:img href="../../../{back_img_path_resp['relative_path']}"
                                    width="1396" height="890"/>
                        </alef_image>
                        """
                    except Exception as e:
                        print(f"Warning: {e}")
                        back_img_tag = ""
                else:
                    print("Back image is not found in popup vaues")
                    back_img_tag = ""

                back_section = f"""
                <alef_section
                        xlink:label="{temp[10]}"
                        xp:name="alef_section" xp:description=""
                        xp:fieldtype="folder" customclass="Normal">
                    <alef_column
                            xlink:label="{temp[11]}"
                            xp:name="alef_column" xp:description=""
                            xp:fieldtype="folder" width="auto"
                            cellspan="1">
                        <alef_html
                                xlink:label="{back_text_resp['hashcode']}"
                                xp:name="alef_html"
                                xp:description=""
                                xp:fieldtype="html"
                                src="../../../{back_text_resp['relative_path']}"/>
                        {back_img_tag}
                    </alef_column>
                </alef_section>
                """
            else:
                print(f"Warning: Back section is not present in popup value glossary.json")
                back_text_resp = {"hashcode":"", "front_text_resp":""}
                back_img_tag = ""
                back_section = ""
                # raise Exception(f"Error: Back section is not present in popup value Glossary.json --> {deck_oj}")

            if not "back" in deck_oj:
                all_tags.append(
                    f"""
                    <alef_popupvalue xlink:label="{temp[0]}"
                                     xp:name="alef_popupvalue" xp:description=""
                                     xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[1]}"
                                              xp:name="alef_section_general"
                                              xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[2]}"
                                         xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto">
                                         
                                <alef_html
                                    xlink:label="{front_text_resp['hashcode']}"
                                    xp:name="alef_html"
                                    xp:description=""
                                    xp:fieldtype="html"
                                    src="../../../{front_text_resp['relative_path']}"/>
                                
                                {front_img_tag}
                            </alef_column>
                        </alef_section_general>
                    </alef_popupvalue>
                    """
                )
            elif not "front" in deck_oj:
                all_tags.append(
                    f"""
                    <alef_popupvalue xlink:label="{temp[0]}"
                                     xp:name="alef_popupvalue" xp:description=""
                                     xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[1]}"
                                              xp:name="alef_section_general"
                                              xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[2]}"
                                         xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto">

                                <alef_html
                                    xlink:label="{back_text_resp['hashcode']}"
                                    xp:name="alef_html"
                                    xp:description=""
                                    xp:fieldtype="html"
                                    src="../../../{back_text_resp['relative_path']}"/>
                                {back_img_tag}
                            </alef_column>
                        </alef_section_general>
                    </alef_popupvalue>
                    """
                )
            else:
                all_tags.append(
                    f"""
                    <alef_popupvalue xlink:label="{temp[0]}"
                                     xp:name="alef_popupvalue" xp:description=""
                                     xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[1]}"
                                              xp:name="alef_section_general"
                                              xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[2]}"
                                         xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto">
                                <alef_flipcards xlink:label="{temp[3]}"
                                                xp:name="alef_flipcards" xp:description=""
                                                xp:fieldtype="folder" customtype="Flipcard"
                                                height="500" multipleopen="false"
                                                flipdirection="Right">
                                    {question_statement}
                                    <alef_flipcard xlink:label="{temp[7]}"
                                                   xp:name="alef_flipcard" xp:description=""
                                                   xp:fieldtype="folder" centered="true">
                                        {front_section}
                                        {back_section}
                                    </alef_flipcard>
                                </alef_flipcards>
                            </alef_column>
                        </alef_section_general>
                    </alef_popupvalue>
                    """
                )
        return {
            "all_tags": all_tags,
            "exiting_hashcode":exiting_hashcode,
            "all_files":all_files
        }
    return {}


def get_popup_mlo_small_from_text(text: str, input_other_jsons_data: dict, all_files: set, exiting_hashcode: set,
                            enable_question_statement=None):
    if text:
        all_tags = []
        # get span info
        span_info = extract_span_info(text=text)
        if isinstance(span_info, str):
            return ''
        for span_content, span_attr_obj in span_info.items():

            temp = []
            for _ in range(15):
                hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp)
                temp.append(hashcode_temp)

            data_ref = span_attr_obj["data-ref"]
            if data_ref is None:
                continue
            deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]

            front_img = deck_oj['front']['img']
            front_content_list = deck_oj['front']['content']
            front_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][front_])
                                      for front_ in front_content_list])
            front_text_resp = write_html_mlo(text=front_text, exiting_hashcode=exiting_hashcode, align="center")
            all_files.add(front_text_resp['relative_path'])
            exiting_hashcode.add(front_text_resp['hashcode'])

            back_img = deck_oj['back']['img']
            back_content_list = deck_oj['back']['content']
            back_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'][back_])
                                     for back_ in back_content_list])
            back_text_resp = write_html_mlo(text=back_text, exiting_hashcode=exiting_hashcode, align="center")
            all_files.add(back_text_resp['relative_path'])
            exiting_hashcode.add(back_text_resp['hashcode'])

            front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]
            back_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][back_img]

            front_img_path_resp = copy_to_hashcode_dir(src_path=front_img_path, exiting_hashcode=exiting_hashcode)
            all_files.add(front_img_path_resp['relative_path'])
            exiting_hashcode.add(front_img_path_resp['hashcode'])

            back_img_path_resp = copy_to_hashcode_dir(src_path=back_img_path, exiting_hashcode=exiting_hashcode)
            all_files.add(back_img_path_resp['relative_path'])
            exiting_hashcode.add(back_img_path_resp['hashcode'])

            all_tags.append(
                f"""
                <alef_popupvalue xlink:label="{temp[0]}"
                                 xp:name="alef_popupvalue" xp:description=""
                                 xp:fieldtype="folder">
                    <alef_section_general xlink:label="{temp[1]}"
                                          xp:name="alef_section_general"
                                          xp:description="" xp:fieldtype="folder">
                        <alef_column xlink:label="{temp[2]}"
                                     xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto">
                            <alef_flipcards xlink:label="{temp[3]}"
                                            xp:name="alef_flipcards" xp:description=""
                                            xp:fieldtype="folder" customtype="Flipcard"
                                            height="500" multipleopen="false"
                                            flipdirection="Right">
                                <alef_flipcard xlink:label="{temp[7]}"
                                               xp:name="alef_flipcard" xp:description=""
                                               xp:fieldtype="folder" centered="true">
                                    <alef_section
                                            xlink:label="{temp[8]}"
                                            xp:name="alef_section" xp:description=""
                                            xp:fieldtype="folder" customclass="Normal">
                                        <alef_column
                                                xlink:label="{temp[9]}"
                                                xp:name="alef_column" xp:description=""
                                                xp:fieldtype="folder" width="auto"
                                                cellspan="1">
                                            <alef_html
                                                    xlink:label="{front_text_resp['hashcode']}"
                                                    xp:name="alef_html"
                                                    xp:description=""
                                                    xp:fieldtype="html"
                                                    src="../../../{front_text_resp['relative_path']}"/>
                                            <alef_image
                                                    xlink:label="{front_img_path_resp['hashcode']}"
                                                    xp:name="alef_image"
                                                    xp:description=""
                                                    xp:fieldtype="image" alt="">
                                                <xp:img href="../../../{front_img_path_resp['relative_path']}"
                                                        width="1136" height="890"/>
                                            </alef_image>
                                        </alef_column>
                                    </alef_section>
                                    <alef_section
                                            xlink:label="{temp[10]}"
                                            xp:name="alef_section" xp:description=""
                                            xp:fieldtype="folder" customclass="Normal">
                                        <alef_column
                                                xlink:label="{temp[11]}"
                                                xp:name="alef_column" xp:description=""
                                                xp:fieldtype="folder" width="auto"
                                                cellspan="1">
                                            <alef_html
                                                    xlink:label="{back_text_resp['hashcode']}"
                                                    xp:name="alef_html"
                                                    xp:description=""
                                                    xp:fieldtype="html"
                                                    src="../../../{back_text_resp['relative_path']}"/>
                                            <alef_image
                                                    xlink:label="{back_img_path_resp['hashcode']}"
                                                    xp:name="alef_image"
                                                    xp:description=""
                                                    xp:fieldtype="image" alt="">
                                                <xp:img href="../../../{back_img_path_resp['relative_path']}"
                                                        width="1396" height="890"/>
                                            </alef_image>
                                        </alef_column>
                                    </alef_section>
                                </alef_flipcard>
                            </alef_flipcards>
                        </alef_column>
                    </alef_section_general>
                </alef_popupvalue>
                """
            )
        return {
            "all_tags": all_tags,
            "exiting_hashcode":exiting_hashcode,
            "all_files":all_files
        }
    return {}


def is_valid_xml(xml_string):
    try:
        etree.fromstring(xml_string)
        return True
    except Exception as e:
        if "Namespace" in str(e) and "prefix" in str(e):
            return True
        else:
            print(e)
            return str(e)


def write_to_file(file_path, content):
    """
    Write content to a text file.

    Args:
        file_path (str): The path to the file to write to.
        content (str): The content to write into the file.
    """
    try:
        # Open the file in 'write' mode ('w')
        with open(file_path, 'w') as file:
            # Write the content to the file
            file.write(content)
        print("Content written to", file_path)
    except IOError:
        print("Error: Unable to write to file", file_path)


def convert_html_to_strong(html_str):
    html_str = html_str.replace("<br/>", "<br>").replace("<br>", "#####")
    # Parse the HTML string
    soup = BeautifulSoup(html_str, 'html.parser')

    # Find all <span> tags with style attribute containing "font-family: Roboto-Bold;"
    span_tags = soup.find_all(lambda tag:
                              (tag.name == 'span' and
                               'Roboto-Bold' in tag.get('style', '') or
                               'textBold' in tag.get('class', [])))

    # Replace <span> tags with <strong> tags
    for span_tag in span_tags:
        if span_tag:
            try:
                strong_tag = soup.new_tag('strong')
                # Join all string contents within the <span> tag
                strong_tag.string = ''.join(span_tag.stripped_strings)
                span_tag.replace_with(strong_tag)
            except Exception as e:
                print(f'Error in span tag to strong tag conversion --> {e}')

    # Return the modified HTML
    resp = str(soup)
    resp = resp.replace("#####", "<br>")

    return resp


def assign_class_html(html_str, search_term, class_id):
    html_str = html_str.replace("<br/>", "<br>").replace("<br>", "#####")
    # Parse the HTML string
    soup = BeautifulSoup(html_str, 'html.parser')

    # Find all <span> tags with style attribute containing "font-family: Roboto-Bold;"
    span_tags = soup.find_all(lambda tag:
                              (tag.name == 'span' and
                               search_term in tag.get('style', '')))

    for tag in span_tags:
        # Assign class as orangeText
        tag['class'] = [class_id]

    # Return modified HTML
    resp = str(soup)
    resp = resp.replace("#####", "<br>")

    return resp


def remove_html_tags(text):
    if text:
        try:
            soup = BeautifulSoup(text, "html.parser")
            text = soup.get_text()
        except Exception as e:
            if "<" in text and ">" in text:
                try:
                    text = re.sub(r'<.*?>', '', text)  # Removes anything between < and >
                except Exception as e:
                    print("Error: unable to remove html tag because of ", e)
    return text



def get_teachers_note_id(html_string):
    # Parse the HTML content
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find the span tag with class 'teacherNotes'
    teacher_notes_span = soup.find('span', class_='teacherNotes')

    if teacher_notes_span:
        teacher_notes_id = teacher_notes_span['id']
        teacher_notes_text = teacher_notes_span.text

        # Remove the span tag
        teacher_notes_span.extract()
        # Get the remaining string
        context = {
            "html_string": str(soup),
            "teacher_notes_id": teacher_notes_id,
            "teacher_notes_text": teacher_notes_text
        }
        return context
    else:
        return {}


def get_teacher_note(text: str, exiting_hashcode: set,
                     all_files: set, input_other_jsons_data):

    if not "teacherNotes" in text:
        return {}

    teacher_note = get_teachers_note_id(html_string=text)

    if teacher_note:
        remaining_text = teacher_note.get("html_string")
        teacher_notes_id = teacher_note.get("teacher_notes_id")
        teacher_notes_text = teacher_note.get("teacher_notes_text")

        teacher_note_html_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][teacher_notes_id]

        resp = write_html_mlo(
            text=teacher_note_html_text,
            exiting_hashcode=exiting_hashcode,
            align=""
        )

        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        temp = []
        for _ in range(3):
            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp)
            temp.append(hashcode_temp)

        xml = f"""
            <alef_popup xlink:label="{temp[0]}" xp:name="alef_popup" xp:description="" xp:fieldtype="folder" icon="define" popupTitle="{teacher_notes_text}" full_screen="false" icon_text="{teacher_notes_text}">
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp[0]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}"/>
                    </alef_column>
                </alef_section>
            </alef_popup>
        """

        return {
            "remaining_text":remaining_text,
            "teachers_note_xml": xml,
            "exiting_hashcode": exiting_hashcode,
            "all_files": all_files
        }
    else:
        return {}