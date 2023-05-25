import os
import requests
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import date
import json


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

    def get_pages(self, db_id, headers):
        url = f"https://api.notion.com/v1/databases/{db_id}/query/"
        payload = {"page_size": 1000}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        # print("---------data-----------\n", data)
        import json

        with open("db.json", "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        results = data["results"]
        # print("---------resutls-----------\n", results)
        return results


def main(db_id, spreadsheet_id, sheet_name):
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
    pages = notion_client.get_pages(db_id, headers)
    print("pages-- ", pages)
    assignee_list, tasks_list = [], []
    for page in pages:
        # page_id = page["id"]
        props = page["properties"]
        assignee = props["Assignee"]["people"][0]["id"]
        tasks = props["Tasks"]["title"][0]["text"]["content"]
        assignee_list.append(assignee)
        tasks_list.append(tasks)
    print("List of assignee and tasks :", assignee_list, tasks_list)
    # Create tasks in the Notion database
    # if assignee and task already exist from the above loop result skip  the task assignment if not create it
    for ids in userids:
        for task in task_list:
            task_data = {
                "parent": {"database_id": db_id},
                "properties": {
                    "Tasks": {
                        "title": [{"type": "text", "text": {"content": task[0]}}]
                    },
                    "Status": {"select": {"name": "Incomplete", "color": "red"}},
                    "Date": {"date": {"start": current_date}},
                    "Assignee": {
                        "type": "people",
                        "people": [{"object": "user", "id": ids}],
                    },
                },
            }
            data = json.dumps(task_data)
            res = requests.request("POST", createUrl, headers=headers, data=data)
            print(
                f"Task '{task[0]}' created successfully for user ID '{ids}' in the Notion database."
            )
    return res


# dbid='91fb481d21f74876b41353c322b1d320'
if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    load_dotenv(override=True)
    parser = argparse.ArgumentParser(
        description="Example script to create Notion databases and import tasks from Google Sheets."
    )
    parser.add_argument(
        "db_id",
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
    main(args.db_id, args.spreadsheet_id, args.sheet_name)
