import time
import threading
import json
import os
import sys

with open('actionTasks.json', 'r', encoding="utf-8") as alphabetFile:
    actionTask = json.load(alphabetFile)
    alphabetFile.close()
    
actionTaskTemp = actionTask["testing"]["steps"]
# actionStep = actionTaskTemp["steps"]
# print(actionStep)
for step in actionTaskTemp:
    print(step)

