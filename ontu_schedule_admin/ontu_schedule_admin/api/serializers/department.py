from main.models.department import Department
from rest_framework import serializers


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "uuid",
            "short_name",
            "full_name",
        ]
