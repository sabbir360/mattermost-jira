from flask import Flask, request, jsonify
from requests import post as post_request
from urllib.parse import quote_plus
from json import dumps as json_dumps
from config import *

app = Flask(__name__)


def post_to_mattermost_(text, channel=CHANNEL, username=USER_NAME, icon=USER_ICON):

    payload = """{}"channel": "{}", "text": "{}", "username": "{}", "icon_url":"{}"{}""".\
        format("payload={", channel, quote_plus(text), username, quote_plus(icon), "}")

    # payload = "payload={"+payload+"}"
    print(payload)
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = curl_request("POST", MM_URL+"hooks/"+HOOK_ID, data=payload, headers=headers)
    result = response.text
    print("---hook response---")
    print(result)
    return result


def post_to_mattermost(attachment, channel=CHANNEL, username=USER_NAME, icon=USER_ICON):
    # This function submits the new hook to mattermost
    data = {
        'attachments': [attachment],
        'username': USER_NAME,
        'icon_url': icon,
        'channel': channel
    }
    # Post the webhook
    response = post_request(
        MM_URL+"hooks/"+HOOK_ID,
        data=json_dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        err = 'Request to mattermost returned an error %s, the response is:\n%s'
        raise ValueError(err % (response.status_code, response.text))

    print("---hook response---")
    print(response.text)
    return "Posted successfully."


@app.route('/', methods=['GET'])
def hello_world():
    return "Welcome to W3IM"


@app.route('/hooks/<token>', methods=['POST', 'GET'])
def mattermost_jira(token):
    if token == HOOK_ID:

        data = request.get_json(force=True)
        # print("-------------START------------------")
        print(data)
        # print("-------------END------------------")
        if data and data.get("issue_event_type_name", None) and data.get("issue", None):
            issue_type = data.get("issue_event_type_name").replace("_", " ").replace("issue", "").title().strip()
            issue_details = data.get("issue", None)
            user_details = data.get("user", None)
            key = issue_details.get('key', "N/A")
            user_name = user_details.get('displayName', "N/A")
            user_photo = "http://icons.iconarchive.com/icons/papirus-team/papirus-status/512/avatar-default-icon.png"

            if issue_type == "Generic":
                issue_type = "Changed on "
            elif issue_type == "Work Started":
                issue_type = "Started Work on"
            elif issue_type == "Worklog Deleted":
                issue_type = "Deleted Worklog"
            elif issue_type == "Worklog Updated":
                issue_type = "Updated Worklog"
            elif issue_type == "Work Stopped":
                issue_type = "Stopped Work on"
            elif issue_type == "Work Logged":
                issue_type = "Logged work on"
            elif issue_type == "Comment Edited":
                issue_type = "Edited comment on"
            elif issue_type == "Commented":
                issue_type = "Commented on"

            if user_details:
                user_photo = user_details['avatarUrls']['48x48']
            issue_fields = issue_details.get('fields', None)

            if issue_fields:

                title = issue_fields.get("summary", "N/A")
                description = issue_fields.get("description", "N/A")[:30]
                creator = issue_fields.get('creator', None)
                if creator:
                    creator = creator.get("displayName", "N/A")
                else:
                    creator = "N/A"

                project_data = issue_fields.get("project", None)
                project = "N/A"
                if project_data:
                    project = project_data.get("name", "N/A")

                assignee = issue_fields.get('assignee', None)
                if assignee:
                    assignee = assignee.get("displayName", "N/A")
                else:
                    assignee = "N/A"

                # assignee = issue_fields.get('assignee', {}).get("displayName", "N/A")
                status = issue_fields.get('status', {}).get("name", "N/A")

                post_data = dict()
                post_data['author_name'] = user_name
                post_data['author_icon'] = user_photo
                post_data['author_link'] = JIRA_URL+"issues/?jql=assignee%3D\"{}\"".format(user_name)
                post_data['title'] = title
                post_data['text'] = description
                post_data['title_link'] = JIRA_URL+key
                post_data['fields'] = [
                    {
                        "short": True,
                        "title": "Issue Type",
                        "value": issue_type
                    },
                    {
                        "short": True,
                        "title": "Project",
                        "value": project
                    },
                    {
                        "short": True,
                        "title": "Assignee",
                        "value": assignee
                    },
                    {
                        "short": True,
                        "title": "Status",
                        "value": status
                    },

                ]
                return post_to_mattermost(post_data)

            else:
                return "No Issue data!"
    else:
        print("Wrong hook.")

    return token


@app.route('/oauth', methods=['POST', 'GET'])
def oauth():

    return "Thanks for using my app"


if __name__ == "__main__":
    app.run(debug=DEBUG)
