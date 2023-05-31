import inquirer
import json
import httpx
import os
import bs4
import sys
import time
from modules import getcourses

def totalcalculator():
    if os.path.exists("./jsons/cookies.json"):
        with open('./jsons/config.json') as f:
            config = json.load(f)
        with open('./jsons/cookies.json') as f:
            cookies = json.load(f)

        client = httpx.Client(cookies=cookies, headers={"User-Agent": config["User-Agent"]})

        courses = getcourses.getcourses()
        totalList = []

        if len(courses) > 0: #there are courses to add
            for item in courses:
                totalList.append((item[1], item[0]))

            totalQuestion = [
                inquirer.Checkbox(
                    "courses",
                    message="What courses do you want to total?",
                    choices=totalList,
                ),
            ]

            totalAnswer = inquirer.prompt(totalQuestion)
            if len(totalAnswer) > 0:
                for course in totalAnswer["courses"]:
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
                    assignmentLister = courseSoup.find("table", {"id": "assignments-student-table"})
                    assignmentList = assignmentLister.find("tbody").findChildren("tr")
                    gotPoints = 0.0
                    totalPoints = 0.0
                    for assignment in assignmentList:
                        if assignment.find("div", {"class": "submissionStatus--text"}): #still being graded/not submitted
                            pass
                        elif assignment.find("td", {"class": "submissionStatus"}): #grade available
                            grade = assignment.find("td", {"class": "submissionStatus"}).text
                            parsedGrade = grade.split(" / ")
                            gotPoints += float(parsedGrade[0])
                            totalPoints += float(parsedGrade[1])
                    
                    if gotPoints > 0.0 and totalPoints > 0.0: #there are assignments to print
                        percentage = round(gotPoints/totalPoints*100, 2)
                        print("\n" + courseName + ": " + str(gotPoints) + "/" + str(totalPoints) + " -> " + str(percentage) + "%")
                        time.sleep(0.5)
            else:
                return(0) #user did not choose class, kick them out to main menu
        else:
            print("You don't have any Gradescope courses. Please add a course before using this script")
            sys.exit(1)

    else:
        print("Cookies not saved. Please (re)run setup.py.")
        sys.exit(1)