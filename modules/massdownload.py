import inquirer
import json
import httpx
import os
import bs4
import sys
import time
import pathvalidate
from tqdm import tqdm
from modules import getcourses

def massdownload():
    if os.path.exists("./jsons/cookies.json"):
        with open('./jsons/config.json') as f:
            config = json.load(f)
        with open('./jsons/cookies.json') as f:
            cookies = json.load(f)
        if not os.path.exists("./downloads"):
            os.mkdir("./downloads")

        transport = httpx.HTTPTransport(retries=3) #high retry amount due to fickle nature of mass pdf downloading
        client = httpx.Client(cookies=cookies, headers={"User-Agent": config["User-Agent"]}, transport=transport)

        courses = getcourses.getcourses()
        downloadList = []

        if len(courses) > 0:
            for item in courses:
                downloadList.append((item[1], item[0]))

            downloadQuestion = [
                inquirer.Checkbox(
                    "courses",
                    message="What courses do you want to archive?",
                    choices=downloadList,
                ),
            ]

            downloadAnswer = inquirer.prompt(downloadQuestion)
            if len(downloadAnswer) > 0:
                for course in downloadAnswer["courses"]:
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
                    courseName = pathvalidate.sanitize_filepath(courseSoup.find("h1", {"class": "courseHeader--title"}).text)
                    assignmentLister = courseSoup.find("table", {"id": "assignments-student-table"})
                    assignmentList = assignmentLister.find("tbody").findChildren("tr")

                    if len(assignmentList) > 0:
                        print(courseName + ": (trying to download " + str(len(assignmentList)) + " assignments):\n")
                        for item in assignmentList:
                            linkSection = item.find("th", {"class": "table--primaryLink"})
                            if linkSection.find("a"):
                                downloadLink = "https://www.gradescope.com" + linkSection.find("a")["href"] + ".pdf"
                                fileName = downloadLink.split("/")[-1]
                                with client.stream("GET", downloadLink, timeout=15) as r: #high timeout needed because gradescope doesn't prioritize file downloads!

                                    if not os.path.exists("./downloads/" + courseName):
                                        os.mkdir("./downloads/" + courseName)

                                    with open("./downloads/" + courseName + "/" + fileName, "wb") as f:
                                        with tqdm(unit_scale=True, unit_divisor=1024, unit="B", desc=fileName) as progress:
                                            num_bytes_downloaded = r.num_bytes_downloaded
                                            for data in r.iter_bytes():
                                                f.write(data)
                                                progress.update(r.num_bytes_downloaded - num_bytes_downloaded)
                                                num_bytes_downloaded = r.num_bytes_downloaded
                            time.sleep(1) #high sleep value to not overload gradescope servers
                    else:
                        print("Could not find assignments to download.")
                        sys.exit(1)

            else:
                return(0) #user did not choose class, kick them out to main menu
        else:
            print("You don't have any Gradescope courses. Please add a course before using this script")
            sys.exit(1)

    else:
        print("Cookies not saved. Please (re)run setup.py.")
        sys.exit(1)