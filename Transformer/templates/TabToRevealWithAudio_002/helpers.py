from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, get_popup_mlo_from_text,extract_span_info
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode):

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

def image(input_json_data, input_other_jsons_data, exiting_hashcode):
    """
    :param input_json_data: {
              "tabType": "image",
              "tabHeaderTxt": "text_108",
              "TabContentText": "text_036",
              "audio": "aud_008",
              "bgImage": "img_034"
            },
            {
              "tabType": "image",
              "tabHeaderTxt": "text_109",
              "TabContentText": "text_036",
              "audio": "aud_008",
              "imageData": {
                "src": "img_040"
              }
            }
    :param input_other_jsons_data:
    :param exiting_hashcode:
    :return:
    """
    all_files = set()
    all_tags = []

    temp = []
    for _ in range(10):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    tabHeaderTxt = input_json_data.get("tabHeaderTxt", None)
    if tabHeaderTxt:
        tabHeaderTxt_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
    else:
        print("tabHeaderTxt Is not provided")
        tabHeaderTxt_text = ""

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                              xp:description="{htmlentities.encode(tabHeaderTxt_text)}" xp:fieldtype="folder"
                                              customclass="Normal">
        """
    )

    imageData = input_json_data.get("imageData", None)
    if imageData:
        imageData_src = imageData.get("src", None)
        if imageData_src:
            imageData_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageData_src]
            resp_img = copy_to_hashcode_dir(src_path=imageData_src, exiting_hashcode=exiting_hashcode)
            all_files.add(resp_img['relative_path'])
            exiting_hashcode.add(resp_img['hashcode'])
            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[7]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                        <alef_image xlink:label="{resp_img['hashcode']}" xp:name="alef_image"
                                    xp:description="" xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp_img['relative_path']}"
                                    width="1583" height="890"/>
                        </alef_image>
                    </alef_column>
                """
            )

    audio = input_json_data.get("audio", None)
    if audio:
        audio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio]
        resp = copy_to_hashcode_dir(src_path=audio_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="1" alignment="Center"
                         cellspan="1">
                <alef_audionew xlink:label="{temp[2]}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}"
                                    xp:name="alef_audiofile" xp:description=""
                                    audiocontrols="No" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
            </alef_column>
            """
        )
    else:
        print("Warning: Audio not found so ignoring audio tag")

    TabContentText = input_json_data.get("TabContentText", None)
    if TabContentText:
        TabContentText_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][TabContentText]

        popup_response = get_popup_mlo_from_text(
            text=TabContentText_text,
            input_other_jsons_data=input_other_jsons_data,
            all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            enable_question_statement=False
        )

        if popup_response:

            all_files = popup_response['all_files']
            exiting_hashcode = popup_response['exiting_hashcode']
            popup = "\n".join(popup_response['all_tags'])

            TabContentText_text_HtmlText = text_en_html_to_html_text(html_string=TabContentText_text)

            resp_text = write_html(
                text=TabContentText_text_HtmlText,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                        <alef_tooltip xlink:label="{temp[4]}" xp:name="alef_tooltip"
                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                """
            )
        else:

            resp_text = write_html(
                text=TabContentText_text,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                    </alef_column>
                """
            )

    else:
        print("tabHeaderTxt Is not provided so ignoring tag")

    bgImage = input_json_data.get("bgImage", None)
    if bgImage:
        bgImage_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][bgImage]
        resp = copy_to_hashcode_dir(src_path=bgImage_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[6]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                            xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}"
                            width="1583" height="890"/>
                </alef_image>
            </alef_column>
            """
        )

    all_tags.append(
        """
        </alef_section>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def video(input_json_data, input_other_jsons_data, exiting_hashcode):
    """

    :param input_json_data: {
              "tabHeaderTxt": "text_112",
              "TabContentText": "text_088",
              "audio": "p011_audio_2",
              "tabType": "video",
              "videoData": {
                "src": "vid_003"
              }
            }
    :param input_other_jsons_data:
    :param exiting_hashcode:
    :return:
    """
    all_files = set()
    all_tags = []

    temp = []
    for _ in range(10):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    tabHeaderTxt = input_json_data.get("tabHeaderTxt", None)
    if tabHeaderTxt:
        tabHeaderTxt_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
    else:
        print("tabHeaderTxt Is not provided")
        tabHeaderTxt_text = ""

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                              xp:description="{htmlentities.encode(tabHeaderTxt_text)}" xp:fieldtype="folder"
                                              customclass="Normal">
        """
    )

    videoData = input_json_data.get("videoData", None)
    if videoData:
        videoData_src = input_json_data.get("src", None)
        if videoData_src:
            videoData_src = input_other_jsons_data['INPUT_VIDEO_JSON_DATA'][videoData_src]
            resp_vid = copy_to_hashcode_dir(src_path=videoData_src, exiting_hashcode=exiting_hashcode)
            all_files.add(resp_vid['relative_path'])
            exiting_hashcode.add(resp_vid['hashcode'])
            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[7]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                        <alef_video xlink:label="{temp[8]}" xp:name="alef_video"
                                    xp:description="" xp:fieldtype="movie">
                            <xp:mov xp:fieldtype="movie" alt="" xlink:label="{resp_vid['hashcode']}"
                                    href="../../../{resp_vid['relative_path']}" xp:description=""
                                    xp:name="alef_video"/>
                        </alef_video>
                    </alef_column>
                """
            )

    audio = input_json_data.get("audio", None)
    if audio:
        audio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio]
        resp = copy_to_hashcode_dir(src_path=audio_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="1" alignment="Center"
                         cellspan="1">
                <alef_audionew xlink:label="{temp[2]}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}"
                                    xp:name="alef_audiofile" xp:description=""
                                    audiocontrols="No" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
            </alef_column>
            """
        )
    else:
        print("Warning: Audio not found so ignoring audio tag")

    TabContentText = input_json_data.get("TabContentText", None)
    if TabContentText:
        TabContentText_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][TabContentText]

        popup_response = get_popup_mlo_from_text(
            text=TabContentText_text,
            input_other_jsons_data=input_other_jsons_data,
            all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            enable_question_statement=False
        )

        if popup_response:

            all_files = popup_response['all_files']
            exiting_hashcode = popup_response['exiting_hashcode']
            popup = "\n".join(popup_response['all_tags'])

            TabContentText_text_HtmlText = text_en_html_to_html_text(html_string=TabContentText_text)

            resp_text = write_html(
                text=TabContentText_text_HtmlText,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                        <alef_tooltip xlink:label="{temp[4]}" xp:name="alef_tooltip"
                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                """
            )
        else:

            resp_text = write_html(
                text=TabContentText_text,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                    </alef_column>
                """
            )

    else:
        print("tabHeaderTxt Is not provided so ignoring tag")

    all_tags.append(
        """
        </alef_section>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def button_with_popup(input_json_data, input_other_jsons_data, exiting_hashcode):
    """

    :param input_json_data: {
              "tabHeaderTxt": "text_110",
              "TabContentText": "text_087",
              "audio": "p011_audio_1",
              "tabType": "buttonWithPopup",
              "extraImages": [
                {
                  "src": "img_054",
                  "imageZoom": false
                }
              ],
              "buttonData": [
                {
                  "buttonTxt": "p011_btnText_1",
                  "hoverClass": "btn1Hover",
                  "popupData": {
                    "type": "v",
                    "textFirst": false,
                    "title": "p011_btnText_1",
                    "description": "p011_textContent_1",
                    "audio": "p011_popupAudio_1",
                    "imageData": { "src": "p011_popupImage_1" }
                  }
                },
                {
                  "buttonTxt": "p011_btnText_2",
                  "hoverClass": "btn2Hover",

                  "popupData": {
                    "type": "v",
                    "textFirst": false,
                    "title": "p011_btnText_2",
                    "description": "p011_textContent_2",
                    "audio": "p011_popupAudio_2",
                    "imageData": { "src": "p011_popupImage_2" }
                  }
                },

                {
                  "buttonTxt": "p011_btnText_3",
                  "hoverClass": "btn3Hover",

                  "popupData": {
                    "type": "v",
                    "textFirst": false,
                    "title": "p011_btnText_3",
                    "description": "p011_textContent_3",
                    "audio": "p011_popupAudio_3",
                    "imageData": { "src": "p011_popupImage_3" }
                  }
                }
              ]
            }
    :param input_other_jsons_data:
    :param exiting_hashcode:
    :return:
    """

    all_files = set()
    all_tags = []

    temp = []
    for _ in range(10):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    tabHeaderTxt = input_json_data.get("tabHeaderTxt", None)
    if tabHeaderTxt:
        tabHeaderTxt_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
    else:
        print("tabHeaderTxt Is not provided")
        tabHeaderTxt_text = ""

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                              xp:description="{htmlentities.encode(tabHeaderTxt_text)}" xp:fieldtype="folder"
                                              customclass="Normal">
        """
    )

    imageData = input_json_data.get("imageData", None)
    if imageData:
        imageData_src = input_json_data.get("src", None)
        if imageData_src:
            imageData_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][imageData_src]
            resp_img = copy_to_hashcode_dir(src_path=imageData_src, exiting_hashcode=exiting_hashcode)
            all_files.add(resp_img['relative_path'])
            exiting_hashcode.add(resp_img['hashcode'])
            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[7]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                        <alef_image xlink:label="{resp_img['hashcode']}" xp:name="alef_image"
                                    xp:description="" xp:fieldtype="image" alt="">
                            <xp:img href="../../../{resp_img['relative_path']}"
                                    width="1583" height="890"/>
                        </alef_image>
                    </alef_column>
                """
            )

    audio = input_json_data.get("audio", None)
    if audio:
        audio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][audio]
        resp = copy_to_hashcode_dir(src_path=audio_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="1" alignment="Center"
                         cellspan="1">
                <alef_audionew xlink:label="{temp[2]}" xp:name="alef_audionew"
                               xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}"
                                    xp:name="alef_audiofile" xp:description=""
                                    audiocontrols="No" xp:fieldtype="file"
                                    src="../../../{resp['relative_path']}"/>
                </alef_audionew>
            </alef_column>
            """
        )
    else:
        print("Warning: Audio not found so ignoring audio tag")

    TabContentText = input_json_data.get("TabContentText", None)
    if TabContentText:
        TabContentText_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][TabContentText]

        popup_response = get_popup_mlo_from_text(
            text=TabContentText_text,
            input_other_jsons_data=input_other_jsons_data,
            all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            enable_question_statement=False
        )

        if popup_response:

            all_files = popup_response['all_files']
            exiting_hashcode = popup_response['exiting_hashcode']
            popup = "\n".join(popup_response['all_tags'])

            TabContentText_text_HtmlText = text_en_html_to_html_text(html_string=TabContentText_text)

            resp_text = write_html(
                text=TabContentText_text_HtmlText,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                        <alef_tooltip xlink:label="{temp[4]}" xp:name="alef_tooltip"
                                      xp:description="" xp:fieldtype="folder">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                            {popup}
                        </alef_tooltip>
                    </alef_column>
                """
            )
        else:

            resp_text = write_html(
                text=TabContentText_text,
                exiting_hashcode=exiting_hashcode,
            )
            all_files.add(resp_text['relative_path'])
            exiting_hashcode.add(resp_text['hashcode'])

            all_tags.append(
                f"""
                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                 xp:description="" xp:fieldtype="folder" width="5" alignment="Left"
                                 cellspan="1">
                            <alef_html xlink:label="{resp_text['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp_text['relative_path']}"/>
                    </alef_column>
                """
            )

    else:
        print("tabHeaderTxt Is not provided so ignoring tag")

    bgImage = input_json_data.get("bgImage", None)
    if bgImage:
        bgImage_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][bgImage]
        resp = copy_to_hashcode_dir(src_path=bgImage_src, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        all_tags.append(
            f"""
            <alef_column xlink:label="{temp[6]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="6" cellspan="1">
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                            xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../{resp['relative_path']}"
                            width="1583" height="890"/>
                </alef_image>
            </alef_column>
            """
        )

    all_tags.append(
        """
        </alef_section>
        """
    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES": exiting_hashcode,
        "MANIFEST_FILES": all_files
    }

    return response


def flipcards(input_json_data, input_other_jsons_data, exiting_hashcode):
    """

    :param input_json_data: {
              "tabHeaderTxt": "text_113",
              "TabContentText": "text_089",
              "tabType": "cards",
              "container": [
                {
                  "deck": {
                    "front": {
                      "content": "text_067",
                      "img": "img_038",
                      "audio": "aud_027"
                    },
                    "back": {
                      "content": "text_068",
                      "img": "img_039",
                      "audio": "aud_023"
                    }
                  }
                },
                {
                  "deck": {
                    "front": {
                      "content": "text_069",
                      "img": "img_040",
                      "audio": "aud_028"
                    },
                    "back": {
                      "content": "text_070",
                      "img": "img_041",
                      "audio": "aud_024"
                    }
                  }
                },
                {
                  "deck": {
                    "front": {
                      "content": "text_071",
                      "img": "img_042",
                      "audio": "aud_029"
                    },
                    "back": {
                      "content": "text_072",
                      "img": "img_043",
                      "audio": "aud_025"
                    }
                  }
                },
                {
                  "deck": {
                    "front": {
                      "content": "text_073",
                      "img": "img_044",
                      "audio": "aud_030"
                    },
                    "back": {
                      "content": "text_074",
                      "img": "img_045",
                      "audio": "aud_026"
                    }
                  }
                }
              ]
            }
    :param input_other_jsons_data:
    :param exiting_hashcode:
    :return:
    """

    all_files = set()
    all_tags = []

    temp = []
    for _ in range(20):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    tabHeaderTxt = input_json_data.get("tabHeaderTxt", None)
    if tabHeaderTxt:
        tabHeaderTxt_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][tabHeaderTxt]
    else:
        print("tabHeaderTxt Is not provided")
        tabHeaderTxt_text = ""

    all_tags.append(
        f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                                              xp:description="{htmlentities.encode(tabHeaderTxt_text)}" xp:fieldtype="folder"
                                              customclass="Normal">
            <alef_column xlink:label="{temp[1]}" xp:name="alef_column"
                         xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_flipcards xlink:label="{temp[2]}"
                                xp:name="alef_flipcards" xp:description="" xp:fieldtype="folder"
                                customtype="Flipcard" height="500" multipleopen="true"
                                flipdirection="Right">
                    <alef_questionstatement xlink:label="{temp[3]}"
                                            xp:name="alef_questionstatement" xp:description=""
                                            xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[4]}"
                                              xp:name="alef_section_general" xp:description=""
                                              xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[5]}"
                                         xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto"/>
                        </alef_section_general>
                    </alef_questionstatement>
        """
    )

    container = input_json_data.get("container", None)
    if container:
        for each_card_obj in container:

            temp3 = []
            for _ in range(20):
                hashcode_temp3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode_temp3)
                temp3.append(hashcode_temp3)

            front_obj = each_card_obj['deck'].get('front', None)
            if "content" in front_obj:
                front_objcontent = front_obj['content']
                front_objcontent_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][front_objcontent]


                # get span info
                span_info = extract_span_info(text=front_objcontent_text)
                if isinstance(span_info, str):

                    front_objcontent_text_resp = write_html(text=front_objcontent_text,
                                                            exiting_hashcode=exiting_hashcode)
                    all_files.add(front_objcontent_text_resp['relative_path'])
                    exiting_hashcode.add(front_objcontent_text_resp['hashcode'])

                    front_objcontent_text_xml = f"""
                    <alef_html xlink:label="{front_objcontent_text_resp['hashcode']}"
                                           xp:name="alef_html" xp:description=""
                                           xp:fieldtype="html"
                                           src="../../../{front_objcontent_text_resp['relative_path']}"/>
                    """
                else:

                    html_text = text_en_html_to_html_text(html_string=front_objcontent_text)

                    front_objcontent_text_resp = write_html(text=html_text,
                                                            exiting_hashcode=exiting_hashcode)
                    all_files.add(front_objcontent_text_resp['relative_path'])
                    exiting_hashcode.add(front_objcontent_text_resp['hashcode'])

                    # span_info
                    all_pop_ups = []
                    for span_content, span_attr_obj in span_info.items():

                        temp2 = []
                        for _ in range(4):
                            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L",
                                                                        k=27)
                            exiting_hashcode.add(hashcode_temp2)
                            temp2.append(hashcode_temp2)

                        data_ref = span_attr_obj["data-ref"]
                        if data_ref is None:
                            continue
                        deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref][
                            "deck"]

                        front_img = deck_oj['front']['img']
                        front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]
                        front_img_path_resp = copy_to_hashcode_dir(src_path=front_img_path,
                                                                   exiting_hashcode=exiting_hashcode)
                        all_files.add(front_img_path_resp['relative_path'])
                        exiting_hashcode.add(front_img_path_resp['hashcode'])

                        all_pop_ups.append(
                            f"""
                            <alef_popupvalue xlink:label="{temp2[1]}"
                                             xp:name="alef_popupvalue" xp:description=""
                                             xp:fieldtype="folder">
                                <alef_section_general
                                        xlink:label="{temp2[2]}"
                                        xp:name="alef_section_general" xp:description=""
                                        xp:fieldtype="folder">
                                    <alef_column
                                            xlink:label="{temp2[3]}"
                                            xp:name="alef_column" xp:description=""
                                            xp:fieldtype="folder" width="auto">
                                        <alef_image xlink:label="{front_img_path_resp['hashcode']}"
                                            xp:name="alef_image" xp:description=""
                                            xp:fieldtype="image" alt="" customAlign="Center">
                                            <xp:img href="../../../{front_img_path_resp['relative_path']}"
                                            width="304" height="200"/>
                                        </alef_image>
                                    </alef_column>
                                </alef_section_general>
                            </alef_popupvalue>
                            """
                        )

                    all_pop_ups_xml = "\n".join(all_pop_ups)
                    front_objcontent_text_xml = f"""
                    <alef_tooltip xlink:label="{temp3[0]}"
                                  xp:name="alef_tooltip" xp:description=""
                                  xp:fieldtype="folder">
                        <alef_html xlink:label="{front_objcontent_text_resp['hashcode']}"
                                   xp:name="alef_html" xp:description=""
                                   xp:fieldtype="html"
                                   src="../../../{front_objcontent_text_resp['relative_path']}"/>
                        {all_pop_ups_xml}
                    </alef_tooltip>
                    """
            else:
                front_objcontent_text_xml = ""

            if "img" in front_obj:
                front_objimg = front_obj['img']
                front_objimg_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][front_objimg]
                front_objimg_src_resp = copy_to_hashcode_dir(src_path=front_objimg_src, exiting_hashcode=exiting_hashcode)
                all_files.add(front_objimg_src_resp['relative_path'])
                exiting_hashcode.add(front_objimg_src_resp['hashcode'])

                front_objimg_src_xml = f"""
                <alef_image xlink:label="{front_objimg_src_resp['hashcode']}"
                                        xp:name="alef_image" xp:description=""
                                        xp:fieldtype="image" alt="" customAlign="Center">
                    <xp:img href="../../../{front_objimg_src_resp['relative_path']}"
                            width="304" height="200"/>
                </alef_image>
                """
            else:
                front_objimg_src_xml = ""

            if "audio" in front_obj:
                front_objaudio = front_obj['audio']
                front_objaudio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][front_objaudio]
                front_objaudio_src_resp = copy_to_hashcode_dir(src_path=front_objaudio_src,
                                                             exiting_hashcode=exiting_hashcode)
                all_files.add(front_objaudio_src_resp['relative_path'])
                exiting_hashcode.add(front_objaudio_src_resp['hashcode'])

                front_objaudio_src_xml = f"""
                <alef_audionew xlink:label="{temp3[2]}"
                                           xp:name="alef_audionew" xp:description=""
                                           xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{front_objaudio_src_resp['hashcode']}"
                                    xp:name="alef_audiofile" xp:description=""
                                    audiocontrols="No" xp:fieldtype="file"
                                    src="../../../{front_objaudio_src_resp['relative_path']}"/>
                </alef_audionew>
                """
            else:
                front_objaudio_src_xml = ""

            back_obj = each_card_obj['deck'].get('back', None)
            if "content" in back_obj:
                back_objcontent = back_obj['content']
                back_objcontent_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][back_objcontent]

                back_objcontent_text_resp = write_html(text=back_objcontent_text, exiting_hashcode=exiting_hashcode)
                all_files.add(back_objcontent_text_resp['relative_path'])
                exiting_hashcode.add(back_objcontent_text_resp['hashcode'])

                back_objcontent_text_xml = f"""
                <alef_html xlink:label="{back_objcontent_text_resp['hashcode']}"
                                       xp:name="alef_html" xp:description=""
                                       xp:fieldtype="html"
                                       src="../../../{back_objcontent_text_resp['relative_path']}"/>
                """

                # get span info
                span_info = extract_span_info(text=back_objcontent_text)
                if isinstance(span_info, str):

                    back_objcontent_text_resp = write_html(text=back_objcontent_text,
                                                            exiting_hashcode=exiting_hashcode)
                    all_files.add(back_objcontent_text_resp['relative_path'])
                    exiting_hashcode.add(back_objcontent_text_resp['hashcode'])

                    front_objcontent_text_xml = f"""
                                    <alef_html xlink:label="{back_objcontent_text_resp['hashcode']}"
                                                           xp:name="alef_html" xp:description=""
                                                           xp:fieldtype="html"
                                                           src="../../../{back_objcontent_text_resp['relative_path']}"/>
                                    """
                else:

                    html_text = text_en_html_to_html_text(html_string=back_objcontent_text)

                    back_objcontent_text_resp = write_html(text=html_text,
                                                            exiting_hashcode=exiting_hashcode)
                    all_files.add(back_objcontent_text_resp['relative_path'])
                    exiting_hashcode.add(back_objcontent_text_resp['hashcode'])

                    # span_info
                    all_pop_ups = []
                    for span_content, span_attr_obj in span_info.items():

                        temp2 = []
                        for _ in range(4):
                            hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L",
                                                                         k=27)
                            exiting_hashcode.add(hashcode_temp2)
                            temp2.append(hashcode_temp2)

                        data_ref = span_attr_obj["data-ref"]
                        if data_ref is None:
                            continue
                        deck_oj = input_other_jsons_data["INPUT_COMMON_GLOSSARY_JSON_DATA"]["glossaryData"][data_ref][
                            "deck"]

                        front_img = deck_oj['front']['img']
                        front_img_path = input_other_jsons_data["INPUT_COMMON_GLOSSARY_IMAGES_DATA"][front_img]
                        front_img_path_resp = copy_to_hashcode_dir(src_path=front_img_path,
                                                                   exiting_hashcode=exiting_hashcode)
                        all_files.add(front_img_path_resp['relative_path'])
                        exiting_hashcode.add(front_img_path_resp['hashcode'])

                        all_pop_ups.append(
                            f"""
                                            <alef_popupvalue xlink:label="{temp2[1]}"
                                                             xp:name="alef_popupvalue" xp:description=""
                                                             xp:fieldtype="folder">
                                                <alef_section_general
                                                        xlink:label="{temp2[2]}"
                                                        xp:name="alef_section_general" xp:description=""
                                                        xp:fieldtype="folder">
                                                    <alef_column
                                                            xlink:label="{temp2[3]}"
                                                            xp:name="alef_column" xp:description=""
                                                            xp:fieldtype="folder" width="auto">
                                                        <alef_image xlink:label="{front_img_path_resp['hashcode']}"
                                                            xp:name="alef_image" xp:description=""
                                                            xp:fieldtype="image" alt="" customAlign="Center">
                                                            <xp:img href="../../../{front_img_path_resp['relative_path']}"
                                                            width="304" height="200"/>
                                                        </alef_image>
                                                    </alef_column>
                                                </alef_section_general>
                                            </alef_popupvalue>
                                            """
                        )

                    all_pop_ups_xml = "\n".join(all_pop_ups)
                    back_objcontent_text_xml = f"""
                                    <alef_tooltip xlink:label="{temp[11]}"
                                                  xp:name="alef_tooltip" xp:description=""
                                                  xp:fieldtype="folder">
                                        <alef_html xlink:label="{back_objcontent_text_resp['hashcode']}"
                                                   xp:name="alef_html" xp:description=""
                                                   xp:fieldtype="html"
                                                   src="../../../{back_objcontent_text_resp['relative_path']}"/>
                                        {all_pop_ups_xml}
                                    </alef_tooltip>
                                    """

            else:
                back_objcontent_text_xml = ""

            if "img" in back_obj:
                back_objimg = back_obj['img']
                back_objimg_src = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][back_objimg]
                back_objimg_src_resp = copy_to_hashcode_dir(src_path=back_objimg_src, exiting_hashcode=exiting_hashcode)
                all_files.add(back_objimg_src_resp['relative_path'])
                exiting_hashcode.add(back_objimg_src_resp['hashcode'])

                back_objimg_src_xml = f"""
                                <alef_image xlink:label="{back_objimg_src_resp['hashcode']}"
                                                        xp:name="alef_image" xp:description=""
                                                        xp:fieldtype="image" alt="" customAlign="Center">
                                    <xp:img href="../../../{back_objimg_src_resp['relative_path']}"
                                            width="304" height="200"/>
                                </alef_image>
                                """
            else:
                back_objimg_src_xml = ""

            if "audio" in back_obj:
                back_objaudio = back_obj['audio']
                back_objaudio_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][back_objaudio]

                back_objaudio_src_resp = copy_to_hashcode_dir(src_path=back_objaudio_src,
                                                               exiting_hashcode=exiting_hashcode)
                all_files.add(back_objaudio_src_resp['relative_path'])
                exiting_hashcode.add(back_objaudio_src_resp['hashcode'])

                back_objaudio_src_xml = f"""
                                <alef_audionew xlink:label="{temp3[3]}"
                                                           xp:name="alef_audionew" xp:description=""
                                                           xp:fieldtype="folder">
                                    <alef_audiofile xlink:label="{back_objaudio_src_resp['hashcode']}"
                                                    xp:name="alef_audiofile" xp:description=""
                                                    audiocontrols="No" xp:fieldtype="file"
                                                    src="../../../{back_objaudio_src_resp['relative_path']}"/>
                                </alef_audionew>
                                """
            else:
                back_objaudio_src_xml = ""

            all_tags.append(
                f"""
                <alef_flipcard xlink:label="{temp3[4]}"
                       xp:name="alef_flipcard" xp:description=""
                       xp:fieldtype="folder" centered="true">
                    <alef_section xlink:label="{temp3[5]}"
                                  xp:name="alef_section" xp:description=""
                                  xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp3[6]}"
                                     xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            {front_objcontent_text_xml}
                            {front_objimg_src_xml}
                            {front_objaudio_src_xml}
                        </alef_column>
                    </alef_section>
                    <alef_section xlink:label="{temp3[7]}"
                                  xp:name="alef_section" xp:description=""
                                  xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp3[8]}"
                                     xp:name="alef_column" xp:description=""
                                     xp:fieldtype="folder" width="auto" cellspan="1">
                            {back_objcontent_text_xml}
                            {back_objimg_src_xml}
                            {back_objaudio_src_xml}
                        </alef_column>
                    </alef_section>
                </alef_flipcard>
                """
            )
    else:
        print("container Is not provided")

    all_tags.append(
        """
                </alef_flipcards>
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