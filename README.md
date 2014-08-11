photokeeper
===========

Small script set to backup photos unidirectionally

THIS IS FAR FROM READY. I have little time to pursue this project and things here should be broken most of the time


# Plan

## EXIF and path handling

- Make sure I can get from the EXIF the proper info
- Make sure I can create a usefull path for the backup
- Treat improper data (bad or missing EXIF and its destination
- Treat video files

## File comparision

- Find a way to avoid doing two copies of the same file
- Register that the photo has been through the backup process
- Increment this (as when I add glacier to the vanilla HD backup)
- Compare file binarily

## Log the process

- Get a sqlite3 database up and running
- Decide the info that goes there
- Do it

## UX

- Study UX options (both GUIs multi-platform and terminal-only)

