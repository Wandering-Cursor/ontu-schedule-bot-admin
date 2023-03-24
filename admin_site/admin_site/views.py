"""
Core site views
"""
from rest_framework.views import APIView

from django.http.request import HttpRequest
from django.shortcuts import render


class BaseView(APIView):
    """A view that just returns ok for top level requests"""
    def get(self, request: HttpRequest):
        """ok for GET"""
        return render(
            request=request,
            template_name="templates/base.html"
        )

    def post(self, request: HttpRequest):
        """ok for POST"""
        return render(
            request=request,
            template_name="templates/base.html"
        )
