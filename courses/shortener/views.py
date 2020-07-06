from django.db import IntegrityError
from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import redirect

from .models import URLShortener


class LengthenURL(APIView):
    def get(self, request: Request, shortHash: str):
        shortener: URLShortener = URLShortener.objects.get(
            shortHash=shortHash
        )

        redirectURL: str = request.get_host() + shortener.urlSuffix
        print(shortener.urlSuffix)

        return redirect(shortener.urlSuffix)


def shortenURL(urlSuffix: str) -> str:
    """This function is used to shorten the length of the URL. This
    function does not have any associated with any URL.

    :param urlSuffix: The absolute address that has to be shortened. For
        example, '/media/courses/images/image.png'.

    :return: The first 15 characters of the SHA256 hash generated for
        the URL.
    :rtype: str
    """
    # Create and save this URL.
    try:
        shortener = URLShortener.objects.create(urlSuffix=urlSuffix)
    except IntegrityError:
        # This URL pattern already has a hash stored.
        existingURL: URLShortener = URLShortener.objects.get(
            urlSuffix=urlSuffix
        )

        return existingURL.shortHash

    return shortener.shortHash
