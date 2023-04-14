import requests
import json

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("Please add the config file path")

name_of_community = config.get("COMMUNITY_NAME", "name")

query = """
query ($cursor: String) {
  repository(owner: "%s", name: "community") {
    discussions(first: 100, after: $cursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        locked
        category{
            name
      }
    }
  }
}
}
""" % name_of_community
token_details = config.get("BEARER", "token")

url = 'https://api.github.com/graphql'
headers = {"Authorization": "bearer " +token_details}

cursor = None
count = 0

while True:
    variables = {'cursor': cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        try:
            json_data = json.loads(response.text)
            discussions = json_data["data"]["repository"]["discussions"]["nodes"]
            count += len([d for d in discussions if d["locked"] is True and d["category"] != "announcements"])
            has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
            if has_next_page:
                cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
            else:
                break
        except KeyError as e:
            print("Response missing expected fields:", e)
            print(response.content)
            break
        except Exception as e:
            print("Error processing response:", e)
            print(response.content)
            break
    else:
        print("Request failed with status code:", response.status_code)
        print(response.content)
        break

print(f"Total count of locked discussions (excluding announcements category): {count}")


