from admin_site_database.model_files.message_campaign import MessageCampaign
from admin_site_endpoints.views.BaseAPIView import BaseAPIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


class GetMessageCampaign(BaseAPIView):
    def get(self, request: Request):
        campaign_id = request.query_params.get("campaign_id")
        if not campaign_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        campaign = MessageCampaign.objects.filter(id=campaign_id).first()
        if not campaign:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(data=campaign.as_json())
