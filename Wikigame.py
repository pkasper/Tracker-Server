#import random
import uuid
from binascii import a2b_base64
import os
import sys
import time
import random

import DbConnector
import WikiGameController
import User
import TutorialData

database_connection = DbConnector.DbConnector()


class WikiGame:
    user_controller = None
    url_prefix = "http://localhost/wikigame/"
    game_id = 0
    socket = 0
#    menu_state = bool(random.getrandbits(1))
    menu_state = False
    game = None
    gamelist_name = 'PLAIN_1'
    gamelist = None
    list_index = 0
    session_id = str(uuid.uuid4())
    tutorial_completed = False
    tutorial_data = None

    def __init__(self, _socket, _uuid):
        self.tutorial_data = None
        self.socket = _socket
        self.socket.write_json_message("handshake", str(uuid.uuid4()))
        self.gamelist = WikiGameController.fetch_list(self.gamelist_name)['game_ids'].split(',')
        random.shuffle(self.gamelist)
        print(self.gamelist)
        self.user_controller = User.User(self)
        self.session_id = _uuid
        print("STARTING WIKIGAME WITH SESSION ID: " + self.session_id)

    def handle_message(self, _message_container):
        if _message_container['type'] == "DEBUG_RESET":
            WikiGameController.update_session(self.session_id,
                                  self.gamelist_name,
                                  self.list_index,
                                  self.user_controller.get_attributes()['id'][0],
                                  True,
                                  self.tutorial_completed,
                                  ",".join(self.gamelist))
            return
        if _message_container['type'] == "handshake":
            self.game_id = _message_container['message']
        elif _message_container['type'] == "start":
            self.setup()
        elif _message_container['type'] == "session_response":
            self.restore_session(_message_container['message'])
        elif _message_container['type'] == "user_feature":
                self.user_controller.set_attribute(_message_container['message'])
        elif self.user_controller.complete:
            if not self.game:
                if not self.tutorial_completed:
                    self.tutorial(_message_container)
                else:
                    print("Game not started!")
                return
            elif _message_container['game_features']['game_status']['game_id'] == self.game['game_name']:
                if _message_container['type'] == "event":
                    self.store_log(_message_container['game_features']['timestamp'], _message_container['message'], _message_container['game_features'])
                    if _message_container['message'] == "load":
                        self.check_page(_message_container['game_features']['game_status']['current_page'])
                elif _message_container['type'] == "abort":
                    self.game_abort()
                elif _message_container['type'] == "screenshot":
                    screenshot_location = self.store_screenshot(_message_container['message'])
                    self.store_log(_message_container['game_features']['timestamp'], 'screenshot', screenshot_location)
                elif _message_container['type'] == "link_data":
                    self.store_log(_message_container['game_features']['timestamp'], 'link_data', _message_container['message'])
            else:
                print("Gamename missmatch")

        else:
            print('User not set!')

    def setup(self):
        self.socket.write_json_message("menu_state", self.menu_state)
        self.socket.write_json_message("session_request", ())

    def restore_session(self, _session_id):
        session_data = WikiGameController.fetch_session(_session_id)

        if session_data:
            self.session_id = session_data['session_id']
            self.gamelist_name = session_data['list_name']
            self.tutorial_completed = session_data['tutorial_completed']
            self.gamelist = session_data['mission_list'].split(',')
            self.list_index = session_data['list_index']
            self.user_controller.load_user(session_data['user_id'])
            self.socket.write_json_message("dialog", {"title": "Restoring game", "text": "Restarting at game: " + str(self.list_index + 1) + "/" + str(len(self.gamelist))})

        else:
            self.user_controller.new_user()

    def session_start(self):
        WikiGameController.update_session(self.session_id,
                                          self.gamelist_name,
                                          self.list_index,
                                          self.user_controller.get_attributes()['id'][0],
                                          False,
                                          self.tutorial_completed,
                                          ",".join(self.gamelist))

        if not self.tutorial_completed:
            self.tutorial()
        else:
            self.game_start()

    def game_start(self):
        if self.list_index >= len(self.gamelist):
            self.socket.write_json_message("session_complete", "Session complete. Thank you!")
#            self.socket.write_json_message("reset", "")
            WikiGameController.update_session(self.session_id,
                                              self.gamelist_name,
                                              self.list_index,
                                              self.user_controller.get_attributes()['id'][0],
                                              True,
                                              self.tutorial_completed,
                                              ",".join(self.gamelist))
            return
        self.game = WikiGameController.fetch_game(self.gamelist[self.list_index])
        self.socket.write_json_message("new_game", self.game)
        self.store_log(0, "GAME_STARTED", self.game['game_name'])

