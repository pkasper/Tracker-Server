
class TutorialData:
    current_step = None
    tutorial_data = []

    def __init__(self):
        self.step("tutorial_welcome",
                  {"type": "tutorial", "message": {"name": 'tutorial_welcome', "type": 'tutorial', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "center", "offset": "0"}}, "arrow_position": "", "title": "WELCOME", "text": "Let's start with a quick tutorial"}},
                  {"type": "tutorial_close", "message": "tutorial_welcome"})

        self.step("tutorial_intro",
                  {"type": "tutorial", "message": {"name": 'tutorial_intro', "type": 'tutorial', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "center", "offset": "0"}}, "arrow_position": "", "title": "Basics", "text": "You will be tasked to navigate through this wiki network.<br><br>Every individual task will dump you onto a random site and you have to find the target site. Let's give it a try."}},
                  {"type": "tutorial_close", "message": "tutorial_intro"})

        self.step("first_mission",
                  {"message": {"goal_page": {"url": "wiki-schools/wp/l/Livermorium.htm", "link": "wiki-schools\\wp\\l\\Livermorium.htm", "id": 3356, "name": "Livermorium"}, "start_page": {"url": "wiki-schools/wp/e/English_language.htm", "link": "wiki-schools\\wp\\e\\English_language.htm", "id": 1924, "name": "English language"}, "game_name": "PLAIN_2_21175f63-286e-476b-b202-3710806d1dde", "distance": 3}, "type": "new_game"},
                  {"type": "event", "message": "load", "url": "wiki-schools/wp/e/English_language.htm"})

        self.step("tutorial_landingpage",
                  {"type": "tutorial", "message": {"name": 'tutorial_landingpage', "type": 'tutorial', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "top", "offset": "5rem"}}, "arrow_position": "topcenter", "title": "Where am I?", "text": "As you can see you have been thrown onto the article about the English Language. Up here you see some details about your task."}},
                  {"type": "tutorial_close", "message": "tutorial_landingpage"})

        self.step("tutorial_startpage",
                  {"type": "tutorial", "message": {"name": 'tutorial_startpage', "type": 'tutorial', "position": {"x": {"alignment": "left", "offset": "3rem"}, "y": {"alignment": "top", "offset": "5rem"}}, "arrow_position": "topleft", "title": "Start Site", "text": "This is the site you started out on. "}},
                  {"type": "tutorial_close", "message": "tutorial_startpage"})

        self.step("tutorial_targetpage",
                  {"type": "tutorial", "message": {"name": 'tutorial_targetpage', "type": 'tutorial', "position": {"x": {"alignment": "right", "offset": "3rem"}, "y": {"alignment": "top", "offset": "5rem"}}, "arrow_position": "topright", "title": "Target", "text": "And this is where you need to go. These markers are links so you can click on them. They will open a new window where you can get information about your target so you do not move blindly."}},
                  {"type": "tutorial_close", "message": "tutorial_targetpage"})

        self.step("tutorial_path_sections",
                 {"type": "tutorial", "message": {"name": 'tutorial_path_sections', "type": 'tutorial', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "top", "offset": "5rem"}}, "arrow_position": "topcenter", "title": "Shortest Path", "text": "The coloured sections indicate how many steps are the total minimum to reach the goal. But this should not matter to you. <br><br>You can always open or close this info bar by clickong on the strap in the middle."}},
                 {"type": "tutorial_close", "message": "tutorial_path_sections"})

        self.step("tutorial_start_mission",
                  {"type": "tutorial", "message": {"name": 'tutorial_start_mission', "type": 'tutorial', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "center", "offset": "0"}}, "arrow_position": "", "title": "Good Luck!", "text": "Now please go ahead and try to find your target article by following links."}},
                  {"type": "event", "message": "load", "url": "wiki-schools/wp/l/Livermorium.htm"})

        self.step("tutorial_success",
                  {"type": "tutorial", "message": {"name": 'tutorial_success', "type": 'emphasis', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "center", "offset": "0"}}, "arrow_position": "", "title": "Well Done!", "text": "You found your target. There is one more thing you need to learn though. Close this message to load another task."}},
                  {"type": "tutorial_close", "message": "tutorial_success"})

        self.step("second_mission",
                  {"message": {"goal_page": {"url": "wiki-schools/wp/f/Ferdinand_Magellan.htm", "link": "wiki-schools\\wp\\f\\Ferdinand_Magellan.htm", "id": 2070, "name": "Ferdinand Magellan"}, "start_page": {"url": "wiki-schools/wp/s/Soil.htm", "link": "wiki-schools\\wp\\s\\Soil.htm", "id": 4902, "name": "Soil"}, "game_name": "PLAIN_2_113f3291-bbdf-4092-b27e-2b053d27851d", "distance": 3}, "type": "new_game"},
                  {"type": "event", "message": "load", "url": "wiki-schools/wp/s/Soil.htm"})

        self.step("tutorial_abort_button",
                  {"type": "tutorial", "message": {"name": 'tutorial_abort_button', "type": 'error', "position": {"x": {"alignment": "left", "offset": "13rem"}, "y": {"alignment": "bottom", "offset": "0"}}, "arrow_position": "leftbottom", "title": "Abort Button", "text": "If you feel like you cannot find the target you can abort the individual task at any time. Please try this and abort the current task!"}},
                  {"type": "abort", "message": None})

        self.step("tutorial_end",
                  {"type": "tutorial", "message": {"name": 'tutorial_end', "type": 'emphasis', "position": {"x": {"alignment": "center", "offset": "0"}, "y": {"alignment": "center", "offset": "0"}}, "arrow_position": "", "title": "DONE!", "text": "And we're done. You now know how this study works. Good luck! <br><br><br> Close this message to start the study."}},
                  {"type": "tutorial_close", "message": "tutorial_end"})

    def step(self, _step_name, _sent_message, _wait_for):
        self.tutorial_data.append({"name": _step_name, "sent_message": _sent_message, "wait_for": _wait_for})

