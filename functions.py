import settings 
import subprocess
import pgpy 
import fabric
import os
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
        messagelist = conn.run('ls %s' % msgdir, hide=True).stdout
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
        if x==True:
            return checkedpassword(is_correct=True)
        elif x==False:
            return checkedpassword(is_correct=False)

def pgpgetuid(pgp,password):
        try:
            with pgp.unlock(password) as up:
                    x = up.userids[0]
        except Exception as e:
            print(repr(e))
            return checkedpassword(is_correct=False, other_error=repr(e))
        else:
            return x.name

def cachemessages(uid,messagelist):
    maindir = os.path.dirname(os.path.realpath(__file__))
    cachedir = str('%s/cache' % maindir) 
    cachedircont = subprocess.run(['ls',str('%s' % cachedir)], capture_output=True).stdout.decode()

    if uid not in cachedircont:
        os.mkdir(str('%s/%s' % (cachedir, uid)))
    try:
        cacheuiddircont = subprocess.run(['ls', str('%s/%s' % (cachedir,uid))], capture_output=True).stdout.decode()
    except FileNotFoundError:
        print('FileNotFoundError')
        filemessages = {}
        return filemessages

    for i in messagelist:
        if "Unencryptable message" not in messagelist[i]:
            if i not in cacheuiddircont:
                os.system("touch %s/\'%s\'/\'%s\'" % (cachedir, uid, i))
                with open(str("%s/%s/%s" % (cachedir, uid, i)), 'w') as file:            
                    file.write(messagelist[i])

def getcache(uid):
    maindir = os.path.dirname(os.path.realpath(__file__))
    cachedir = str('%s/cache' % maindir) 

    try:
        cacheuiddircont = subprocess.run(['ls', str('%s/%s' % (cachedir,uid))], capture_output=True).stdout.decode()
    except FileNotFoundError:
        print('FileNotFoundError')
        filemessages = {}
        return filemessages
    except Exception as e:
        print('Caching error:', repr(e))
        quit()

    filelist=cacheuiddircont.splitlines()
    filelist.sort()
    filemessages={}

    for i in filelist:
        try:
           msgcat=subprocess.run(['cat', str('%s/%s/%s' % (cachedir,uid,i))], capture_output=True).stdout.decode()
        except Exception as e:
            print(repr(e))
            print('error')
            return str("There was an error, perhaps the file directory doesn't exist or the ssh details were wrong?: %s" % repr(e))
        filemessages[i] = msgcat

    return filemessages

class Message:
    def __init__(self, content, is_decrypted):
        self.content = content
        self.is_decrypted = is_decrypted

def messagescompare(cachedlist,sshlist):
    masterlist = {}
    for i in sshlist:
        if i in cachedlist:
            masterlist[i] = Message(content=cachedlist[i], is_decrypted = True)
        else:
            masterlist[i] = Message(content=sshlist[i], is_decrypted = False)
    return masterlist


def messagesget(sshhost,sshuser,sshport,password,msgdir):
    conn = fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)
    
    try: 
        messagelist = conn.run('ls %s' % msgdir, hide=True).stdout
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))

    filelist=messagelist.splitlines()
    filelist.sort()
    filemessages={}

    for i in filelist:
        try:
            msgcat = conn.run('cat \'%s\'/\'%s\'' % (msgdir,i), hide=True)
        except Exception as e:
            return str("There was an error, perhaps the file directory doesn't exist or the ssh details were wrong?: %s" % repr(e))
        filemessages[i] = msgcat.stdout

    return filemessages

def messagesunlock(filemessages, usrpgp, password):
    decryptedmessages = {}
    
    for i in filemessages:
        if filemessages[i].is_decrypted == False:
            msg = pgpy.PGPMessage.from_blob(filemessages[i].content)
            try: 
                with usrpgp[0].unlock(password):
                    decryptmsg = usrpgp[0].decrypt(msg).message
            except Exception as e:
                filemessages[i] = str("Unencryptable message (Could be made by you or someone who wasn't talking to you")
                continue
            else:
                filemessages[i] = decryptmsg
                print('tryna decrypt', decryptmsg)
        elif filemessages[i].is_decrypted == True:
            filemessages[i] = filemessages[i].content    
            continue 
    
    return filemessages
    
def sendmessage(message, recpgp, sshhost,sshuser,sshport,password):    
    filename = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn=fabric.Connection(host=sshhost, user=sshuser, port=sshport, connect_kwargs={'password': password}, connect_timeout=5)

    msg = pgpy.PGPMessage.new(message)
    
    try:
        msg = recpgp[0].encrypt(msg)
    except Exception as e:
        #print(recpgp[0])
        print(repr(e))
        print('pgperror')
        quit()
        return checkedpassword(is_correct=False, other_error=repr(e))

    try:
        conn.run(str("echo \'%s\' > %s/\'%s\'" % (msg, messagesdirectory, filename)), hide=True)
    except Exception as e:
        return checkedpassword(is_correct=False, other_error=repr(e))
    else:
        return checkedpassword(is_correct=True)

