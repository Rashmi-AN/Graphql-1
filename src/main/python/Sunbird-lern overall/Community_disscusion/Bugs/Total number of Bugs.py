import json
import requests

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("Please add the config file path")

name_of_community = config.get("COMMUNITY_NAME", "name")

query = """
query($cursor: String) {
  repository(owner: "%s", name: "community") {
    discussions(first: 100, after: $cursor) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        category {
          slug
        }
      }
    }
  }
}
""" % name_of_community
token_details = config.get("BEARER", "token")

url = 'https://api.github.com/graphql'
headers = {"Authorization": "bearer " + token_details}

has_next_page = True
end_cursor = None
num_bugs = 0
discussions_seen = set()

while has_next_page:
    variables = {"cursor": end_cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]
        end_cursor = discussions["pageInfo"]["endCursor"]
        has_next_page = discussions["pageInfo"]["hasNextPage"]
        bug_discussions = [d for d in discussions["nodes"] if d["category"]["slug"] == "issues" and d["id"] not in discussions_seen]
        num_bugs += len(bug_discussions)
        discussions_seen.update(d["id"] for d in bug_discussions)
    else:
        print("Request failed with status code:", response.status_code)
        break

print("Total number of bugs:", num_bugs)

