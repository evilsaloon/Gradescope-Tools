import inquirer
import json
import httpx
import os
import bs4
import sys
import time
from modules import getcourses

def internalinfo():
    if os.path.exists("./jsons/cookies.json"):
        with open('./jsons/config.json') as f:
            config = json.load(f)
        with open('./jsons/cookies.json') as f:
            cookies = json.load(f)

        client = httpx.Client(cookies=cookies, headers={"User-Agent": config["User-Agent"]})

        courses = getcourses.getcourses()
        internalList = []

        if len(courses) > 0: #there are courses to iterate over
            for item in courses:
                internalList.append((item[1], item[0]))

            internalQuestion = [
                inquirer.Checkbox(
                    "courses",
                    message="What courses do you want to see?",
                    choices=internalList,
                ),
            ]

            internalAnswer = inquirer.prompt(internalQuestion)
            if len(internalAnswer) > 0:
                for course in internalAnswer["courses"]:
                    url = "https://www.gradescope.com/courses/" + str(course)
                    try:
                        coursePage = client.get(url)
                        cookies["_gradescope_session"] = coursePage.cookies["_gradescope_session"]
                    except:
                        print("Network error! Please try again later.")
                        sys.exit(1)
                    if coursePage.status_code != 200:
                        print("Account details are incorrect. Try deleting cookies.json and rerunning setup.py")
                        sys.exit(1)

                    courseSoup = bs4.BeautifulSoup(coursePage.text, features="html.parser")
                    courseName = courseSoup.find("h1", {"class": "courseHeader--title"}).text
                    scripts = courseSoup.find_all("script")
                    classesPrinted = 0
                    for item in scripts:
                        if len(item.attrs) == 0: #the script tag we need always has 0 attributes. if it isn't found, the module will print nothing
                            gon = item.text[13:-8].split(";")
                            extensions = json.loads(gon[2].split("=")[1])
                            print(courseName + ":\n")
                            print("Assignment extensions supported: ", extensions, "\n")
                            pageContext = json.loads(gon[3].split("page_context=")[1])
                            print("Page context: ", json.dumps(pageContext, indent=1), "\n")
                            classesPrinted += 1
                    time.sleep(0.5)
                    if classesPrinted == 0: #classes WERE selected, but NO SCRIPT tag was found!
                        print("<script> tag with internal info not found. Please open an issue and report this error.")
                        sys.exit(1)
            else:
                return(0) #user did not choose class, kick them out to main menu
        else:
            print("You don't have any Gradescope courses. Please add a course before using this script")
            sys.exit(1)
    else:
        print("Cookies not saved. Please (re)run setup.py.")
        sys.exit(1)