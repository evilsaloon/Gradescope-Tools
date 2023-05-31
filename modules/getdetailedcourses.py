import json
import os
import sys
import httpx
import bs4
import time
from modules import getcourses

def getdetailedcourses(tracked):
    if os.path.exists("./jsons/cookies.json") and os.path.exists("./jsons/config.json") and os.path.exists("./jsons/coursesTracked.json"):
        with open('./jsons/config.json') as f:
            config = json.load(f)
        with open('./jsons/cookies.json') as f:
            cookies = json.load(f)

        client = httpx.Client(cookies=cookies, headers={"User-Agent": config["User-Agent"]})
        detailedCourses = {}

        if tracked == True:
            with open('./jsons/coursesTracked.json') as f:
                courses = json.load(f)
        else:
            courses = getcourses.getcourses()

        if len(courses) > 0: #will return empty dict and skip expensive network calls if there are no courses to scrape
            for course in courses: #going to each course's page to scrape assignments
                if tracked == True:
                    url = "https://www.gradescope.com/courses/" + str(course)
                else:
                    url = "https://www.gradescope.com/courses/" + str(course[0])
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
                assignmentLister = courseSoup.find("table", {"id": "assignments-student-table"}) #there is only 1 table with this id
                assignmentList = assignmentLister.find("tbody").findChildren("tr") #only 1 tbody in table. children are always tr.
                detailedDict = {}

                if len(assignmentList) > 0: #checking that there are courses to list
                    for assignment in assignmentList:
                        name = assignment.find("th").text
                        grade = ""

                        if assignment.find("div", {"class": "submissionStatus--text"}): #still being graded/not submitted
                            grade = "NA"
                        elif assignment.find("td", {"class": "submissionStatus"}): #grade available
                            grade = assignment.find("td", {"class": "submissionStatus"}).text

                        detailedDict[name] = grade
                    if tracked == True:
                        detailedCourses[int(course)] = detailedDict
                    else:
                        detailedCourses[int(course[0])] = detailedDict

                    time.sleep(0.5)
            
            with open("./jsons/coursesDetailed.json", "w") as f:
                json.dump(dict(detailedCourses), f)
            with open("./jsons/cookies.json", "w") as f:
                json.dump(dict(cookies), f)

        return detailedCourses
    else:
        print("Cookies and config are missing. Please (re)run setup.py.")
        sys.exit(1)