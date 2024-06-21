from Transformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh, transcript_generator, remove_html_tags,
                                 text_en_html_to_html_text, text_en_html_to_html_text_v1,
                                 get_popup_mlo_from_text, convert_html_to_strong)
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
    all_files = set()
    all_tags = [
        """
        <!-- Thumbnail_TextImage_001 -->
        """
    ]

    thumbnails_list = input_json_data["pageData"]["args"].get("thumbnails", [])

    for idx, thumbnail in enumerate(thumbnails_list):
        idx = idx + 1

        try:
            # Assuming input_other_jsons_data and input_json_data are properly defined

            # Extract ELA_DF and drop rows where 'left' is NaN
            ELA_DF = input_other_jsons_data.get("ELA_TEXTBOX_POSITIONS")
            ELA_DF = ELA_DF.dropna(subset=['left'])

            # Extract necessary values
            screen_number = input_json_data['screen_number']
            COURSE_ID = input_other_jsons_data['COURSE_ID']

            # Filter ELA_DF based on conditions
            ELA_DF = ELA_DF[
                (ELA_DF["TopicID"] == COURSE_ID) &
                (ELA_DF["Screen#"] == screen_number)
                ]

            # Ensure there's at least one row matching the conditions
            if not ELA_DF.empty:
                ELA_DF_DICT = ELA_DF.iloc[0].to_dict()  # Take the first row
                top = int(float(ELA_DF_DICT['top']))
                bottom = int(float(ELA_DF_DICT['bottom']))
                left = int(float(ELA_DF_DICT['left']))
                right = int(float(ELA_DF_DICT['right']))
                print(f"Got positions: left: {left}, right: {right}, top: {top}, bottom: {bottom}")
            else:
                # Handle case where no rows match the conditions
                top = 118
                bottom = 668
                left = 30
                right = 1121

        except Exception as e:
            print(f"Warning: {e}")
            # Assign default values
            top = 118
            bottom = 668
            left = 30
            right = 1121

        temp = []
        for _ in range(10):
            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp)
            temp.append(hashcode_temp)

        target_link = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(target_link)
        temp.append(target_link)

        try:
            col_list = thumbnail.get("col")
            col_obj = col_list[0][0]

            title = col_obj.get("title")
            audioData = col_obj.get("audioData")

            try:
                backgroundImageId = col_obj.get("backgroundImage")

                ImgSrc = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][backgroundImageId]
                imgfile_resp = copy_to_hashcode_dir(src_path=ImgSrc, exiting_hashcode=exiting_hashcode)
                all_files.add(imgfile_resp['relative_path'])
                exiting_hashcode.add(imgfile_resp['hashcode'])

                img_tag = f"""
                <alef_image xlink:label="{imgfile_resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../{imgfile_resp['relative_path']}" width="1920" height="1080">
                    	<maplink xlink:name="New Link" name="New Link" type="internal" targetid="LW66C5DAG67JEJBGMYQPVBXIG7A" ShowMode="" left="{left}" right="{right}" top="{top}" bottom="{bottom}" />
                    </xp:img>
                </alef_image>
                """
            except Exception as e:
                img_tag = ""
                print(f"Warning: {e}")

            try:
                textAreaTextId = col_obj.get("text")
                textAreaText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][textAreaTextId]

                if audioData:
                    transcript_resp = transcript_generator(
                        html_string=textAreaText,
                        audio_transcript=audioData
                    )
                else:
                    transcript_resp = {"text": textAreaText, "transcript":[]}

                # textAreaMergeHtmlText = text_en_html_to_html_text_v1(html_string=textAreaText)
                textAreaMergeHtmlText = remove_html_tags(textAreaText)
                # textAreaMergeHtmlText = textAreaText.replace("toolKit", "jsx_tooltip")
                resp = write_html(
                    text=textAreaMergeHtmlText,
                    exiting_hashcode=exiting_hashcode,
                    align=None
                )
                all_files.add(resp['relative_path'])
                exiting_hashcode.add(resp['hashcode'])

                if "data-ref" in textAreaText:
                    popup_response = get_popup_mlo_from_text(
                        text=textAreaText,
                        input_other_jsons_data=input_other_jsons_data,
                        all_files=all_files,
                        exiting_hashcode=exiting_hashcode,
                        enable_question_statement=False
                    )

                    if popup_response:
                        all_files = popup_response['all_files']
                        exiting_hashcode = popup_response['exiting_hashcode']
                        # popup = "\n".join(popup_response['all_tags'])
                        textAreaHtml = ""
                        for each_popup in popup_response['all_tags']:
                            textAreaHtml = f"""
                            <alef_tooltip xlink:label="{temp[0]}" xp:name="alef_tooltip" xp:description="" xp:fieldtype="folder">
                                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                                {each_popup}
                            </alef_tooltip>
                            """

                        img_tag = img_tag.replace("LW66C5DAG67JEJBGMYQPVBXIG7A", temp[0])
                    else:
                        textAreaHtml = f"""
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                        """
                        img_tag = img_tag.replace("LW66C5DAG67JEJBGMYQPVBXIG7A", resp['hashcode'])

                else:
                    textAreaHtml = f"""
                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                    """
                    img_tag = img_tag.replace("LW66C5DAG67JEJBGMYQPVBXIG7A", resp['hashcode'])

            except Exception as e:
                transcript_resp = {"text": "", "transcript": []}
                textAreaHtml = ""
                print(f"Warning: {e}")

            ########
            # Audio File
            ########
            try:
                textAreaAudioId = col_obj.get("audio")

                textAreaAudioIdSrc = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][textAreaAudioId]
                audiofile_resp = copy_to_hashcode_dir(src_path=textAreaAudioIdSrc,
                                                      exiting_hashcode=exiting_hashcode)
                all_files.add(audiofile_resp['relative_path'])
                exiting_hashcode.add(audiofile_resp['hashcode'])

                if transcript_resp["transcript"]:
                    audio_tag = f"""
                    <alef_audionew xlink:label="{temp[1]}" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                        <alef_audiofile xlink:label="{audiofile_resp['hashcode']}" xp:name="alef_audiofile" xp:description="" audiocontrols="No" xp:fieldtype="file" src="../../../{audiofile_resp['relative_path']}" />
                        <alef_audiotranscript xlink:label="{temp[2]}" xp:name="alef_audiotranscript" xp:description="" xp:fieldtype="text">{transcript_resp["transcript"]}</alef_audiotranscript>
                    </alef_audionew>
                    """
                else:
                    audio_tag = f"""
                    <alef_audionew xlink:label="{temp[1]}" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                        <alef_audiofile xlink:label="{audiofile_resp['hashcode']}" xp:name="alef_audiofile" xp:description="" audiocontrols="Yes" xp:fieldtype="file" src="../../../{audiofile_resp['relative_path']}" />
                    </alef_audionew>
                    """

            except Exception as e:
                print(f"Error: {e}")
                audio_tag = ""

            all_tags.append(
                f"""
                <alef_section xlink:label="{temp[3]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp[4]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_reader xlink:label="{temp[5]}" xp:name="alef_reader" xp:description="" xp:fieldtype="folder" has_reader="Yes" is_bordered="No">
                            {img_tag}
                            {audio_tag}
                            {textAreaHtml}
                        </alef_reader>
                    </alef_column>
                </alef_section>
                """
            )

        except Exception as e:
            print(f"Warning: {e}")

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
