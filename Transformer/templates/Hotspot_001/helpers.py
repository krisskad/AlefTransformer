from Transformer.helpers import (remove_html_tags, generate_unique_folder_name, convert_html_to_strong,
                                 get_popup_mlo_from_text, text_en_html_to_html_text, mathml2latex_yarosh)
from django.conf import settings
import os, shutil


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


def hotspotitem_v_false(popup_obj, input_json_data, input_other_jsons_data, exiting_hashcode, view_obj, hotspot, idx, targetid):
    type = popup_obj.get("type", None)  # v OR h
    textFirst = popup_obj.get("textFirst", None)  # "true" or "false"

    all_tags = [
        f"""
        <!-- Popup id:{idx} type:{type} textFirst:{textFirst}-->
        """
    ]
    all_files = set()

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    try:
        if popup_obj:
            imageData = popup_obj.get("imageData", None)
            if imageData:
                imageDataSrc = imageData.get("src", None)
                imageDataSrcPath = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageDataSrc]

                resp_image = copy_to_hashcode_dir(
                    src_path=imageDataSrcPath,
                    exiting_hashcode=exiting_hashcode
                )
                all_files.add(resp_image['relative_path'])
                exiting_hashcode.add(resp_image['hashcode'])

                try:
                    view_obj_image = view_obj["pageData"]["args"]["hotspots"][idx]
                    popup_img = view_obj_image["popup"]
                    imageDataObj = popup_img["imageData"]
                    width = float(imageDataObj["width"].replace("px", ""))
                    height = float(imageDataObj["height"].replace("px", ""))
                except Exception as e:
                    print(f"Warning: While looking into view.json for popup image height and width error occurred: {e}")
                    print("Setting up constant width height as w:1335 & h:890")
                    width = "1335"
                    height = "890"

                image_tag = f"""
                <alef_column xlink:label="{temp[0]}"
                                             xp:name="alef_column" xp:description=""
                                             xp:fieldtype="folder" width="12" alignment="Center"
                                             cellspan="1">
                    <alef_image xlink:label="{resp_image['hashcode']}"
                                xp:name="alef_image" xp:description=""
                                xp:fieldtype="image" alt="" customWidth="800">
                        <xp:img href="../../../{resp_image['relative_path']}"
                                width="{int(width)}" height="{int(height)}"/>
                    </alef_image>
                </alef_column>
                """
            else:
                image_tag = ""
        else:
            image_tag = ""
    except Exception as e:
        print(f"Warning: Popup image issue {e}")
        image_tag = ""

    try:
        audioId = popup_obj.get("audio", None)
        if audioId:
            AudioDataSrcPath = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audioId]

            resp_audio = copy_to_hashcode_dir(
                src_path=AudioDataSrcPath,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp_audio['relative_path'])
            exiting_hashcode.add(resp_audio['hashcode'])

            audio_tag = f"""
                <alef_column xlink:label="{temp[1]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="1" cellspan="1">
                    <alef_audionew xlink:label="{temp[2]}"
                                   xp:name="alef_audionew" xp:description=""
                                   xp:fieldtype="folder">
                        <alef_audiofile
                                xlink:label="{resp_audio['hashcode']}"
                                xp:name="alef_audiofile" xp:description=""
                                audiocontrols="No" xp:fieldtype="file"
                                src="../../../{resp_audio['relative_path']}"/>
                    </alef_audionew>
                </alef_column>
                """
        else:
            audio_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        audio_tag = ""

    try:
        descId = popup_obj.get("description", None)
        if descId:
            desc_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][descId]
            HtmlText = text_en_html_to_html_text(html_string=desc_text)
            if "<math" in HtmlText:
                HtmlText = mathml2latex_yarosh(html_string=HtmlText)

            resp_desc = write_html(
                text=HtmlText,
                exiting_hashcode=exiting_hashcode,
                align=None
            )

            all_files.add(resp_desc['relative_path'])
            exiting_hashcode.add(resp_desc['hashcode'])

            popup_response = get_popup_mlo_from_text(
                text=desc_text,
                input_other_jsons_data=input_other_jsons_data,
                all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                enable_question_statement=False
            )

            if popup_response:
                all_files = popup_response['all_files']
                exiting_hashcode = popup_response['exiting_hashcode']
                popup = "\n".join(popup_response['all_tags'])
                description_tag = f"""
                        <alef_column xlink:label="{temp[3]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto" cellspan="1">                          
                           <alef_tooltip xlink:label="{temp[6]}" xp:name="alef_tooltip"
                                                          xp:description="" xp:fieldtype="folder">
                                <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{resp_desc['relative_path']}"/>
                                {popup}
                            </alef_tooltip>
                        </alef_column>
                        """

            else:

                description_tag = f"""
                        <alef_column xlink:label="{temp[3]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_html xlink:label="{resp_desc['hashcode']}"
                                       xp:name="alef_html" xp:description=""
                                       xp:fieldtype="html"
                                       src="../../../{resp_desc['relative_path']}"/>
                        </alef_column>
                        """
        else:
            description_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        description_tag = ""

    try:
        text_id = hotspot.get("text", None)
        if text_id:
            hotspot_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
            hotspot_text = remove_html_tags(text=hotspot_text)
        else:
            hotspot_text = ""
    except Exception as e:
        hotspot_text = ""
        print(f"Warning: {e}")

    try:
        title_id = popup_obj.get("title", None)
        if title_id:
            hotspot_title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title_id]
            hotspot_title = remove_html_tags(text=hotspot_title)
        else:
            hotspot_title = ""
    except Exception as e:
        hotspot_title = ""
        print(f"Warning: {e}")

    all_tags.append(
        f"""
        <alef_hotspotitem xlink:label="{targetid}" xp:name="alef_hotspotitem"
                          xp:description="{hotspot_text}" xp:fieldtype="folder"
                          hotspotName="{hotspot_title}" hotspotShape="Square"
                          fullscreen="False">
            <alef_section xlink:label="{temp[5]}" xp:name="alef_section"
                          xp:description="" xp:fieldtype="folder" customclass="Normal">
                <alef_column xlink:label="{temp[6]}" xp:name="alef_column"
                             xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_section xlink:label="{temp[7]}"
                                  xp:name="alef_section" xp:description="" xp:fieldtype="folder"
                                  customclass="Normal">
                        {image_tag}
                        <alef_column xlink:label="{temp[8]}"
                                     xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="12" cellspan="1">
                            <alef_section xlink:label="{temp[9]}"
                                          xp:name="alef_section" xp:description=""
                                          xp:fieldtype="folder" customclass="Normal">
                                {audio_tag}
                                {description_tag}
                            </alef_section>
                        </alef_column>
                    </alef_section>
                </alef_column>
            </alef_section>
        </alef_hotspotitem>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def hotspotitem_v_true(popup_obj, input_json_data, input_other_jsons_data, exiting_hashcode, view_obj, hotspot, idx, targetid):
    type = popup_obj.get("type", None)  # v OR h
    textFirst = popup_obj.get("textFirst", None)  # "true" or "false"

    all_tags = [
        f"""
        <!-- Popup id:{idx} type:{type} textFirst:{textFirst}-->
        """
    ]
    all_files = set()

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    try:
        if popup_obj:
            imageData = popup_obj.get("imageData", None)
            if imageData:
                imageDataSrc = imageData.get("src", None)
                imageDataSrcPath = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageDataSrc]

                resp_image = copy_to_hashcode_dir(
                    src_path=imageDataSrcPath,
                    exiting_hashcode=exiting_hashcode
                )
                all_files.add(resp_image['relative_path'])
                exiting_hashcode.add(resp_image['hashcode'])

                try:
                    view_obj_image = view_obj["pageData"]["args"]["hotspots"][idx]
                    popup_img = view_obj_image["popup"]
                    imageDataObj = popup_img["imageData"]
                    width = float(imageDataObj["width"].replace("px", ""))
                    height = float(imageDataObj["height"].replace("px", ""))
                except Exception as e:
                    print(f"Warning: While looking into view.json for popup image height and width error occurred: {e}")
                    print("Setting up constant width height as w:1335 & h:890")
                    width = "1335"
                    height = "890"

                image_tag = f"""
                <alef_column xlink:label="{temp[0]}"
                                             xp:name="alef_column" xp:description=""
                                             xp:fieldtype="folder" width="12" alignment="Center"
                                             cellspan="1">
                    <alef_image xlink:label="{resp_image['hashcode']}"
                                xp:name="alef_image" xp:description=""
                                xp:fieldtype="image" alt="" customWidth="800">
                        <xp:img href="../../../{resp_image['relative_path']}"
                                width="{int(width)}" height="{int(height)}"/>
                    </alef_image>
                </alef_column>
                """
            else:
                image_tag = ""
        else:
            image_tag = ""
    except Exception as e:
        image_tag = ""

    try:
        audioId = popup_obj.get("audio", None)
        if audioId:
            AudioDataSrcPath = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audioId]

            resp_audio = copy_to_hashcode_dir(
                src_path=AudioDataSrcPath,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp_audio['relative_path'])
            exiting_hashcode.add(resp_audio['hashcode'])

            audio_tag = f"""
                <alef_column xlink:label="{temp[1]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="1" cellspan="1">
                    <alef_audionew xlink:label="{temp[1]}"
                                   xp:name="alef_audionew" xp:description=""
                                   xp:fieldtype="folder">
                        <alef_audiofile
                                xlink:label="{resp_audio['hashcode']}"
                                xp:name="alef_audiofile" xp:description=""
                                audiocontrols="No" xp:fieldtype="file"
                                src="../../../{resp_audio['relative_path']}"/>
                    </alef_audionew>
                </alef_column>
                """
        else:
            audio_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        audio_tag = ""

    try:
        descId = popup_obj.get("description", None)
        if descId:
            desc_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][descId]

            HtmlText = text_en_html_to_html_text(html_string=desc_text)
            if "<math" in HtmlText:
                HtmlText = mathml2latex_yarosh(html_string=HtmlText)

            resp_desc = write_html(
                text=HtmlText,
                exiting_hashcode=exiting_hashcode,
                align=None
            )

            all_files.add(resp_desc['relative_path'])
            exiting_hashcode.add(resp_desc['hashcode'])

            popup_response = get_popup_mlo_from_text(
                text=desc_text,
                input_other_jsons_data=input_other_jsons_data,
                all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                enable_question_statement=False
            )

            if popup_response:
                all_files = popup_response['all_files']
                exiting_hashcode = popup_response['exiting_hashcode']
                popup = "\n".join(popup_response['all_tags'])
                description_tag = f"""
                        <alef_column xlink:label="{temp[3]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto" cellspan="1">                          
                           <alef_tooltip xlink:label="{temp[6]}" xp:name="alef_tooltip"
                                                          xp:description="" xp:fieldtype="folder">
                                <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{resp_desc['relative_path']}"/>
                                {popup}
                            </alef_tooltip>
                        </alef_column>
                        """

            else:

                description_tag = f"""
                        <alef_column xlink:label="{temp[3]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_html xlink:label="{resp_desc['hashcode']}"
                                       xp:name="alef_html" xp:description=""
                                       xp:fieldtype="html"
                                       src="../../../{resp_desc['relative_path']}"/>
                        </alef_column>
                        """
        else:
            description_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        description_tag = ""

    try:
        text_id = hotspot.get("text", None)
        if text_id:
            hotspot_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
            hotspot_text = remove_html_tags(text=hotspot_text)
        else:
            hotspot_text = ""
    except Exception as e:
        hotspot_text = ""
        print(f"Warning: {e}")

    try:
        title_id = popup_obj.get("title", None)
        if title_id:
            hotspot_title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title_id]
            hotspot_title = remove_html_tags(text=hotspot_title)
        else:
            hotspot_title = ""
    except Exception as e:
        hotspot_title = ""
        print(f"Warning: {e}")

    all_tags.append(
        f"""
        <alef_hotspotitem xlink:label="{targetid}" xp:name="alef_hotspotitem"
                          xp:description="{hotspot_text}" xp:fieldtype="folder"
                          hotspotName="{hotspot_title}" hotspotShape="Square"
                          fullscreen="False">
            <alef_section xlink:label="{temp[4]}" xp:name="alef_section"
                          xp:description="" xp:fieldtype="folder" customclass="Normal">
                <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                             xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                    <alef_section xlink:label="{temp[6]}"
                                  xp:name="alef_section" xp:description="" xp:fieldtype="folder"
                                  customclass="Normal">
                        <alef_column xlink:label="{temp[7]}"
                                     xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="12" cellspan="1">
                            <alef_section xlink:label="{temp[8]}"
                                          xp:name="alef_section" xp:description=""
                                          xp:fieldtype="folder" customclass="Normal">
                                {audio_tag}
                                {description_tag}
                            </alef_section>
                        </alef_column>
                        {image_tag}
                    </alef_section>
                </alef_column>
            </alef_section>
        </alef_hotspotitem>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def hotspotitem_h_true(popup_obj, input_json_data, input_other_jsons_data, exiting_hashcode, view_obj, hotspot, idx, targetid):
    type = popup_obj.get("type", None)  # v OR h
    textFirst = popup_obj.get("textFirst", None)  # "true" or "false"

    all_tags = [
        f"""
        <!-- Popup id:{idx} type:{type} textFirst:{textFirst}-->
        """
    ]
    all_files = set()

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    try:
        if popup_obj:
            imageData = popup_obj.get("imageData", None)
            if imageData:
                imageDataSrc = imageData.get("src", None)
                imageDataSrcPath = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageDataSrc]

                resp_image = copy_to_hashcode_dir(
                    src_path=imageDataSrcPath,
                    exiting_hashcode=exiting_hashcode
                )
                all_files.add(resp_image['relative_path'])
                exiting_hashcode.add(resp_image['hashcode'])

                try:
                    view_obj_image = view_obj["pageData"]["args"]["hotspots"][idx]
                    popup_img = view_obj_image["popup"]
                    imageDataObj = popup_img["imageData"]
                    width = float(imageDataObj["width"].replace("px", ""))
                    height = float(imageDataObj["height"].replace("px", ""))
                except Exception as e:
                    print(f"Warning: While looking into view.json for popup image height and width error occurred: {e}")
                    print("Setting up constant width height as w:1335 & h:890")
                    width = "1335"
                    height = "890"

                image_tag = f"""
                <alef_column xlink:label="{temp[0]}"
                                             xp:name="alef_column" xp:description=""
                                             xp:fieldtype="folder" width="6"
                                             cellspan="1">
                    <alef_image xlink:label="{resp_image['hashcode']}"
                                xp:name="alef_image" xp:description=""
                                xp:fieldtype="image" alt="">
                        <xp:img href="../../../{resp_image['relative_path']}"
                                width="{int(width)}" height="{int(height)}"/>
                    </alef_image>
                </alef_column>
                """
            else:
                image_tag = ""
        else:
            image_tag = ""
    except Exception as e:
        image_tag = ""

    try:
        audioId = popup_obj.get("audio", None)
        if audioId:
            AudioDataSrcPath = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audioId]

            resp_audio = copy_to_hashcode_dir(
                src_path=AudioDataSrcPath,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp_audio['relative_path'])
            exiting_hashcode.add(resp_audio['hashcode'])

            audio_tag = f"""
                <alef_column xlink:label="{temp[1]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="1" cellspan="1">
                    <alef_audionew xlink:label="{temp[1]}"
                                   xp:name="alef_audionew" xp:description=""
                                   xp:fieldtype="folder">
                        <alef_audiofile
                                xlink:label="{resp_audio['hashcode']}"
                                xp:name="alef_audiofile" xp:description=""
                                audiocontrols="No" xp:fieldtype="file"
                                src="../../../{resp_audio['relative_path']}"/>
                    </alef_audionew>
                </alef_column>
                """
        else:
            audio_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        audio_tag = ""

    try:
        descId = popup_obj.get("description", None)
        if descId:
            desc_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][descId]

            HtmlText = text_en_html_to_html_text(html_string=desc_text)
            if "<math" in HtmlText:
                HtmlText = mathml2latex_yarosh(html_string=HtmlText)

            resp_desc = write_html(
                text=HtmlText,
                exiting_hashcode=exiting_hashcode,
                align=None
            )

            all_files.add(resp_desc['relative_path'])
            exiting_hashcode.add(resp_desc['hashcode'])

            popup_response = get_popup_mlo_from_text(
                text=desc_text,
                input_other_jsons_data=input_other_jsons_data,
                all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                enable_question_statement=False
            )

            if popup_response:
                all_files = popup_response['all_files']
                exiting_hashcode = popup_response['exiting_hashcode']
                popup = "\n".join(popup_response['all_tags'])
                description_tag = f"""
                    <alef_column xlink:label="{temp[3]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="auto" cellspan="1">                          
                       <alef_tooltip xlink:label="{temp[6]}" xp:name="alef_tooltip"
                                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_desc['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                    """

            else:

                description_tag = f"""
                    <alef_column xlink:label="{temp[3]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_html xlink:label="{resp_desc['hashcode']}"
                                   xp:name="alef_html" xp:description=""
                                   xp:fieldtype="html"
                                   src="../../../{resp_desc['relative_path']}"/>
                    </alef_column>
                    """
        else:
            description_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        description_tag = ""

    try:
        text_id = hotspot.get("text", None)
        if text_id:
            hotspot_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
            hotspot_text = remove_html_tags(text=hotspot_text)
        else:
            hotspot_text = ""
    except Exception as e:
        hotspot_text = ""
        print(f"Warning: {e}")

    try:
        title_id = popup_obj.get("title", None)
        if title_id:
            hotspot_title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title_id]
            hotspot_title = remove_html_tags(text=hotspot_title)
        else:
            hotspot_title = ""
    except Exception as e:
        hotspot_title = ""
        print(f"Warning: {e}")

    all_tags.append(
        f"""
        <alef_hotspotitem xlink:label="{targetid}" xp:name="alef_hotspotitem"
                          xp:description="{hotspot_text}" xp:fieldtype="folder"
                          hotspotName="{hotspot_title}" hotspotShape="Square"
                          fullscreen="False">
            <alef_section xlink:label="{temp[4]}" xp:name="alef_section"
                          xp:description="" xp:fieldtype="folder" customclass="Normal">
                {description_tag}
                {audio_tag}
                {image_tag}
            
            </alef_section>
        </alef_hotspotitem>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def hotspotitem_h_false(popup_obj, input_json_data, input_other_jsons_data, exiting_hashcode, view_obj, hotspot, idx, targetid):
    type = popup_obj.get("type", None)  # v OR h
    textFirst = popup_obj.get("textFirst", None)  # "true" or "false"

    all_tags = [
        f"""
        <!-- Popup id:{idx} type:{type} textFirst:{textFirst}-->
        """
    ]
    all_files = set()

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    try:
        if popup_obj:
            imageData = popup_obj.get("imageData", None)
            if imageData:
                imageDataSrc = imageData.get("src", None)
                imageDataSrcPath = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageDataSrc]

                resp_image = copy_to_hashcode_dir(
                    src_path=imageDataSrcPath,
                    exiting_hashcode=exiting_hashcode
                )
                all_files.add(resp_image['relative_path'])
                exiting_hashcode.add(resp_image['hashcode'])

                try:
                    view_obj_image = view_obj["pageData"]["args"]["hotspots"][idx]
                    popup_img = view_obj_image["popup"]
                    imageDataObj = popup_img["imageData"]
                    width = float(imageDataObj["width"].replace("px", ""))
                    height = float(imageDataObj["height"].replace("px", ""))
                except Exception as e:
                    print(f"Warning: While looking into view.json for popup image height and width error occurred: {e}")
                    print("Setting up constant width height as w:1335 & h:890")
                    width = "1335"
                    height = "890"

                image_tag = f"""
                <alef_column xlink:label="{temp[0]}"
                                             xp:name="alef_column" xp:description=""
                                             xp:fieldtype="folder" width="6"
                                             cellspan="1">
                    <alef_image xlink:label="{resp_image['hashcode']}"
                                xp:name="alef_image" xp:description=""
                                xp:fieldtype="image" alt="">
                        <xp:img href="../../../{resp_image['relative_path']}"
                                width="{int(width)}" height="{int(height)}"/>
                    </alef_image>
                </alef_column>
                """
            else:
                image_tag = ""
        else:
            image_tag = ""
    except Exception as e:
        image_tag = ""

    try:
        audioId = popup_obj.get("audio", None)
        if audioId:
            AudioDataSrcPath = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audioId]

            resp_audio = copy_to_hashcode_dir(
                src_path=AudioDataSrcPath,
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp_audio['relative_path'])
            exiting_hashcode.add(resp_audio['hashcode'])

            audio_tag = f"""
                <alef_column xlink:label="{temp[1]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="1" cellspan="1">
                    <alef_audionew xlink:label="{temp[1]}"
                                   xp:name="alef_audionew" xp:description=""
                                   xp:fieldtype="folder">
                        <alef_audiofile
                                xlink:label="{resp_audio['hashcode']}"
                                xp:name="alef_audiofile" xp:description=""
                                audiocontrols="No" xp:fieldtype="file"
                                src="../../../{resp_audio['relative_path']}"/>
                    </alef_audionew>
                </alef_column>
                """
        else:
            audio_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        audio_tag = ""

    try:
        descId = popup_obj.get("description", None)
        if "SC6_L017_LRN2_S04_textContent_4" == descId:
            pass
        if descId:
            desc_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][descId]

            HtmlText = text_en_html_to_html_text(html_string=desc_text)
            if "<math" in HtmlText:
                HtmlText = mathml2latex_yarosh(html_string=HtmlText)

            resp_desc = write_html(
                text=HtmlText,
                exiting_hashcode=exiting_hashcode,
                align=None
            )

            all_files.add(resp_desc['relative_path'])
            exiting_hashcode.add(resp_desc['hashcode'])

            popup_response = get_popup_mlo_from_text(
                text=desc_text,
                input_other_jsons_data=input_other_jsons_data,
                all_files=all_files,
                exiting_hashcode=exiting_hashcode,
                enable_question_statement=False
            )

            if popup_response:
                all_files = popup_response['all_files']
                exiting_hashcode = popup_response['exiting_hashcode']
                popup = "\n".join(popup_response['all_tags'])
                description_tag = f"""
                    <alef_column xlink:label="{temp[3]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="auto" cellspan="1">                          
                       <alef_tooltip xlink:label="{temp[6]}" xp:name="alef_tooltip"
                                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_desc['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_desc['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                    """

            else:

                description_tag = f"""
                    <alef_column xlink:label="{temp[3]}"
                                                 xp:name="alef_column" xp:description=""
                                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_html xlink:label="{resp_desc['hashcode']}"
                                   xp:name="alef_html" xp:description=""
                                   xp:fieldtype="html"
                                   src="../../../{resp_desc['relative_path']}"/>
                    </alef_column>
                    """
        else:
            description_tag = ""

    except Exception as e:
        print(f"Warning: {e}")
        description_tag = ""

    try:
        text_id = hotspot.get("text", None)
        if text_id:
            hotspot_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_id]
            hotspot_text = remove_html_tags(text=hotspot_text)
        else:
            hotspot_text = ""
    except Exception as e:
        hotspot_text = ""
        print(f"Warning: {e}")

    try:
        title_id = popup_obj.get("title", None)
        if title_id:
            hotspot_title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title_id]
            hotspot_title = remove_html_tags(text=hotspot_title)
        else:
            hotspot_title = ""
    except Exception as e:
        hotspot_title = ""
        print(f"Warning: {e}")

    all_tags.append(
        f"""
        <alef_hotspotitem xlink:label="{targetid}" xp:name="alef_hotspotitem"
                          xp:description="{hotspot_text}" xp:fieldtype="folder"
                          hotspotName="{hotspot_title}" hotspotShape="Square"
                          fullscreen="False">
            <alef_section xlink:label="{temp[4]}" xp:name="alef_section"
                          xp:description="" xp:fieldtype="folder" customclass="Normal">
                {image_tag}
                {audio_tag}
                {description_tag}
            </alef_section>
        </alef_hotspotitem>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def sort_extra_texts_by_top(extra_texts):
    for idx, extra_text in enumerate(extra_texts):
        top_value = extra_text.get('top', '0px')
        # Remove 'px' and convert to float
        top_value_float = float(top_value.replace('px', ''))
        extra_text['top'] = top_value_float
        extra_text['id'] = idx

    sorted_extra_texts = sorted(extra_texts, key=lambda x: x['top'])
    return sorted_extra_texts