import base64
import json
import logging
import time
import threading

import requests


# This is designed for OpenHab
# TODO: Refactor to work with arbitrary REST Server
class OpenHabRestInterface(threading.Thread):
    prev_state = {}  # stores item states
    update = False

    def __init__(self, host, port, user, pwd, group, queue):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.auth = base64.encodestring("%s:%s" % (self.user,
                                                   self.pwd)).replace("\n", "")
        self.basic_header = {
            "Authorization": "Basic %s" % self.auth,
            "Content-type": "text/plain"
        }  # Header for basic connections (returns only text)
        self.polling_header = {
            "Authorization": "Basic %s" % self.auth,
            "Accept": "application/json"
        }  # Header for polling (returns json object)
        self.add_header = {
            "Authorization": "Basic %s" % self.auth,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }  # Header for adding items

        # NULL Logger if none is set
        self.logger = logging.getLogger("NULL")
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(logging.NOTSET)
        self.args = (group, queue)
        threading.Thread.__init__(
            self, target=self.poll_status, args=self.args)

    # If you want logging you can set the logger here
    def set_logger(self, logger_name):
        self.logger = logging.getLogger(logger_name)

    # Returns the state of the specified item
    def get_item_state(self, item):
        retval = requests.get("http://" + self.host + ":" + str(self.port) +
                              "/rest/items/" + item + "/state")
        if retval.status_code != requests.codes.ok:
            self.logger.error("GET returned: %s" % retval.status_code)
            return None
        else:
            value = retval.text
            self.prev_state[item] = value
            self.logger.info(item + ": " + str(value))
            return value

    # Updates the state of the specified item
    def update_item_state(self, item, state, no_update=False):
        openhab_url = "http://%s:%s/rest/items/%s/state" % (self.host,
                                                            self.port, item)
        retval = requests.put(openhab_url,
                              data=str(state),
                              headers=self.basic_header)

        if retval.status_code != requests.codes.accepted:
            self.logger.error("PUT returned : %s for item: %s" %
                              (retval.status_code, item))
            return False
        #  Add to prev_state to prevent endless loops
        if not no_update:
            self.prev_state[item] = state
        return True

    # Polls all Members of a Group and queues new values
    def poll_status(self, group, queue):
        self.update = True
        url = "http://%s:%s/rest/items/%s" % (self.host, self.port, group)
        param = {"type": "json"}

        while self.update:
            queue.join()  # Wait until queue is empty
            retval = requests.get(url,
                                  params=param,
                                  headers=self.polling_header)

            if retval.status_code != requests.codes.ok:
                self.logger.error("GET returned: %s for Group:%s" %
                                  (retval.status_code, group))
                time.sleep(0.5)
                continue

            # Get all items in the group and check for new values
            for member in retval.json()["members"]:
                item = member["name"]
                state = member["state"]
                if item in self.prev_state:
                    if state != self.prev_state[item]:
                        self.logger.debug("New State of %s: %s" %
                                          (item, state))
                        queue.put({item: state})
                else:
                    queue.put({item: state})
                    self.prev_state[item] = state
            time.sleep(0.5)

    # Add a new item to openHab
    def add_item(self, name, item_type, label, category, group):
        # Construct the new Item
        item = {
            "name": name,
            "type": item_type,
            "label": label,
            "category": category,
            "groupNames": [group]
        }

        item_json = json.dumps(item)  # create json
       # item_json = json.dumps(list(item))  # create json
        print "item %s" % item_json
        # Push new Item and return success/failure
        url = "http://%s:%s/rest/items/%s" % (self.host, self.port, name)
        for i in range(0, 2):  # Try 3 times if failure
            retval = requests.put(url, data=item_json, headers=self.add_header)
            if retval.status_code != requests.codes.ok:
                if i == 2:
                    self.logger.error("PUT returned: %s" % retval.status_code)
                    return False
            else:
                break

        return True

    # Delete Item from openHab
    def delete_item(self, name):
        url = "http://%s:%s/rest/items/%s" % (self.host, self.port, name)
        retval = requests.delete(url)
        if retval.status_code != requests.codes.ok:
            self.logger.error("DELETE returned: %s" % retval.status_code)
            return False

        return True
