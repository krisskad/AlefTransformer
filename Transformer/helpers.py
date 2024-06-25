import glob
# import random
import shutil
import random
import string
# import os
import json
from django.conf import settings
from bs4 import BeautifulSoup, Tag
# import traceback
import os
import zipfile
from lxml import etree
# import xml.etree.ElementTree as ET
import re
import html
import htmlentities


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


def extract_span_info_v1(text):
    if "data-ref" in text or "id=" in text:
        soup = BeautifulSoup(text, 'html.parser')
        spans = soup.find_all('span')

        if not spans:
            return text

        span_info = []
        for span in spans:
            content = span.text.strip()
            span_info.append({
                'content':content,
                'id': span.get('id'),
                'data-ref': span.get('data-ref')
            })
    else:
        span_info = ''
    return span_info


def extract_span_info_v2(text):
    # List to store objects
    toolkit_objects = []

    if "data-ref" in text or "id=" in text:

        # Parse the HTML content
        soup = BeautifulSoup(text, 'html.parser')

        # Function to recursively search and store objects
        def store_toolkit_objects(element):
            # Check if the element has a class attribute
            if element.has_attr('class') and 'toolKit' in element['class']:
                # Create dictionary with desired attributes
                toolkit_object = {
                    'content': element.text.strip(),
                    'id': element.get('id'),
                    'data-ref': element.get('data-ref')
                }
                # Append object to list
                toolkit_objects.append(toolkit_object)
            # Recursively call for all children of the current element
            for child in element.children:
                if child.name:
                    store_toolkit_objects(child)

        # Start recursively storing objects
        store_toolkit_objects(soup)
    return toolkit_objects


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


def text_en_html_to_html_text_v1(html_string):
    # Parse the HTML
    soup = BeautifulSoup(html_string, 'html.parser')

    # Find all span and br elements
    elements = soup.find_all(['span', 'br'])

    final_list = []
    # Loop through the selected elements and do something with them
    for element in elements:
        if element.name == 'span':
            if element.get('id', '').startswith("spn_"):  # Check if id starts with 'spn_'
                final_list += [str(i) for i in element.contents]
        elif element.name == 'br':
            final_list.append("<br>")

    context = "".join(final_list)
    return context


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
    # html_entities = {
    #     '<': '&lt;',
    #     '>': '&gt;',
    #     '&': '&amp;',
    #     '"': '&quot;',
    #     "'": '&apos;',
    #     '/': '&#47;',
    #     '#': '&#35;',
    #     ' ': '&nbsp;'
    # }

    """ MathML to LaTeX conversion with XSLT from krishna kadam"""
    html_string = html.unescape(html_string)
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
        newdom = htmlentities.encode(newdom)
        newdom = newdom.replace("&nbsp;", "\; ").replace("<0xa0>", "\; ")
        newdom = f"\({newdom}\)"

        # for char, entity in html_entities.items():
        #     newdom = newdom.replace(char, entity)

        latex_output = f"""<span class="math-tex">{str(newdom)}</span>"""

        mathml_element = html.unescape(str(mathml_element))
        html_string = html_string.replace(str(mathml_element), latex_output)

    return html_string


def write_html_mlo(text, exiting_hashcode, align="center"):
    try:
        text = assing_class_for_color(text)
    except:
        pass

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


