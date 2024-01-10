from Transformer.helpers import generate_unique_folder_name, text_en_html_to_html_text, get_popup_mlo_from_text, mathml2latex_yarosh
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


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):
    # store all file paths like hashcode/filename
    all_files = set()
    all_tags = []

    # Extracting variables
    # poster = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][input_json_data["pageData"]["args"]["poster"]]
    title = input_json_data["pageData"]["args"]["title"]
    src = input_json_data["pageData"]["args"]["src"]
    showAnswer = input_json_data["pageData"]["args"].get("showAnswer", None)
    iButtonAlt = input_json_data["pageData"]["args"]["iButtonAlt"]
    dropDownText = input_json_data["pageData"]["args"]["dropDownText"]
    submitCount = input_json_data["pageData"]["args"]["submitCount"]
    feedback = input_json_data["pageData"]["args"].get("feedback", None)
    hint = input_json_data["pageData"]["args"].get("hint", None)
    dropDowns = input_json_data["pageData"]["args"]["dropDowns"]

    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][title]
    qHtmlText = text_en_html_to_html_text(html_string=text)

    resp = write_html(text=qHtmlText, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    temp = []
    for _ in range(40):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

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
        all_files=popup_response['all_files']
        exiting_hashcode=popup_response['exiting_hashcode']
        all_tags=all_tags+popup_response['all_tags']

    all_tags.append(
        """
                        </alef_tooltip>
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        """
    )

    drop_Down_Text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][dropDownText]

    for i, obj in enumerate(dropDowns):
        title = obj['title']
        image = obj.get('image', None)
        answer = obj['answer']
        options = obj['options']

        all_tags.append(
            f"""
                <alef_options xlink:label="{temp[7]}" xp:name="alef_options"
                              xp:description="{i}" xp:fieldtype="folder" label="{htmlentities.encode(title)}"
                              excerpt="{htmlentities.encode(drop_Down_Text)}">
            """
        )

        if image:
            resp = copy_to_hashcode_dir(
                src_path=input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][image],
                exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            all_tags.append(
                f"""
                     <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                            xp:description="" xp:fieldtype="image" alt="">
                        <xp:img href="../../../{resp['relative_path']}"
                            width="834" height="890"/>
                    </alef_image>
                """
            )

        for j, option in enumerate(options):
            is_answer = "No"
            if str(answer) == str(j):
                is_answer = "Yes"
            text = option['option']
            oText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text]

            if "<math" in oText:
                oText = mathml2latex_yarosh(equation=oText)

            o_resp = write_html(
                text=oText, exiting_hashcode=exiting_hashcode
            )
            all_files.add(o_resp['relative_path'])
            exiting_hashcode.add(o_resp['hashcode'])

            all_tags.append(
                f"""
                <alef_option xlink:label="{temp[8]}" xp:name="alef_option"
                             xp:description="" xp:fieldtype="folder" iscorrect="{is_answer}">
                    <alef_optionvalue xlink:label="{temp[9]}"
                                      xp:name="alef_optionvalue" xp:description=""
                                      xp:fieldtype="folder">
                        <alef_section_general xlink:label="{temp[10]}"
                                              xp:name="alef_section_general" xp:description=""
                                              xp:fieldtype="folder">
                            <alef_column xlink:label="{temp[11]}"
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

    if feedback:
        count = 1
        for key, val in feedback.items():
            if count > 2:
                break

            main_key = key.split("_")[0]

            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]
            resp = write_html(
                text=text, exiting_hashcode=exiting_hashcode
            )
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

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
                                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                               xp:description="" xp:fieldtype="html"
                                               src="../../../{resp['relative_path']}"/>
                                </alef_column>
                            </alef_section_general>
                        </alef_{main_key}feedback>
                    """
            )
            count = count + 1

    if hint:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][hint]
        resp = write_html(
            text=text, exiting_hashcode=exiting_hashcode
        )
        all_files.add(resp['relative_path'])
        exiting_hashcode.add(resp['hashcode'])
        all_tags.append(
            f"""
                    <alef_hint xlink:label="LAPL54RA7QMGETBYH5OVQUIPMKE" xp:name="alef_hint"
                               xp:description="" xp:fieldtype="folder">
                        <alef_section_general xlink:label="LBT3EYWPWKWLEPETPNEHXLUS4KY"
                                              xp:name="alef_section_general" xp:description=""
                                              xp:fieldtype="folder">
                            <alef_column xlink:label="LPE5SMKOTKFLEXAEMW2BKHS74DU" xp:name="alef_column"
                                         xp:description="" xp:fieldtype="folder" width="auto">
                                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                           xp:description="" xp:fieldtype="html"
                                           src="../../../{resp['relative_path']}"/>
                            </alef_column>
                        </alef_section_general>
                    </alef_hint>
                """
        )

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
