from Transformer.helpers import generate_unique_folder_name
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
    # src = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][input_json_data["pageData"]["args"]["src"]]
    text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_json_data["pageData"]["args"]["text"]]

    # visibleElements = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][
    #     input_json_data["pageData"]["args"]["visibleElements"]]
    container = input_json_data["pageData"]["args"]["container"]

    temp = []
    for _ in range(40):
        hashcode_temp = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp)
        temp.append(hashcode_temp)

    resp = write_html(text=text, exiting_hashcode=exiting_hashcode)
    exiting_hashcode.add(resp['hashcode'])
    all_files.add(resp['relative_path'])

    all_tags.append(
        f"""
                <alef_section xlink:label="{temp[0]}" xp:name="alef_section"
                              xp:description="{htmlentities.encode(ques)}" xp:fieldtype="folder" customclass="Normal">
                    <alef_column xlink:label="L7NDSACLUKKJUBE7ALSOHDYVHLQ" xp:name="alef_column" xp:description=""
                                 xp:fieldtype="folder" width="auto" cellspan="1">
                        <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description=""
                                   xp:fieldtype="html"
                                   src="../../../{resp['relative_path']}"/>
                        <alef_flipcards xlink:label="{temp[1]}" xp:name="alef_flipcards"
                                        xp:description="" xp:fieldtype="folder" customtype="Flipcard" height="500"
                                        multipleopen="true" flipdirection="Right">
                            <alef_questionstatement xlink:label="{temp[2]}"
                                                    xp:name="alef_questionstatement" xp:description=""
                                                    xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[3]}"
                                                      xp:name="alef_section_general" xp:description=""
                                                      xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[4]}" xp:name="alef_column"
                                                 xp:description="" xp:fieldtype="folder" width="auto"/>
                                </alef_section_general>
                            </alef_questionstatement>
        """
    )

    for each_cat in container:
        front = each_cat["deck"]['front']
        back = each_cat["deck"]['back']

        front_text = front.get("content", None)
        front_img = front.get("img")
        front_aud = front.get("audio")
        front_tags = []
        if front_text:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][front_text]
            resp = write_html(text=text, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])
            front_tags.append(
                f"""
                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp['relative_path']}"/>
                """
            )

        if front_img:
            img = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][front_img]
            resp = copy_to_hashcode_dir(src_path=img, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])
            front_tags.append(
                f"""
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                        xp:description="" xp:fieldtype="image" alt="">
                                <xp:img href="../../../{resp['relative_path']}"
                                        width="696" height="890"/>
                            </alef_image>
                """
            )

        if front_aud:
            aud = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][front_aud]
            resp = copy_to_hashcode_dir(src_path=aud, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])
            front_tags.append(
                f"""
                            <alef_audionew xlink:label="{temp[5]}"
                                           xp:name="alef_audionew" xp:description=""
                                           xp:fieldtype="folder">
                                <alef_audiofile xlink:label="{resp['hashcode']}"
                                                xp:name="alef_audiofile" xp:description=""
                                                audiocontrols="No" xp:fieldtype="file"
                                                src="../../../{resp['relative_path']}"/>
                            </alef_audionew>
                """
            )

        back_text = back.get("content")
        back_img = back.get("img")
        back_aud = back.get("audio")

        back_tags = []
        if back_text:
            text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][back_text]
            resp = write_html(text=text, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])
            back_tags.append(
                f"""
                <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html"
                                       xp:description="" xp:fieldtype="html"
                                       src="../../../{resp['relative_path']}"/>
                """
            )

        if back_img:
            img = input_other_jsons_data['INPUT_IMAGES_JSON_DATA'][back_img]
            resp = copy_to_hashcode_dir(src_path=img, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])
            back_tags.append(
                f"""
                <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image"
                                        xp:description="" xp:fieldtype="image" alt="">
                                <xp:img href="../../../{resp['relative_path']}"
                                        width="696" height="890"/>
                            </alef_image>
                """
            )

        if back_aud:
            aud = input_other_jsons_data['INPUT_AUDIO_JSON_DATA'][back_aud]
            resp = copy_to_hashcode_dir(src_path=aud, exiting_hashcode=exiting_hashcode)
            exiting_hashcode.add(resp['hashcode'])
            all_files.add(resp['relative_path'])

            back_tags.append(
                f"""
                            <alef_audionew xlink:label="{temp[6]}"
                                           xp:name="alef_audionew" xp:description=""
                                           xp:fieldtype="folder">
                                <alef_audiofile xlink:label="{resp['hashcode']}"
                                                xp:name="alef_audiofile" xp:description=""
                                                audiocontrols="No" xp:fieldtype="file"
                                                src="../../../{resp['relative_path']}"/>
                            </alef_audionew>
                """
            )

        all_front_tags = "\n".join(front_tags)
        all_back_tags = "\n".join(back_tags)

        all_tags.append(
            f"""
                <alef_flipcard xlink:label="{temp[7]}" xp:name="alef_flipcard"
                               xp:description="" xp:fieldtype="folder" centered="true">
                    <alef_section xlink:label="{temp[8]}" xp:name="alef_section"
                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp[9]}" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                                    {all_front_tags}
                        </alef_column>
                    </alef_section>
                    <alef_section xlink:label="{temp[10]}" xp:name="alef_section"
                                  xp:description="" xp:fieldtype="folder" customclass="Normal">
                        <alef_column xlink:label="{temp[11]}" xp:name="alef_column"
                                     xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
                                    {all_back_tags}
                        </alef_column>
                    </alef_section>
                </alef_flipcard>
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