def calculate_video_duration(video_path):
    # import module
    import cv2

    # create video capture object
    data = cv2.VideoCapture(video_path)

    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)

    # calculate duration of the video
    seconds = round(frames / fps)

    return seconds


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
    cleaned_html = re.sub(pattern, ' ', html_string)

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
        span_info = extract_span_info_v2(text=text)
        if isinstance(span_info, str):
            return ''

        if span_info:
            pass
        else:
            return ''

        for each_obj in span_info:

            data_ref = each_obj["data-ref"]
            if data_ref is None:
                continue

            temp = []
            for _ in range(15):
                hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp)
                temp.append(hashcode_temp)

            try:
                look_into_app = False
                deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]
            except Exception as e:
                look_into_app = True
                print(f"While creating popup card {data_ref} not found in INPUT_COMMON_GLOSSARY_JSON_DATA")
                print("Looking into INPUT_APP_GLOSSARY_JSON_DATA")
                deck_oj = input_other_jsons_data["INPUT_APP_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref]["deck"]

            if "front" in deck_oj:
                front_content_list = deck_oj['front'].get('content', [])
                if look_into_app:
                    front_text = "<hr>".join([str(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'].get(front_, '')).replace("<br>", " ")
                                              for front_ in front_content_list if front_ is not None and front_ != ''])
                else:
                    front_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'].get(front_, '')).replace("<br>", " ")
                                              for front_ in front_content_list if front_ is not None and front_ != ''])

                # front_text = assign_class_html(html_str=front_text, search_term="color", class_id='orangeText')
                front_text_resp = write_html_mlo(text=front_text, exiting_hashcode=exiting_hashcode)
                all_files.add(front_text_resp['relative_path'])
                exiting_hashcode.add(front_text_resp['hashcode'])

                front_img = deck_oj.get('front', None).get('img', None)
                if front_img:
                    try:
                        if look_into_app:
                            front_img_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][front_img]
                        else:
                            front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]

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

                back_content_list = deck_oj['back'].get('content', [])

                if look_into_app:
                    back_text = "<hr>".join([str(input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'].get(back_, '')).replace("<br>", " ")
                                             for back_ in back_content_list if back_ is not None and back_ != ''])
                else:
                    back_text = "<hr>".join([str(input_other_jsons_data['INPUT_COMMON_TEXT_JSON_DATA'].get(back_, '')).replace("<br>", " ")
                                             for back_ in back_content_list if back_ is not None and back_ != ''])
                back_text = assign_class_html(html_str=back_text, search_term="color", class_id='orangeText')
                back_text_resp = write_html_mlo(text=back_text, exiting_hashcode=exiting_hashcode)
                all_files.add(back_text_resp['relative_path'])
                exiting_hashcode.add(back_text_resp['hashcode'])

                back_img = deck_oj.get('back', None).get('img', None)
                if back_img:
                    try:
                        if look_into_app:
                            back_img_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][back_img]
                        else:
                            back_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][back_img]

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


def convert_html_to_strong_v1(html_str):
    # Replace <br/> and <br> with a placeholder
    html_str = html_str.replace("<br/>", "<br>").replace("<br>", "#####")

    # Parse the HTML string
    soup = BeautifulSoup(html_str, 'html.parser')

    # Find all <span> tags with style attribute containing "font-family: Roboto-Bold;"
    span_tags = soup.find_all(lambda tag: (tag.name == 'span' and
                                           ('Roboto-Bold' in tag.get('style', '')) or
                                           ('textBold' in tag.get('class', []))))

    # Replace <span> tags with <strong> tags
    for span_tag in span_tags:
        if span_tag:
            try:
                # Create a new <strong> tag
                strong_tag = soup.new_tag('strong')

                # Join all string contents within the <span> tag
                strong_tag.string = ''.join(span_tag.stripped_strings)

                # Copy all other styles and attributes except `textBold` class and `font-family: Roboto-Bold;`
                try:
                    style = span_tag['style']
                except:
                    style = ''

                try:
                    classes = span_tag['class']
                except:
                    classes = []

                # Remove 'Roboto-Bold' from the style attribute
                styles = [s.strip() for s in style.split(';') if 'Roboto-Bold' not in s]
                new_style = '; '.join(styles)
                if new_style:
                    strong_tag['style'] = new_style

                # Remove 'textBold' class
                new_classes = [cls for cls in classes if cls != 'textBold']
                if new_classes:
                    strong_tag['class'] = new_classes

                # Replace the original span tag with the new strong tag
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
        # Remove the style attribute containing RGB color
        # Check if 'color:rgb(' is present in the style attribute
        if 'color:rgb(' in tag['style']:
            # Remove the style attribute containing RGB color
            del tag['style']

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


