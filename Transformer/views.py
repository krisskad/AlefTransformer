from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from Transformer.main import process_data
import zipfile
import os
import csv
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


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


class ZipHandlingViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def handle_zip(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']

        # Ensure the 'INPUT' and 'OUTPUT' directories exist
        input_dir = 'INPUT'
        output_dir = 'OUTPUT'
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Save the uploaded zip file to 'INPUT' directory
        with open(os.path.join(input_dir, uploaded_file.name), 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Extract the uploaded zip file to 'INPUT' directory
        with zipfile.ZipFile(os.path.join(input_dir, uploaded_file.name), 'r') as zip_ref:
            zip_ref.extractall(input_dir)

        # Create a new zip file from 'OUTPUT' directory contents
        output_zip_path = os.path.join(output_dir, 'output.zip')
        with zipfile.ZipFile(output_zip_path, 'w') as output_zip:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, output_dir)
                    output_zip.write(file_path, arcname=rel_path)

        # Create a CSV file for logs
        logs_file_path = os.path.join(output_dir, 'logs.csv')
        with open(logs_file_path, 'w', newline='') as logs_csv:
            csv_writer = csv.writer(logs_csv)
            csv_writer.writerow(['Log Entry 1', 'Log Entry 2', 'Log Entry 3'])  # Add your log entries here

        # Prepare the HTTP response with the zipped file and logs.csv
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="output.zip"'

        # Write the output zip file to the response
        with open(output_zip_path, 'rb') as output_zip_file:
            response.write(output_zip_file.read())

        # Add logs.csv to the response
        with open(logs_file_path, 'rb') as logs_csv_file:
            response.write(logs_csv_file.read())

        # Cleanup: Remove uploaded file and generated files
        os.remove(os.path.join(input_dir, uploaded_file.name))
        os.remove(output_zip_path)
        os.remove(logs_file_path)

        return response
