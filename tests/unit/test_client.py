import os

import pytest
import requests
from requests.exceptions import (
    ConnectTimeout,
    HTTPError,
    ProxyError,
    ReadTimeout,
    SSLError,
    TooManyRedirects,
)
from requests.models import Response


from crux._client import CruxClient
from crux.exceptions import (
    CruxClientConnectionError,
    CruxClientHTTPError,
    CruxClientTimeout,
    CruxClientTooManyRedirects,
)
from crux.models.model import CruxModel


class SampleModel(CruxModel):
    @property
    def attr_1(self):
        return self.raw_model["attr1"]

    @attr_1.setter
    def attr_1(self, attr_1):
        self.raw_model["attr1"] = attr_1

    @property
    def attr_2(self):
        return self.raw_model["attr2"]

    @attr_2.setter
    def attr_2(self, attr_2):
        self.raw_model["attr1"] = attr_2


@pytest.fixture
def client():
    os.environ["CRUX_API_KEY"] = "1235"
    return CruxClient(crux_config=None)


def monkeypatch_delete_call(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    json=None,
    data=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    delete_resp = Response()
    delete_resp.status_code = 204
    return delete_resp


def test_client_delete(client, monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", monkeypatch_delete_call)
    resp = client.api_call(
        method="DELETE", path=["test-path"], model=None, headers=None
    )

    assert resp is True


def monkeypatch_get_call_with_no_model(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    json=None,
    data=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    get_resp = Response()
    get_resp.status_code = 200
    get_resp._content = b'{"data":"dummy"}'
    return get_resp


def test_client_get_with_no_model(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session, "request", monkeypatch_get_call_with_no_model
    )
    resp = client.api_call(method="GET", path=["test-path"], model=None, headers=None)

    assert resp.json() == {"data": "dummy"}


def monkeypatch_get_call(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    json=None,
    data=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    get_resp = Response()
    get_resp.status_code = 200
    get_resp._content = b'{"attr1":"dummy1","attr2":"dummy2"}'
    return get_resp


def test_client_get_with_model(client, monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", monkeypatch_get_call)

    resp = client.api_call(method="GET", path=["test-path"], model=SampleModel)

    assert resp.attr_1 == "dummy1"
    assert resp.attr_2 == "dummy2"


def monkeypatch_post_call(
    self,
    method=None,
    url=None,
    headers=None,
    stream=False,
    params=None,
    data=None,
    json=None,
    proxies=None,
    timeout=None,
):
    get_resp = Response()
    get_resp.status_code = 200
    get_resp._content = b'{"attr1":"dummy1","attr2":"dummy2"}'
    return get_resp


def test_client_post(client, monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", monkeypatch_post_call)
    sample_obj = SampleModel(raw_model={"attr1": "dummy1", "attr2": "dummy2"})
    resp = client.api_call(
        method="POST", path=["test-path"], model=SampleModel, json=sample_obj.raw_model
    )

    assert resp.attr_1 == "dummy1"
    assert resp.attr_2 == "dummy2"


def monkeypatch_put_call(
    self,
    method=None,
    url=None,
    headers=None,
    stream=False,
    json=None,
    params=None,
    data=None,
    proxies=None,
    timeout=None,
):
    get_resp = Response()
    get_resp.status_code = 200
    get_resp._content = b'{"attr1":"dummy1","attr2":"dummy2"}'
    return get_resp


def test_client_put(client, monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", monkeypatch_put_call)
    sample_obj = SampleModel(raw_model={"attr1": "dummy1", "attr2": "dummy2"})
    resp = client.api_call(
        method="PUT", path=["test-path"], model=SampleModel, json=sample_obj.raw_model
    )

    assert resp.attr_1 == "dummy1"
    assert resp.attr_2 == "dummy2"


def monkeypatch_get_list_call(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    get_resp = Response()
    get_resp.status_code = 200
    get_resp._content = (
        b'[{"attr1":"dummy1","attr2":"dummy2"},{"attr1":"dummy3","attr2":"dummy4"}]'
    )
    return get_resp


def test_client_get_list_with_model(client, monkeypatch):
    monkeypatch.setattr(requests.sessions.Session, "request", monkeypatch_get_list_call)

    resp = client.api_call(method="GET", path=["test-path"], model=SampleModel)

    assert resp[0].attr_1 == "dummy1"
    assert resp[0].attr_2 == "dummy2"
    assert resp[1].attr_1 == "dummy3"
    assert resp[1].attr_2 == "dummy4"


def monkeypatch_client_http_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    response = Response()
    response.status_code = 404
    raise HTTPError("Test HTTP Error", response=response)


def test_client_http_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session, "request", monkeypatch_client_http_exception
    )

    with pytest.raises(CruxClientHTTPError) as http_error:
        client.api_call(method="GET", path=["test-path"], model=SampleModel)
    assert http_error.value.response.status_code == 404


def monkeypatch_test_client_proxy_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    raise ProxyError("Test Proxy Error")


def test_client_proxy_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session, "request", monkeypatch_test_client_proxy_exception
    )

    with pytest.raises(CruxClientConnectionError):
        client.api_call(method="GET", path=["test-path"], model=SampleModel)


def monkeypatch_test_client_ssl_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    raise SSLError("Test Proxy Error")


def test_client_ssl_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session, "request", monkeypatch_test_client_ssl_exception
    )

    with pytest.raises(CruxClientConnectionError):
        client.api_call(method="GET", path=["test-path"], model=SampleModel)


def monkeypatch_test_client_connect_timeout_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    raise ConnectTimeout("Test Connect Timeout Error")


def test_client_connect_timeout_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session,
        "request",
        monkeypatch_test_client_connect_timeout_exception,
    )

    with pytest.raises(CruxClientTimeout):
        client.api_call(method="GET", path=["test-path"], model=SampleModel)


def monkeypatch_test_client_read_timeout_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    raise ReadTimeout("Test Connect Timeout Error")


def test_client_read_timeout_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session,
        "request",
        monkeypatch_test_client_read_timeout_exception,
    )

    with pytest.raises(CruxClientTimeout):
        client.api_call(method="GET", path=["test-path"], model=SampleModel)


def monkeypatch_test_too_many_redirects_exception(
    self,
    method=None,
    url=None,
    headers=None,
    params=None,
    data=None,
    json=None,
    stream=False,
    proxies=None,
    timeout=None,
):
    raise TooManyRedirects("Test Connect Timeout Error")


def test_client_too_many_redirects_exception(client, monkeypatch):
    monkeypatch.setattr(
        requests.sessions.Session,
        "request",
        monkeypatch_test_too_many_redirects_exception,
    )

    with pytest.raises(CruxClientTooManyRedirects):
        client.api_call(method="GET", path=["test-path"], model=SampleModel)
