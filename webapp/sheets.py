import json
import yaml
import os
from typing import List, Dict, Any

from google.cloud import storage
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.auth.transport.requests import Request


SPREADSHEET_ID = "144Gb6lhsflflL6MfCQcMSEsQDK819A_5EuZa6_rFtHk"
# TODO: define all questions in file and generate form/headers/etc from that yaml file
question_file = "./questions.yaml"
assert os.path.exists(question_file), question_file
with open(question_file, "r") as question_def_file:
    question_def_dicts = yaml.safe_load_all(question_def_file)
    HEADERS = [d["label"] for d in question_def_dicts] + [
        "password"
    ]  # password is stored in sheet, but not a question in survey

sheets_service = None


def init_sheets_service():
    global sheets_service
    if sheets_service:
        return sheets_service
    else:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            "./secret.json", scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=credentials)
        sheets_service = service.spreadsheets()
        return sheets_service


def get_all_sheet_titles():
    sheets_service = init_sheets_service()
    return [
        x["properties"]["title"]
        for x in sheets_service.get(spreadsheetId=SPREADSHEET_ID)
        .execute()
        .get("sheets")
    ]


def create_tab(tab_name):
    sheets_service = init_sheets_service()
    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": tab_name,
                    }
                }
            }
        ]
    }
    result = sheets_service.batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body
    ).execute()
    print(result)
    write_to_sheet(tab_name, HEADERS)


def submit_to_survey(data):
    for h in HEADERS:
        assert h in data
    write_to_sheet(
        data["School"],
        [data[h] for h in HEADERS],
    )


def write_to_sheet(tab_name: str, values: List[str]):
    sheets_service = init_sheets_service()
    if tab_name not in get_all_sheet_titles():
        create_tab(tab_name)
    value_range_body = {"values": [values]}
    request = sheets_service.values().append(
        range=f"{tab_name}",
        spreadsheetId=SPREADSHEET_ID,
        body=value_range_body,
        valueInputOption="RAW",
    )
    response = request.execute()
    print(response)


cache = {}


def get_sheet_data(tab_name: str) -> Dict[str, List[Dict[str, str]]]:
    global cache
    sheets_service = init_sheets_service()
    if tab_name in cache:
        print(f"Sheets cache hit for {tab_name}")
        return cache[tab_name]
    else:
        result = (
            sheets_service.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=f"{tab_name}")
            .execute()
        )
        values = result["values"]
        keys = values[0]
        sheet = []
        for data in values[1:]:
            row = {k: v for (k, v) in zip(keys, data)}
            sheet.append(row)
        cache[tab_name] = sheet
        return cache[tab_name]


def get_schools():
    sheets_service = init_sheets_service()
    result = sheets_service.get(spreadsheetId=SPREADSHEET_ID).execute()
    all_sheets = [x["properties"]["title"] for x in result["sheets"]]
    # TODO: fix
    return [x for x in all_sheets if "Email" not in x]
