#!/c/Users/swenninger/AppData/Local/Programs/Python/Python36-32/python.exe

# Created by Samuel Wenninger
# Last modified 5/11/2017

import json, subprocess, os, sys, platform, psutil, paramiko

# Desc: Read the settings file and turn it into a Python data structure (dict/list)
# Input: N/A
# Output: The python representation of the JSON settings object or False if the settings
#         object is malformed.
def readFile():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return False

def printBoxMenu(menu, largestLine):
    print('-' * (largestLine + 4))
    for line in menu:
        print('| ' + line + (' ' * (largestLine - len(line))) +' |')
    print('-' * (largestLine + 4))


# Desc: Prompt the user to select a mode and a task
# Input: "settings" - a Python dict version of the settings JSON file
# Output: The index of the task to run in the tasks array
#         "False" - if invalid user input
def getUserInput(settings):
    location = {}
    menu = []
    largestLine = 0
    # Prompt the user to select the mode
    for index, item in enumerate(settings['modes']):
        line = str(index + 1) + ') ' + str(item['name'])
        if len(line) > largestLine:
            largestLine = len(line)
        menu.append(line)
    printBoxMenu(menu, largestLine)
    mode = int(input('Choice: '))
    # Ensure the user's choice is within bounds
    if mode > len(settings['modes']) or mode < 1: return False
    location['modeIndex'] = mode - 1
    menu = []
    largestLine = 0
    taskCount = 0
    # Prompt the user to select the task
    for task in settings['modes'][mode-1]['tasks']:
        taskCount += 1
        line = str(taskCount) + ') ' + str(task['name'])
        if len(line) > largestLine:
            largestLine = len(line)
        menu.append(line)
    printBoxMenu(menu, largestLine)
    mode = int(input('Choice: '))
    # Ensure the user's choice is within bounds
    if mode > taskCount or mode < 1: return False
    location['taskIndex'] = mode - 1
    # Index is one less than the user inputted selection
    return location

# Desc: Run a given task in the correct context given the tasks index
# Input: "location" - a dict containing the "modeIndex" and "taskIndex"
# Output:
def runTask(settings, location):
    #subprocess.run('mkdir -v test')
    commandList = []
    prevProjectId = False
    for commandId in settings['modes'][location['modeIndex']]['tasks'][location['taskIndex']]['commandSequence']:
        # Get the command object
        command = settings['commands'][str(commandId)]
        # Get the projectId associated with the command
        commandProjectId = int(command['projectId'])
        # If the next command is in a different project than the previous command, switch directories
        # to the location of said project before executing the requested command
        if prevProjectId is False or commandProjectId != prevProjectId:
            prevProjectId = commandProjectId
            print(os.getcwd())
            os.chdir(str(settings['projects'][str(commandProjectId)]['path'][PLATFORM]))
            print(os.getcwd())
        printBoxMenu([command['name']], len(command['name']))
        # The subprocess causes the output to be buffered so a manual flush is required here.
        sys.stdout.flush()
        for item in command['commandList'][PLATFORM]:
            subprocess.run(item, shell=True)
    return

def main():
    settings = readFile()
    if settings is False:
        print('Error: Malformed JSON settings file')
        return

    location = getUserInput(settings)
    if location is False:
        print('Error: Invalid option selected')
        return

    runTask(settings, location)
    return

if __name__ == '__main__':
    PLATFORM = ''
    ppid = os.getppid()
    if psutil.Process(ppid).name() == 'cmd.exe' or platform.system() == 'Windows':
        PLATFORM = 'Windows'
    else:
        PLATFORM = platform.system()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('fxdeva10.factset.com')
    stdin, stdout, stderr = ssh.exec_command('ls')
    print(stdout.readlines())
    #main()

# To Do
## Add an upload prebuild task
### Prompt the user for a prebuild folder and a prebuild name
### Use PROMPT to prompt a user and VAR somewhere afterwards
## Add a -f (file) option to allow the user to pass in a different settings.json file