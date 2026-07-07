from typing import Union

import requests
from requests.auth import HTTPBasicAuth


class HTTPAuth:
    @staticmethod
    def HTTPAuthBasic(
        username: Union[str, bytes], password: Union[str, bytes], **kwargs
    ) -> HTTPBasicAuth:
        return HTTPBasicAuth(username=username, password=password)


class HTTPBasicRequest(requests):
    def __init__(self):
        super().__init__()
