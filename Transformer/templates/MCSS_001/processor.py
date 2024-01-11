from Transformer.helpers import generate_unique_folder_name
from django.conf import settings
import os, shutil
import htmlentities


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
        <!-- MCSS_001 -->

        """
    ]
    # Extracting variables
    ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    # submit = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["submit"]]
    # showAnswer = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"].get("showAnswer", None)]
    submitCount = input_json_data["pageData"]["args"]["submitCount"]
    # rightContainer = input_json_data["pageData"]["args"].get("rightContainer", None)
    feedback = input_json_data["pageData"]["args"].get("feedback", None)
    # hint = input_json_data["pageData"]["args"].get("hint", None)
    options = input_json_data["pageData"]["args"].get("options", None)

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
    write_html(text=ques, destination_file_path=path_to_html)

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_path)

    hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode1)
    hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode2)
    hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode3)
    hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode4)
    hashcode5 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode5)
    hashcode6 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode6)

    all_tags.append(
        f"""
                <alef_section xlink:label="{hashcode1}" xp:name="alef_section" xp:description=""
                              xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{hashcode2}" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_multiplechoice xlink:label="{hashcode3}" xp:name="alef_multiplechoice"
                                             xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button"
                                             questionfullwidth="false" questiontitle=" " questionnumber=" "
                                             nofcolumns="2" submitattempts="{submitCount}" showtitle="false"
                                             alignstatement="center" showbackground="false" shuffleoptions="true"
                                             validation="Yes">
                            <alef_questionstatement xlink:label="{hashcode4}"
                                                    xp:name="alef_questionstatement" xp:description=""
                                                    xp:fieldtype="folder">
                                <alef_section_general xlink:label="{hashcode5}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{hashcode6}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{relative_path}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_questionstatement>
        """
    )

    for each_op in options:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_op['text']]

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
        write_html(text=text, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        is_correct = "Yes" if each_op['ans'] == 1 else "No"

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)
        hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode2)
        hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode3)
        hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode4)

        all_tags.append(
            f"""
                            <alef_choice xlink:label="{hashcode1}" xp:name="alef_choice"
                                         xp:description="" xp:fieldtype="folder" isCorrect="{is_correct}" label=" ">
                                <alef_choicevalue xlink:label="{hashcode2}"
                                                  xp:name="alef_choicevalue" xp:description=""
                                                  xp:fieldtype="folder">
                                    <alef_section_general xlink:label="{hashcode3}"
                                                          xp:name="alef_section_general" xp:description=""
                                                          xp:fieldtype="folder">
                                        <alef_column xlink:label="{hashcode4}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto">
                                            <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                       xp:description="" xp:fieldtype="html"
                                                       src="../../../{relative_path}"/>
                                        </alef_column>
                                    </alef_section_general>
                                </alef_choicevalue>
                            </alef_choice>
            """
        )
    count = 1
    for key, val in feedback.items():
        if count > 2:
            break
        main_key = key.split("_")[0]

        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
        write_html(text=text, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)
        hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode2)
        hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode3)

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
                                        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{relative_path}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_{main_key}feedback>
            """
        )
        count = count + 1

    try:
        image = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["image"]]
        resp = copy_to_hashcode_dir(src_path=image, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        all_tags.append(
            f"""
                                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                            xp:description="" xp:fieldtype="image" alt="">
                                    <xp:img href="../../../{resp['relative_path']}" width="301"
                                            height="155"/>
                                </alef_image>
            """
        )
    except Exception as e:
        print(f"image key is not present under args of (ignoring alef_image tag) MCSS_001: {e}")

    all_tags.append(
        """
        </alef_multiplechoice>
        """
    )

    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode1)

    all_tags.append(f"""
                        <alef_audionew xlink:label="{hashcode1}" xp:name="alef_audionew"
                                       xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                            xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                            src="../../../{resp['relative_path']}"/>
                        </alef_audionew>
    """)

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

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    return xml_output
