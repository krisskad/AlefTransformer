from Transformer.helpers import (generate_unique_folder_name,
                                 mathml2latex_yarosh,
                                 text_en_html_to_html_text,
                                 get_popup_mlo_from_text, convert_html_to_strong)
from django.conf import settings
import os, shutil
import htmlentities


def write_html(text, exiting_hashcode, align=None):
    try:
        from Transformer.helpers import assing_class_for_color
        text = assing_class_for_color(text)
    except:
        pass
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
        <!-- InputBox_001 -->
        """
    ]

    src = input_json_data["pageData"]["args"].get("src", None)
    inputBoxes = input_json_data["pageData"]["args"].get("inputBoxes", [])
    extraTexts = input_json_data["pageData"]["args"].get("extraTexts", [])

    buttonsPos = input_json_data["pageData"]["args"].get("buttonsPos", "") # Burger Writing GO
    bookPopUpButton = input_json_data["pageData"]["args"].get("bookPopUpButton", "") # Plot Diagram

    template_type = ""
    if buttonsPos:
        template_type = "Burger Writing GO"

    if bookPopUpButton:
        template_type = "Plot Diagram"

    if not template_type:
        raise Exception("No template identity found : please check input structure.json and note which type of template is this?")

    view_ref = input_json_data["pageData"]['viewRef']
    extraTextViewsorted_data = []

    try:
        view_obj = input_other_jsons_data["INPUT_VIEW_JSON_DATA"]["pages"][view_ref]
        extra_text_css_list = view_obj["pageData"]["args"]["extraTexts"]
        extraTextView = []
        for i, j in zip(extra_text_css_list, extraTexts):
            i["text"] = j["text"]
            extraTextView.append(i)

        # Define a custom key function to extract the integer value from the "top" key
        def sort_by_top(item):
            return int(float(item["top"].replace("px", "")))

        # Sort the data using the custom key function
        extraTextViewsorted_data = sorted(extraTextView, key=sort_by_top)

    except Exception as e:
        print(f"Error: {e}")

    title = ""
    if len(inputBoxes) < len(extraTexts):
        # there are more input and less text (There are title) remove title from text
        try:
            titleobj = extraTextViewsorted_data[0]
            title = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][titleobj["text"]]
            extraTextViewsorted_data.pop(0)
        except Exception as e:
            print(f"Error : {e}")

    html_list = []
    try:
        if inputBoxes:
            for idx, hml_obj in enumerate(extraTextViewsorted_data):
                text_obj = extraTextViewsorted_data[idx]
                text = input_other_jsons_data['INPUT_EN_TEXT_JSON_DATA'][text_obj["text"]]

                if text:
                    resp = write_html(
                        text=text,
                        exiting_hashcode=exiting_hashcode
                    )
                    exiting_hashcode.add(resp['hashcode'])
                    all_files.add(resp['relative_path'])

                    html_xml = f"""
                    <alef_html xlink:label="{resp['hashcode']}" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../{resp['relative_path']}" />
                    """
                    html_list.append(html_xml)
    except Exception as e:
        print(e)

    temp = []
    for _ in range(5):
        hashcode_temp2 = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="L", k=27)
        exiting_hashcode.add(hashcode_temp2)
        temp.append(hashcode_temp2)

    html_join = "\n".join(html_list)
    all_tags.append(f"""
    <alef_section xlink:label="LN6ZCOMIZHRAE7JIIMDOLN4EFDU" xp:name="alef_section" xp:description="" xp:fieldtype="folder" customclass="Normal">
        <alef_column xlink:label="LGGJXTICOSAXEZCJ2Z6FYIHPYBM" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto" cellspan="1">
            <alef_reader xlink:label="LP7JCXLKP7VYU5DNQZSN2BHBOVA" xp:name="alef_reader" xp:description="" xp:fieldtype="folder" has_reader="Yes" is_bordered="No">
                <alef_image xlink:label="LUPSU4UMNV7JUFJTDOICDDVDJSM" xp:name="alef_image" xp:description="" xp:fieldtype="image" alt="">
                    <xp:img href="../../../LUPSU4UMNV7JUFJTDOICDDVDJSM/reader.png" width="1860" height="812">
                        <maplink xlink:name="New Link" name="New Link" xlink:href="../../../1/mlo/T7KP3OIZ2WREPBI2GM7LDEXRZU/tooltip_RDHA2CASDLWUTGRZBZNLS7XDNQ.html#LQ64735LIRKUUPCAPSV6V3G2X4M" href="../../../1/mlo/T7KP3OIZ2WREPBI2GM7LDEXRZU/tooltip_RDHA2CASDLWUTGRZBZNLS7XDNQ.html#LQ64735LIRKUUPCAPSV6V3G2X4M" type="internal" targetid="LQ64735LIRKUUPCAPSV6V3G2X4M" ShowMode="" left="30" right="1121" top="118" bottom="668" />
                    </xp:img>
                </alef_image>
                <alef_audionew xlink:label="LZQTGTYRWJDUUFKDMZSZCD5FRBA" xp:name="alef_audionew" xp:description="" xp:fieldtype="folder">
                    <alef_audiofile xlink:label="LAFMKGC5RYAFUNFHC36DHMNYLBE" xp:name="alef_audiofile" xp:description="" audiocontrols="No" xp:fieldtype="file" src="../../../LAFMKGC5RYAFUNFHC36DHMNYLBE/sampleRnD2.mp3" />
                    <alef_audiotranscript xlink:label="L2HQ36EUTPMOELDUZ6AKHPABASA" xp:name="alef_audiotranscript" xp:description="" xp:fieldtype="text">[{"type":"text","value":"The","ts":0.53,"end_ts":0.75,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Museum","ts":0.77,"end_ts":1.19,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":1.77,"end_ts":1.99,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":2.33,"end_ts":2.55,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Future","ts":2.55,"end_ts":2.83,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"One","ts":4.42,"end_ts":4.64,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":4.66,"end_ts":4.88,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Dubai's","ts":5.15,"end_ts":5.64,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"most","ts":5.87,"end_ts":6.16,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"famous","ts":6.26,"end_ts":6.68,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"landmarks","ts":7.24,"end_ts":7.68,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"is","ts":8.26,"end_ts":8.48,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":8.82,"end_ts":9.04,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Museum","ts":9.1,"end_ts":9.52,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":9.9,"end_ts":10.12,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":10.46,"end_ts":10.68,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Future","ts":10.68,"end_ts":10.96,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"The","ts":11.98,"end_ts":12.2,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"museum","ts":12.2,"end_ts":12.6,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"was","ts":13.14,"end_ts":13.36,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"founded","ts":13.36,"end_ts":13.72,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"by","ts":13.98,"end_ts":14.2,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":14.58,"end_ts":14.8,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Dubai","ts":14.89,"end_ts":15.24,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Future","ts":15.42,"end_ts":15.84,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"Foundation","ts":16.05,"end_ts":16.72,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"on","ts":17.3,"end_ts":17.52,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"February 22, 2022","ts":18.16,"end_ts":21.4,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"The","ts":22.77,"end_ts":22.99,"confidence":0.92},{"type":"punct","value":" "},{"type":"text","value":"Museum","ts":22.99,"end_ts":23.39,"confidence":0.91},{"type":"punct","value":" "},{"type":"text","value":"of","ts":23.53,"end_ts":23.75,"confidence":0.92},{"type":"punct","value":" "},{"type":"text","value":"the","ts":23.75,"end_ts":23.95,"confidence":0.83},{"type":"punct","value":" "},{"type":"text","value":"Future","ts":23.95,"end_ts":24.19,"confidence":0.87},{"type":"punct","value":" "},{"type":"text","value":"was","ts":24.81,"end_ts":25.03,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"created","ts":25.03,"end_ts":25.47,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"to","ts":26.01,"end_ts":26.23,"confidence":0.96},{"type":"punct","value":" "},{"type":"text","value":"allow","ts":26.44,"end_ts":26.79,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"visitors","ts":27.07,"end_ts":27.35,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"to","ts":27.85,"end_ts":28.07,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"look","ts":28.07,"end_ts":28.31,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"beyond","ts":28.73,"end_ts":29.15,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"the","ts":29.49,"end_ts":29.71,"confidence":0.91},{"type":"punct","value":" "},{"type":"text","value":"present","ts":29.71,"end_ts":30.03,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"and","ts":30.65,"end_ts":30.87,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"towards","ts":30.87,"end_ts":31.35,"confidence":0.93},{"type":"punct","value":" "},{"type":"text","value":"the","ts":31.85,"end_ts":32.07,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"possibilities","ts":32.07,"end_ts":32.75,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"of","ts":33.05,"end_ts":33.27,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"the","ts":33.29,"end_ts":33.51,"confidence":0.96},{"type":"punct","value":" "},{"type":"text","value":"future","ts":33.51,"end_ts":33.75,"confidence":0.97},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"There","ts":34.75,"end_ts":35.1,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"you","ts":35.64,"end_ts":35.86,"confidence":0.96},{"type":"punct","value":" "},{"type":"text","value":"can","ts":35.88,"end_ts":36.1,"confidence":0.97},{"type":"punct","value":" "},{"type":"text","value":"explore","ts":36.1,"end_ts":36.58,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"how","ts":37.0,"end_ts":37.22,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"society","ts":37.41,"end_ts":37.9,"confidence":0.98},{"type":"punct","value":" "},{"type":"text","value":"could","ts":38.31,"end_ts":38.66,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"evolve","ts":39.2,"end_ts":39.62,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"in","ts":40.2,"end_ts":40.42,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":40.42,"end_ts":40.58,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"coming","ts":40.58,"end_ts":40.82,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"decades","ts":40.82,"end_ts":41.26,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"using","ts":41.91,"end_ts":42.26,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"science","ts":42.33,"end_ts":42.82,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"and","ts":43.2,"end_ts":43.42,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"technology","ts":43.91,"end_ts":44.58,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"The","ts":45.94,"end_ts":46.16,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"museum","ts":46.16,"end_ts":46.56,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"is","ts":47.02,"end_ts":47.24,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"A","ts":47.56,"end_ts":47.68,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"gateway","ts":47.68,"end_ts":47.92,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"to","ts":48.58,"end_ts":48.8,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":48.82,"end_ts":49.04,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"world","ts":49.04,"end_ts":49.36,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"In","ts":49.78,"end_ts":50.0,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"50","ts":50.25,"end_ts":50.6,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"years","ts":50.69,"end_ts":51.04,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"from","ts":51.19,"end_ts":51.48,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"now","ts":51.58,"end_ts":51.8,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"Each","ts":52.7,"end_ts":52.99,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"floor","ts":53.12,"end_ts":53.47,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":53.53,"end_ts":53.75,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":53.75,"end_ts":53.91,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"museum","ts":53.91,"end_ts":54.23,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"has","ts":54.69,"end_ts":54.91,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"A","ts":55.19,"end_ts":55.31,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"story","ts":55.36,"end_ts":55.71,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"that","ts":56.06,"end_ts":56.35,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"is","ts":56.35,"end_ts":56.55,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"brought","ts":56.55,"end_ts":56.99,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"to","ts":57.01,"end_ts":57.23,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"life","ts":57.3,"end_ts":57.59,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"by","ts":58.41,"end_ts":58.63,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"technology","ts":58.63,"end_ts":59.23,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"such","ts":59.46,"end_ts":59.75,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"as","ts":59.75,"end_ts":59.95,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"augmented","ts":60.66,"end_ts":61.27,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"reality","ts":61.58,"end_ts":62.07,"confidence":0.99},{"type":"punct","value":"."},{"type":"punct","value":" "},{"type":"text","value":"Some","ts":63.66,"end_ts":63.95,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":63.97,"end_ts":64.19,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"the","ts":64.21,"end_ts":64.43,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"topics","ts":64.43,"end_ts":64.71,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"include","ts":65.38,"end_ts":65.87,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"The","ts":66.33,"end_ts":66.55,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"future","ts":66.55,"end_ts":66.91,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"of","ts":67.17,"end_ts":67.39,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"space","ts":67.48,"end_ts":67.83,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"travel","ts":67.85,"end_ts":68.27,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"and","ts":68.53,"end_ts":68.75,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"living","ts":68.81,"end_ts":69.23,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"climate","ts":69.62,"end_ts":70.11,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"change","ts":70.13,"end_ts":70.55,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"and","ts":70.81,"end_ts":71.03,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"ecology","ts":71.55,"end_ts":71.83,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"health","ts":72.37,"end_ts":72.79,"confidence":0.99},{"type":"punct","value":","},{"type":"punct","value":" "},{"type":"text","value":"wellness","ts":73.59,"end_ts":73.67,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"and","ts":74.05,"end_ts":74.27,"confidence":0.99},{"type":"punct","value":" "},{"type":"text","value":"spirituality","ts":74.75,"end_ts":75.55,"confidence":0.97},{"type":"punct","value":"."}]</alef_audiotranscript>
                </alef_audionew>
                <alef_tooltip xlink:label="LRDHA2CASDLWUTGRZBZNLS7XDNQ" xp:name="alef_tooltip" xp:description="" xp:fieldtype="folder">
                    <alef_html xlink:label="LQ64735LIRKUUPCAPSV6V3G2X4M" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../LQ64735LIRKUUPCAPSV6V3G2X4M/emptyHtmlModel.html" />
                    <alef_popupvalue xlink:label="LNAUTOFYYUAOUJILUA4XUL7STRY" xp:name="alef_popupvalue" xp:description="" xp:fieldtype="folder">
                        <alef_section_general xlink:label="LQF7ZW7BZD45EDNNU43OUNFBAMU" xp:name="alef_section_general" xp:description="" xp:fieldtype="folder">
                            <alef_column xlink:label="LPXPIZA3KNPNULDXHZC27T2WH2E" xp:name="alef_column" xp:description="" xp:fieldtype="folder" width="auto">
                                <alef_html xlink:label="LGPVK33AMZRSU5APOSRU2ADCNQI" xp:name="alef_html" xp:description="" xp:fieldtype="html" src="../../../LGPVK33AMZRSU5APOSRU2ADCNQI/emptyHtmlModel.html" />
                            </alef_column>
                        </alef_section_general>
                    </alef_popupvalue>
                </alef_tooltip>
            </alef_reader>
        </alef_column>
    </alef_section>
    """)

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
