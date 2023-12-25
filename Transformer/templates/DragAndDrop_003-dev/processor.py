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
    all_tags = []

    # Extracting variables
    title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["title"]]
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]

    submit = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["submit"]]
    submitCount = input_json_data["pageData"]["args"]["submitCount"]
    showAnswer = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["showAnswer"]]
    feedback = input_json_data["pageData"]["args"]["feedback"]
    feedBackAudio = input_json_data["pageData"]["args"]["feedBackAudio"]
    hint = input_json_data["pageData"]["args"]["hint"]

    # visibleElements = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
    #     input_json_data["pageData"]["args"]["visibleElements"]]
    dropItems = input_json_data["pageData"]["args"]["dropItems"]
    dragItems = input_json_data["pageData"]["args"]["dragItems"]

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
    write_html(text=title, destination_file_path=path_to_html)

    relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
    all_files.add(relative_path)

    all_tags.append(
        f"""
                <alef_section xlink:label="LAGP5JVTSXWSEFK7WPB4RLJF7KA" xp:name="alef_section"
                              xp:description="{htmlentities.encode(title)}"
                              xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="LMU6YDLDPOQFEFFPIU4W47OS7TU" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_categorization xlink:label="LMUW7ZRIVRJBEVJQDUE477YI4MY" xp:name="alef_categorization"
                                             xp:description="" xp:fieldtype="folder"
                                             href="categorization_MUW7ZRIVRJBEVJQDUE477YI4MY.json"
                                             alef_categorizationtype="Normal" categorization_type="Text with Image"
                                             alef_shownumberofoptions="No" alef_limitanswer="No"
                                             alef_stickyoptions="No" alef_verticaloptions="No" invertoptions="No"
                                             submitattempts="{submitCount}" validation="No" theme="Standard">
                            <alef_categorizationquestion xlink:label="LJPET2PRM5BFE3P76ISP6USYCVQ"
                                                         xp:name="alef_categorizationquestion" xp:description=""
                                                         xp:fieldtype="folder">
                                <alef_section_general xlink:label="LIC5PRWIUFPCE3OFUI7JEMAOJKE"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="LPZOHCNTCVDZEVOVMNNMYR2K2BY" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{relative_path}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_categorizationquestion>
        """
    )

    all_tags.append(
        """
        <alef_categories xlink:label="LXSQPFAIORFAEVA7DBAUHKMT7TQ" xp:name="alef_categories"
                                                 xp:description="" xp:fieldtype="folder">
        """
    )

    for each_cat in dropItems:
        title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_cat['title']]
        all_tags.append(
            f"""
                                    <alef_category xlink:label="LXCVFVETT3Z3ENJRO4YM5U74WNU" xp:name="alef_category"
                                               xp:description="{htmlentities.encode(title)}" xp:fieldtype="folder"> 
            """
        )

        for each_option in dragItems:
            image = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][each_option['image']]

            resp = copy_to_hashcode_dir(src_path=image, exiting_hashcode=exiting_hashcode)
            all_files.add(resp['relative_path'])
            exiting_hashcode.add(resp['hashcode'])

            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][each_option['text']]
            if each_option['dropId'] == each_cat['dropId']:
                all_tags.append(
                    f"""
                                                <alef_option xlink:label="L7O32R5LWYEIELE37L7CH6UDGEM" xp:name="alef_option"
                                                             xp:description="" xp:fieldtype="folder" label="{htmlentities.encode(text)}">
                                                    <alef_optionvalue xlink:label="L3BAYOQVBTLAE3M5WBPKMNTXVEQ"
                                                                      xp:name="alef_optionvalue" xp:description=""
                                                                      xp:fieldtype="folder">
                                                        <alef_section_general xlink:label="L7KJP4TV52TBEDGFFH36BHUVDOA"
                                                                              xp:name="alef_section_general" xp:description=""
                                                                              xp:fieldtype="folder">
                                                            <alef_column xlink:label="LGK2O44722UTUFCKHKDVTPEDRL4"
                                                                         xp:name="alef_column" xp:description=""
                                                                         xp:fieldtype="folder" width="auto">
                                                                <alef_image xlink:label="{resp['hashcode']}"
                                                                            xp:name="alef_image" xp:description=""
                                                                            xp:fieldtype="image" alt="">
                                                                    <xp:img href="../../../{resp['relative_path']}"
                                                                            width="301" height="155"/>
                                                                </alef_image>
                                                            </alef_column>
                                                        </alef_section_general>
                                                    </alef_optionvalue>
                                                </alef_option>
                    """
                )
        all_tags.append("</alef_category>")

    all_tags.append(
        """
        </alef_categories>
        """
    )

    # add all hint, feedback, etc
    for key, val in feedback.items():
        base_key = key.split("_")[0]

        text_val = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
        write_html(text=text_val, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        all_tags.append(
            f"""
                            <alef_{base_key}feedback xlink:label="LLFNJUQLYEPDUNJGAFPEHHJF3XE"
                                                  xp:name="alef_correctfeedback" xp:description=""
                                                  xp:fieldtype="folder">
                                <alef_section_general xlink:label="LSP5XORCFXW5UJCFCDBNH7NYTMA"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="L3NF6ET56GRVUFCMWXNP6YRMK3U" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{relative_path}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_correctfeedback>
            
            """
        )

    # add all hint, feedback, etc
    for key, val in hint.items():
        text_val = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][val]

        hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode)

        path_to_hashcode = os.path.join(settings.OUTPUT_DIR, hashcode)
        os.makedirs(path_to_hashcode, exist_ok=True)

        path_to_html = os.path.join(str(path_to_hashcode), "emptyHtmlModel.html")
        write_html(text=text_val, destination_file_path=path_to_html)

        relative_path = os.path.join(hashcode, "emptyHtmlModel.html")
        all_files.add(relative_path)

        all_tags.append(
            f"""
                            <alef_hint xlink:label="LVUI4NMC5VA5EZCIED2ME6OH2II" xp:name="alef_hint"
                                       xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="LHWPYNYVVGDYEFK3QTHPZQS6KYQ"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="LQVYLB3XVE7SEZOMN6ODS53VSLY" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_html xlink:label="{hashcode}" xp:name="alef_html"
                                                   xp:description="" xp:fieldtype="html"
                                                   src="../../../{relative_path}"/>
                                    </alef_column>
                                </alef_section_general>
                            </alef_hint>

            """
        )

    all_tags.append("</alef_categorization>")

    resp = copy_to_hashcode_dir(src_path=src, exiting_hashcode=exiting_hashcode)
    all_files.add(resp['relative_path'])
    exiting_hashcode.add(resp['hashcode'])

    all_tags.append(
        f"""
                        <alef_audionew xlink:label="LN5PBOJAOYJOE7GX2SLAMZKBPR4" xp:name="alef_audionew"
                                       xp:description="" xp:fieldtype="folder">
                            <alef_audiofile xlink:label="{resp['hashcode']}" xp:name="alef_audiofile"
                                            xp:description="" audiocontrols="Yes" xp:fieldtype="file"
                                            src="../../../{resp['relative_path']}"/>
                        </alef_audionew>
        """
    )

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
