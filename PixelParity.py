import os, paramiko, sys, time, select, re
from tkinter.filedialog import askdirectory
from tkinter import messagebox

#This program is basically a poor man's google drive that constantly update files on the remote server whenever a local change is made
#use cases:
#keep an offsite backup of a folder 
#write python on PC, but execute it on a raspberry pi



'''
To Do: 
DONE!   Select local folder 
DONE!   Select remote Folder
DONE!   See data in local folder
DONE!   See data in remote folder
See if changes in local folder
See if changes in remote folder

Compare data in each folder
Add ability to toggle whether to replace local file if remote one is newer
    By default should the local folder always have the newest file version?
        Or should whatevr is newest always take priority over both?
Replace file in remote folder with local file
Replace file in local folder with remote file
Make it check the folders on a set timer
    Add ability to adjust the timer during run time

Add ability to check and copy whole folders and everything in directories, not just the top-most files
Make logo for project. Probably in the same style as my normal PA

Make a verion that autoruns/auto selects folders without the user having to do anything

Can Python run in the Taskkbar?
    quick goolgle says maybe: https://stackoverflow.com/questions/9494739/how-to-build-a-systemtray-app-for-windows
    *.pyw - execute your script in background mode without command prompt


Extra Credit:
Add ability to select both local folders
See if there is a way to make it check only when there is a change
    How intesive is it to do a check? 
        Can it just constanly be checking times on both platforms? Or is it too intesive and should only happen on a timer


    extra extra credit: 
        add ability to select two remote folders?
        Add ability to slect different chekcing timers for each directory
            i.e. 30 seconds for local and 60 seconds for remote
'''

class ToolBox(object):
    ip= 'PixelZero.local' #'192.168.0.19' #'PixelDac.local'
    user='pi'
    password='0000'
    channel=paramiko.SSHClient()
    #channel.open_sftp() #not initializing, once init SSH gets run it'll be here
    LocalDir=''
    LocalStats={}
    RemoteDir=''
    RemoteStats={}
    IgnoreFiles=[]
    IgnoreDir=['.git']

def GetFile(Rpath, Lpath):
    ToolBox.sftp.get(Rpath,Lpath)
    print("get")


def SendFile(Rpath, Lpath):
    ToolBox.sftp.put(Lpath, Rpath)
    print("send")

'''
make this recoursive, have it return a dictionary of the values within that folder.
If it finds a folder, call this function again and go intide that folder until it returns the values inside if itself

dir: file data, SubDir 

{RootDir: [File, age], [File, age], {SecondDir: [File, age]}}

{PixelParity: ['Different ways to see local files.txt', 'Fileupdater - Copy.pyw', 'PixelParity.py', 'README.md', {testFolder: [testfile.txt]},  ]}
'''
def getLocalStats(WorkingDir):

    localStats={}
    currdir=re.sub(r'.*/', '', WorkingDir) #gets only the current directory
    
    localStats.setdefault(currdir, [])

    #get files in directory
    files = [f for f in os.listdir(WorkingDir) if os.path.isfile(os.path.join(WorkingDir, f))]
    
    #fills dictionay with files and their ages
    for num in range(len(files)):
        if files[num] not in ToolBox.IgnoreFiles: #ignore Files
            localStats[currdir].append([files[num], int(os.path.getmtime(WorkingDir+'/'+files[num]))]) #floor() rounds down. int() truncates if any issues come up with slightly off times, look here
        else:
            print("Ignoring %s"%files[num])
    
    #get sub directories within this directory
    dir = [f for f in os.listdir(WorkingDir) if os.path.isdir(os.path.join(WorkingDir, f))]
    
    #recursively call this function to get the files within the subdirectory
    for num in range(len(dir)):
        if dir[num] not in ToolBox.IgnoreDir: #ignore Folders
            localStats[currdir].append(getLocalStats(WorkingDir+'/'+dir[num]))
        else:
            print("Ignoring %s"%dir[num])
    
    #ToolBox.LocalStats = localStats #not going to automatically update the master record, it should have to be updated once comparison is complete
    return localStats
    
def getRemoteStats(WorkingDir):

    localStats={}
    currdir=re.sub(r'.*/', '', WorkingDir) #gets only the current directory
    localStats.setdefault(currdir, [])

    #get files within the current folder
    files = SSHCommand('ls %s -p | grep -v /'%WorkingDir, debug=False).split('\n')

    #fills dictionay with files and their ages
    for num in range(len(files)):
        if files[num] not in ToolBox.IgnoreFiles and files[num]: #ignore Files
            localStats[currdir].append([files[num], int(SSHCommand("stat %s -c '%%Y'"%("'"+WorkingDir+'/'+files[num]+"'")).replace('\n',''))])

        else: 
            if files[num]:
                print("Ignoring %s"%repr(files[num]))


    #Get sub directories within this directory
    #If there are no subdirectories an error gets sent out, so I effectively catch it
    dir = SSHCommand('ls -d %s/*/'%WorkingDir, debug=False, AcceptableError='No such file or directory').split('\n') 
    
    #recursively call this function to get the files within the subdirectory
    for num in range(len(dir)):
        if dir[num] not in ToolBox.IgnoreDir and dir[num]: #ignore Folders
            localStats[currdir].append(getRemoteStats(dir[num][:-1])) 
        else:
            if dir[num]:
                print("Ignoring %s"%repr(dir[num]))
    
    #ToolBox.RemoteStats = localStats #not going to automatically update the master record, it should have to be updated once comparison is complete
    return localStats

