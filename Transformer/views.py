from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
from Transformer.main import process_data


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