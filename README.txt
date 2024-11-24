HOW TO RUN

run "start.bat" to download reddit videos into the Videos folder

run "startall.bat" to download all videos, pictures and gifs to the specified folders

archive.json is there so the script can log everything it downloads, so it doesn't ever download any duplicates



WHAT YOU NEED

You need Python: https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe

You need VS Code: https://code.visualstudio.com/docs/?dv=win64user



HOW TO CHANGE THE SUBREDDIT

to change what subreddit it scans, go to line 94 for Video.py, and line 125 for all.py



HOW TO GET EVERYTHING WORKING

open the scripts in vs code, open a new terminal, and run the following code in both scripts

pip install praw yt-dlp requests json subprocess os time random

Keep all these files in the same folder, or they wont work properly!

DONT CHANGE ANYTHING ELSE ABOUT THE SCRIPT, IT IS ALREADY SET UP FOR YOU!

