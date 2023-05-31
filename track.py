import json
import os
import sys
from pyrogram import Client
from modules import getcourses, getdetailedcourses

if os.path.exists("./jsons/coursesTracked.json"):
    with open('./jsons/coursesTracked.json') as f:
        coursesToTrack = json.load(f)
    with open('./jsons/config.json') as f:
        config = json.load(f)

    out = ""
    if config["detailedTracking"] == True:
        with open('./jsons/coursesDetailed.json') as f:
            coursesOld = json.load(f)
        courses = getdetailedcourses.getdetailedcourses(True)
        courseChanges = {}

        if len(courses) > 0 and len(coursesOld) > 0: #making sure we have courses to iterate over
            for course in courses: #for each element in remote course list
                if int(course) in coursesToTrack: #find an element that is in our tracking list
                    for findCourse in coursesOld: #and then for each element in our old list
                        if int(findCourse) == int(course): #find the element which is the same
                            for assignment in courses[course]:

                                assignmentGrade = ""
                                oldAssignmentGrade = ""
                                removed = False
                                added = False
                                
                                for assignmentOld in coursesOld[str(course)]:
                                    if assignment == assignmentOld:
                                        assignmentGrade = courses[course][assignment]
                                        oldAssignmentGrade = coursesOld[str(course)][assignmentOld]
                                        break
                                    if assignmentOld not in courses[course]: #assignment has been removed
                                        oldAssignmentGrade = coursesOld[str(course)][assignmentOld]
                                        coursesOld[str(course)].pop(assignmentOld)
                                        removed = True
                                    if assignment not in coursesOld[str(course)]: # assignment has been added
                                        assignmentGrade = courses[course][assignment]
                                        added = True
                                    if added == True or removed == True:
                                        break
                                    
                                if added == True: #assignment has been added
                                    if not courseChanges.get(int(course)):
                                        courseChanges[int(course)] = {}
                                    if not courseChanges[int(course)].get("A"):
                                        courseChanges[int(course)]["A"] = {}
                                    courseChanges[int(course)]["A"][assignment] = assignmentGrade
                                if removed == True: #assignment has been removed
                                    if not courseChanges.get(int(course)):
                                        courseChanges[int(course)] = {}
                                    if not courseChanges[int(course)].get("R"):
                                        courseChanges[int(course)]["R"] = {}
                                    courseChanges[int(course)]["R"][assignmentOld] = oldAssignmentGrade
                                if assignmentGrade != oldAssignmentGrade and added == False and removed == False: #grade has been modified
                                    if not courseChanges.get(int(course)):
                                        courseChanges[int(course)] = {}
                                    if not courseChanges[int(course)].get("M"):
                                        courseChanges[int(course)]["M"] = {}
                                    courseChanges[int(course)]["M"][assignment] = [assignmentGrade, oldAssignmentGrade]
                            break
            
            if len(courseChanges) > 0:
                with open('./jsons/courses.json') as f:
                    courseListing = json.load(f)

                out += "Alert! Found changes in Gradescope assignment grading."
                for course in courseChanges:
                    for item in courseListing:
                        if item[0] == course: #found course
                            out += "\n" + item[1] + " (" + item[2] + "):"
                            for typeOfChange in courseChanges[course]:
                                if typeOfChange == 'A': #added
                                    for changedItem in courseChanges[course][typeOfChange]:
                                        name = changedItem
                                        grade = courseChanges[course][typeOfChange][changedItem]
                                        out += "\n" + "Grade for " + name + " has been added: " + grade
                                elif typeOfChange == 'R': #removed
                                    for changedItem in courseChanges[course][typeOfChange]:
                                        name = changedItem
                                        grade = courseChanges[course][typeOfChange][changedItem]
                                        out += "\n" + "Grade for " + name + " has been removed. Old grade: " + grade
                                elif typeOfChange == 'M':
                                    for changedItem in courseChanges[course][typeOfChange]:
                                        name = changedItem
                                        oldGrade = courseChanges[course][typeOfChange][changedItem][1]
                                        newGrade = courseChanges[course][typeOfChange][changedItem][0]
                                        out += "\n" + "Grade for " + name + " has been modified: " + oldGrade + " -> " + newGrade
                            out += "\n"
        else:
            print("You don't have any Gradescope courses. Please add a course before using this script")
            sys.exit(1)


    else:
        with open('./jsons/courses.json') as f:
            coursesOld = json.load(f)
        courses = getcourses.getcourses() #have to get courses after reading from json because getcourses overwrites json with new data
        more = []
        less = []

        if len(courses) > 0 and len(coursesOld) > 0: #making sure we have courses to iterate over
            for course in courses: #for each element in remote course list
                if course[0] in coursesToTrack: #find an element that is in our tracking list
                    for findCourse in coursesOld: #and then for each element in our old list
                        if findCourse[0] == course[0]: #find the element which is the same
                            if int(findCourse[3].split()[0]) == int(course[3].split()[0]): #comparing number of assignments
                                break
                            elif int(findCourse[3].split()[0]) > int(course[3].split()[0]): #more assignments in old list = assignment hidden
                                course[3] = int(course[3].split()[0])
                                course.append(int(findCourse[3].split()[0]))
                                more.append(course)
                            elif int(findCourse[3].split()[0]) < int(course[3].split()[0]): #less assignments in old list = assignment published
                                course[3] = int(course[3].split()[0])
                                course.append(int(findCourse[3].split()[0]))
                                less.append(course)

            if len(more) > 0:
                out += "Assignments hidden:"
                for item in more:
                    out += "\n" + item[1] + " (" + item[2] + ") | " + str(item[4]) + " -> " + str(item[3])
                out = out + "\n"
            if len(less) > 0:
                out += "Assignments published:"
                for item in less:
                    out += "\n" + item[1] + " (" + item[2] + ") | " + str(item[4]) + " -> " + str(item[3])
                out = out + "\n"
            if len(less) > 0 or len(more) > 0:
                out = "Alert! Found changes in Gradescope assignment count.\n" + out

    if out != "":
        for trackingAlertMethod in config["trackingAlerts"]:
            if trackingAlertMethod == "print":
                print(out)
            elif trackingAlertMethod == "telegram":
                with Client("./jsons/pyrogram") as app:
                    app.send_message(config["telegramUsername"], out)

else:
    print("No courses to track found. Rerun setup.py with the tracking option enabled.")
    sys.exit(1)