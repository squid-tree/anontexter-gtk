import settings 
import pgpy 
import fabric
import os
import multiprocessing
from pgpy import PGPKey
import inspect
from fabric import Connection
from settings.settings import * 
from datetime import datetime
import sys

class checkedpassword():
    def __init__(self, is_correct, other_error=None):
        self.is_correct = is_correct
        self.other_error=None

def sshpasswordverif(sshhost,sshuser,sshport,password):
    try:
        conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)
        conn.open()
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e)) 
    else:
        return checkedpassword(is_correct=True)

def pgppasswordverif(usrpgp, password):
    try:
        usrpgp.unlock(password)
    except pgpy.errors.PGPDecryptionError:
        return checkedpassword(is_correct=False)
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        return checkedpassword(is_correct=True)



def messagesget(sshhost,sshuser,sshport,password):
    conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)
    
    try: 
        messagelist = conn.run('ls %s' % messagesdirectory).stdout
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))

    filelist=messagelist.splitlines()
    filelist.sort()
    filemessages={}

    for i in filelist:
        try:
            msgcat = conn.run('cat \'%s\'/\'%s\'' % (messagesdirectory,i))
        except Exception as e:
            return str("There was an error, perhaps the file directory doesn't exist or the ssh details were wrong?: %s" % repr(e))
        filemessages[i] = msgcat.stdout

    return filemessages

def messagesunlock(filemessages, usrpgp):
    decryptedmessages = {}

    for i in filemessages:
        msg = pgpy.PGPMessage.from_blob(filemessages[i])
        try: 
            with usrpgp.unlock(password):
                decryptmsg = usrpgp.decrypt(msg).message
        except Exception as e:
            decryptedmessages[i] = str("Unencryptable message (Could be made by you or someone who wasn't talking to you")
            continue
        else:
            decryptedmessages[i] = decryptmsg
            continue

        print("Message successfully sent")

def sendmessage(message, recpgp):    
    filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        msg = recpgp[0].encrypt(message)
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))

    try:
        conn.run(str("echo \'%s\' > %s/\'%s\'" % (msg, messagesdirectory, filename)))
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        return checkedpassword(is_correct=True)
