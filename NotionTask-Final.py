import json
import os
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import date


class NotionClient:
    def __init__(self, notion_key):
        self.notion_key = notion_key
        self.default_headers = {
            "Authorization": f"Bearer {self.notion_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def create_database(self, data):
        url = "https://api.notion.com/v1/databases"
        response = self.session.post(url, json=data)
        # print("-----response json----- ", response.json())
        return response.json()

    def get_user_id(self, header):
        url = "https://api.notion.com/v1/users"
        response = requests.get(url, headers=header)
        data = response.json()
        user_list = []
        # Extract and print the user IDs
        if "results" in data:
            results = data["results"]
            print(results)

            for result in results:
                if result.get("type") == "person":
                    user_id = result.get("id")
                    user_list.append(user_id)
                    print("User ID:", user_id)
                    print("---")
        else:
            print("Error:", data.get("message", "Unknown error occurred."))
        # print("-----response json----- ", response.json())
        return user_list


def main(page_id, spreadsheet_id, sheet_name):
    notion_client = NotionClient(os.getenv("NOTION_KEY"))
    # Connect to Google Sheets API
    service_account_file = "credentials2.json"
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes
    )
    service = build("sheets", "v4", credentials=creds)
    # Read data from Google Sheets
    sheet = service.spreadsheets()
    # Get the Sheet with tasks
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    )
    values = result.get("values", [])
    # column_names = values[0]
    task_list = values[1:]
    token = os.getenv("NOTION_KEY")
    print("----------notion Client --------- \n", token)
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    userids = notion_client.get_user_id(headers)
    print("________user id________\n", userids)
    createUrl = "https://api.notion.com/v1/pages"
    current_date = str(date.today())
    # Create a database for each developer
    catches = {
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [
            {
                "type": "text",
                "text": {"content": "user id test 2", "link": None},
            }
        ],
        "properties": {
            "Tasks": {"title": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Incompleted", "color": "red"},
                        {"name": "Completed", "color": "green"},
                    ]
                }
            },
            "Date": {"date": {}},
            "Assignee": {"type": "people", "people": {}},
        },
    }
    catches_create_response = notion_client.create_database(catches)
    # print("_________DAtabase id_____________", catches_create_response["id"])
    # Create tasks in the Notion database
    for ids in userids:
        for task in task_list:
            task_data = {
                "parent": {"database_id": catches_create_response["id"]},
                "properties": {
                    "Tasks": {
                        "title": [{"type": "text", "text": {"content": task[0]}}]
                    },
                    "Status": {"select": {"name": "Incompleted", "color": "red"}},
                    "Date": {"date": {"start": current_date}},
                    "Assignee": {
                        "type": "people",
                        "people": [{"object": "user", "id": ids}],
                    },
                },
            }
            print(
                "-------------------------------------------task data -----------------------------------\n",
                task_data,
            )
            data = json.dumps(task_data)
            res = requests.request("POST", createUrl, headers=headers, data=data)
            # print("Notion Create API response:", res.status_code)
            print(f"Task '{task[0]}' created successfully in the Notion database.")
    return res


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    load_dotenv(override=True)
    parser = argparse.ArgumentParser(
        description="Example script to create Notion databases and import tasks from Google Sheets."
    )
    parser.add_argument(
        "page_id",
        type=str,
        help="A Notion Page ID to create the databases under",
    )
    parser.add_argument(
        "spreadsheet_id",
        type=str,
        help="The ID of the Google Spreadsheet",
    )
    parser.add_argument(
        "sheet_name",
        type=str,
        help="The name of the sheet with tasks in the Google Spreadsheet",
    )

    args = parser.parse_args()
    main(args.page_id, args.spreadsheet_id, args.sheet_name)
