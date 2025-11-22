from main.models.group import Group
from rest_framework import serializers

from ontu_schedule_admin.api.serializers.faculty import FacultySerializer


class GroupSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer()

    class Meta:
        model = Group
        fields = [
            "uuid",
            "short_name",
            "faculty",
        ]
