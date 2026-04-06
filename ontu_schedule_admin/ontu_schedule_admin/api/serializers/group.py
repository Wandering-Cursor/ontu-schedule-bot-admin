from main.models.group import Group
from ontu_schedule_admin.api.serializers.faculty import FacultySerializer
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer()

    class Meta:
        model = Group
        fields = [
            "uuid",
            "short_name",
            "faculty",
        ]
