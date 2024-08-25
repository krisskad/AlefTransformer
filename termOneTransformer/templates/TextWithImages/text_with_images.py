from Transformer.helpers import (generate_unique_folder_name,
                                 text_en_html_to_html_text,
                                 get_popup_mlo_from_text, get_teacher_note, replace_br_after_punctuation,
                                 convert_html_to_strong, remove_html_tags, mathml2latex_yarosh
                                 )
from django.conf import settings
import os, shutil
import htmlentities

def write_html(text, exiting_hashcode, align=None):
    try:
        from Transformer.helpers import assing_class_for_color
        text = assing_class_for_color(text)
    except:
        pass
    text = convert_html_to_strong(html_str=text)
    text = replace_br_after_punctuation(text)

    if align:
        template = f"""
        <html>
        <head>
            <title></title>
        </head>
        <body style="font-family:Helvetica, 'Helvetica Neue', Arial !important; font-size:13px;">
            <div style="text-align:center">{text}</div>
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
def get_text_with_image_xml(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    class_id = "Text with Images"
    align = True
    all_files = set()
    all_tags = [
        """
        <!-- TextwithImage_001 class_id Text with Images-->

        """
    ]
    try :
    # Assigning values to variables
        #print("in first try")
        template_data = input_json_data["templateConfig"]
        #print(template_data[0].get("title"))
        title=template_data[0].get("title")
        description=template_data[0].get("description")
        imageContent_list = input_json_data["templateConfig"][0].get("images")
    except Exception as e:
        print(f"Error: TextwithImage_001 --> {e}")

    if "<math" in title:
        title_src = mathml2latex_yarosh(html_string=title)
    else:
        title_src = remove_html_tags(title)

    try:
        HtmlText = text_en_html_to_html_text(html_string=description)
        resp = write_html(
            text=HtmlText,
            exiting_hashcode=exiting_hashcode,
            align=align
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
    except:
        raise Exception(f"Error: TextwithImage_001 ")

    try:
        teachers_note_xml = ""
        teacher_resp = get_teacher_note(
            text=description, all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            input_other_jsons_data=input_other_jsons_data
        )

        if teacher_resp:
            text = teacher_resp["remaining_text"]
            teachers_note_xml = teacher_resp["teachers_note_xml"]
            exiting_hashcode.update(teacher_resp["exiting_hashcode"])
            all_files.update(teacher_resp["all_files"])

    except Exception as e:
        teachers_note_xml = ""
        print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

    temp = []
    for _ in range(10):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)
    all_tags.append(
        f"""
               <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                         xp:description="{htmlentities.encode(title_src)}" xp:fieldtype="folder"
                                         customclass="{class_id}">
                   <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                            xp:fieldtype="folder" width="auto" cellspan="1">
                       <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description=""
                                              xp:fieldtype="html"
                                              src="../../../{resp['relative_path']}"/>
                       {teachers_note_xml}
               """
    )

    # Adding images into section
    all_tags.append(
        f"""
           <alef_section xlink:label="{temp[3]}" xp:name="alef_section"
                                             xp:description="" xp:fieldtype="folder" customclass="Normal">
           """
    )
    for each_img in imageContent_list:
        try:
            src_image_path =each_img.get("src")
            print(src_image_path)
        except Exception as e:
            print(f"Warning: TextwithImage_001 --> image {e}")
            continue

        resp = copy_to_hashcode_dir(
            src_path=src_image_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        try:
            src_en_text =each_img.get("imgText")
            if "<math" in src_en_text:
                src_en_text = mathml2latex_yarosh(html_string=src_en_text)
            else:
                src_en_text = remove_html_tags(src_en_text)

        except Exception as e:
            print(f"Warning: TextwithImage_001 --> label not found {e}")
            src_en_text = ""

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)

        all_tags.append(
            f"""
                    <alef_column xlink:label="{hashcode1}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                                        xp:description="" xp:fieldtype="image" alt="{htmlentities.encode(src_en_text)}">
                            <xp:img href="../../../{resp['relative_path']}" width="688" height="890"/>
                        </alef_image>
                    </alef_column>
                """
        )
    # Closing image section
    all_tags.append(
        """
        </alef_section>
        """
    )
    try:

        src_path = input_json_data["graphics_path"] + "/audio/audio.mp3"
        resp = copy_to_hashcode_dir(
            src_path=src_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode4)

        all_tags.append(
            f"""
                <alef_audionew xlink:label="{hashcode4}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                    xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
            """
        )
    except:
        print(f"Error: TextwithImage_001 --> audio not found")

    all_tags.append(
        """
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
