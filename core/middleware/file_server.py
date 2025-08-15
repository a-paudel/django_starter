from typing import Any

from django.http import FileResponse, HttpRequest

from config import settings


class ServeStaticFilesMiddleware:
    def __init__(self, next) -> None:
        self.next = next

    def __call__(self, request: HttpRequest) -> Any:
        path = request.path_info.removeprefix("/")
        if path.startswith(settings.STATIC_URL):
            # serve static file
            file = settings.STATIC_ROOT / path.removeprefix(settings.STATIC_URL)
            if file.exists():
                return FileResponse(file.open("rb"))

        resp = self.next(request)
        return resp


class ServeMediaFilesMiddleware:
    def __init__(self, next) -> None:
        self.next = next

    def __call__(self, request: HttpRequest) -> Any:
        path = request.path_info.removeprefix("/")
        if path.startswith(settings.MEDIA_URL):
            # serve MEDIA file
            file = settings.MEDIA_ROOT / path.removeprefix(settings.MEDIA_URL)
            if file.exists():
                return FileResponse(file.open("rb"))

        resp = self.next(request)
        return resp
