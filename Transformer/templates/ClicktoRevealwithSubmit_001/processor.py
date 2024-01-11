from Transformer.helpers import generate_unique_folder_name
from django.conf import settings
import os, shutil


def write_html(text, destination_file_path):
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


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = [
        """
        <!-- ClicktoRevealwithSubmit_001 -->

        """
    ]
    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    text_en_id = input_json_data['pageData']['args']['ques']
    submitCount = input_json_data['pageData']['args']['submitCount']
    # multiAnswer = input_json_data['pageData']['args']['multiAnswer']
    thumbs = input_json_data['pageData']['args']['thumbs']
    nofcolumns = len(thumbs)

    text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][text_en_id]
    destination_file_path = os.path.join(settings.OUTPUT_DIR, hashcode, "emptyHtmlModel.html")
    html_file_path = str(os.path.join(hashcode, "emptyHtmlModel.html"))

    # Create the unique folder if it doesn't exist
    relative_file = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_file)

    # create folder
    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    write_html(text=text_en_data, destination_file_path=destination_file_path)
    all_tags = [f"""
        <alef_section xlink:label="LAP7NYP2JN6KE5KGPUQIKOYLTA4" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="LJWIBTGLBLI4EPEFWZLGS3A6FSQ" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
        <alef_multiplechoice xlink:label="LOVEQZON5YZEEFMM4JTJKJVPHI4" xp:name="alef_multiplechoice" xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button" mcq_type="Image Only" questionfullwidth="false" questiontitle=" " questionnumber="1" nofcolumns="{nofcolumns}" submitattempts="{submitCount}" showtitle="true" alignstatement="left" showbackground="true" shuffleoptions="false" validation="Yes">
            <alef_questionstatement xlink:label="LEDRZJ2QUU62UDEKOZUCSLAZRGE" xp:name="alef_questionstatement" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="LO7IEOFM6KYTEVLZGBKB6IKW7U4" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="LLCUDPN4QIAWUJJSFHBNTPTXYME" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                        <alef_html xlink:label="{hashcode}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        """]

    # choices
    for each_thumb in thumbs:

        en_title = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][each_thumb['title']]
        image_thumb_relative_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][each_thumb['image']]

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

        temp = []
        for _ in range(4):
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp.append(hashcode)

        all_tags.append(f"""
                        <alef_choice xlink:label="{temp[0]}" xp:name="alef_choice" xp:description="" xp:fieldtype="folder" isCorrect="{isCorrect}" label="{en_title}">
                            <alef_choicevalue xlink:label="{temp[1]}" xp:name="alef_choicevalue" xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_image xlink:label="{image_thumb_hashcode}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                                            <xp:img href="../../../{image_relative_path}" width="765" height="890" />
                                        </alef_image>
                                    </alef_column>
                                </alef_section_general>
                            </alef_choicevalue>
                        </alef_choice>
                    """)

    feedback = input_json_data['pageData']['args']['feedback']
    feedback_added = set()
    for key, val in feedback.items():
        if key in feedback_added:
            continue

        temp = []
        for _ in range(4):
            # Generate a unique folder name for each file
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp.append(hashcode)

        if "correct" == key:
            text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][val]
            destination_file_path = os.path.join(settings.OUTPUT_DIR, temp[0], "emptyHtmlModel.html")
            html_file_path = str(os.path.join(temp[0], "emptyHtmlModel.html"))

            # Create the unique folder if it doesn't exist
            relative_file = os.path.join(temp[0], "emptyHtmlModel.html")
            all_files.add(relative_file)

            # create folder
            path_to_hashcode = os.path.join(settings.OUTPUT_DIR, temp[0])
            os.makedirs(path_to_hashcode, exist_ok=True)

            write_html(text=text_en_data, destination_file_path=destination_file_path)
            all_tags.append(f"""
                    <alef_correctfeedback xlink:label="{temp[1]}" xp:name="alef_correctfeedback" xp:description="" xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                <alef_html xlink:label="{temp[0]}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                            </alef_column>
                        </alef_section_general>
                    </alef_correctfeedback>
                """)

        if "incorrect_2" in key:
            text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][val]
            destination_file_path = os.path.join(settings.OUTPUT_DIR, temp[0], "emptyHtmlModel.html")
            html_file_path = str(os.path.join(temp[0], "emptyHtmlModel.html"))

            # Create the unique folder if it doesn't exist
            relative_file = os.path.join(temp[0], "emptyHtmlModel.html")
            all_files.add(relative_file)

            # create folder
            path_to_hashcode = os.path.join(settings.OUTPUT_DIR, temp[0])
            os.makedirs(path_to_hashcode, exist_ok=True)

            write_html(text=text_en_data, destination_file_path=destination_file_path)
            all_tags.append(f"""
                <alef_incorrectfeedback xlink:label="{temp[1]}" xp:name="alef_incorrectfeedback" xp:description="" xp:fieldtype="folder">
                    <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                        <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                            <alef_html xlink:label="{temp[0]}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                        </alef_column>
                    </alef_section_general>
                </alef_incorrectfeedback>
                """)

        if "incorrect_1" in key:
            text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][val]
            destination_file_path = os.path.join(settings.OUTPUT_DIR, temp[0], "emptyHtmlModel.html")
            html_file_path = str(os.path.join(temp[0], "emptyHtmlModel.html"))

            # Create the unique folder if it doesn't exist
            relative_file = os.path.join(temp[0], "emptyHtmlModel.html")
            all_files.add(relative_file)

            # create folder
            path_to_hashcode = os.path.join(settings.OUTPUT_DIR, temp[0])
            os.makedirs(path_to_hashcode, exist_ok=True)

            write_html(text=text_en_data, destination_file_path=destination_file_path)
            all_tags.append(f"""
                <alef_partialfeedback xlink:label="{temp[1]}" xp:name="alef_partialfeedback" xp:description="" xp:fieldtype="folder">
                    <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                        <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                            <alef_html xlink:label="{temp[0]}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                        </alef_column>
                    </alef_section_general>
                </alef_partialfeedback>
                """)

        feedback_added.add(key)

    hint = input_json_data['pageData']['args']['hint']
    hint_added = set()
    for key, val in hint.items():
        if key in hint_added:
            continue

        temp = []
        for _ in range(4):
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp.append(hashcode)

        if "text" in key:
            text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][val]
            destination_file_path = os.path.join(settings.OUTPUT_DIR, temp[0], "emptyHtmlModel.html")
            html_file_path = str(os.path.join(temp[0], "emptyHtmlModel.html"))

            # Create the unique folder if it doesn't exist
            relative_file = os.path.join(temp[0], "emptyHtmlModel.html")
            all_files.add(relative_file)

            # create folder
            path_to_hashcode = os.path.join(settings.OUTPUT_DIR, temp[0])
            os.makedirs(path_to_hashcode, exist_ok=True)

            write_html(text=text_en_data, destination_file_path=destination_file_path)
            all_tags.append(f"""
            <alef_hint xlink:label="{temp[1]}" xp:name="alef_hint" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                        <alef_html xlink:label="{temp[0]}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{html_file_path}" />
                    </alef_column>
                </alef_section_general>
            </alef_hint>
            """)
        hint_added.add(key)

    all_tags.append("""</alef_multiplechoice>""")

    feedBackAudio = input_json_data['pageData']['args']['feedBackAudio']

    ### Adding correct audio
    for key, val in feedBackAudio.items():

        temp = []
        for _ in range(4):
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

    all_tags.append(
        """
        </alef_column>
        </alef_section>
        """,

    )

    response = {
        "XML_STRING": "".join(all_tags),
        "GENERATED_HASH_CODES":exiting_hashcode,
        "MANIFEST_FILES":all_files
    }

    return response


def process_page_data(page_data, other_json_data, exiting_hashcode):
    # Custom processing for ClicktoRevealwithSubmit_001
    # Use page_data as needed

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    return xml_output