'''
5 pssibilities for deleting and creating new files:
1 Always Delete if file is not found on one to keep parity between the two (though what is the difference between a new file vs a deleted one?)
2 Never delete - always make sure file is at both places, so if it is missing on one, copy it over
3 Local drive is law, remote drive is Slave - deletion and addition will only take place on the remote drive because the local drive is always right and remote drive is just a backup #this might be the one I am going to go with until #5 figured out
4 Bias to remote drive - always copy follow whatever is on the remote drive - if new file copy it over , if file missing delete it
5 If i knew about it previously and it is missing delete it on both, but if it is new make it exist on both (this requires a local copy of the layout of the folders) #this is the best method, but requires more work
    this actually need to happen anyways during runtime 
'''

'''
Keep a manafest of the directories in a test file that is stored in both folders, but ignore it during the comparison.
Only update the file and copy it onto both after finishing a comparison, when it is totally up to date


'''


#comparison the first time this program is rerun to make sure manafests are correct and cache is set up
def FirstTimeComparison():
    
    localStats = getLocalStats(ToolBox.LocalDir)
    initSSH()
    remotestats = getRemoteStats(ToolBox.RemoteDir)
    
    print('Local:') 
    print(localStats)
    print('Remote:')
    print(remotestats)

#compares the values of both directories and ballances them so they contain the same items
def CompareDirectories():
    ToolBox.LocalDir
    ToolBox.RemoteDir


#compares current local state to the cached local state to see if files have been added or deleted
def CheckChangesLocal():
    CurrState = getLocalStats(ToolBox.LocalDir)

    if CurrState == ToolBox.LocalStats:
        print("they are the same")
    else:
        print("they are different")
        print(CurrState)
        print(ToolBox.LocalStats)



    return False

#compares current remote state to the cached local state to see if files have been added or deleted
def CheckChangesRemote():
    return False


def SSHCommand(command, debug=False, AcceptableError='',Split=False):
    
    error = ''
    output = ''
    if debug:
        print('!!!!! Excecuting "%s" !!!!!'%command)
    stdin, stdout, stderr = ToolBox.channel.exec_command(command)

    error = stderr.read().decode('utf-8')#.replace('\r','')
    if error:
        if AcceptableError not in error:
            print('!!!error!!!')
            print(repr(error))

    # Wait for the command to terminate
    while not stdout.channel.exit_status_ready():
        # Only print data if there is data to read in the channel
        if stdout.channel.recv_ready():
            rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                output = stdout.channel.recv(4096).decode('utf-8')
    
    if Split: #returns each line as it's own value in an array
        return output.split('\n')
    else:
        return output

def initSSH():
    ToolBox.channel = paramiko.SSHClient()
    ToolBox.channel.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ToolBox.channel.connect(ToolBox.ip, username=ToolBox.user, password=ToolBox.password, port=22, timeout=2)
        ToolBox.sftp = ToolBox.channel.open_sftp()
        #print('Successful ssh and sftp\n')
        return True
    except:
        print("SSH Failure")
        return False

def GetSSH():
    Connection=False
    
    while not Connection:

        hold=input("What is the ip of the device?\n(Leave empty for %s)\n"%ToolBox.ip)
        if hold != '':
            ToolBox.ip = hold

        hold=input("What is the username?\n(Leave empty for %s)\n"%ToolBox.user)
        if hold != '':
            ToolBox.user = hold

        hold = input("What is the password?\n(Leave empty for %s)\n"%ToolBox.password)
        if hold != '':
            ToolBox.password = hold

        if not initSSH():
            hold = input("Would you like to try to reconnect? (Y/n)")
            if hold.lower() != 'n':
                sys.exit()

def getLocalDir():
    messagebox.showinfo('Select Directory', 'Please select the folder that will be backed up')
    WorkingDir = askdirectory()
    print(WorkingDir)
    return WorkingDir

#nned to think of a better name for this cunction, but it basically lets the user send in commands to the SSH deivce
def EmulateConsole():    
    command=''
    print('Enter SSH Command:')
    while command != 'exit':
        command = input()
        response = SSHCommand(command)
        print(response)

def main():
    #initSSH()
    #LocalDir = getDir()
    ToolBox.LocalDir = 'C:/Users/Pixel Amp/Desktop/PixelParity'
    ToolBox.RemoteDir = '/home/pi/PixelParity'

    ToolBox.LocalStats = getLocalStats(ToolBox.LocalDir)

    input('waiting')
    
    CheckChangesLocal()

    #FirstTimeComparison()

    ToolBox.channel.close()


if __name__ == "__main__":
    main()