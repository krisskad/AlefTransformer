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
    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
    exiting_hashcode.add(hashcode)

    text_en_id = input_json_data['pageData']['args']['ques']
    submitCount = input_json_data['pageData']['args']['submitCount']
    multiAnswer = input_json_data['pageData']['args']['multiAnswer']
    thumbs = input_json_data['pageData']['args']['thumbs']
    nofcolumns = len(thumbs)

    text_en_data = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][text_en_id]
    destination_file_path = os.path.join(settings.OUTPUT_DIR, hashcode, "emptyHtmlModel.html")
    write_html(text=text_en_data, destination_file_path=destination_file_path)
    all_tags = [f"""
        <alef_section xlink:label="LAP7NYP2JN6KE5KGPUQIKOYLTA4" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="LJWIBTGLBLI4EPEFWZLGS3A6FSQ" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
        <alef_multiplechoice xlink:label="LOVEQZON5YZEEFMM4JTJKJVPHI4" xp:name="alef_multiplechoice" xp:description="" xp:fieldtype="folder" alef_type="MC Radio Button" mcq_type="Image Only" questionfullwidth="false" questiontitle=" " questionnumber="1" nofcolumns="{nofcolumns}" submitattempts="{submitCount}" showtitle="true" alignstatement="left" showbackground="true" shuffleoptions="false" validation="Yes">
            <alef_questionstatement xlink:label="LEDRZJ2QUU62UDEKOZUCSLAZRGE" xp:name="alef_questionstatement" xp:description="" xp:fieldtype="folder">
                <alef_section_general xlink:label="LO7IEOFM6KYTEVLZGBKB6IKW7U4" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                    <alef_column xlink:label="LLCUDPN4QIAWUJJSFHBNTPTXYME" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                        <alef_html xlink:label="{hashcode}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{destination_file_path}" />
                    </alef_column>
                </alef_section_general>
            </alef_questionstatement>
        """]

    # choices
    for each_thumb in thumbs:

        if "title" in each_thumb:
            en_title = input_other_jsons_data["INPUT_EN_TEXT_JSON_DATA"][each_thumb['title']]
        else:
            en_title = ""
        if "image" in each_thumb:
            image_thumb_relative_path = input_other_jsons_data["INPUT_IMAGES_JSON_DATA"][each_thumb['image']]

            image_thumb_hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(image_thumb_hashcode)
            image_thumb_destination_file_path = str(os.path.join(settings.OUTPUT_DIR, image_thumb_hashcode, os.path.basename(image_thumb_relative_path)))
            image_thumb_src_file_path = str(os.path.join(settings.INPUT_APP_DIR, image_thumb_relative_path))
            shutil.copy2(image_thumb_src_file_path, image_thumb_destination_file_path)
        else:
            image_thumb_destination_file_path = ""

        if int(each_thumb['ans']):
            isCorrect = "Yes"
        else:
            isCorrect = "No"

        temp = []
        for _ in range(4):
            hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
            exiting_hashcode.add(hashcode)
            temp.append(hashcode)

        temp_choice = f"""
                        <alef_choice xlink:label="{temp[0]}" xp:name="alef_choice" xp:description="" xp:fieldtype="folder" isCorrect="{isCorrect}" label="{en_title}">
                            <alef_choicevalue xlink:label="{temp[1]}" xp:name="alef_choicevalue" xp:description="" xp:fieldtype="folder">
                                <alef_section_general xlink:label="{temp[2]}" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                                    <alef_column xlink:label="{temp[3]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                        <alef_image xlink:label="{uuid}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                                            <xp:img href="../../../{image_thumb_destination_file_path}" width="765" height="890" />
                                        </alef_image>
                                    </alef_column>
                                </alef_section_general>
                            </alef_choicevalue>
                        </alef_choice>
                    """

    return all_tags


def process_page_data(page_data, other_json_data, exiting_hashcode):
    # Custom processing for ClicktoRevealwithSubmit_001
    # Use page_data as needed

    xml_output = create_mlo(
        input_json_data=page_data,
        input_other_jsons_data=other_json_data,
        exiting_hashcode=exiting_hashcode
    )

    RESPONSE = {
        "XML_OUTPUT":xml_output,
        "GENERATED_HASH_CODES":exiting_hashcode
    }
    return RESPONSE
