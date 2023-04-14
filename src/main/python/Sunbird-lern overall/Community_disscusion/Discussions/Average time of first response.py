import requests
import json
from datetime import datetime

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
        id
        createdAt
        comments(first: 1) {
          nodes {
            createdAt
          }
        }
      }
    }
  }
}
""" % name_of_community
token_details = config.get("BEARER", "token")

url = 'https://api.github.com/graphql'
headers = {"Authorization": "bearer " + token_details}

cursor = None
count = 0
total_response_time = 0

while True:
    variables = {'cursor': cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]["nodes"]
        for d in discussions:
            if d["comments"]["nodes"]:
                posted_time = datetime.strptime(d["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                response_time = datetime.strptime(d["comments"]["nodes"][0]["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                total_response_time += (response_time - posted_time).total_seconds()
                count += 1
        has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
        if has_next_page:
            cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
        else:
            break
    else:
        print("Request failed with status code:", response.status_code)
        break

if count > 0:
    avg_response_time = total_response_time / count / 3600
    print(f"Average time of first response: {avg_response_time:.2f} hours")
else:
    print("No discussions with comments found.")


