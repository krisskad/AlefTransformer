
from .text_with_images import get_text_with_image_xml
from .text_left import get_text_left_xml


def create_mlo(input_json_data, input_other_jsons_data, exiting_hashcode):

    try:
        imageContent_list = input_json_data["pageData"]["args"]["textFieldData"].get("imageContent")

        if len(imageContent_list)>1:
            print("Text with Images")
            return get_text_with_image_xml(
                input_json_data, input_other_jsons_data, exiting_hashcode
            )
        else:
            # print("Text- Left")
            return get_text_left_xml(
                input_json_data, input_other_jsons_data, exiting_hashcode
            )
    except Exception as e:
        print(f"Error: TextwithImage_001 --> {e}")
        return {}


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
        raise Exception(f"Error: {e}")
    return xml_output
