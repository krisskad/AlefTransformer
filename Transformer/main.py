import importlib
from django.conf import settings


def call_package(page_data):
    template_id = page_data['pageData']['templateID']

    try:
        package_name = f"templates.{template_id}.processor"
        module = importlib.import_module(package_name)
        return module.process_page_data(page_data)
    except ModuleNotFoundError:
        print(f"No package found for templateID: {template_id}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_data(data):
    for item in data:
        section = call_package(item)


# Example list of dictionaries
data_list = [
    {
        "pageType": "Misc",
        "pageData": {
            "viewRef": "page_002",
            "templateID": "ClicktoRevealwithSubmit_001",
            "args": {
                "ques": "text_007",
                "src": "aud_001",
                "background": {
                    "type": "class",
                    "src": "bg_backgroundColor_2"
                },
                "submitCount": 2,
                "multiAnswer": True,
                "thumbs": [
                    {
                        "image": "img_002",
                        "title": "text_008",
                        "ans": 1
                    },
                    {
                        "image": "img_015",
                        "title": "text_009",
                        "ans": 0
                    },
                    {
                        "image": "img_020",
                        "title": "text_010",
                        "ans": 0
                    },
                    {
                        "image": "img_007",
                        "title": "text_011",
                        "ans": 0
                    }
                ],
                "submit": "text_012",
                "showAnswer": "text_013",
                "feedback": {
                    "correct": "text_014",
                    "incorrect_1": "text_015",
                    "incorrect_2": "text_016"
                },
                "feedBackAudio": {
                    "correct": "aud_001",
                    "incorrect_1": "aud_002",
                    "incorrect_2": "aud_003",
                    "hint": "aud_004"
                },

                "hint": {
                    "text": "text_017"
                }
            }
        }
    }
]

process_data(data_list)
