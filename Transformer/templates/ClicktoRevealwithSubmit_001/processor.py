from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong,
                                 remove_html_tags, mathml2latex_yarosh, get_teacher_note)
from django.conf import settings
import os, shutil


def write_html(text, destination_file_path):
    try:
        from Transformer.helpers import assing_class_for_color
        text = assing_class_for_color(text)
    except:
        pass
    text = convert_html_to_strong(html_str=text)

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

    with open(destination_file_path, "w") as file:
        file.write(template.strip())


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


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    STATUS = []
    all_tags = [
        """
        <!-- ClicktoRevealwithSubmit_001 -->

        """
    ]
    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    try:
        text_en_id = input_json_data['pageData']['args']['ques']

    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)

    try:
        submitCount = input_json_data['pageData']['args']['submitCount']
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)

    # multiAnswer = input_json_data['pageData']['args']['multiAnswer']
    try:
        thumbs = input_json_data['pageData']['args']['thumbs']
        nofcolumns = len(thumbs)
    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)

    try:
        text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][text_en_id]

        if "<math" in text_en_data:
            text_en_data = mathml2latex_yarosh(html_string=text_en_data)

    except Exception as e:
        msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
        STATUS.append(msg)
        raise Exception(msg)

    try:
        teachers_note_xml = ""
        teacher_resp = get_teacher_note(
            text=text_en_data, all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            input_other_jsons_data=input_other_jsons_data
        )

        if teacher_resp:
            text_en_data = teacher_resp["remaining_text"]
            teachers_note_xml = teacher_resp["teachers_note_xml"]
            exiting_hashcode.update(teacher_resp["exiting_hashcode"])
            all_files.update(teacher_resp["all_files"])

    except Exception as e:
        teachers_note_xml = ""
        print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

    destination_file_path = os.path.join(settings.OUTPUT_DIR, hashcode, "emptyHtmlModel.html")
    html_file_path = str(os.path.join(hashcode, "emptyHtmlModel.html"))

    # Create the unique folder if it doesn't exist
    relative_file = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_file)

    # create folder
    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    write_html(text=text_en_data, destination_file_path=destination_file_path)

    temp = []
    for _ in range(10):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags = all_tags + [f"""
        <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
        <alef_multiplechoice xlink:label="{temp[2]}" xp:name="alef_multiplechoice" xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button" mcq_type="Image Only" questionfullwidth="false" questiontitle=" " questionnumber="1" nofcolumns="{nofcolumns}" submitattempts="{submitCount}" showtitle="true" alignstatement="left" showbackground="true" shuffleoptions="false" validation="Yes">
            <alef_questionstatement xlink:label="{temp[3]}" xp:name="alef_questionstatement" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp[4]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                        <alef_html xlink:label="{hashcode}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                        {teachers_note_xml}
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        """]

    # choices
    for each_thumb in thumbs:
        try:
            en_title = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][each_thumb['title']]
            if "<math" in en_title:
                en_title = mathml2latex_yarosh(html_string=en_title)
            else:
                en_title = remove_html_tags(en_title)
        except:
            en_title = ""
            print('Error: ClicktoRevealwithSubmit_001 --> title not found')
            # raise Exception('Error: ClicktoRevealwithSubmit_001 --> title not found')

        try:
            image_thumb_relative_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][each_thumb['image']]
        except Exception as e:
            msg = f'Error: {input_json_data["pageData"]["templateID"]} --> {e}'
            STATUS.append(msg)
            raise Exception(msg)

        image_thumb_hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(image_thumb_hashcode)
        image_thumb_destination_file_path = str(os.path.join(settings.OUTPUT_DIR, image_thumb_hashcode, os.path.basename(image_thumb_relative_path)))

        image_relative_path = str(os.path.join(image_thumb_hashcode, os.path.basename(image_thumb_relative_path)))
        image_thumb_src_file_path = str(os.path.join(settings.INPUT_APP_DIR, image_thumb_relative_path))

        # Create the unique folder if it doesn't exist
        relative_file = os.path.join(image_thumb_hashcode, os.path.basename(image_thumb_relative_path))
        all_files.add(relative_file)

        # create folder
        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, image_thumb_hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        shutil.copy2(image_thumb_src_file_path, image_thumb_destination_file_path)

        if int(each_thumb['ans']):
            isCorrect = "Yes"
        else:
            isCorrect = "No"

        temp1 = []
        for _ in range(4):
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp1.append(hashcode)

        all_tags.append(f"""
                        <alef_choice xlink:label="{temp1[0]}" xp:name="alef_choice" xp:description="" xp:fieldtype="folder" isCorrect="{isCorrect}" label="{en_title}">
                            <alef_choicevalue xlink:label="{temp1[1]}" xp:name="alef_choicevalue" xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp1[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp1[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_image xlink:label="{image_thumb_hashcode}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                                            <xp:img href="../../../{image_relative_path}" width="765" height="890" />
                                        </alef_image>
                                    </alef_column>
                                </alef_section_general>
                            </alef_choicevalue>
                        </alef_choice>
                    """)

    from Transformer.helpers import get_xml_feedback, get_xml_hint
    try:
        feedback = input_json_data["pageData"]["args"].get("feedback", None)
        # get feedback xml
        feedback_resp = get_xml_feedback(
            feedback=feedback,
            exiting_hashcode=exiting_hashcode,
            all_files=all_files,
            input_other_jsons_data=input_other_jsons_data
        )
        all_tags.append(feedback_resp["XML_STRING"])
        exiting_hashcode.add(feedback_resp["GENERATED_HASH_CODES"])
        all_files.add(feedback_resp["MANIFEST_FILES"])
    except:
        pass

    try:
        hint = input_json_data["pageData"]["args"].get("hint", None)
        # get feedback xml
        hint_resp = get_xml_hint(
            hint=hint,
            exiting_hashcode=exiting_hashcode,
            all_files=all_files,
            input_other_jsons_data=input_other_jsons_data
        )
        all_tags.append(hint_resp["XML_STRING"])
        exiting_hashcode.add(hint_resp["GENERATED_HASH_CODES"])
        all_files.add(hint_resp["MANIFEST_FILES"])
    except:
        pass

    all_tags.append("""</alef_multiplechoice>""")

    try:
        feedBackAudio = input_json_data['pageData']['args']['feedBackAudio']

        ### Adding correct audio
        for key, val in feedBackAudio.items():

            temp = []
            for _ in range(5):
                hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(hashcode)
                temp.append(hashcode)

            if "correct" == key:

                audio_thumb_relative_path = input_other_jsons_data["INPUT_AUDIO_JSON_DATA"][val]

                audio_thumb_hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
                exiting_hashcode.add(audio_thumb_hashcode)
                audio_thumb_destination_file_path = str(
                    os.path.join(settings.OUTPUT_DIR, audio_thumb_hashcode, os.path.basename(audio_thumb_relative_path)))
                audio_relative_path = str(os.path.join(audio_thumb_hashcode, os.path.basename(audio_thumb_relative_path)))
                audio_thumb_src_file_path = str(os.path.join(settings.INPUT_APP_DIR, audio_thumb_relative_path))

                # Create the unique folder if it doesn't exist
                relative_file = os.path.join(audio_thumb_hashcode, os.path.basename(audio_thumb_relative_path))
                all_files.add(relative_file)

                # create folder
                path_to_hashcode = os.path.join(settings.OUTPUT_DIR, audio_thumb_hashcode)
                os.makedirs(path_to_hashcode, exist_ok=True)

                shutil.copy2(audio_thumb_src_file_path, audio_thumb_destination_file_path)

                all_tags.append(
                    f"""
                        <alef_audionew xlink:label="{temp[0]}" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{audio_thumb_hashcode}" xp:name="alef_audiofile" xp:description="" audiocontrols="Yes" xp:fieldtype="file" src="../../../{audio_relative_path}" />
                        </alef_audionew>
                        """
                )
                break
    except:
        print('warning: ClicktoRevealwithSubmit_001 --> feedbackAudio not found')


    try:
        temp = []
        for _ in range(2):
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp.append(hashcode)

        aud_id = input_json_data['pageData']['args']['src']
        src_audio_path = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][aud_id]

        resp = copy_to_hashcode_dir(
            src_path=src_audio_path,
            exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])

        all_tags.append(
            f"""
                <alef_audionew xlink:label="{temp[0]}" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile" xp:description="" audiocontrols="Yes" xp:fieldtype="file" src="../../../{resp['relative_path']}" />
                </alef_audionew>
                """
        )
    except:
        print('warning: ClicktoRevealwithSubmit_001 --> src audio not found')

    all_tags.append(
        """
        </alef_column>
        </alef_section>
        """,

    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES":exiting_hashcode,
        "MANIFEST_FILES":all_files,
        "STATUS": STATUS
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