def assing_class_for_color(html_string):

    color_data = [
      {"color": "Red", "hex": "#ff0000", "rgb": "rgb(255, 0, 0)", "class": "redText"},
      {"color": "Red", "hex": "#ff0000", "rgb": "", "class": "redText"},
      {"color": "Magenta", "hex": "#FF00FF", "rgb": "rgb(255, 0, 255)", "class": "purpleText"},
      {"color": "Magenta", "hex": "#FF00FF", "rgb": "", "class": "purpleText"},
      {"color": "Orange", "hex": "#F28705", "rgb": "", "class": "orangeText"},
      {"color": "Orange", "hex": "#FD7F23", "rgb": "", "class": "orangeText"},
      {"color": "Orange", "hex": "", "rgb": "rgb(253, 127, 35)", "class": "orangeText"},
      {"color": "Orange", "hex": "", "rgb": "rgb(242, 135, 5)", "class": "orangeText"},
      {"color": "Blue", "hex": "", "rgb": "rgb(0, 0, 255)", "class": "blueText_d"},
      {"color": "Blue", "hex": "#1456eb", "rgb": "", "class": "blueText_d"},
      {"color": "Blue", "hex": "#0000FF", "rgb": "", "class": "blueText_d"},
      {"color": "Blue", "hex": "", "rgb": "", "class": "blueText_d"},
      {"color": "Blue", "hex": "#0728e6", "rgb": "", "class": "blueText_d"},
      {"color": "Indigo", "hex": "#4B0082", "rgb": "", "class": "purpleText_d"},
      {"color": "Violet", "hex": "#7F00FF", "rgb": "", "class": "purpleText_d"},
      {"color": "Purple", "hex": "#803D94", "rgb": "", "class": "purpleText_d"},
      {"color": "Violet", "hex": "", "rgb": "rgb(127, 0, 255)", "class": "purpleText_d"},
      {"color": "Indigo", "hex": "", "rgb": "rgb(75, 0, 130)", "class": "purpleText_d"},
      {"color": "Cyan", "hex": "#00CCC2", "rgb": "", "class": "cyanText"},
      {"color": "Cyan", "hex": "", "rgb": "rgb(0, 204, 194)", "class": "cyanText"},
      {"color": "Green", "hex": "#1f9125", "rgb": "", "class": "greenText"},
      {"color": "Green", "hex": "#00FF00", "rgb": "", "class": "greenText"},
      {"color": "Green", "hex": "#4AAC00", "rgb": "", "class": "greenText"},
      {"color": "Green", "hex": "", "rgb": "rgb(74, 172, 0)", "class": "greenText"}
      ]

    soup = BeautifulSoup(html_string, 'html.parser')

    for tag in soup.find_all():
        style = tag.get('style', '')

        for color in color_data:
            if color["hex"].strip():
                if color["hex"].lower().replace(" ", "") in style.lower().replace(" ", ""):
                    tag_class = tag.get('class', [])
                    if not color["class"] in tag_class:
                        tag_class.append(color["class"])
                        tag['class'] = tag_class

                    tag['style'] = ";".join([i for i in style.split(";") if "color" not in i])
                    break

            if color["rgb"].strip():
                if color["rgb"].lower().replace(" ", "") in style.lower().replace(" ", ""):
                    tag_class = tag.get('class', [])
                    if not color["class"] in tag_class:
                        tag_class.append(color["class"])
                        tag['class'] = tag_class

                    tag['style'] = ";".join([i for i in style.split(";") if "color" not in i])
                    break

    return str(soup)


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


