# Gradescope-Tools

## About

This repo contains a collection of useful tools for [Gradescope](https://www.gradescope.com):

1. Assignment grade tracking.
    * Basic: Tracks total number of assignments per class, notifies when total changes.
    * Detailed: Tracks each assignment's grades, notifies when assignments are added and removed (with grade history) and grades are changed.
    * Notifications are handled via console printing or Telegram. More methods may be added in the future.
2. Download all (graded) PDFs for any class.
3. Calculate (non-weighted) percentage total for any class' grades.
4. Print internal info about any class.

The project does not use the mobile API (if there is one), and instead uses queries which have been reversed from browser queries to the Gradescope servers. Because of this, these tools are entirely reliant on HTML scraping (specifically the bs4 Python library). At any time, Gradescope can change the layout of any of the pages used, breaking these tools. If this happens, please open an issue request, and I will try to fix it.

**NOTE: SSO ACCOUNTS ARE NOT SUPPORTED! YOU MUST BE ABLE TO LOGIN WITH A USERNAME AND PASSWORD TO USE THESE TOOLS!**

**NOTE: ONLY GRADESCOPE.COM ACCOUNTS ARE SUPPORTED! YOU CANNOT USE A .CA, .COM.AU OR .EU ACCOUNT WITH THESE TOOLS!** (this may change in the future with enough requests)

NOTE: While I have tested these tools extensively, I have yet to use them for an extended period of time, as this is a summer coding project and I don't have any summer classes that use Gradescope. Something may or may not break. Feel free to open an issue request if something breaks.

## Setup and Prerequisites

These tools are designed to run on Python 3.8+ (Tested on 3.11, presumed to be working on 3.10 and 3.9, may or may not work on earlier versions). If your version of Python is too old, consider updating in order to use these tools.

Setup:

```
pip install requirements.txt
python3 setup.py
```

The setup will drop files into a ./jsons/ folder. It is preferable to run setup.py from the repo folder.

Pyrogram and TyCrypto are optional prerequisites and can be removed if the Telegram notification module is not used.

Here's how to set up Telegram notifications:

0. Get a Telegram account (or add a username to your existing one).
1. Contact [BotFather](https://t.me/BotFather) and create a new bot (or use an existing one).
2. Obtain a Telegram [App ID and Hash](https://core.telegram.org/api/obtaining_api_id).
3. Message your bot with `/start` (it won't respond, this is normal).
4. Start `setup.py` and choose the Telegram notification method.

## Usage

```
cd Gradescope-Tools
python3 run.py
```

Use the arrow keys to move up and down the menu. For menus with multiple options, you can use the space key to select one or multiple elements. Enter sends the input to the script.

If you want to run the course tracker, you will need to add track.py to your crontab (Linux) or task scheduler (Windows). The tracker script is designed to run in the repo folder: `* * * * * cd ~/Gradescope-Tools && python3 track.py` for crontab. I don't use Windows Server, please refer to Google for the runline there.

The modules can serve as helpful starter tools in your own Gradescope adventures. They cannot be run by themselves without `run.py`, but you are free to use the code contained within them.

## Q&A

Q: Do I need to set up a database to use these tools?<br>A: No, these tools were designed to run without a database on portable devices and low-powered servers, hence the cloud of .json files in the `./jsons` folder.

Q: Will my account get banned for using these tools?<br>A: No idea. I have taken great efforts to ensure that heavy network queries (like the ones in the detailed notification mode) do not accidentally spam the servers (there is an arbitrary 0.5 seconds of sleep in between network calls), and I make no attempts to pass these tools off as a legitimate browser (The default user-agent is uniquely identifiable from a common browser, the headers aren't the same as a browser, etc).

The current Gradescope [TOS](https://www.gradescope.com/tos), as of the time of writing, prohibit "using any automated system [...] to access the Service in a manner **that sends more request messages to the Gradescope servers than a human can reasonably produce in the same period of time by using a conventional on-line web browser**" (emphasis mine). It may be allowable to use simple automation tools to simplify the experience, however, I am not a lawyer, and using these tools is up to your own risk.

Please use these tools responsibly, and know that they are provided as-is. I may or may not update them in the future if they break.

Q: Why does the graded PDF downloader take so long?<br>A: The reasoning is the same as the previous question. It would be unethical for me to release tools that get Gradescope accounts banned, so I cannot take advantage of async downloading methods, and instead the scripts downloads graded assignments synchronously, about as fast as a user can open new tabs to download the files.

Q: Why can't I download original non-graded PDFs?<br>A: The link to non-graded PDFs is obtained via an obfuscated giga-JS library that is too much work to reverse. Realistically, as a student, I only care about the graded PDF, so I decided to not waste my time reversing the library and only export graded PDFs.

## Notice of Non-Affiliation and Disclaimer

Gradescope-Tools is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Turnitin, LLC, or any of its subsidiaries or its affiliates. The official Gradescope website can be found at http://www.gradescope.com.

The names Gradescope and Turnitin as well as related names, marks, emblems and images are registered trademarks of their respective owners.