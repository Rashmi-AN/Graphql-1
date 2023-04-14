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
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]["nodes"]
        count += len([d for d in discussions if d["locked"] is True])
        has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
        if has_next_page:
            cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
        else:
            break
    else:
        print("Request failed with status code:", response.status_code)
        break

print(f"Total count of locked discussions: {count}")


