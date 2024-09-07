#from termOneTransformer.helpers import generate_unique_folder_name, convert_html_to_strong
from django.conf import settings
import os, shutil
import htmlentities
from termOneTransformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh,
                                 text_en_html_to_html_text,
                                 get_popup_mlo_from_text, get_teacher_note,
                                 convert_html_to_strong,
                                 remove_html_tags)
def write_html(text, exiting_hashcode, align=None):
    try:
        from termOneTransformer.helpers import assing_class_for_color
        text = assing_class_for_color(text)
    except:
        pass
    #print(f"in write_html {text}")
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

    asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)
    destination_src_path = os.path.join(str(path_to_hashcode), str(os.path.basename(src_path)))
    shutil.copy2(str(asset_abs_path), str(destination_src_path))

    relative_path = os.path.join(hashcode, str(os.path.basename(src_path)))

    response = {
        "relative_path": relative_path,
        "hashcode": hashcode,
    }

    return response

def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    print("in Corosal")
    all_files = set()
    all_tags = [
        """<!-- Carousel --> """
    ]



    # Assigning values to variables
    try:
        #print(input_json_data["graphics_path"] + "/audio/audio.mp3")
        src_path = input_json_data["graphics_path"] + "/audio/audio.mp3"
    except:
        raise Exception("Error: Audio --> src audio not found")

    try:
        template_data = input_json_data["templateConfig"]
        slides = template_data[0].get("templateConfigData").get("elements")
        #print(slides)
    except:
        raise Exception("Error:showElements not found")

    try:
        title=template_data[0].get("templateConfigData").get("title")
        description=template_data[0].get("templateConfigData").get("description")
        if "<math" in title:
            title = mathml2latex_yarosh(html_string=title)

        if "<math" in description:
            description = mathml2latex_yarosh(html_string=description)
        #print(description)
        #print(title)
        try:
            teachers_note_xml = ""
            teacher_resp = get_teacher_note(
                text=description, all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                input_other_jsons_data=input_other_jsons_data
            )

            if teacher_resp:
                description = teacher_resp["remaining_text"]
                teachers_note_xml = teacher_resp["teachers_note_xml"]
                exiting_hashcode.update(teacher_resp["exiting_hashcode"])
                all_files.update(teacher_resp["all_files"])

        except Exception as e:
            teachers_note_xml = ""
            print(f"Error: Corosal --> While creating teachers note --> {e}")
    except:
        raise Exception("Error:Description not found")

    HtmlText = text_en_html_to_html_text(html_string=description)
    #print(HtmlText)
    content = f"<strong>{title}</strong><br><br>{HtmlText}"
    #print(content)
    resp = write_html(
        text=content,
        exiting_hashcode=exiting_hashcode,
        align='center'
    )
    #print(resp)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])
    temp=[]
    for _ in range(11):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)
    all_tags.append(
        f"""
                    <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                                      xp:fieldtype="folder" customclass="Normal">
                            <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto" cellspan="1">
                                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{resp['relative_path']}"/>
                                 {teachers_note_xml}
                """
    )
    all_tags.append(
        f"""
           <alef_presentation xlink:label="{temp[3]}" xp:name="alef_presentation"
                                  xp:description="" xp:fieldtype="folder" type="Image Carousel"
                                  showtitle="false" multipleopen="false" firstopen="false">
           """
    )
    for slide in slides:
        text=slide.get("text")
        image_url=slide.get("cssObj").get("background-image").split("(")
        image_split=image_url[1].split(")")
        image_path=image_split[0]
        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)
            text=text.replace("(","").replace(")","")
            text=text.replace("\\","")
        resp = copy_to_hashcode_dir(
            src_path=image_path,
            exiting_hashcode=exiting_hashcode
        )
        #print(f"resp {resp}")
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        temp2 = []
        for _ in range(2):
            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp2)
            temp2.append(hashcode_temp2)

        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)

        else:
            text = remove_html_tags(text)


        all_tags.append(
            f"""
                        <alef_section xlink:label="{temp2[0]}" xp:name="alef_section"
                                      xp:description="" xp:fieldtype="folder" customclass="Normal">
                            <alef_column xlink:label="{temp2[1]}" xp:name="alef_column"
                                         xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                            xp:description="{htmlentities.encode(text)}"
                                            xp:fieldtype="image" alt="">
                                    <xp:img href="../../../{resp['relative_path']}"
                                            width="1575" height="890"/>
                                </alef_image>
                            </alef_column>
                        </alef_section>
                    """
        )

    all_tags.append(
            """
                    </alef_presentation>
                </alef_column>
            </alef_section>
            """
        )

    response = {
            "XML_STRING": "".join(all_tags),
            "GENERATED_HASH_CODES": exiting_hashcode,
            "MANIFEST_FILES": all_files,

        }
    #print(response)
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
