#sys imports
import json
import os
import sys
import getpass
#pip imports
import inquirer
from pyrogram import Client
import httpx
import bs4
#custom functions
from modules import getdetailedcourses, trackingsetup, getcourses

print("Making config...")

if not os.path.exists("./jsons"):
    os.mkdir("./jsons")

configQuestions = [
    inquirer.Text("User-Agent", message="What user agent should the script use?", default="Gradescope-Tools dev0.1"),
    inquirer.Confirm("useOlds", message="Do you want \"older courses\" to be used?", default=True),
    inquirer.Confirm("trackingSetup", message="Do you want courses to be added to the tracking list?", default=True)
]
configAnswer = inquirer.prompt(configQuestions)
configAnswer["detailedTracking"] = False #false by default

if configAnswer["trackingSetup"] == True:
    trackingQuestions = [
        inquirer.Confirm("detailedTracking", message="Do you want the tracking to be detailed?", default=True),
        inquirer.Checkbox("trackingAlerts", message="What alert methods do you want to use?", choices=[
            ("Print to console", "print"),
            ("Send Telegram message", "telegram")
        ])
    ]
    trackingAnswers = inquirer.prompt(trackingQuestions)
    configAnswer["detailedTracking"] = trackingAnswers["detailedTracking"]
    configAnswer["trackingAlerts"] = trackingAnswers["trackingAlerts"]

    ### Tracking Module Setup###
    #So far, only Telegram is supported (print doesn't require setup), but other modules may be added on top of this in the future#
    if "telegram" in trackingAnswers["trackingAlerts"] and not os.path.exists("./jsons/pyrogram.session"):
        print("Please read the Telegram section of the README to set up this method")
        apiid = input("API ID: ")
        apihash = input("API Hash: ")
        userid = input("Username: ")
        configAnswer["telegramUsername"] = userid
        print("When Pyrogram prompts you to insert a number or bot token, insert a bot token.")
        with Client("./jsons/pyrogram", int(apiid), apihash) as app:
            app.send_message(userid, "Telegram setup complete!")
    elif "telegram" in trackingAnswers["trackingAlerts"]:
        userid = input("Username: ")

try:
    with open("./jsons/config.json", "w") as f:
        json.dump(configAnswer, f)
    print("Config made and written to disk")
except:
    print("Could not write config file to disk. Check your permissions or if the ./jsons folder exists.")
    sys.exit(1)

print("Checking for Gradescope auth cookies...")

if not os.path.exists("./jsons/cookies.json"):
    print("Gradescope cookies not found, please enter email and password:")
    #Step 1: get CSRF token from webpage
    client = httpx.Client(headers={"User-Agent": configAnswer["User-Agent"]})

    try:
        loginPage = client.get("https://www.gradescope.com/")
    except:
        print("Network error! Please try again later.")
        sys.exit(1)
    if loginPage.status_code != 200:
        raise ValueError("Unknown status code during initial GET")
    
    loginSoup = bs4.BeautifulSoup(loginPage.text, features="html.parser")
    loginForm = loginSoup.find("form", {"action": "/login"})
    loginChildren = loginForm.findChildren("input", {"name": "authenticity_token"})

    if len(loginChildren) == 1: #we found the authenticity token we need in the login form
        authenticityToken = loginChildren[0].get("value")
    else:
        raise ValueError("Multiple or no tokens in login form")

    #Step 2: login with creds and save cookies
    loggedIn = False
    while loggedIn == False:
        userEmail = input("Email: ")
        userPassword = getpass.getpass("Password: ")
        loginPayload = {"utf8": "✓", "authenticity_token": authenticityToken, "session[email]": userEmail, "session[password]": userPassword, "session[remember_me]": "0", "session[remember_me]": "1", "commit": "Log In", "session[remember_me_sso]": "0"}
        
        try:
            loginAction = client.post("https://www.gradescope.com/login", data=loginPayload)
        except:
            print("Network error! Please try again later.")
            sys.exit(1)
        if loginAction.status_code == 302:
            try:
                with open("./jsons/cookies.json", "w") as f:
                    json.dump(dict(client.cookies), f)
                print("Cookies saved as cookies.json.")
                loggedIn = True
            except:
                print("Could not write cookies to disk. Check your permissions or if the ./jsons folder exists.")
                sys.exit(1)
        elif loginAction.status_code == 200:
            print("Invalid username or password! Try again.")
        else:
            raise ValueError("Unknown status code during login phase")

else:
    print("Cookies found!")

if configAnswer["trackingSetup"] == True:
    print("Initiating tracking setup...\nUse arrow keys to navigate, space to select course, enter to finalize options.")
    trackingsetup.trackingsetup()
    if configAnswer["detailedTracking"] == True:
        getdetailedcourses.getdetailedcourses(True)
else:
    getcourses.getcourses()

print("Saved preferences!")