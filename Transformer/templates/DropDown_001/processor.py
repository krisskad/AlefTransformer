from Transformer.helpers import (generate_unique_folder_name, text_en_html_to_html_text,
                                 get_popup_mlo_from_text, mathml2latex_yarosh,
                                 convert_html_to_strong, remove_html_tags)
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode, align=None):
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
    try:
        # store all file paths like hashcode/filename
        all_files = set()
        all_tags = [
            """
            <!-- DropDown_001 -->

            """
        ]

        # Extracting variables
        # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
        title = input_json_data["pageData"]["args"].get("title")
        # src = input_json_data["pageData"]["args"].get("src")
        showAnswer = input_json_data["pageData"]["args"].get("showAnswer", None)
        # iButtonAlt = input_json_data["pageData"]["args"].get("iButtonAlt", None)
        dropDownText = input_json_data["pageData"]["args"].get("dropDownText")
        submitCount = input_json_data["pageData"]["args"].get("submitCount")
        feedback = input_json_data["pageData"]["args"].get("feedback", None)
        hint = input_json_data["pageData"]["args"].get("hint", None)
        dropDowns = input_json_data["pageData"]["args"].get("dropDowns")

        temp = []
        for _ in range(40):
            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode_temp)
            temp.append(hashcode_temp)

        try:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title]
            qHtmlText = text_en_html_to_html_text(html_string=text)

            resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            validation = "No"
            if showAnswer:
                validation = "Yes"
            all_tags.append(
                f"""
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section" xp:description=""
                      xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="{temp[1]}" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_selectablank xlink:label="{temp[2]}" xp:name="alef_selectablank"
                                           xp:description="" xp:fieldtype="folder" submitattempts="{submitCount}"
                                           type="Dropdown" autowidth="false" validation="{validation}">
                            <alef_questionstatement xlink:label="{temp[3]}"
                                                    xp:name="alef_questionstatement" xp:description=""
                                                    xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[4]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[5]}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_tooltip xlink:label="{temp[6]}"
                                                      xp:name="alef_tooltip" xp:description=""
                                                      xp:fieldtype="folder">
                                            <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                                       xp:description="" xp:fieldtype="html"
                                                       src="../../../{resp['relative_path']}"/>
                """
            )

            popup_response = get_popup_mlo_from_text(
                text=text,
                input_other_jsons_data=input_other_jsons_data,
                all_files=all_files,
                exiting_hashcode=exiting_hashcode
            )

            if popup_response:
                all_files = popup_response['all_files']
                exiting_hashcode = popup_response['exiting_hashcode']
                all_tags = all_tags + popup_response['all_tags']

            all_tags.append(
                """
                                </alef_tooltip>
                            </alef_column>
                        </alef_section_general>
                    </alef_questionstatement>
                """
            )
        except Exception as e:
            raise Exception(f'Error: DropDown_001 --> {e}')

        try:
            drop_Down_Text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][dropDownText]
            if "<math" in drop_Down_Text:
                drop_Down_Text = mathml2latex_yarosh(html_string=drop_Down_Text)
            else:
                drop_Down_Text = remove_html_tags(drop_Down_Text)

        except:
            drop_Down_Text = ""
            print('Warning: DropDown_001 --> dropDown text not found')

        html_drop_down = []
        for i, obj in enumerate(dropDowns):
            html_drop_down.append(
                f"""
                <span class="dropdown">{i}</span>
                """
            )
            try:
                title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][obj['title']]
                if "<math" in title:
                    title = mathml2latex_yarosh(html_string=title)
                else:
                    title = remove_html_tags(title)

            except Exception as e:
                title = ""
                print(f"Warning: DropDown_001 title not present in DropDown list {e}")

            image = obj.get('image', None)
            answer = obj.get('answer')
            options = obj.get('options')

            all_tags.append(
                f"""
                    <alef_options xlink:label="{temp[7]}" xp:name="alef_options"
                                  xp:description="{i}" xp:fieldtype="folder" label="{htmlentities.encode(title)}"
                                  excerpt="{htmlentities.encode(drop_Down_Text)}">
                """
            )

            try:
                if image:
                    imageresp = copy_to_hashcode_dir(
                        src_path=input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][image],
                        exiting_hashcode=exiting_hashcode
                    )
                    all_files.add(imageresp['relative_path'])
                    exiting_hashcode.add(imageresp['hashcode'])

                    all_tags.append(
                        f"""
                             <alef_image xlink:label="{imageresp['hashcode']}" xp:name="alef_image"
                                    xp:description="" xp:fieldtype="image" alt="">
                                <xp:img href="../../../{imageresp['relative_path']}"
                                    width="834" height="890"/>
                            </alef_image>
                        """
                    )
            except Exception as e:
                print(f"Warning: DropDown_001 image key not present in args {e}")

            try:
                if options:
                    for j, option in enumerate(options):
                        is_answer = "No"
                        if str(answer) == str(j):
                            is_answer = "Yes"
                        optiontext = option['option']
                        try:
                            oText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][optiontext]
                        except Exception as e:
                            print(f"Warning: DropDown_001 oText key not present in args {e}")
                            continue

                        if "<math" in oText:
                            oText = mathml2latex_yarosh(html_string=oText)

                        o_resp = write_html(
                            text=oText, exiting_hashcode=exiting_hashcode
                        )
                        all_files.add(o_resp['relative_path'])
                        exiting_hashcode.add(o_resp['hashcode'])

                        temp1 = []
                        for _ in range(10):
                            hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L",
                                                                        k=27)
                            exiting_hashcode.add(hashcode_temp)
                            temp1.append(hashcode_temp)

                        all_tags.append(
                            f"""
                            <alef_option xlink:label="{temp1[0]}" xp:name="alef_option"
                                         xp:description="" xp:fieldtype="folder" iscorrect="{is_answer}">
                                <alef_optionvalue xlink:label="{temp1[1]}"
                                                  xp:name="alef_optionvalue" xp:description=""
                                                  xp:fieldtype="folder">
                                    <alef_section_general xlink:label="{temp1[2]}"
                                                          xp:name="alef_section_general" xp:description=""
                                                          xp:fieldtype="folder">
                                        <alef_column xlink:label="{temp1[3]}"
                                                     xp:name="alef_column" xp:description=""
                                                     xp:fieldtype="folder" width="auto">
                                            <alef_html xlink:label="{o_resp['hashcode']}"
                                                       xp:name="alef_html" xp:description="" xp:fieldtype="html"
                                                       src="../../../{o_resp['relative_path']}"/>
                                        </alef_column>
                                    </alef_section_general>
                                </alef_optionvalue>
                            </alef_option>
                            """
                        )
                    all_tags.append(
                        "</alef_options>"
                    )
                else:
                    print("Warning: DropDown_001 : option key not found")
            except Exception as e:
                print(f"Warning: DropDown_001 options not present in args {e}")

        # write html
        manual_html_opt = "".join(html_drop_down)
        op_resp = write_html(
            text=manual_html_opt, exiting_hashcode=exiting_hashcode
        )
        all_files.add(op_resp['relative_path'])
        exiting_hashcode.add(op_resp['hashcode'])

        all_tags.append(
            f"""
                    <alef_html xlink:label="{op_resp['hashcode']}" xp:name="alef_html"
                       xp:description="" xp:fieldtype="html"
                       src="../../../{op_resp['relative_path']}"/>
            """
        )

        try:
            if feedback:
                count = 1
                for key, val in feedback.items():
                    if count > 2:
                        break

                    main_key = key.split("_")[0]

                    try:
                        feedbacktext = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
                    except Exception as e:
                        print(f"Warning: DropDown_001 feedback text not present in args {e}")
                        continue

                    feedbackresp = write_html(
                        text=feedbacktext, exiting_hashcode=exiting_hashcode
                    )
                    all_files.add(feedbackresp['relative_path'])
                    exiting_hashcode.add(feedbackresp['hashcode'])

                    temp2 = []
                    for _ in range(10):
                        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L",
                                                                    k=27)
                        exiting_hashcode.add(hashcode_temp)
                        temp2.append(hashcode_temp)

                    all_tags.append(
                        f"""
                                <alef_{main_key}feedback xlink:label="{temp2[0]}"
                                                      xp:name="alef_{main_key}feedback" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_section_general xlink:label="{temp2[1]}"
                                                          xp:name="alef_section_general" xp:description=""
                                                          xp:fieldtype="folder">
                                        <alef_column xlink:label="{temp2[2]}" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto">
                                            <alef_html xlink:label="{feedbackresp['hashcode']}" xp:name="alef_html"
                                                       xp:description="" xp:fieldtype="html"
                                                       src="../../../{feedbackresp['relative_path']}"/>
                                        </alef_column>
                                    </alef_section_general>
                                </alef_{main_key}feedback>
                            """
                    )
                    count = count + 1
            else:
                print("Warning: DropDown_001 : feedback is not found")
        except Exception as e:
            print(f"Warning: DropDown_001 feedback key not present in args {e}")

        try:
            if hint:
                hinttext = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][hint['text']]
                hintresp = write_html(
                    text=hinttext, exiting_hashcode=exiting_hashcode
                )
                all_files.add(hintresp['relative_path'])
                exiting_hashcode.add(hintresp['hashcode'])
                all_tags.append(
                    f"""
                            <alef_hint xlink:label="{temp[15]}" xp:name="alef_hint"
                                       xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[16]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[17]}" xp:name="alef_column"
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
            """
                    </alef_selectablank>
                </alef_column>
            </alef_section>
            """
        )

        response = {
            "XML_STRING": "".join(all_tags),
            "GENERATED_HASH_CODES": exiting_hashcode,
            "MANIFEST_FILES": all_files
        }
    except Exception as e:
        response = {
            "XML_STRING": "",
            "GENERATED_HASH_CODES": exiting_hashcode,
            "MANIFEST_FILES": []
        }
        print(f"Error in DropDown_001: {e}")

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
