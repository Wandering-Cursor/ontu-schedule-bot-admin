from main.models.faculty import Faculty
from rest_framework import serializers


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = [
            "uuid",
            "short_name",
        ]
