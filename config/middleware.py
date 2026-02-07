from django.utils import translation

class ForceDefaultLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        translation.activate('fa')
        request.LANGUAGE_CODE = 'fa'
        response = self.get_response(request)
        return response
