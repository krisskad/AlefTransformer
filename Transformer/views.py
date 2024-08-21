from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from Transformer.main import process_data, iterative_process_data

import os
import datetime
import zipfile
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from django.conf import settings
import shutil
from .serializers import FileUploadSerializer, DeleteSerializer  # Import your serializer
from .helpers import zip_folder_contents, validate_inputs_dirs, replace_chars_in_json  # Import your function to process the zip file
import termOneTransformer.helpers as termOneHelpers
import termOneTransformer.main as termOneMain

def index(request):
    return render(request, 'index.html')


class HomeView(ViewSet):
    def list(self, request):
        return Response(status=status.HTTP_200_OK,
                        data={"query": "str", "user_id": "str", "reference_number": "int", "prompt": "str"})

    def post(self, request):
        process_data()
        return Response(
            status=status.HTTP_200_OK,
            data={}
        )


class UploadViewSet(viewsets.ViewSet):
    parser_classes = [FileUploadParser]
    serializer_class = FileUploadSerializer

    def list(self, request):
        return Response({'zip_file_url': "str", 'log_file_url': "str"})

    def post(self, request):
        if not 'file' in request.data:
            return Response({'error': 'File key not found in request data'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.data['file']  # Assuming the file is sent as 'file' in the request
        template_ids = request.data.get("template_ids", None)  # Assuming the file is sent as 'file' in the request

        # Create a folder for the current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_data_folder = f"media/{current_time}"
        output_folder = str(settings.OUTPUT_DIR)
        os.makedirs(output_data_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        # Save the uploaded zip file to the 'INPUT' folder
        input_folder = str(settings.INPUT_DIR)
        os.makedirs(input_folder, exist_ok=True)
        input_zip_path = os.path.join(input_folder, uploaded_file.name)

        with open(input_zip_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Extract the zip file into the 'INPUT' folder
        with zipfile.ZipFile(input_zip_path, 'r') as zip_ref:
            zip_ref.extractall(input_folder)

        # Call the function to process the zip content
        process_data(template_ids=template_ids)

        # remove input data
        shutil.rmtree(input_folder)

        # zipping output
        print("zipping output")

        zip_folder_contents(
            folder_path=str(output_folder),
            zip_filename=str(os.path.join(settings.BASE_DIR, output_data_folder, "output.zip"))
        )

        # remove output data
        shutil.rmtree(output_folder)

        # Return the URL to the created zip file and log file
        zip_file_url = f"media/{current_time}/output.zip"
        log_file_url = f"media/{current_time}/log.txt"  # Replace 'your_log_file.txt' with the actual log file name

        return Response({'zip_file_url': zip_file_url, 'log_file_url': log_file_url, "folder_name": current_time})


class DeleteFolderViewSet(viewsets.ViewSet):
    serializer_class = DeleteSerializer

    def create(self, request):
        folder_name = request.data.get('folder_name')

        if folder_name:
            folder_path = f"media/{folder_name}"  # Assuming folders are in the 'media' directory
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)  # if you want to delete folders recursively
                    # os.rmdir(folder_path)  # This deletes only empty directories
                    return Response({'message': f"Folder '{folder_name}' deleted successfully"})
                except Exception as e:
                    return Response({'error': f"Failed to delete folder: {str(e)}"}, status=500)
            else:
                return Response({'error': f"Folder '{folder_name}' does not exist"}, status=404)
        else:
            return Response({'error': 'Please provide a folder_name'}, status=400)


class LocalFileProcessViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({'zip_file_url': "str", 'log_file_url': "str"})

    def post(self, request):
        input_dir = request.data.get("courses_path", None)  # Assuming the file is sent as 'file' in the request
        output_dir = request.data.get("output_path", None)  # Assuming the file is sent as 'file' in the request
        common_dir = request.data.get("common_path", None)  # Assuming the file is sent as 'file' in the request
        term = request.data.get("terms", None)

        if term == "Term 1":
            all_dir_list = termOneHelpers.validate_inputs_dirs(input_dir=input_dir, output_dir=output_dir, common_dir=common_dir)
            if isinstance(all_dir_list, dict):
                return Response(data=all_dir_list)
            resp = termOneMain.iterative_process_data(all_dir_objs=all_dir_list, input_dir=input_dir)
        elif term == "Term 2":
            all_dir_list = validate_inputs_dirs(
                input_dir=input_dir,
                output_dir=output_dir,
                common_dir=common_dir
            )

            if isinstance(all_dir_list, dict):
                return Response(data=all_dir_list)

            # replace all with '
            # for each in all_dir_list:
            #     for key, each_file in each.items():
            #         print(each_file)
            #         if os.path.isfile(each_file) and ".json" in each_file:
            #             replace_chars_in_json(json_path=each_file)

            # Call the function to process the zip content
            resp = iterative_process_data(all_dir_objs=all_dir_list)

        return Response(data=resp)

