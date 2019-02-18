import os, paramiko, sys, time
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from os import walk
#from os.path import isfile, join

#this program is basically a poor man's google drive that constantly update files on the remote server whenever a local change is made
#A use case for this would be to write python on PC, but execute it on a raspberry pi


'''
To Do: 
Select local folder
Select remote Folder
See data in local folder
See data in remote folder
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

class SSH(object):
    ip='192.168.0.8'
    user='pi'
    password='0000'
    channel=paramiko.channel.Channel

def getDir():
    messagebox.showinfo('Select Directory', 'Please the folder that will be backed up')
    WorkingDir = askdirectory()
    print(WorkingDir)
    return WorkingDir

def getLocalStats(WorkingDir):

    localStats={}

    onlyfiles = [f for f in os.listdir(WorkingDir) if os.path.isfile(os.path.join(WorkingDir, f))]

    for i in range(len(onlyfiles)):
        localStats[onlyfiles[i]]=[int(os.path.getmtime(WorkingDir+'/'+onlyfiles[i])),WorkingDir+'/'+onlyfiles[i],'']
    
    return localStats
    
def getRemoteStats():

    dir = SendCommand('ls')
    print('!!!')
    print(repr(dir[0]))
    print('!!!')
    print(dir[0])
    print('!!!')

    #print('stat %s -c "%%Y"'%str(dir[0]))

    times = SendCommand("stat %s -c '%%Y'"%str(dir[0]))#, expect=':~$')

    print(times)

    #https://askubuntu.com/questions/818093/permanently-disable-color-in-default-terminal
    '''
    Okay I am going to bed fore the night. it is 4:12 am as I write this and I have a thing to do tommorow (today?)
    seeing normal files works fine, but seeing the newly added file normally 'Red Brick Paradise (demo).mp3' is seen as 
    
    '\x07m\x070;36mRed Brick PParadise (demo).mp3\x07m' or '?[0m?[00;36mRed Brick Paradise (demo).mp3?[0m'

    not sure if this is because it is an mp3 and therefore it is colored, or if it is because there are spaces.
        - right now I am leaning more towards the color being the issue. Maybe later I will remove all colrs and that will fix it or I can just flip a swiutch and make it not be weird


    '''



def ExpectCommand(command, expect,delay=0,timeout=5,RaiseFail=False,bkgColor=True,searchCount=1,WriteToLog = True):
    '''
    Thanks Boyang!
    '''
    out = []
    temp = ''
    line_feed_byte = '\r'.encode('utf-8')
    
    if(SSH.channel.send_ready()):
        if command != '':
            print('!! Executing command [%s]' % (command))
        SSH.channel.send(command + '\r')
    else:
        print('Unable to send command')
        return False
    
    #time.sleep(1)
    start = time.time()

    try:
        while True:
            end = time.time()
            if(end - start) >= timeout:
                print('[COULD NOT FIND %s]' %expect)
                if RaiseFail: raise Exception('TimerTimeout')
                else: return False
            byt = SSH.channel.recv(1)
            try: 
                if byt.decode('utf-8') == '': raise Exception('SocketError')
            except: pass
            
            if byt != b'\n': #this is causing issues with the way raspi works 
                try: temp += byt.decode('utf-8').rstrip('\r\t')
                except: pass
            
            if byt == line_feed_byte:
                '''
                if WriteToLog == True:
                    print(temp)
                '''
                out.append(temp)
                if expect:
                    for i in expect.split('|'):
                        if i in temp:
                            print('FOUND [%s] '%i)
                            time.sleep(1)
                            #channel.send('\x03')#termination
                            return out
                elif expect is None and searchCount is not 0: searchCount = searchCount - 1
                else: 
                    return out
                temp = ''
    except Exception as e:
        print(e)
        return False


def SendCommand(command, timeout=3,nBytes=1024,initDelay=0.5, WriteToLog = True):
	out = []
	current_buffer = ''
	if WriteToLog == True:
		print('!! Executing command [%s] !!'%command)
	if(SSH.channel.send_ready()): SSH.channel.send(command + '\r')
	else:
		print('unable to send command')
		return
	time.sleep(initDelay)#initial delay to make sure all the data is buffered
	
	while SSH.channel.recv_ready(): ##get all the output bytes and decode the data and remove all the \r\t
		current_buffer = SSH.channel.recv(nBytes).decode('utf-8').replace('\r','').replace('\t','') 
		
	for i in current_buffer.split('\n'): #cleaning the output and removing the executed command from the output list
		if command not in i and i is not '': out.append(i)	
	return out



def quickConnect():#ip,usr,password):
    connection = paramiko.SSHClient()
    connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection.connect(SSH.ip, username=SSH.user, password=SSH.password, port=22, timeout=2)
    print('successful ssh\n')
    SSH.channel = connection.invoke_shell()
    ExpectCommand('',expect=':~$')
    return SSH.channel

def GetSSH():
    Connection=False
    
    while not Connection:

        hold=input("What is the ip of the device?\n(Leave empty for %s)\n"%SSH.ip)
        if hold != '':
            SSH.ip = hold

        hold=input("What is the username?\n(Leave empty for %s)\n"%SSH.user)
        if hold != '':
            SSH.user = hold

        hold = input("What is the password?\n(Leave empty for %s)\n"%SSH.password)
        if hold != '':
            SSH.password = hold

        try:
            connection = paramiko.SSHClient()
            connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connection.connect(SSH.ip, username=SSH.user, password=SSH.password, port=22, timeout=2)
            print('successful ssh\n')
            SSH.channel = connection.invoke_shell()
            ExpectCommand('',expect=':~$')
            return SSH.channel
        except Exception as e:
            print("Cannot Connect")
            print(e)
            hold = input("Would you like to try to reconnect? (Y/n)")
            if hold.lower() != 'y':
                sys.exit()

def main():
    
    #workingDir = getDir()
    #workingDir = 'C:/Users/Pixel Amp/Desktop/PixelParity'

    #localStats = getLocalStats(workingDir)

    #print(localStats) 

    quickConnect()
    getRemoteStats()
    '''
    command=''
    print('Enter SSH Command:')
    while command != 'exit':
        command = input()
        response = SendCommand(command)#, expect=':~$')
        print(response)
    '''
    
    


    
    



if __name__ == "__main__":
    main()