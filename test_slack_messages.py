import requests
import json
from configs import read_yaml_file
import jsonschema
import simplejson as json


def test_post_a_new_message():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)
    assert response.status_code == 200
    r_channels = response.json()["channels"]

    """Retrieve testing channel ID"""

    for channel in r_channels:
        if channel["name"] == config["test_channel"]:
            test_channel_id = channel["id"]

    """Post a new message """

    message = "This is a testing message Please(test_post_a_new_message)"

    url_post_msg = config["url"] + "chat.postMessage?channel=" + test_channel_id + "&text=" + message + "&pretty=1"

    response = requests.request("GET", url_post_msg, headers=headers, data=None)
    assert response.status_code == 200
    r = response.json()

    "Validate parameters"
    properties = ["ok", "channel", "ts", "message"]
    assert sorted([key for key in r]) == sorted(properties)
    assert r["ok"] is True
    assert r["channel"] is not ""
    assert sorted([key for key in r]) == sorted(properties)

    properties_message = ['bot_id', 'bot_profile', 'team', 'text', 'ts', 'type', 'user']
    assert sorted(list(r["message"].keys())) == sorted(properties_message)
    assert r["message"]["type"] == "message"
    assert r["message"]["text"] == message


def test_post_and_delete_a_new_message():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)
    assert response.status_code == 200
    r_channels = response.json()["channels"]

    """Retrieve testing channel ID"""

    for channel in r_channels:
        if channel["name"] == config["test_channel"]:
            test_channel_id = channel["id"]

    """Post a new message """

    message = "Delete this message"

    url_post_msg = config["url"] + "chat.postMessage?channel=" + test_channel_id + "&text=" + message + "&pretty=1"

    response = requests.request("GET", url_post_msg, headers=headers, data=None)
    assert response.status_code == 200

    ts = response.json()["ts"]

    url_delete_message = config["url"] + "chat.delete?channel=" + test_channel_id + "&ts=" + ts + "&pretty=1"

    response = requests.request("GET", url_delete_message, headers=headers, data=None)
    assert response.status_code == 200

    assert response.json()["ok"] is True
    assert response.json()["channel"] == test_channel_id
    assert response.json()["ts"] == ts


def test_get_list_of_channels():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)
    assert response.status_code == 200
    r_channels = response.json()["channels"]

    """Verify number of channels and channel names"""
    list_of_of_channels = ["random", "event", "test_messages", "general"]
    assert len(r_channels) == len(list_of_of_channels)
    for channel in r_channels:
        assert channel["name"] in list_of_of_channels


def test_get_conversations_history_specific_channel():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)
    assert response.status_code == 200
    r_channels = response.json()["channels"]

    """Retrieve testing channel ID"""

    for channel in r_channels:
        url_history = config["url"] + "conversations.history?" + "channel=" + channel["id"]
        response = requests.request("GET", url_history, headers=headers, data=None)
        assert response.status_code == 200

        """Note: bot must added to every channel first"""
        for message in response.json()["messages"]:
            print(message["text"])


def test_post_schedule_message_with_large_future_date():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)
    assert response.status_code == 200
    r_channels = response.json()["channels"]

    """Retrieve testing channel ID"""

    for channel in r_channels:
        if channel["name"] == config["test_channel"]:
            test_channel_id = channel["id"]

    """Post a new message for scheduled time """

    message = "This is a scheduled message"

    """Unix EPOCH timestamp of time in future to send the message."""
    post_at = 1631515365000


    url_post_msg = config[
                       "url"] + "chat.scheduleMessage?channel=" + test_channel_id + "&text=" + message + "&pretty=1" \
                   + "&post_at=" + str(post_at)
    response = requests.request("GET", url_post_msg, headers=headers, data=None)
    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["error"] == "time_too_far"


def test_jsonschema_validation_approach():
    config = read_yaml_file(r'prod.yaml')

    headers = {
        'Authorization': "Bearer " + config["auth_token"],
        'Content-Type': config["content_type"]
    }
    url_list = config["url"] + "conversations.list"
    response = requests.request("GET", url_list, headers=headers, data=None)

    """Validate jsonschema against returning response"""

    with open('json_schema_validation_conver_list.json', 'r') as f:
        schema_data = f.read()
    schema = json.loads(schema_data)

    jsonschema.validate(response.json(), schema)
