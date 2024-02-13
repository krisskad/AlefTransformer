from Transformer.helpers import generate_unique_folder_name, convert_html_to_strong
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
    all_tags = []

    all_tags = [
        """
        <!-- CustomDragAndDrop_002 -->

        """
    ]

    # Extracting variables
    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]['text']]
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    submitCount = input_json_data["pageData"]["args"]["submitCount"]
    shuffle = input_json_data["pageData"]["args"]["shuffle"]
    feedback = input_json_data["pageData"]["args"]["feedback"]
    dragItems = input_json_data["pageData"]["args"]["dragItems"]

    all_tags.append(
        f"""
            <alef_section xlink:label="LWXGTR3YBFRJETPLSKYWXQAFYJ4" xp:name="alef_section"
                              xp:description="Drag and Drop" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="LZK7INFVC63OE3FC2EOROUG2RKU" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_draganddrop xlink:label="LGBOHT7AOOKCUZBZVLEIMSC6SZQ" xp:name="alef_draganddrop"
                                          xp:description="" xp:fieldtype="folder" submitattempts="{submitCount}"
                                          validation="Yes" autowidth="false" optionwidth="No" invertoptions="No"
                                          stickyoptions="No">
                            <alef_draganddropitem xlink:label="LPO6UU36NWYPU3D3K7CSFLCD6HY"
                                                  xp:name="alef_draganddropitem" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_questionstatement xlink:label="L6D47KARDFEMUNH7WQOG2T5JORM"
                                                        xp:name="alef_questionstatement" xp:description=""
                                                        xp:fieldtype="folder">
                                    <alef_section_general xlink:label="LA4FJGCLMROIETMY27UCVQUPHAY"
                                                          xp:name="alef_section_general" xp:description=""
                                                          xp:fieldtype="folder">
                                        <alef_column xlink:label="LCM4TAGEDZVEETJDP36G5L2IA2I" xp:name="alef_column"
                                                     xp:description="" xp:fieldtype="folder" width="auto"/>
                                    </alef_section_general>
                                </alef_questionstatement>
        """
    )

    for each_op in dragItems:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_op['text']]

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
        hashcode4 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode4)

        all_tags.append(
            f"""
                <alef_option xlink:label="{hashcode1}" xp:name="alef_option"
                             xp:description="{each_op['dropId']}" xp:fieldtype="folder">
                    <alef_optionvalue xlink:label="{hashcode2}"
                                      xp:name="alef_optionvalue" xp:description=""
                                      xp:fieldtype="folder">
                        <alef_section_general xlink:label="{hashcode3}"
                                              xp:name="alef_section_general" xp:description=""
                                              xp:fieldtype="folder">
                            <alef_column xlink:label="{hashcode4}"
                                         xp:name="alef_column" xp:description=""
                                         xp:fieldtype="folder" width="auto">
                                <alef_html xlink:label="{hashcode}"
                                           xp:name="alef_html" xp:description="" xp:fieldtype="html"
                                           src="../../../{relative_path}"/>
                            </alef_column>
                        </alef_section_general>
                    </alef_optionvalue>
                </alef_option>
            """
        )

    extraTexts = input_json_data["pageData"]["args"]["extraTexts"]
    ques_text = "<hr>".join([input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][op['text']] for op in extraTexts])

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
    write_html(text=ques_text, destination_file_path=path_to_html)

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_path)

    all_tags.append(
        f"""
        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                               xp:description="" xp:fieldtype="html"
                                               src="../../../{relative_path}"/>
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

    hint = input_json_data["pageData"]["args"]["hint"].get("text", None)

    if hint:
        text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][hint]

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
        write_html(text=text, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        all_tags.append(
            f"""
                <alef_hint xlink:label="LAPL54RA7QMGETBYH5OVQUIPMKE" xp:name="alef_hint"
                           xp:description="" xp:fieldtype="folder">
                    <alef_section_general xlink:label="LBT3EYWPWKWLEPETPNEHXLUS4KY"
                                          xp:name="alef_section_general" xp:description=""
                                          xp:fieldtype="folder">
                        <alef_column xlink:label="LPE5SMKOTKFLEXAEMW2BKHS74DU" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto">
                            <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{relative_path}"/>
                        </alef_column>
                    </alef_section_general>
                </alef_hint>
            """
        )

    all_tags.append(
        """
                    </alef_draganddropitem>
                </alef_draganddrop>
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
        xml_output = {
            "XML_STRING": "",
            "GENERATED_HASH_CODES": set(),
            "MANIFEST_FILES": set(),
            "STATUS": [f"Error : {e}", ]
        }
    return xml_output
