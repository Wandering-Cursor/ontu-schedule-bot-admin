from django.views import View

from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

# Create your views here.


class ChatInfoView(View):
    def post(self, *args, **kwargs):
        print(self)
        print(args, kwargs)
        return HttpResponse(None)
