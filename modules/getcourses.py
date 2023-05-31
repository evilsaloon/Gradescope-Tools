import httpx
import bs4
import json
import sys

def getcourses():
    with open('./jsons/cookies.json') as f:
        cookies = json.load(f)
    with open('./jsons/config.json') as f:
        config = json.load(f)

    client = httpx.Client(cookies=cookies, headers={"User-Agent": config["User-Agent"]})

    try:
        accountPage = client.get("https://www.gradescope.com/account")
        cookies["_gradescope_session"] = accountPage.cookies["_gradescope_session"]
    except:
        print("Network error! Please try again later.")
        sys.exit(1)
    if accountPage.status_code != 200:
        print("Account details are incorrect. Try deleting cookies.json and rerunning setup.py")
        sys.exit(1)

    courseSoup = bs4.BeautifulSoup(accountPage.text, features="html.parser")
    courseList = courseSoup.find("div", {"class": "courseList"})
    courses = []
    semesters = []

    if len(courseList) > 0: #will return empty list if no courses are found
        for tag in courseList: #each tag is a course
            if (tag.name == "div" and hasattr(tag, "class") and len(tag["class"]) == 1):
                if tag["class"][0] == "courseList--term": #name of semester
                    semesters.append(tag.next)
                elif tag["class"][0] == "courseList--coursesForTerm": #list of courses in term
                    for course in tag:
                        if (course.name == "a" and hasattr(course, "class") and len(course["class"]) == 1 and course["class"][0] == "courseBox"): #course input validation
                            classID = int(course["href"].split("/")[2])
                            shortName = course.find("h3", {"class": "courseBox--shortname"}).text
                            longName = course.find("div", {"class": "courseBox--name"}).text
                            assignments = course.find("div", {"class": "courseBox--assignments"}).text
                            courses.append([classID, shortName, longName, assignments])
                elif tag["class"][0] == "courseList--inactiveCourses" and config['useOlds'] == True: #copy pasted code from above and changed course to oldCourse. list of old courses in term
                    for oldCourse in tag:
                        if oldCourse["class"][0] == "courseList--term": #name of semester
                            semesters.append(oldCourse.next)
                        elif oldCourse["class"][0] == "courseList--coursesForTerm": #list of courses in term
                            for course in oldCourse:
                                if (course.name == "a" and hasattr(course, "class") and len(course["class"]) == 1 and course["class"][0] == "courseBox"): #course input validation
                                    classID = int(course["href"].split("/")[2])
                                    shortName = course.find("h3", {"class": "courseBox--shortname"}).text
                                    longName = course.find("div", {"class": "courseBox--name"}).text
                                    assignments = course.find("div", {"class": "courseBox--assignments"}).text
                                    courses.append([classID, shortName, longName, assignments])

        try:
            with open("./jsons/cookies.json", "w") as f:
                json.dump(dict(cookies), f)
            with open("./jsons/courses.json", "w") as f:
                json.dump(courses, f)
        except:
            print("Could not write courses and cookies to disk. Check your permissions or if the ./jsons folder exists.")
    return(courses)