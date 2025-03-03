from requests import Response, request
from .enums import FetchMethodEnum


def fetch(
    url: str,
    method: FetchMethodEnum = FetchMethodEnum.GET,
    **kwargs,
) -> Response | None:
    """
    :param url: URL to fetch
    :param method: Fetch method
    :param kwargs: Additional arguments to pass to requests library, refer to https://docs.python-requests.org/en/master/api/#requests.request for more information

    :return: Response object if successful, None otherwise
    """
    try:
        response = request(
            method.value,
            url,
            **kwargs,
        )
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"Fetch Exception - {e}")
        return None
