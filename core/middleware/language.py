from django.utils import translation


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get("lang")
        allowed = {"en", "ko"}
        if lang and lang in allowed:
            with translation.override(lang):
                request.LANGUAGE_CODE = lang
                response = self.get_response(request)
                return response
        response = self.get_response(request)
        return response
