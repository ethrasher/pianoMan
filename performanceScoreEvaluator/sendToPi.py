import os
import paramiko # Citation[1,2,3,4]
import warnings # Citation[5]
warnings.filterwarnings(action='ignore',module='.*paramiko.*')
#Note for original developer:python alias to use => pythoncv

def sendFileToPi(fileName):
    try:
        ssh = createSSHClient()  # Citations [1,2,3,4]
        ftp_client = ssh.open_sftp()
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        outGoingDest = scriptPath + "/" + fileName
        inComingDest = "/home/pi/Desktop/PianoManProject/MusicXML_MuseScore/" + fileName
        ftp_client.put(outGoingDest, inComingDest)
        ftp_client.close()
    except:
        raise Exception("Could not make connection to raspberryPi. Make sure pi is on.")

def createSSHClient():
    # DESCRIPTION: makes the connection over SSH to the raspberryPi
    # PARAMETERS: Nothing
    # RETURN: client: a paramiko SSHClient object giving the SSH connection to the raspberryPi

    client = paramiko.SSHClient() #Citations [1,2,3,4]
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname="172.26.197.78", port=22, username="pi", password="pianoMan2019")
    return client