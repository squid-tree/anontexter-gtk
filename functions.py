import settings 
import pgpy 
import fabric
from pgpy import PGPKey
import inspect
from fabric import Connection
from settings.settings import * 
from datetime import datetime

class checkedpassword():
    def __init__(self, is_correct, other_error=None):
        self.is_correct = is_correct
        self.other_error=None

def getpgp(directory):
    try:
        key = pgpy.PGPKey.from_file(directory)
    except:
        print("BIG key error")
        quit()
        return checkedpassword(is_correct=False)
    else:
        return key

def sshpasswordverif(sshhost,sshuser,sshport,password):
    try:
        conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)
        conn.open()
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e)) 
    else:
        return checkedpassword(is_correct=True)

def sshdirverif(sshhost,sshuser,sshport,password,msgdir):
    conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)    
    try: 
        messagelist = conn.run('ls %s' % msgdir).stdout
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        return checkedpassword(is_correct=True) 

def pgppasswordverif(usrpgp, password):
    try:
        with usrpgp[0].unlock(password):
            if usrpgp[0].is_unlocked == True:
                x = True
            else:
                x = False
    except pgpy.errors.PGPDecryptionError as e:
        return checkedpassword(is_correct=False, other_error=repr(e))  
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        print(repr(usrpgp))
        if x==True:
            print('%s is actually correct' % password)
            return checkedpassword(is_correct=True)
        elif x==False:
            print('%s is incorrect' % password)
            return checkedpassword(is_correct=False)

def messagesget(sshhost,sshuser,sshport,password,msgdir):
    conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)
    
    try: 
        messagelist = conn.run('ls %s' % msgdir).stdout
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))

    filelist=messagelist.splitlines()
    filelist.sort()
    filemessages={}

    for i in filelist:
        try:
            msgcat = conn.run('cat \'%s\'/\'%s\'' % (msgdir,i))
        except Exception as e:
            return str("There was an error, perhaps the file directory doesn't exist or the ssh details were wrong?: %s" % repr(e))
        filemessages[i] = msgcat.stdout

    return filemessages

def messagesunlock(filemessages, usrpgp, password):
    decryptedmessages = {}

    for i in filemessages:
        msg = pgpy.PGPMessage.from_blob(filemessages[i])
        try: 
            with usrpgp[0].unlock(password):
                decryptmsg = usrpgp[0].decrypt(msg).message
        except Exception as e:
            decryptedmessages[i] = str("Unencryptable message (Could be made by you or someone who wasn't talking to you")
            print(repr(e))
            continue
        else:
            decryptedmessages[i] = decryptmsg
            continue
    
    return decryptedmessages


def sendmessage(message, recpgp, sshhost,sshuser,sshport,password):    
    filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn=fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)

    msg = pgpy.PGPMessage.new(message)
    
    try:
        msg = recpgp[0].encrypt(msg)
    except Exception as e:
        print(recpgp[0])
        print(repr(e))
        print('pgperror')
        quit()
        return checkedpassword(is_correct=False, other_error=repr(e))

    try:
        conn.run(str("echo \'%s\' > %s/\'%s\'" % (msg, messagesdirectory, filename)))
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        return checkedpassword(is_correct=True)

