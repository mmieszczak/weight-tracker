import datetime
import json
from http import HTTPStatus

import pytest
import requests


@pytest.mark.parametrize(
    ["data", "response_code"],
    (
        ({"date": "2023-01-01", "value": "70"}, HTTPStatus.OK),
        ({"date": "2023-01-01", "value": 70}, HTTPStatus.OK),
        ({"date": "2023-01-01", "value": 75.5}, HTTPStatus.OK),
        ({}, HTTPStatus.BAD_REQUEST),
        ({"value": 69.9}, HTTPStatus.BAD_REQUEST),
        ({"date": "2023-01-01"}, HTTPStatus.BAD_REQUEST),
        ({"date": "2023-01-01", "value": "invalid value"}, HTTPStatus.BAD_REQUEST),
        ({"date": "2023-13-32", "value": 80}, HTTPStatus.BAD_REQUEST),
        ({"date": "invalid date", "value": 80}, HTTPStatus.BAD_REQUEST),
    ),
)
def test_post(server: str, data, response_code: int):
    r = requests.post(f"http://{server}/record", json=data)
    assert r.status_code == response_code


def test_post_missing_content_type(server: str):
    data = {"date": "2023-01-01", "value": 80}
    r = requests.post(f"http://{server}/record", data=json.dumps(data))
    assert r.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("method", ("GET", "POST", "PUT"))
def test_invalid_path(server: str, method: str):
    r = requests.request(method, f"http://{server}/invalid/path")
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_post_and_get(server: str):
    date = "2023-05-15"
    data = {"date": date, "value": 99.0}
    r = requests.post(f"http://{server}/record", json=data)
    r.raise_for_status()
    r = requests.get(f"http://{server}/record", params={"date": date})
    r.raise_for_status()
    assert r.json() == data


@pytest.mark.parametrize("params", ({}, {"date": "invalid format"}))
def test_get_invalid(server: str, params: dict[str, str]):
    r = requests.get(f"http://{server}/record", params=params)
    assert r.status_code == HTTPStatus.BAD_REQUEST


def test_get_not_existing(server: str):
    r = requests.get(f"http://{server}/record", params={"date": "2023-05-15"})
    assert r.status_code == HTTPStatus.NOT_FOUND


def test_post_existing(server: str):
    r = requests.post(
        f"http://{server}/record", json={"date": "2023-05-15", "value": 60}
    )
    r.raise_for_status()
    r = requests.post(
        f"http://{server}/record", json={"date": "2023-05-15", "value": 61}
    )
    assert r.status_code == HTTPStatus.CONFLICT


@pytest.mark.parametrize(
    "data",
    (
        (),
        (("2023-01-15", 99.9),),
        (("2023-01-15", 72.3), ("2023-01-16", 73.5), ("2023-01-17", 75)),
        (("2023-01-17", 75), ("2023-01-16", 73.5), ("2023-01-15", 72.3)),
    ),
)
def test_post_and_get_many(server: str, data: tuple[tuple[str, float], ...]):
    for date, value in data:
        json = {"date": date, "value": value}
        r = requests.post(f"http://{server}/record", json=json)
        r.raise_for_status()
    r = requests.get(f"http://{server}/records")
    expected_records = [{"date": x[0], "value": x[1]} for x in data]
    expected_records.sort(key=lambda x: datetime.date.fromisoformat(x["date"]))
    expected = {"records": expected_records}
    assert r.json() == expected
