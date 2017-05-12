#!/c/Users/swenninger/AppData/Local/Programs/Python/Python36-32/python.exe

# Created by Samuel Wenninger
# Last modified 5/11/2017

import json, subprocess, os, sys, platform, psutil, paramiko
from scp import SCPClient

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

def handlePrompts(settings, commandList, promptResponses):
    stringCommandList = ''.join(commandList)
    if 'PROMPT' not in stringCommandList:
        return commandList
    dirName = False
    newCommandList = []
    for command in commandList:
        if 'PROMPT' in command:
            promptNum = str(command.split('#')[-1])
            # Check for a previous response to the same prompt and use it if it is available.
            if str(promptNum) in promptResponses.keys():
                dirName = promptResponses[str(promptNum)]
            else:
                dirName = input(settings['prompts'][promptNum]['text'])
            promptResponses[str(promptNum)] = dirName
            continue
        if dirName is not False and '{{}}' in command:
            command = command.replace('{{}}', dirName)
        newCommandList.append(command)
    return newCommandList

# Desc: Run a given task in the correct context given the tasks index
# Input: "location" - a dict containing the "modeIndex" and "taskIndex"
# Output:
def runTask(settings, location):
    #subprocess.run('mkdir -v test')
    commandList = []
    prevProjectId = False
    # Keep track of previous responses for commands that use the same prompt so that the user
    # is not prompted multiple times for the same information
    promptResponses = {}
    for commandId in settings['modes'][location['modeIndex']]['tasks'][location['taskIndex']]['commandSequence']:
        # Get the command object
        command = settings['commands'][str(commandId)]
        # Get the projectId associated with the command
        commandProjectId = int(command['projectId'])
        # If the next command is in a different project than the previous command, switch directories
        # to the location of said project before executing the requested command
        if prevProjectId is False or commandProjectId != prevProjectId:
            prevProjectId = commandProjectId
            os.chdir(str(settings['projects'][str(commandProjectId)]['path'][PLATFORM]))
        printBoxMenu([command['name']], len(command['name']))
        # The subprocess causes the output to be buffered so a manual flush is required here.
        sys.stdout.flush()
        updatedCommand = handlePrompts(settings, command['commandList'][PLATFORM], promptResponses)
        stringCommandList = ''.join(updatedCommand)
        if 'WINSSH' not in stringCommandList and 'WINSCP' not in stringCommandList:
            for item in updatedCommand:
                subprocess.run(item, shell=True)
        else:
            arg = False
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if 'WINSSH' in stringCommandList:
                for item in updatedCommand:
                    if arg is True:
                        arg = False
                        server = str(item.split('"')[0].strip())
                        command = str(item.split('"')[1].strip())
                        ssh.connect(server)
                        stdin, stdout, stderr = ssh.exec_command(command)
                        for line in stdout.readlines():
                            print(line)

                    if item == 'WINSSH':
                        arg = True
                        continue
            elif 'WINSCP' in stringCommandList:
                skips = 0
                for index, item in enumerate(updatedCommand):
                    if skips:
                        skips -= 1
                        continue
                    if item == 'WINSCP':
                        fileName = updatedCommand[index + 1]
                        server = updatedCommand[index + 2]
                        dest = updatedCommand[index + 3]
                        ssh.connect(server)
                        scp = SCPClient(ssh.get_transport())
                        scp.put(fileName, dest)
                        skips = 3
                        continue

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
    main()

# To Do
## Add an upload prebuild task
### Prompt the user for a prebuild folder and a prebuild name
### Use PROMPT to prompt a user and VAR somewhere afterwards
## Add a -f (file) option to allow the user to pass in a different settings.json file
