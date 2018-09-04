from flask import Flask, request, jsonify
from requests import request as curl_request
from urllib.parse import quote_plus
from config import *

app = Flask(__name__)


def post_to_mattermost(text, channel=CHANNEL, username=USER_NAME, icon=USER_ICON):

    payload = """{}"channel": "{}", "text": "{}", "username": "{}", "icon_url":"{}"{}""".format("payload={", channel, text, username, quote_plus(icon), "}")

    # payload = "payload={"+payload+"}"
    print(payload)
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = curl_request("POST", MM_URL+"hooks/"+HOOK_ID, data=payload, headers=headers)
    result = response.text
    print(result)
    return result


@app.route('/', methods=['GET'])
def hello_world():
    return "Welcome to W3IM"


@app.route('/hooks/<token>', methods=['POST', 'GET'])
def mattermost_jira(token):
    if token == HOOK_ID:

        data = request.get_json(force=True)

        if data and data.get("issue_event_type_name", None) and data.get("issue", None):
            issue_type = data.get("issue_event_type_name").replace("_", " ").replace("issue", "").title().strip()
            issue_details = data.get("issue", None)
            user_details = data.get("user", None)
            key = issue_details.get('key', "N/A")
            user_name = user_details.get('displayName', "N/A")
            user_photo = None

            if issue_type == "Generic":
                issue_type = "Changed on "
            elif issue_type == "Work Started":
                issue_type = "Started Work on"
            elif issue_type == "Worklog Deleted":
                issue_type = "Deleted Worklog"
            elif issue_type == "Work Stopped":
                issue_type = "Stopped Work on"
            elif issue_type == "Work Logged":
                issue_type = "Logged work on"
            elif issue_type == "Comment Edited":
                issue_type = "Edited comment on"
            elif issue_type == "Commented":
                issue_type = "Commented on"


            print(issue_type)

            if user_details:
                user_photo = user_details['avatarUrls']['48x48']
            issue_fields = issue_details.get('fields', None)

            if issue_fields:

                title = issue_fields.get("summary", "N/A")
                creator = issue_fields.get('creator', None)
                if creator:
                    creator = creator.get("displayName", "N/A")
                else:
                    creator = "N/A"

                assignee = issue_fields.get('assignee', None)
                if assignee:
                    assignee = assignee.get("displayName", "N/A")
                else:
                    assignee = "N/A"

                # assignee = issue_fields.get('assignee', {}).get("displayName", "N/A")
                status = issue_fields.get('status', {}).get("name", "N/A")

                post_data = "###### {} {} [{}]({})\n\n**Ticket:**`{}`\n**Status:**`{}`\n**Creator:**`{}`\n**Assignee:**`{}`"\
                    .format(user_name, issue_type, key, JIRA_URL+key, title, status, creator, assignee)
                if user_photo:
                    return post_to_mattermost(post_data, icon=user_photo)
                else:
                    return post_to_mattermost(post_data)
            else:
                return "No Issue data!"
        # print("-------------START------------------")
        print(data)
        # print("-------------END------------------")
    else:
        print("Wrong hook.")

    return token


@app.route('/oauth', methods=['POST', 'GET'])
def oauth():

    return "Thanks for using my app"


if __name__ == "__main__":
    app.run(debug=DEBUG)
