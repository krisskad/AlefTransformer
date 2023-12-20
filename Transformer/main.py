import importlib
from django.conf import settings
from Transformer.helpers import read_json


def call_package(page_data):
    template_id = page_data['pageData']['templateID']

    try:
        package_name = f"templates.{template_id}.processor"
        module = importlib.import_module(package_name)
        print(f"Package found for templateID: {template_id}")
        return module.process_page_data(page_data)
    except ModuleNotFoundError:
        print(f"No package found for templateID: {template_id}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def process_data():
    INPUT_STRUCTURE_JSON_DATA = read_json(
        file_path=settings.INPUT_STRUCTURE_JSON
    )
    input_pages = INPUT_STRUCTURE_JSON_DATA.get('pages', [])

    MLO_TEMPLATES_OUTPUT_LIST = []
    for item in input_pages:
        section = call_package(item)
        if section:
            MLO_TEMPLATES_OUTPUT_LIST.append(section)