def get_xml_feedback(feedback: dict, input_other_jsons_data: dict,
                     exiting_hashcode: set, all_files: set):
    all_tags = []

    count = 1
    for key, val in feedback.items():

        main_key = key.split("_")[0]

        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
        except:
            print("Error: text not found inside feedback")
            continue

        try:
            text = html.unescape(text)
        except:
            pass

        try:
            text = remove_br(text)
            text = add_space_after_span(text)
        except Exception as e:
            print(f"Error while removing br : {e}")
            pass

        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)

        resp = write_html_mlo(text=text, exiting_hashcode=exiting_hashcode, align="left")
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)
        hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode2)
        hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode3)

        if "incorrect_1" in key:
            all_tags.append(
                f"""
                <alef_partialfeedback xlink:label="{hashcode1}"
                                      xp:name="alef_partialfeedback" xp:description=""
                                      xp:fieldtype="folder">
                    <alef_section_general xlink:label="{hashcode2}"
                                          xp:name="alef_section_general" xp:description=""
                                          xp:fieldtype="folder">
                        <alef_column xlink:label="{hashcode3}" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto">
                            <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp['relative_path']}"/>
                        </alef_column>
                    </alef_section_general>
                </alef_partialfeedback>
            """
            )
            count = count + 1
        else:

            all_tags.append(
                f"""
                <alef_{main_key}feedback xlink:label="{hashcode1}"
                                      xp:name="alef_{main_key}feedback" xp:description=""
                                      xp:fieldtype="folder">
                    <alef_section_general xlink:label="{hashcode2}"
                                          xp:name="alef_section_general" xp:description=""
                                          xp:fieldtype="folder">
                        <alef_column xlink:label="{hashcode3}" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto">
                            <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp['relative_path']}"/>
                        </alef_column>
                    </alef_section_general>
                </alef_{main_key}feedback>
                """
            )
            count = count + 1

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def get_xml_hint(hint: dict, input_other_jsons_data: dict,
                     exiting_hashcode: set, all_files: set):
    all_tags = []

    try:
        if hint:
            hinttext = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][hint['text']]

            try:
                hinttext = html.unescape(hinttext)
            except:
                pass

            if "<math" in hinttext:
                hinttext = mathml2latex_yarosh(html_string=hinttext)

            hintresp = write_html_mlo(
                text=hinttext, exiting_hashcode=exiting_hashcode, align="left"
            )
            all_files.add(hintresp['relative_path'])
            exiting_hashcode.add(hintresp['hashcode'])

            hashcode11 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode11)
            hashcode12 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode12)
            hashcode13 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode13)

            all_tags.append(
                f"""
                        <alef_hint xlink:label="{hashcode11}" xp:name="alef_hint"
                                   xp:description="" xp:fieldtype="folder">
                            <alef_section_general xlink:label="{hashcode12}"
                                                  xp:name="alef_section_general" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_column xlink:label="{hashcode13}" xp:name="alef_column"
                                             xp:description="" xp:fieldtype="folder" width="auto">
                                    <alef_html xlink:label="{hintresp['hashcode']}" xp:name="alef_html"
                                               xp:description="" xp:fieldtype="html"
                                               src="../../../{hintresp['relative_path']}"/>
                                </alef_column>
                            </alef_section_general>
                        </alef_hint>
                    """
            )
        else:
            print("Warning: hint is not found")
    except Exception as e:
        print(f"Warning: hint key not present in args {e}")

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def remove_char_from_keys(data, char):
    if isinstance(data, dict):
        return {key.replace(char, ''): remove_char_from_keys(value, char) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_char_from_keys(item, char) for item in data]
    else:
        return data


def replace_chars_in_json(json_path):
    # Open the JSON file for reading
    with open(json_path, 'r') as file:
        # Read the file content and decode using unicode_escape
        data = file.read()

    try:
        # Parse the JSON data
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Problematic location in the JSON file:", data[max(0, e.pos - 10):e.pos + 10])
        return

    # Replace ’ with ' in the JSON data

    modified_data = json.dumps(parsed_data, indent=4, ensure_ascii=False)
    modified_data = modified_data.replace("’", "'")
    modified_data = html.unescape(modified_data)

    # Write the modified JSON back to the file
    with open(json_path, 'w') as file:
        file.write(modified_data)

    print("Replacement done and JSON file updated.")


