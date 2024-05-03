from Transformer.helpers import (generate_unique_folder_name, convert_html_to_strong, get_teacher_note,
                                 write_html_mlo, mathml2latex_yarosh)
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, destination_file_path):
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
    try:
        ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
    except:
        raise Exception("Error: MCSS_001 --> ques not found")

    try:
        teachers_note_xml = ""
        teacher_resp = get_teacher_note(
            text=ques, all_files=all_files,
            exiting_hashcode=exiting_hashcode,
            input_other_jsons_data=input_other_jsons_data
        )

        if teacher_resp:
            ques = teacher_resp["remaining_text"]
            teachers_note_xml = teacher_resp["teachers_note_xml"]
            exiting_hashcode.update(teacher_resp["exiting_hashcode"])
            all_files.update(teacher_resp["all_files"])

    except Exception as e:
        teachers_note_xml = ""
        print(f"Error: TextwithImage_001 --> While creating teachers note --> {e}")

    try:
        src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    except:
        raise Exception("Error: MCSS_001 --> src not found")

    image_check = input_json_data["pageData"]["args"].get("image", None)

    # submit = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["submit"]]
    # showAnswer = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"].get("showAnswer", None)]
    try:
        submitCount = input_json_data["pageData"]["args"]["submitCount"]
    except:
        submitCount = 3
        print("Error: MCSS_001 --> submitCount not found")

    # rightContainer = input_json_data["pageData"]["args"].get("rightContainer", None)
    feedback = input_json_data["pageData"]["args"].get("feedback", None)
    hint = input_json_data["pageData"]["args"].get("hint", None)
    options = input_json_data["pageData"]["args"].get("options", None)

    """
    :Number of column logic
    rightContainer = True (numberOfCol = 2) 
    rightContainer = False (numberOfCol = 1)
    
    If rightContainer key is not present in input then numberOfCol = 1, 
    If Image is present then its numberOfCol = 1
    """
    try:
        if "rightContainer" in input_json_data["pageData"]["args"]:
            rightContainer = input_json_data["pageData"]["args"]["rightContainer"]
            if rightContainer: # True
                nofcolumns = 2
            else:
                nofcolumns = 1
        else:
            nofcolumns = 1

        if image_check:
            nofcolumns = 1
    except Exception as e:
        print(f"Error in MCSS_001 While assigning number of columns for mcq options: --> {e} "
              f"[We are setting it number of column as 1]")
        nofcolumns = 1

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")

    if "<math" in ques:
        ques = mathml2latex_yarosh(html_string=ques)

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


    try:
        questionfullwidth = "false"
        image = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["image"]]
        resp = copy_to_hashcode_dir(src_path=image, exiting_hashcode=exiting_hashcode)
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        image_tag = f"""
            <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                        xp:description="" xp:fieldtype="image" alt="">
                <xp:img href="../../../{resp['relative_path']}" width="301"
                        height="155"/>
            </alef_image>
            """

    except Exception as e:
        questionfullwidth = "true"
        image_tag = ""
        # print(f"MCSS_001 : {e}")
        print("Warning: MCSS_001 --> image not found so setting up questionfullwidth = true")

    try:
        view_css = input_other_jsons_data['INPUT_VIEW_JSON_DATA']["pages"][input_json_data['pageData']["viewRef"]]["pageData"]["args"]["quesCss"]
        ques_align = view_css['textAlign']
        # ques_width = view_css['width']
    except Exception as e:
        ques_align = "left"
        # ques_width = "100%"
        print("Error: ", e)

    all_tags.append(
        f"""
                <alef_section xlink:label="{hashcode1}" xp:name="alef_section" xp:description=""
                              xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{hashcode2}" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_multiplechoice xlink:label="{hashcode3}" xp:name="alef_multiplechoice"
                                             xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button"
                                             questionfullwidth="{questionfullwidth}" questiontitle=" " questionnumber=" "
                                             nofcolumns="{nofcolumns}" submitattempts="{submitCount}" showtitle="false"
                                             alignstatement="{ques_align}" showbackground="false" shuffleoptions="true"
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
                                        {teachers_note_xml}
                                    </alef_column>
                                </alef_section_general>
                            </alef_questionstatement>
        """
    )

    for each_op in options:
        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_op['text']]
        except:
            print("Error: MCSS_001 --> text not found inside option")
            continue

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")

        if "<math" in text:
            text = mathml2latex_yarosh(html_string=text)

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
        # if count > 2:
        #     break
        main_key = key.split("_")[0]

        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
        except:
            print("Error: MCSS_001 --> text not found inside feedback")
            continue

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")

        try:
            from Transformer.helpers import remove_br, add_space_after_span
            text = remove_br(text)
            text = add_space_after_span(text)
        except Exception as e:
            pass

        write_html(text=text, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        hashcode1 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode1)
        hashcode2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode2)
        hashcode3 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode3)

        if "incorrect_1" in key:
            all_tags.append(
                f"""
                <alef_partialfeedback xlink:label="{hashcode1}"
                                      xp:name="alef_partialfeedback" xp:description=""
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
                </alef_partialfeedback>
            """
            )
            count = count + 1
        else:

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
        if hint:
            hinttext = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][hint['text']]
            hintresp = write_html_mlo(
                text=hinttext, exiting_hashcode=exiting_hashcode
            )
            all_files.add(hintresp['relative_path'])
            exiting_hashcode.add(hintresp['hashcode'])

            hashcode11 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode11)
            hashcode12 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode12)
            hashcode13 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode13)

            all_tags.append(
                f"""
                        <alef_hint xlink:label="{hashcode11}" xp:name="alef_hint"
                                   xp:description="" xp:fieldtype="folder">
                            <alef_section_general xlink:label="{hashcode12}"
                                                  xp:name="alef_section_general" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_column xlink:label="{hashcode13}" xp:name="alef_column"
                                             xp:description="" xp:fieldtype="folder" width="auto">
                                    <alef_html xlink:label="{hintresp['hashcode']}" xp:name="alef_html"
                                               xp:description="" xp:fieldtype="html"
                                               src="../../../{hintresp['relative_path']}"/>
                                </alef_column>
                            </alef_section_general>
                        </alef_hint>
                    """
            )
        else:
            print("Warning: DropDown_001 : hint is not found")
    except Exception as e:
        print(f"Warning: DropDown_001 hint key not present in args {e}")

    all_tags.append(
        image_tag
    )

    all_tags.append(
        """
        </alef_multiplechoice>
        """
    )

    try:
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
    except:
        print("Error: MCSS_001 --> src audio not found")

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
