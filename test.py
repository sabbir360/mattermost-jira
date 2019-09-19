from app import post_to_mattermost

print("Simple Test...")
post_to_mattermost(dict(text="Simple Test Passed!"))

print("-----------------")
print("Extreme Test.....")
post_to_mattermost(dict(text="""**Extreme test passed!**\n
The "Gothic entry" for I can eat glass in particular is outside of BMP: 𐌼𐌰𐌲 𐌲𐌻𐌴𐍃 𐌹̈𐍄𐌰𐌽, 𐌽𐌹 𐌼𐌹𐍃 𐍅𐌿 𐌽𐌳𐌰𐌽 𐌱𐍂𐌹𐌲𐌲𐌹𐌸.
"""), icon="https://kbob.github.io/images/sample-4_thumb.jpg")

print("-----------------")
print("Formatted Test.....")
key = "Key goes here"
user_name = "Username"
user_photo = "http://icons.iconarchive.com/icons/papirus-team/papirus-status/512/avatar-default-icon.png"
issue_type = "Generic"
title = "This is title"
description = "This is issue description. \n New line."
assignee = "assignee"
status = "Done"

post_data = dict()
post_data['author_name'] = user_name
post_data['author_icon'] = user_photo
post_data['author_link'] = "issues/?jql=assignee%3D\"{}\"".format(user_name)
post_data['title'] = title
post_data['text'] = description
post_data['title_link'] = key
post_data['fields'] = [
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
    {
        "short": True,
        "title": "Project",
        "value": "Thunder Charm"
    },
    {
        "short": True,
        "title": "Type",
        "value": "Type goes here"
    },
]

post_to_mattermost(post_data)
