import inquirer
import json
import os
import sys
from modules import getcourses

def trackingsetup():
    if os.path.exists("./jsons/cookies.json"):
        courses = getcourses.getcourses()
        trackList = []
        for item in courses:
            trackList.append((item[1], item[0]))

        trackQuestion = [
            inquirer.Checkbox(
                "courses",
                message="What courses do you want to track?",
                choices=trackList,
            ),
        ]

        trackAnswer = inquirer.prompt(trackQuestion)

        try:
            with open("./jsons/coursesTracked.json", "w") as f:
                json.dump(trackAnswer["courses"], f)
        except:
            print("Could not write courses to disk. Check your permissions or if the ./jsons folder exists.")

    else:
        print("Cookies not found. Please (re)run setup.py.")
        sys.exit(1)