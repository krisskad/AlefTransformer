import os
from django.conf import settings
from Transformer.helpers import write_xml, generate_unique_folder_name

IMSMANIFEST_XML = """
<?xml version="1.0" encoding="utf-8"?>
<manifest
	xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
	xmlns:xp="http://www.giuntilabs.com/exact/xp_v1d0"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd  http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p2.xsd  http://www.giuntilabs.com/exact/xp_v1d0 xp_v1d0.xsd" version="1.0" identifier="_7OF76UUEBREUDOH3HSLHK4ZD7A" xp:packtype="lo">
	<organizations />
	<resources>
        {}
	</resources>
</manifest>
"""


def write_imsmanifest_xml(all_manifest_files, exiting_hashcode, input_other_jsons_data, courseID):
    file_tags = []
    mlo_html_path = ""
    mlo_html_folder_hash = ""
    for each in all_manifest_files:
        if "1/mlo/" in each and "mlo.html" in each:
            mlo_html_path = each
            mlo_html_folder_hash = each.replace("1/mlo/", "").replace("/mlo.html", "")
        temp = f"""<file href="{each}" />"""
        file_tags.append(temp)

    file_tag_string = "\n".join(file_tags)

    resource_html = f"""
    <resource identifier="res{mlo_html_folder_hash}" type="webcontent" href="{mlo_html_path}" xp:type="lo">
        <metadata>
            <schema>IMS Content</schema>
            <schemaversion>1.1</schemaversion>
            <lom
                xmlns="http://www.imsglobal.org/xsd/imsmd_v1p2">
                <general>
                    <title>
                        <langstring xml:lang="x-none">{courseID}</langstring>
                    </title>
                </general>
            </lom>
        </metadata>
        {file_tag_string}
    </resource>
    """

    hashcode = generate_unique_folder_name(existing_hashcode=exiting_hashcode, prefix="_", k=27)

    ims_file_content = f"""
    <?xml version="1.0" encoding="utf-8"?>
    <manifest
        xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
        xmlns:xp="http://www.giuntilabs.com/exact/xp_v1d0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd  http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p2.xsd  http://www.giuntilabs.com/exact/xp_v1d0 xp_v1d0.xsd" version="1.0" identifier="{hashcode}" xp:packtype="lo">
        <organizations />
        <resources>
            {resource_html}
        </resources>
    </manifest>
    """
    ims_file_content = ims_file_content.replace("\n\n", "\n")
    file_path = os.path.join(settings.OUTPUT_DIR, "imsmanifest.xml")

    write_xml(
        xml_content=ims_file_content,
        file_path=file_path
    )

    return True
