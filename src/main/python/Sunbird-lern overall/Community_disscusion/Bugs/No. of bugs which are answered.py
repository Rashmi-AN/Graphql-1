import requests
import json

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("Please add the config file path")

name_of_community = config.get("COMMUNITY_NAME", "name")

def get_discussions(page_cursor=None):
    query = """
    query($cursor: String) {
      repository(owner: "%s", name: "community") {
        discussions(first: 100, after: $cursor) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            category {
              slug
            }
            comments(first: 1) {
              totalCount
              nodes{
                isAnswer
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
    variables = {'cursor': page_cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]
        nodes = discussions["nodes"]
        has_next_page = discussions["pageInfo"]["hasNextPage"]
        end_cursor = discussions["pageInfo"]["endCursor"]
        if page_cursor is not None:
            nodes = filter_duplicate_discussions(nodes)
        if has_next_page:
            next_nodes, next_end_cursor = get_discussions(end_cursor)
            nodes.extend(next_nodes)
            end_cursor = next_end_cursor
        return nodes, end_cursor
    else:
        raise Exception("Request failed with status code:", response.status_code)


def filter_duplicate_discussions(discussions):
    ids = set()
    filtered_discussions = []
    for discussion in discussions:
        if discussion["id"] not in ids:
            ids.add(discussion["id"])
            filtered_discussions.append(discussion)
    return filtered_discussions


nodes, end_cursor = get_discussions()
bug_discussions = [d for d in nodes if d["category"]["slug"] == "issues"]
answered_bugs = [d for d in bug_discussions if d["comments"]["totalCount"] > 0]
num_answered_bugs = len(answered_bugs)
print("Number of answered bugs:", num_answered_bugs)