def transcript_generator(html_string: str, audio_transcript: dict):
    soup = BeautifulSoup(html_string, 'html.parser')

    main = []
    title_list = []
    content_list = []

    # Extract title section
    title_section = soup.find(id='title')
    if title_section:
        title_spans = title_section.find_all('span')

        for title_span in title_spans:
            if title_span.name == 'br':
                content_list.append('<br>')
                continue

            if title_span.name == 'span':
                title_contents = title_span.text
                title_list.append(title_contents)
                title_span_id = title_span.get('id')  # Get the id attribute of the span
                # print(title_span_id)

                title_audio_timestamp = audio_transcript.get(title_span_id)

                if title_audio_timestamp:
                    start_time = title_audio_timestamp[0] / 1000
                    end_time = title_audio_timestamp[1] / 1000

                    ts = start_time
                    end_ts = start_time + end_time

                    ts = round(ts, 3)
                    end_ts = round(end_ts, 3)

                    title_tokens = re.findall(r'\w+|[^\w\s]|\s$', title_contents)

                    for i_token in title_tokens:
                        if i_token in string.punctuation:
                            # token_html = htmlentities.encode(i_token)
                            # if not token_html == i_token:
                            #     print(f"Warning: There are html entities present in transcript which can cause xml crash so we are converting it into html encoding check below--> \n Original {i_token}\n Encoded {token_html}")
                            main.append(
                                {"type": "punct", "value": i_token}
                            )
                        elif i_token == " ":
                            main.append(
                                {"type": "punct", "value": i_token}
                            )
                        else:
                            token_html = htmlentities.encode(i_token)
                            if not token_html == i_token:
                                print(
                                    f"Warning: There are html entities present in transcript which can cause xml crash so we are converting it into html encoding check below--> \n Original {i_token}\n Encoded {token_html}")
                            main.append(
                                {"type": "text", "value": i_token, "ts": ts, "end_ts": end_ts, "confidence": 0.99}
                            )

    # Extract content section
    content_section = soup.find('span', id='content')
    if content_section:
        content_spans = content_section.find_all()
        for content_span in content_spans:
            if content_span.name == 'br':
                content_list.append('<br>')
                continue
            if content_span.name == 'span':
                content_contents = content_span.text
                content_list.append(content_contents)

                content_span_id = content_span.get('id')  # Get the id attribute of the span
                # print(content_span_id)

                content_audio_timestamp = audio_transcript.get(content_span_id)

                if content_audio_timestamp:
                    start_time = content_audio_timestamp[0] / 1000
                    end_time = content_audio_timestamp[1] / 1000

                    ts = start_time
                    end_ts = start_time + end_time

                    ts = round(ts, 3)
                    end_ts = round(end_ts, 3)

                    content_tokens = re.findall(r'\w+|[^\w\s]|\s$', content_contents)

                    for j_token in content_tokens:
                        if j_token in string.punctuation:
                            token_html = htmlentities.encode(j_token)
                            if not token_html == j_token:
                                print(
                                    f"Warning: There are html entities present in transcript which can cause xml crash so we are converting it into html encoding check below--> \n Original {j_token}\n Encoded {token_html}")
                            main.append(
                                {"type": "punct", "value": htmlentities.encode(token_html)}
                            )
                        elif j_token == " ":
                            main.append(
                                {"type": "punct", "value": j_token}
                            )
                        else:
                            # token_html = htmlentities.encode(j_token)
                            # if not token_html == j_token:
                            #     print(
                            #         f"Warning: There are html entities present in transcript which can cause xml crash so we are converting it into html encoding check below--> \n Original {j_token}\n Encoded {token_html}")
                            main.append(
                                {"type": "text", "value": j_token, "ts": ts, "end_ts": end_ts, "confidence": 0.99}
                            )

    title_text = "".join(title_list)
    content_text = "".join(content_list)
    text_area = f"<strong>{title_text}</strong><br>{content_text}"
    context = {
        "text":text_area,
        "transcript":json.dumps(main)
    }
    return context
