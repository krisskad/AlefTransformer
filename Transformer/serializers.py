from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    class Meta:
        fields = ['file', ]


class DeleteSerializer(serializers.Serializer):
    folder_name = serializers.CharField(required=True)
    class Meta:
        fields = ['folder_name', ]