#        self.socket.write_json_message("hint", {"type": "hint", "text": "SOLUTION", "url": self.game['goal_page']['link']})
#        hubs = WikiGameController.fetch_hubs(WikiGameController.get_page_by_link(self.game['start_page']['link']), 5)
#        for hub in hubs:
#            self.socket.write_json_message("hint", {"type": "hint", "text": hub['name'], "url": hub['link']})

    def game_abort(self):
        self.store_log(0, "GAME_ABORTED", self.game['game_name'])
        self.socket.write_json_message("game_complete", "Aborted game #" + str(self.list_index + 1) + "/" + str(len(self.gamelist)))
        self.list_index += 1
        self.socket.write_json_message("session_update", self.session_id)
        WikiGameController.update_session(self.session_id,
                                          self.gamelist_name,
                                          self.list_index,
                                          self.user_controller.get_attributes()['id'][0],
                                          False,
                                          self.tutorial_completed,
                                          ",".join(self.gamelist))
        self.game_start()

    def check_page(self, _current_page):
        current_page = WikiGameController.get_page_by_link(_current_page)
        if not current_page:
            print("UNKNOWN PAGE")
            return
        print("Comparing " + str(current_page['id']) + " AND " + str(self.game['goal_page']['id']))
        if current_page['id'] == self.game['goal_page']['id']:

            database_connection.commit()
            self.store_log(0, "GAME_COMPLETED", self.game_id)
            self.socket.write_json_message("game_complete", "Completed game #" + str(self.list_index + 1) + "/" + str(len(self.gamelist)))
            self.list_index += 1
            self.socket.write_json_message("session_update", self.session_id)
            WikiGameController.update_session(self.session_id,
                                              self.gamelist_name,
                                              self.list_index,
                                              self.user_controller.get_attributes()['id'][0],
                                              False,
                                              self.tutorial_completed,
                                              ",".join(self.gamelist))
            self.game_start()
        else:
            if not current_page:
                return
            hubs = WikiGameController.fetch_hubs(current_page, 5, 0)
            for hub in hubs:
                self.socket.write_json_message("hint", {"type": "hint", "text": hub['name'], "url": hub['url']})
#            distance = WikiGameController.get_distance(current_page['id'], self.game['goal_page']['id'])
#            self.socket.write_json_message("current_distance", distance)
            print("Comparison complete")

    def store_screenshot(self, _png_data):
        storepath = "C:\Users\Patrick\Desktop\WIKIGAME_IMAGES" + os.sep
#        print("IMAGE DATA: " + _png_data[22:])
        image_data = a2b_base64(_png_data[22:])

#        screenshot_path = (storepath +
#                           str(self.user_controller.attributes['name'][0]) +
#                           os.sep + str(self.list_index) + '_' + str(self.game_id) +
#                           os.sep)
        screenshot_path = os.path.join(storepath +
                                       self.user_controller.attributes['name'][0] +
                                       os.sep +
                                       self.gamelist_name +
                                       '_' +
                                       str(self.list_index) +
                                       '_' +
                                       str(self.game['game_name']) +
                                       os.sep)

        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        filename = str(time.time()) + ".png"

        screenshot_file = open(os.path.join(screenshot_path, filename), "wb")
        screenshot_file.write(image_data)
        screenshot_file.close()
        print("Screenshot created in: " + screenshot_path)

        database_connection.execute("INSERT INTO screenshots (path, screenshot_data)"
                                    "VALUES (%s, %s)",
                                    (os.path.join(screenshot_path, filename), _png_data),
                                    "INSERT")
        database_connection.commit()
        return os.path.join(screenshot_path, filename)

    def store_log(self, _timestamp, _action, _payload):
        server_timestamp = int(time.time())
        storepath = "C:\Users\Patrick\Desktop\WIKIGAME_LOG" + os.sep
        log_path = os.path.join(storepath + self.user_controller.attributes['name'][0] + os.sep)

        if not os.path.exists(log_path):
            os.makedirs(log_path)
        filename = str(self.gamelist_name + "_" + str(self.list_index) + "_" + self.game['game_name']) + ".txt"

        log_file = open(os.path.join(log_path, filename), 'a')
        log_file.write(str(server_timestamp))
        log_file.write("\t")
        log_file.write(str(_timestamp))
        log_file.write("\t")
        log_file.write(str(_action))
        if _payload:
            log_file.write("\t")
            log_file.write(str(_payload))
        log_file.write("\n")
        log_file.close()

##
#   remove return to disable database logging -> reduces server load!
##
        return
        database_connection.execute("INSERT INTO log (session_id, client_timestamp, server_timestamp, type, payload) "
                                    "VALUES (%s, %s, %s, %s, %s)",
                                    (self.session_id, _timestamp, server_timestamp, str(_action), str(_payload)),
                                    "INSERT")

    def tutorial(self, _message=None):
        if not self.tutorial_data:
            self.tutorial_data = TutorialData.TutorialData()

        def next_step(self):
            if len(self.tutorial_data.tutorial_data) == 0:
                self.tutorial_completed = True
                print("TUTORIAL DONE!")
                self.socket.write_json_message("tutorial", "CLEAR_ALL")
                self.session_start()
                return
            self.tutorial_data.current_step = self.tutorial_data.tutorial_data.pop(0)
            self.socket.write_json_message(self.tutorial_data.current_step['sent_message']['type'], self.tutorial_data.current_step['sent_message']['message'])

        if not self.tutorial_data.current_step:
            next_step(self)
            return

        if self.tutorial_data.current_step['wait_for']['message'] == _message['message'] and self.tutorial_data.current_step['wait_for']['type'] == _message['type']:
            if self.tutorial_data.current_step['wait_for']['message'] == "load":
                if WikiGameController.clean_link(self.tutorial_data.current_step['wait_for']['url']) == WikiGameController.clean_link(_message['game_features']['game_status']['current_page']):
                    next_step(self)
            else:
                next_step(self)
