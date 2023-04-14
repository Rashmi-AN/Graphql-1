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










# import json
# import requests
#
# query = """
# query($cursor: String) {
#   repository(owner: "sunbird-ed", name: "community") {
#     discussions(first: 100, after: $cursor) {
#       pageInfo {
#         endCursor
#         hasNextPage
#       }
#       nodes {
#         category {
#           slug
#         }
#       }
#     }
#   }
# }
# """
#
# url = 'https://api.github.com/graphql'
# headers = {"Authorization": "bearer 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"}
#
# has_next_page = True
# end_cursor = None
# num_bugs = 0
#
# while has_next_page:
#     variables = {"cursor": end_cursor}
#     response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
#
#     if response.status_code == 200:
#         json_data = json.loads(response.text)
#         discussions = json_data["data"]["repository"]["discussions"]
#         end_cursor = discussions["pageInfo"]["endCursor"]
#         has_next_page = discussions["pageInfo"]["hasNextPage"]
#         bug_discussions = [d for d in discussions["nodes"] if d["category"]["slug"] == "bugs"]
#         num_bugs += len(bug_discussions)
#     else:
#         print("Request failed with status code:", response.status_code)
#         break
#
# print("Total number of bugs:", num_bugs)






# import requests
# import json
#
# query = """
# query {
#   repository(owner: "sunbird-ed", name: "community") {
#     discussions(first: 100) {
#       totalCount
#       nodes {
#         category {
#           slug
#           # createdAt
#           # isAnswerable
#         }
#       }
#     }
#   }
# }
# """
#
# url = 'https://api.github.com/graphql'
# headers = {"Authorization": "bearer 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"}
# response = requests.post(url, headers=headers, json={'query': query})
#
# if response.status_code == 200:
#     json_data = json.loads(response.text)
#     discussions = json_data["data"]["repository"]["discussions"]["nodes"]
#     bug_discussions = [d for d in discussions if d["category"]["slug"] == "bugs"]
#     num_bugs = len(bug_discussions)
#     print("Total number of bugs:", num_bugs)
# else:
#     print("Request failed with status code:", response.status_code)




# import requests
#
# # Define the GraphQL query
# query = """query {
#   repository(owner: "sunbird-ed", name: "community") {
#     discussions(first: 100) {
#       totalCount
#     }
#   }
# }"""
#
# # Set the GitHub API endpoint URL and the authentication token in the headers
# url = 'https://api.github.com/graphql'
# headers = {"Authorization": "bearer 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"}
#
# # Send the GraphQL query as a JSON payload and receive the response
# response = requests.post(url, headers=headers, json={'query': query})
#
# # Parse the JSON response and extract the total count of discussions
# json_data = response.json()
# total_count = json_data['data']['repository']['discussions']['totalCount']
#
# # Print the total count of discussions with the "bugs" category slug
# print(f"Total number of discussions with the 'bugs' category slug: {total_count}")
