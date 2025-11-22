from main.models.teacher import Teacher
from rest_framework import serializers

from ontu_schedule_admin.api.serializers.department import DepartmentSerializer


class TeacherSerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Teacher
        fields = [
            "uuid",
            "short_name",
            "full_name",
            "departments",
        ]
