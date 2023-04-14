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
headers = {"Authorization": "bearer " +token_details}

has_next_page = True
end_cursor = None
category_counts = {}
discussions_seen = set()

while has_next_page:
    variables = {"cursor": end_cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]
        end_cursor = discussions["pageInfo"]["endCursor"]
        has_next_page = discussions["pageInfo"]["hasNextPage"]
        for discussion in discussions["nodes"]:
            category_slug = discussion["category"]["slug"]
            if category_slug == "announcements":
                continue  # Skip this discussion if it's in the "announcements" category
            if category_slug not in category_counts:
                category_counts[category_slug] = 0
            if discussion["id"] not in discussions_seen:
                category_counts[category_slug] += 1
                discussions_seen.add(discussion["id"])
    else:
        print("Request failed with status code:", response.status_code)
        break

total_count = sum(category_counts.values())
print(f"Total discussion count: {total_count}")

print("Discussion counts by category:")
for category_slug, count in category_counts.items():
    print(f"{category_slug}: {count}")
