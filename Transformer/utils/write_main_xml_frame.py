import glob

import htmlentities
import os
from Transformer.helpers import generate_unique_folder_name, write_xml, write_html, copy_to_hashcode_dir, remove_html_tags, mathml2latex_yarosh
# import shutil
from django.conf import settings


MLO_HTML_TEMPLATE = """
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <script>
      function changePage(obj) {
        page_url = obj.value;
        console.log("page_url", page_url);
        iframePage = document.getElementById("alef_page_viewer");
        iframePage.src = page_url;
      }
      function errorpage() {
        iframePage = document.getElementById("alef_page_viewer");
        iframePage.src = "./mloerror.html";
      }
    </script>
  </head>
  <body>
    <p>
      This MLO contains the following pages.
      <select onchange="changePage(this);">
        <option value="">-- Select a page ---</option>
        <option value="page_3LHLS7DTRTJUNCWSZX3M3LWYTA.html">Matter</option>
        <option value="customization_default_DQRSTW5TXC3UZGLTLGSB2TV24A_LY5EORGU3LTXEBHTBMMECJBF76E.html">Custom_R&amp;I</option>
        <option value="./manuscript.html">Manuscript</option>
        <option value="./mloerror.html">Error Log</option>
        <option value="./localization.html">Localization</option>
        <option value="./images.html">Images</option>
        <option value="./audios.html">Audios</option>
        <option value="./videos.html">Videos</option>
        <option value="./assetsquantities.html">Assets quantities</option>
        <option value="./page_accessibility.html">Accessibility Attributes</option>
      </select>
    </p>
    <iframe src="./mloerror.html" width="100%" height="90%" name="alef_page_viewer" id="alef_page_viewer"></iframe>
  </body>
</html>
"""


