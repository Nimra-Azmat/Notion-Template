import requests

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# Define your Notion API key
# NOTION_API_KEY = "secret_14kL4bIykQ8C6mqbRm3y0jPnHM3vduJIe9XYMt8wOz4"
NOTION_API_KEY = "secret_XlKy7czcwez7UfyBfLpSYHXN8lWp3hOfAOhiD3sSkJ5"

# Set the Notion API endpoint and headers
url = "https://api.notion.com/v1/users"
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16",
}

# Send a GET request to retrieve user data
response = requests.get(url, headers=headers)
data = response.json()
userlist = []
# Extract and print the user IDs
if "results" in data:
    results = data["results"]
    print(results)

    for result in results:
        # if result.get("type") == "person":
        user_id = result.get("id")
        user_name = result.get("name", "Unknown")
        mail = result.get("person", "none")
        userlist.append(user_id)
        print("User ID:", user_id)
        print("User Name:", user_name)
        print("User mail:", mail)
        print("---")
else:
    print("Error:", data.get("message", "Unknown error occurred."))
print(userlist)


# # Define the scope and credentials file
# scope = [
#     "https://spreadsheets.google.com/feeds",
#     "https://www.googleapis.com/auth/drive",
# ]
# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     "credentials2.json", scope
# )
# client = gspread.authorize(credentials)

# sheet = client.open("Developers_List").get_worksheet(1)  # Index 1 represents Sheet 2


# values = userlist

# existing_data = sheet.col_values(1)


# new_values = [value for value in values if value not in existing_data]

# # Append the new values to the existing data
# updated_data = existing_data + new_values

# # Clear the current data in the first column of Sheet 2
# sheet.update("A1:A", [[]])

# # Update the first column of Sheet 2 with the updated values
# for i, value in enumerate(updated_data, start=1):
#     sheet.update_cell(i, 1, value)

# print("Values added successfully.")
