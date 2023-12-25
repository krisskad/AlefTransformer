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
    ques = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["ques"]]
    src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["text"]]

    # visibleElements = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
    #     input_json_data["pageData"]["args"]["visibleElements"]]
    container = input_json_data["pageData"]["args"]["container"]

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
                <alef_section xlink:label="LVZDBLZEO5UIURBBOOMF3OVEHSU" xp:name="alef_section"
                              xp:description="{htmlentities.encode(ques)}" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="L7NDSACLUKKJUBE7ALSOHDYVHLQ" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_html xlink:label="{hashcode}" xp:name="alef_html" xp:description=""
                                   xp:fieldtype="html"
                                   src="../../../{relative_path}"/>
                        <alef_flipcards xlink:label="LPIMJL36YBCDULNW7UX2FSDZYJQ" xp:name="alef_flipcards"
                                        xp:description="" xp:fieldtype="folder" customtype="Flipcard" height="500"
                                        multipleopen="true" flipdirection="Right">
                            <alef_questionstatement xlink:label="LYUZLULHGZGYETD4EWTKSDNMITU"
                                                    xp:name="alef_questionstatement" xp:description=""
                                                    xp:fieldtype="folder">
                                <alef_section_general xlink:label="LGCKBEQUYXEWENJLCOIJGFJ5534"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="LQ3ORPLEF72FE7IV742Z5ZPBSAY" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto"/>
                                </alef_section_general>
                            </alef_questionstatement>
        """
    )

    for each_cat in container:
        front = each_cat["deck"]['front']
        back = each_cat["deck"]['back']

        front_text = front.get("content")
        front_img = front.get("img")
        front_aud = front.get("audio")

        back_text = front.get("content")
        back_img = front.get("img")
        back_aud = front.get("audio")

        all_tags.append(
            """
                <alef_flipcard xlink:label="LMNEYFT6QMUEEXOHNDMZABBQXRM" xp:name="alef_flipcard"
                               xp:description="" xp:fieldtype="folder" centered="true">
                    <alef_section xlink:label="LEFA6RDV6S4AU5EXQDIQQ3JHM24" xp:name="alef_section"
                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="LMYMP6MIC74UERCNCJYZQE3KUSY" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_html xlink:label="LNJLLUYT3BWKEDOUZ56TORFUQ54" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../LNJLLUYT3BWKEDOUZ56TORFUQ54/emptyHtmlModel.html"/>
                            <alef_image xlink:label="LHLPZBKDD3IXUHCX4TS2C3LWUCQ" xp:name="alef_image"
                                        xp:description="" xp:fieldtype="image" alt="">
                                <xp:img href="../../../LHLPZBKDD3IXUHCX4TS2C3LWUCQ/flipImg1.png"
                                        width="696" height="890"/>
                            </alef_image>
                            <alef_audionew xlink:label="LSGL3KLC4G4NEPOKPII67KVA5DQ"
                                           xp:name="alef_audionew" xp:description=""
                                           xp:fieldtype="folder">
                                <alef_audiofile xlink:label="L2WYH6TZX5UNEPPIZONDLDGPSWY"
                                                xp:name="alef_audiofile" xp:description=""
                                                audiocontrols="No" xp:fieldtype="file"
                                                src="../../../L2WYH6TZX5UNEPPIZONDLDGPSWY/CS_ELA5_L011_CON_S02_AUD_002.mp3"/>
                            </alef_audionew>
                        </alef_column>
                    </alef_section>
                    <alef_section xlink:label="L2XPHD3JYLHKEBL7VTN3WBNHM4Q" xp:name="alef_section"
                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="LRBOJEYPGOS3EZG7KQOPTVDKKOE" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                            <alef_html xlink:label="L2XCQWKRIC7AULP5EVYTJVN4Q2I" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../L2XCQWKRIC7AULP5EVYTJVN4Q2I/emptyHtmlModel.html"/>
                            <alef_audionew xlink:label="LNNN237KB2RWEHPCBWXDGPYRXOU"
                                           xp:name="alef_audionew" xp:description=""
                                           xp:fieldtype="folder">
                                <alef_audiofile xlink:label="LGM7QC3FL2OWETEWLHQCHHNPSCE"
                                                xp:name="alef_audiofile" xp:description=""
                                                audiocontrols="No" xp:fieldtype="file"
                                                src="../../../LGM7QC3FL2OWETEWLHQCHHNPSCE/CS_ELA6_L017_ANL_S08_AUD_001.mp3"/>
                            </alef_audionew>
                        </alef_column>
                    </alef_section>
                </alef_flipcard>
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