def write_mlo(lo_id, sections, input_other_jsons_data, exiting_hashcode):
    all_files = set()
    all_tags = [
        """<?xml version="1.0" encoding="utf-8"?>""",
        f"""<alef_mlo xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xp="http://www.giuntilabs.com/exact/xp_v1d0" xlink:label="LT7KP3OIZ2WREPBI2GM7LDEXRZU" xp:name="mlo" xp:description="{lo_id}" href="mlo.html" xp:version="3.1" xp:editortype="webeditor" xml:space="preserve" xml:class="" webeditorsafe="true" xp:deliverytype="SCORM" direction="LTR" sequence="000" xp:templateversion="1.0" xp:derivedItemClass="">"""
    ]

    if input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA'].get('head', None):
        try:
            head = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['head']]
            head = remove_html_tags(head)
        except:
            head = ""
    else:
        head = ""

    if input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA'].get('title', None):
        try:
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['title']]
            title = remove_html_tags(title)
        except:
            title = ""
    else:
        title = ""

    if input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA'].get('subtitle', None):
        try:
            subtitle = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['subtitle']]
            subtitle = remove_html_tags(subtitle)
            subtitle = subtitle.replace("—", "-")
        except:
            subtitle = ""
    else:
        subtitle = ""

    if "goalText" in input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']:
        try:
            goalText = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'].get(input_other_jsons_data['INPUT_STRUCTURE_JSON_DATA']['goalText'], None)

            if "<math" in goalText:
                goalText = remove_html_tags(goalText)
        except:
            goalText = ""

        # goalText = remove_html_tags(goalText)
        if goalText:
            goalText = htmlentities.encode(goalText)
            goalText = goalText.replace("&nbsp;", " ")
            lesson_objective_param = f'lessonObjective="{goalText}"'
        else:
            lesson_objective_param = ""
    else:
        lesson_objective_param = ""

    launchPage_img = ""
    # for key, val in input_other_jsons_data['INPUT_IMAGES_JSON_DATA'].items():
    #     if "launchPage" in val:
    #         resp = copy_to_hashcode_dir(exiting_hashcode=exiting_hashcode, src_path=val)
    #         all_files.add(resp['relative_path'])
    #         exiting_hashcode.add(resp['hashcode'])
    #         launchPage_img = f"""
    #                 <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
    #                     <xp:img href="../../../{resp['relative_path']}" width="1920" height="1080" />
    #                 </alef_image>
    #                 """
    #         break
    try:
        if not launchPage_img:
            all_images = glob.glob(os.path.join(settings.INPUT_APP_DIR, "images", "*"))
            for each_img in all_images:
                if "launchPage" in each_img:
                    resp = copy_to_hashcode_dir(src_path=os.path.join("images", os.path.basename(each_img)), exiting_hashcode=exiting_hashcode)
                    all_files.add(resp['relative_path'])
                    exiting_hashcode.add(resp['hashcode'])
                    launchPage_img = f"""
                            <alef_image xlink:label="{resp['hashcode']}" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                                <xp:img href="../../../{resp['relative_path']}" width="1920" height="1080" />
                            </alef_image>
                            """
                    break
    except Exception as e:
        raise Exception(f"Error: launchPage image --> {e}")

    temp = []
    for _ in range(9):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    all_tags.append(
        f"""
        <alef_page xlink:label="{temp[0]}" xp:name="alef_page" xp:description="{htmlentities.encode(head)}" xp:fieldtype="folder" unittitle="{htmlentities.encode(title)} | {htmlentities.encode(subtitle)}" view="Normal" direction="LTR" allowautoplay="false" style="Style 1" customizationid="R_n_I_custom" width="1440" height="810" fixeddimension="No" includetoolkit="No" sequence="000">
        <alef_section xlink:label="{temp[1]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="{temp[2]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
        <alef_presentation xlink:label="{temp[3]}" xp:name="alef_presentation" xp:description="" xp:fieldtype="folder" type="Carousel" ela_title1="{htmlentities.encode(title)}" ela_title2="{htmlentities.encode(subtitle)}" {lesson_objective_param} showtitle="false" multipleopen="false" firstopen="false">
        <alef_section xlink:label="{temp[4]}" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="{temp[5]}" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1" />
        </alef_section>
        {launchPage_img}
        """,
    )

    # all_sections = "\n".join(sections)

    all_tags.append(sections)

    all_tags.append(
        """
        </alef_presentation>
        </alef_column>
        </alef_section>
        </alef_page>
        """
    )

    body = """
    <body>   <html>{"fixed_dimension":true,"width":1920,"height":1080,"show_toc":false,"skin":"reveal_inspire","padding":{"top":"0px","bottom":"0px","right":"0px","left":"0px"},"content_padding":{"top":"0px","bottom":"0px","right":"0px","left":"0px"},"primary_color":"","interactive_color":"","sequence":"free","icon":"","full_screen":"none","show_unit_title":false,"show_lesson_title":false,"summary_screen":false,"feedback_popup":true,"show_how_to":true,"background_image":"","background_repeat":"cover","font_path":"","fonts":{"content":null,"buttons":null,"icons":null},"localization":{}}</html>
    </body>
    """
    all_tags.append(
        f"""
        <customization xlink:label="{temp[6]}" xp:name="customization" xp:description="R_n_I_custom" xp:locked="" xp:globalchunckid="_QTPE575ZBSVU7KQCLZ623JKD5I_2_LNW5NP5L7FL3EDD2SRKZMNIXWUU" xp:chunkid="LNW5NP5L7FL3EDD2SRKZMNIXWUU" xp:packageid="_QTPE575ZBSVU7KQCLZ623JKD5I" xp:packageversion="2" xp:autoupdate="True" xp:lobstername="alef02" xp:linktype="link" xp:class="" xp:fieldtype="folder" xp:templateversion="1.0" xp:derivedItemClass="" fixed_dimension="False" width="1440" height="810" full_screen="None" show_toc="False" skin="Default" padding_top="0px" padding_bottom="0px" padding_left="0px" padding_right="0px" sequence="Free" show_unit_title="False" show_lesson_title="False" content_fontsize="22px" button_fontsize="20px" icon_fontsize="24px" summary_screen="False" primary_color="hsla(215, 17%, 34%)" interactive_color="hsla(178, 70%, 43%)" content_padding_top="0px" content_padding_bottom="0px" content_padding_left="0px" content_padding_right="0px" background_repeat="Extend">

            <alef_customcontent xlink:label="{temp[7]}" xp:name="alef_customcontent" xp:description="" xp:locked="" xp:class="" xp:fieldtype="text">
                
            {body}
            
            </alef_customcontent>

        </customization>

        """
    )

    all_tags.append(
        "</alef_mlo>"
    )

    xml_content = "\n".join(all_tags)

    # create folder
    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)

    path_to_hashcode = str(os.path.join(settings.OUTPUT_DIR, "1", "mlo", hashcode))
    os.makedirs(path_to_hashcode, exist_ok=True)

    path_to_xml = os.path.join(path_to_hashcode, 'mlo.xml')
    path_to_html = os.path.join(path_to_hashcode, 'mlo.html')
    lo_xml_filepath = os.path.join(settings.OUTPUT_DIR, '1', f'lo_{hashcode}.xpl.xml')

    all_files.add(os.path.join("1", "mlo", hashcode, 'mlo.xml'))
    all_files.add(os.path.join("1", "mlo", hashcode, 'mlo.html'))
    all_files.add(os.path.join("1", f'lo_{hashcode}.xpl.xml'))

    xml_content = xml_content.replace("LT7KP3OIZ2WREPBI2GM7LDEXRZU", hashcode)

    write_xml(
        file_path=path_to_xml,
        xml_content=xml_content
    )

    write_xml(
        file_path=lo_xml_filepath,
        xml_content=xml_content
    )

    write_html(
        file_path=path_to_html,
        html_content=MLO_HTML_TEMPLATE
    )

    response = {
        "MANIFEST_FILES":all_files,
        "GENERATED_HASH_CODES":exiting_hashcode,
        "XM_STRING":xml_content
    }

    return response

