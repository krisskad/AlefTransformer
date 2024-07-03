from Transformer.helpers import (generate_unique_folder_name, get_xml_feedback,
                                 mathml2latex_yarosh, transcript_generator, get_xml_hint, get_teacher_note,
                                 text_en_html_to_html_text, remove_html_tags, text_en_html_to_html_text_v1,
                                 get_popup_mlo_from_text, convert_html_to_strong, replace_br_after_punctuation)
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
        <!-- TextArea_MCQ_001 -->
        """
    ]

    src = input_json_data["pageData"]["args"].get("src", None)
    textAreaData = input_json_data["pageData"]["args"].get("textAreaData", {})
    mcqData = input_json_data["pageData"]["args"].get("mcqData", {})

    textAreaAudioTranscriptObj = textAreaData.get("audioData")
    textAreaAudioId = textAreaData.get("audio")

    bookPopUpButton = input_json_data["pageData"]["args"].get("bookPopUpButton", "")
    hintEnable = input_json_data["pageData"]["args"].get("hintEnable", "")
    bookPageNumber = input_json_data["pageData"]["args"].get("bookPageNumber", "")
    reader = textAreaData.get("reader", "true")

    """
    MCQ Column
    """
    try:
        mcq_title_id = mcqData.get("title")

        mcq_title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][mcq_title_id]
        if mcq_title:
            mcq_title = remove_html_tags(text=mcq_title)
    except Exception as e:
        mcq_title = ""

    questions_list = mcqData.get("questions")
    for idx, each_mcq in enumerate(questions_list):
        idx = idx + 1
        temp = []
        for _ in range(15):
            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp)
            temp.append(hashcode_temp)

        mcq_submitCount = each_mcq.get("submitCount")

        """
        Text Area
        """
        textAreaTitleId = textAreaData.get("title")

        try:
            textAreaTitle = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][textAreaTitleId]

            if textAreaTitle:
                textAreaTitle = remove_html_tags(textAreaTitle)
            else:
                textAreaTitle = ""
        except Exception as e:
            textAreaTitle = ""

        try:
            textAreaTextId = textAreaData.get("text")
            textAreaText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][textAreaTextId]

            if str(reader) == "true" or textAreaAudioTranscriptObj:
                transcript_resp = transcript_generator(
                    html_string=textAreaText,
                    audio_transcript=textAreaAudioTranscriptObj
                )
            else:
                transcript_resp = {"text":textAreaText}

            textAreaText = text_en_html_to_html_text_v1(html_string=textAreaText)
            textAreaMergeHtmlText = text_en_html_to_html_text(textAreaText)

            try:
                teachers_note_xml = ""
                teacher_resp = get_teacher_note(
                    text=textAreaMergeHtmlText, all_files=all_files,
                    exiting_hashcode=exiting_hashcode,
                    input_other_jsons_data=input_other_jsons_data
                )

                if teacher_resp:
                    textAreaMergeHtmlText = teacher_resp["remaining_text"]
                    teachers_note_xml = teacher_resp["teachers_note_xml"]
                    exiting_hashcode.update(teacher_resp["exiting_hashcode"])
                    all_files.update(teacher_resp["all_files"])

            except Exception as e:
                teachers_note_xml = ""
                print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

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
                    popup = "\n".join(popup_response['all_tags'])

                    textAreaHtml = f"""
                    <alef_tooltip xlink:label="{temp[0]}" xp:name="alef_tooltip" xp:description="" xp:fieldtype="folder">
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                        {popup}
                    </alef_tooltip>
                    """
                else:
                    textAreaHtml = f"""
                                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                                    """

            else:
                textAreaHtml = f"""
                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                """

            ########
            # Audio File
            ########
            try:

                if textAreaAudioId:
                    textAreaAudioIdSrc = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][textAreaAudioId]
                    audiofile_resp = copy_to_hashcode_dir(src_path=textAreaAudioIdSrc, exiting_hashcode=exiting_hashcode)
                    all_files.add(audiofile_resp['relative_path'])
                    exiting_hashcode.add(audiofile_resp['hashcode'])

                    if str(reader) == "true":
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
                else:
                    audio_tag = ""

            except Exception as e:
                print(f"Error: {e}")
                audio_tag = ""

            """
            Text Area Column
            """
            textAreaSection = f"""
            <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1" hasHighlight="Yes" hasNotes="Yes">
                {textAreaHtml}
                {audio_tag}
            </alef_column>
            """
        except Exception as e:
            textAreaSection = ""
            print(f"Warning: {e}")

        try:
            try:
                mcq_ques_id = each_mcq.get("ques")
                mcq_ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][mcq_ques_id]

                if "<math" in mcq_ques:
                    mcq_ques = mathml2latex_yarosh(html_string=mcq_ques)

                mcq_ques_resp = write_html(
                    text=mcq_ques,
                    exiting_hashcode=exiting_hashcode,
                    align=None
                )
                all_files.add(mcq_ques_resp['relative_path'])
                exiting_hashcode.add(mcq_ques_resp['hashcode'])

                question_html = f"""
                <alef_column xlink:label="{temp[4]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="11" alignment="Left">
                    <alef_html xlink:label="{mcq_ques_resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{mcq_ques_resp['relative_path']}" />
                </alef_column>
                """

            except Exception as e:
                question_html = ""
                print(f"Warning: {e}")

            try:
                mcq_src_id = each_mcq.get("src")
                mcq_mcq_src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][mcq_src_id]
                mcq_audiofile_resp = copy_to_hashcode_dir(src_path=mcq_mcq_src, exiting_hashcode=exiting_hashcode)
                all_files.add(mcq_audiofile_resp['relative_path'])
                exiting_hashcode.add(mcq_audiofile_resp['hashcode'])

                question_audio_col = f"""
                <alef_column xlink:label="{temp[5]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="1" alignment="Center">
                    <alef_audionew xlink:label="{temp[6]}" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                        <alef_audiofile xlink:label="{mcq_audiofile_resp['hashcode']}" xp:name="alef_audiofile" xp:description="" audiocontrols="No" xp:fieldtype="file" src="../../../{mcq_audiofile_resp['relative_path']}" />
                    </alef_audionew>
                </alef_column>
                """

            except Exception as e:
                question_audio_col = ""
                print(f"Warning: {e}")

            question_statement = f"""
            <alef_questionstatement xlink:label="{temp[7]}" xp:name="alef_questionstatement" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp[8]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    {question_audio_col}
                    {question_html}
                </alef_section_general>
            </alef_questionstatement>
            """

        except Exception as e:
            question_statement = ""
            print(f"Error: {e}")

        try:
            mcq_image_id = each_mcq.get("image")
            mcq_mcq_img = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][mcq_image_id]
            mcq_imgfile_resp = copy_to_hashcode_dir(src_path=mcq_mcq_img, exiting_hashcode=exiting_hashcode)
            all_files.add(mcq_imgfile_resp['relative_path'])
            exiting_hashcode.add(mcq_imgfile_resp['hashcode'])

            question_img_tag = f"""
            <alef_image xlink:label="{mcq_imgfile_resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                <xp:img href="../../../{mcq_imgfile_resp['relative_path']}" width="210" height="260" />
            </alef_image>
            """
        except Exception as e:
            question_img_tag = ""
            print(f"Warning: {e}")

        try:
            options_list = each_mcq.get("options")
            options_list_xml = []
            for option in options_list:
                ans = option.get("ans")
                if str(ans) == str(1):
                    ans = "Yes"
                else:
                    ans = "No"

                ans_text_id = option.get("text")
                ans_text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][ans_text_id]

                if "<math" in ans_text:
                    ans_text = mathml2latex_yarosh(html_string=ans_text)

                ans_resp = write_html(
                    text=ans_text,
                    exiting_hashcode=exiting_hashcode,
                    align=None
                )
                all_files.add(ans_resp['relative_path'])
                exiting_hashcode.add(ans_resp['hashcode'])

                temp1 = []
                for _ in range(4):
                    hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                    exiting_hashcode.add(hashcode_temp)
                    temp1.append(hashcode_temp)

                options_list_xml.append(
                    f"""
                    <alef_choice xlink:label="{temp1[0]}" xp:name="alef_choice" xp:description="" xp:fieldtype="folder" isCorrect="{ans}" label=" ">
                        <alef_choicevalue xlink:label="{temp1[1]}" xp:name="alef_choicevalue" xp:description="" xp:fieldtype="folder">
                            <alef_section_general xlink:label="{temp1[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                                <alef_column xlink:label="{temp1[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                    <alef_html xlink:label="{ans_resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{ans_resp['relative_path']}" />
                                </alef_column>
                            </alef_section_general>
                        </alef_choicevalue>
                    </alef_choice>
                    """
                )

            xml_options = "\n".join(options_list_xml)
        except Exception as e:
            xml_options = ""
            print(f"Warning: {e}")

        try:
            feedback = each_mcq.get("feedback", None)
            # get feedback xml
            feedback_resp = get_xml_feedback(
                feedback=feedback,
                exiting_hashcode=exiting_hashcode,
                all_files=all_files,
                input_other_jsons_data=input_other_jsons_data
            )
            # all_tags.append(feedback_resp["XML_STRING"])
            exiting_hashcode.add(feedback_resp["GENERATED_HASH_CODES"])
            all_files.add(feedback_resp["MANIFEST_FILES"])
        except:
            feedback_resp = {"XML_STRING":""}

        if hintEnable == "true":
            try:
                hint = each_mcq.get("hint", None)
                # get feedback xml
                hint_resp = get_xml_hint(
                    hint=hint,
                    exiting_hashcode=exiting_hashcode,
                    all_files=all_files,
                    input_other_jsons_data=input_other_jsons_data
                )
                # all_tags.append(hint_resp["XML_STRING"])
                exiting_hashcode.add(hint_resp["GENERATED_HASH_CODES"])
                all_files.add(hint_resp["MANIFEST_FILES"])
            except:
                hint_resp = {"XML_STRING":""}
        else:
            hint_resp = {"XML_STRING": ""}

        try:
            questionNumber = each_mcq.get("questionNumber", "")
            if questionNumber:
                idx = questionNumber
        except:
            pass

        entire_xml_screen = f"""
        <alef_section xlink:label="{temp[9]}" xp:name="alef_section" xp:description="{textAreaTitle}" xp:fieldtype="folder" customclass="Wireframe- Box">
            {textAreaSection}
            <alef_column xlink:label="{temp[10]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                <alef_multiplechoice xlink:label="{temp[11]}" xp:name="alef_multiplechoice" xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button" questionfullwidth="false" questiontitle="{mcq_title}" questionnumber=" {idx}" nofcolumns="1" submitattempts="{mcq_submitCount}" showtitle="true" alignstatement="left" showbackground="true" shuffleoptions="true" validation="Yes">
                    {question_statement}
                    {xml_options}
                    {question_img_tag}
                    {feedback_resp["XML_STRING"]}
                    {hint_resp["XML_STRING"]}
                </alef_multiplechoice>
            </alef_column>
        </alef_section>
        """

        all_tags.append(entire_xml_screen)

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
