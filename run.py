#sys/pip imports
import os
import sys
import inquirer
#custom functions
from modules import totalcalculator, internalinfo, massdownload

if os.path.exists("./jsons/cookies.json"):
    runtimeQuestions = [
        inquirer.List("run", message="What tool do you want to run?",
        choices=[
            ("Grade total calculator", "calc"),
            ("Class internal info", "int"),
            ("Download graded PDFs", "down"),
            ("Exit", "exit")
        ],)]
    
    while True:
        runtimeAnswer = inquirer.prompt(runtimeQuestions)
        if runtimeAnswer:
            if runtimeAnswer["run"] == "calc":
                totalcalculator.totalcalculator()
            elif runtimeAnswer["run"] == "int":
                internalinfo.internalinfo()
            elif runtimeAnswer["run"] == "down":
                massdownload.massdownload()
            elif runtimeAnswer["run"] == "exit":
                sys.exit(1)
        else: #user pressed ctrl+c
            sys.exit(1)
else:
    print("No account cookies found. Rerun setup.py.")
    sys.exit(1)