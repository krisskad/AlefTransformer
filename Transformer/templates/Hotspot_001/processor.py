from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong, get_teacher_note, get_popup_mlo_from_text,
                                 write_html_mlo, mathml2latex_yarosh, get_xml_feedback, get_xml_hint, remove_html_tags,
                                 text_en_html_to_html_text, remove_div_wrapper)
from django.conf import settings
import os, shutil
import htmlentities
from .helpers import hotspotitem_v_false, hotspotitem_v_true, hotspotitem_h_false, hotspotitem_h_true, sort_extra_texts_by_top


def write_html(text, exiting_hashcode, align=None):
    try:
        from Transformer.helpers import assing_class_for_color
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

    if not "customdnd_hotspot_images" in src_path:
        asset_abs_path = os.path.join(settings.INPUT_APP_DIR, src_path)
    else:
        asset_abs_path = src_path

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
    all_files = set()

    all_tags = [
        """
        <!-- Hostpost_001 -->
        """
    ]

    # Extracting variables
    hotspots = input_json_data["pageData"]["args"]["hotspots"]

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    try:
        view_ref = input_json_data["pageData"]['viewRef']
        view_obj = input_other_jsons_data["INPUT_VIEW_JSON_DATA"]["pages"][view_ref]
    except Exception as e:
        view_obj = {}
        print(f"Warning: view_ref not found please check view.json file : {e}")

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                         xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_hotspot xlink:label="{temp[2]}" xp:name="alef_hotspot"
                              xp:description="" xp:fieldtype="folder" showColor="Yes" hotspotColor="Grey"
                              borderColor="Grey" stembackround="Yes">
        """
    )

    try:
        extraTextsList = input_json_data["pageData"]["args"]["extraTexts"]
        extraTextsViewList = view_obj["pageData"]["args"]["extraTexts"]
        if not extraTextsList:
            question_xml = ""
            print("Warning: Question Statement is not present - assigning it as blank")
        else:
            extraTextsViewList = sort_extra_texts_by_top(extra_texts=extraTextsViewList)
            top_text_index = extraTextsViewList[0].get("id", 0)
            ques_text_id = extraTextsList[top_text_index].get("text", "")

            if ques_text_id:
                ques_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][ques_text_id]
                HtmlText = text_en_html_to_html_text(html_string=ques_text)
                HtmlText = remove_div_wrapper(HtmlText)

                if "<math" in HtmlText:
                    HtmlText = mathml2latex_yarosh(html_string=HtmlText)

                resp_ques = write_html(
                    text=HtmlText,
                    exiting_hashcode=exiting_hashcode,
                    align=None
                )

                all_files.add(resp_ques['relative_path'])
                exiting_hashcode.add(resp_ques['hashcode'])

                popup_response = get_popup_mlo_from_text(
                    text=ques_text,
                    input_other_jsons_data=input_other_jsons_data,
                    all_files=all_files,
                    exiting_hashcode=exiting_hashcode,
                    enable_question_statement=False
                )

                if popup_response:
                    all_files = popup_response['all_files']
                    exiting_hashcode = popup_response['exiting_hashcode']
                    popup = "\n".join(popup_response['all_tags'])

                    all_tags.append(
                        f"""
                        <alef_questionstatement xlink:label="{temp[3]}"
                                                            xp:name="alef_questionstatement" xp:description=""
                                                            xp:fieldtype="folder">
                            <alef_section_general xlink:label="{temp[4]}"
                                                  xp:name="alef_section_general" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                             xp:description="" xp:fieldtype="folder" width="auto">
                                    <alef_tooltip xlink:label="{temp[6]}" xp:name="alef_tooltip"
                                                                  xp:description="" xp:fieldtype="folder">
                                        <alef_html xlink:label="{resp_ques['hashcode']}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{resp_ques['relative_path']}"/>
                                        {popup}
                                    </alef_tooltip>
                                </alef_column>
                            </alef_section_general>
                        </alef_questionstatement>
                        """
                    )
                else:
                    all_tags.append(
                        f"""
                        <alef_questionstatement xlink:label="{temp[3]}"
                                                            xp:name="alef_questionstatement" xp:description=""
                                                            xp:fieldtype="folder">
                            <alef_section_general xlink:label="{temp[4]}"
                                                  xp:name="alef_section_general" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                             xp:description="" xp:fieldtype="folder" width="auto">
                                    <alef_html xlink:label="{resp_ques['hashcode']}" xp:name="alef_html" xp:description=""
                                                   xp:fieldtype="html"
                                                   src="../../../{resp_ques['relative_path']}"/>
    
                                </alef_column>
                            </alef_section_general>
                        </alef_questionstatement>
                        """
                    )
            else:
                question_xml = ""
    except Exception as e:
        question_xml = ""
        print(f"Warning: Question Statement is not present - assigning it as blank {e}")


    map_links = []
    popup_items = []
    hotpost_view = view_obj['pageData']['args'].get("hotspots", [])
    for idx, hotspot in enumerate(hotspots):
        targetid = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(targetid)

        try:
            if hotpost_view:
                top = int(float(hotpost_view[idx].get("top", "").replace("px", "")))
                left = int(float(hotpost_view[idx].get("left", "").replace("px", "")))
                width = int(float(hotpost_view[idx].get("width", "").replace("px", "")))
                height = int(float(hotpost_view[idx].get("height", "").replace("px", "")))
                bottom = top + height
                right = left + width

                maplink_xml = f"""
                    <maplink xlink:name="New Link" name="New Link" type="internal"
                             targetid="{targetid}" ShowMode="" left="{left}"
                             right="{right}" top="{top}" bottom="{bottom}"/>
                """
                map_links.append(maplink_xml)
            else:
                pass
        except Exception as e:
            print(f"Warning: Maplink creation issue {e}")

        popup_obj = hotspot.get("popup", {})

        if popup_obj:
            type = popup_obj.get("type", "v")  # v OR h
            textFirst = popup_obj.get("textFirst", None)  # "true" or "false"
            # title = popup_obj.get("title", None)
            # description = popup_obj.get("description", None)
            # audio = popup_obj.get("audio", None)

            if type == "v" and textFirst == 'false':
                resp = hotspotitem_h_false(
                    popup_obj=popup_obj,
                    input_json_data=input_json_data,
                    input_other_jsons_data=input_other_jsons_data,
                    exiting_hashcode=exiting_hashcode,
                    view_obj=view_obj,
                    hotspot=hotspot,
                    idx=idx,
                    targetid=targetid
                ) # image left and text right

            elif type == "v" and textFirst == 'true':
                resp = hotspotitem_h_true(
                    popup_obj=popup_obj,
                    input_json_data=input_json_data,
                    input_other_jsons_data=input_other_jsons_data,
                    exiting_hashcode=exiting_hashcode,
                    view_obj=view_obj,
                    hotspot=hotspot,
                    idx=idx,
                    targetid=targetid
                )  # image right and text left

            elif type == "h" and textFirst == 'true':
                resp = hotspotitem_v_true(
                    popup_obj=popup_obj,
                    input_json_data=input_json_data,
                    input_other_jsons_data=input_other_jsons_data,
                    exiting_hashcode=exiting_hashcode,
                    view_obj=view_obj,
                    hotspot=hotspot,
                    idx=idx,
                    targetid=targetid
                ) # image bottom and text top

            elif type == "h" and textFirst == 'false':
                resp = hotspotitem_v_false(
                    popup_obj=popup_obj,
                    input_json_data=input_json_data,
                    input_other_jsons_data=input_other_jsons_data,
                    exiting_hashcode=exiting_hashcode,
                    view_obj=view_obj,
                    hotspot=hotspot,
                    idx=idx,
                    targetid=targetid
                ) # image top and text bottom

            else:
                print("type and textFirst are not compatible")
                resp = {}

            if resp:
                all_files = all_files | resp['MANIFEST_FILES']
                exiting_hashcode = exiting_hashcode | resp['GENERATED_HASH_CODES']
                hotspot_item_xml = resp["XML_STRING"]
            else:
                hotspot_item_xml = ""

        else:
            hotspot_item_xml = ""
            print("There is no popup present")

        popup_items.append(hotspot_item_xml)

    try:
        screen_number = input_json_data['screen_number']
        image_name = f"{input_other_jsons_data['COURSE_ID']}_{str(screen_number)}.png"

        image_path = os.path.join(settings.BASE_DIR, 'media', 'customdnd_hotspot_images', image_name)

        main_img_resp = copy_to_hashcode_dir(src_path=image_path, exiting_hashcode=exiting_hashcode)
        exiting_hashcode.add(main_img_resp['hashcode'])
        all_files.add(main_img_resp['relative_path'])

        all_map_links = "\n".join(map_links)
        main_img_tag = f"""
            <alef_image xlink:label="{main_img_resp['hashcode']}" xp:name="alef_image"
                                xp:description="" xp:fieldtype="image" alt="">
                <xp:img href="../../../{main_img_resp['relative_path']}" width="1920"
                        height="1080">
                    {all_map_links}
                </xp:img>
            </alef_image>
        """
    except Exception as e:
        main_img_tag = ""
        print(f"Warning: Main hotspot image issue {e}")

    all_tags.append(
        main_img_tag
    )

    popup_items_xml = "\n".join(popup_items)
    all_tags.append(
        popup_items_xml
    )

    all_tags.append(
        """
        </alef_hotspot>
        """
    )

    temp1 = []
    for _ in range(3):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp1.append(hashcode_temp2)


    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
        if src:
            resp = copy_to_hashcode_dir(
                src_path=src,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            all_tags.append(
                f"""
                <alef_audionew xlink:label="{temp1[0]}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                    xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
                """
            )
    except Exception as e:
        print(f"Warning: Audio did not found in input structure {e}")

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
