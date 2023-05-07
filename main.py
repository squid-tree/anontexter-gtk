import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import functions
from settings.settings import sshhost as o1sshhost
from settings.settings import sshuser as o1sshuser
from settings.settings import sshport as o1sshport
from settings.settings import messagesdirectory as o1messagesdirectory
from settings.settings import recpgpdir as o1recpgpdir
from settings.settings import usrpgpdir as o1usrpgpdir
from settings.settings import userpgppassword as o1userpgppassword 
from settings.settings import sshpassword as o1sshpassword 
import os
import re

settingsdir = str('%s/settings/settings.py' % os.path.dirname(os.path.realpath(__file__)))

def message_list_refresh():
    try:
        masterchecker()[0] == True
        messagelist = functions.messagesget(o1sshhost, o1sshuser, o1sshport,o1sshpassword)
    except Exception as e:
        print(repr(e))
        quit()
    else:
        try:
            messagelist = functions.messagesunlock(messagelist, functions.getpgp(o1usrpgpdir), o1userpgppassword)
        except Exception as e:
            print(repr(e))
            quit()
        else: 
            return messagelist


def masterchecker():
    ip = str(o1sshhost) 
    port = str(o1sshport) 
    user = str(o1sshuser) 
    rcdir = str(o1recpgpdir) 
    usdir = str(o1usrpgpdir) 
    uspwd = str(o1userpgppassword)
    sshpwdtext = str(o1sshpassword)
    sshdirector = str(o1messagesdirectory) 

    counter = 0
    errors = str()

    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        errors = 'Invalid ip address (wrong format or empty)'
        counter += 1 
    elif len(port) <= 0:
        errors = 'Invalid port (wrong format or empty)'
        counter += 1
    elif len(user) <= 0:
        errors = 'Invalid user (wrong format or empty)'
        counter += 1 
    elif os.path.isfile(rcdir) != True:
        errors = 'Invalid file path'
        counter += 1 
    elif os.path.isfile(usdir) != True:
        errors = 'Invalid file path'
        counter += 1 
    elif len(uspwd) <= 0:
        errors = 'Invalid secretkey password (wrong format or empty)'
        counter += 1 
    elif len(sshdirector) <= 0:
        errors = 'Invalid ssh directory format (wrong format or empty)'
        counter += 1 
    elif functions.pgppasswordverif(functions.getpgp(usdir),uspwd).is_correct == False:
        errors = 'Incorrect PGP password'
        counter += 1 
    elif functions.sshpasswordverif(ip,user,port,sshpwdtext).is_correct == False:
        errors = 'Incorrect SSH password'
        counter += 1 
    
    if counter == 0:
        return (True, errors)
    else:
        return (False, errors)

def win_destroy(widget):
    widget.destroy()

class StatusWindow(Gtk.Window):
    def __init__(self, content):
        super().__init__(title='AnonTexter Gtk - Status Window')
        self.connect("destroy", win_destroy)

        frame = Gtk.Frame(label=content)
        
        self.add(frame)

class SettingsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title='Anontexter Gtk - Settings')
        self.connect("destroy", win_destroy)
        
        

        # Defines column Box
        self.column = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL,homogeneous=False)
        self.column.set_halign(Gtk.Align.START)
        
        # Defines SSH fields
        self.ip = Gtk.Entry(placeholder_text="Ip Address of Server")

        self.port = Gtk.Entry(placeholder_text="Server Port")

        self.username = Gtk.Entry(placeholder_text="Server User")
        self.sshdir = Gtk.Entry(placeholder_text="Messages Directory in SSH server")

        self.sshpwd = Gtk.Entry(placeholder_text="SSH Password")
        self.sshpwd.set_visibility(False)

               
        # Defines PGP Key fields and file dialogs
        self.rcpglbl = Gtk.Label("Encrypted PGP key file of recipient")
        
        self.rcpgbox = Gtk.Box(spacing=1)
        self.rcpgdir = Gtk.Entry(placeholder_text="PGP key directory")
        self.rcpgbut = Gtk.Button(label='Choose File')
        self.rcpgbut.connect("clicked", lambda widget: self.filechooser(self.rcpgdir))
        self.rcpgbox.pack_start(self.rcpgbut, False, False, 0)
        self.rcpgbox.pack_start(self.rcpgdir, False, False, 0)
       
        self.uspglbl = Gtk.Label("Encrypted PGP key file of user")
        
        self.uspgbox = Gtk.Box(spacing=1)
        self.uspgdir = Gtk.Entry(placeholder_text="PGP key directory")
        self.uspgbut = Gtk.Button(label='Choose File')
        self.uspgbut.connect("clicked", lambda widget: self.filechooser(self.uspgdir)) 
        self.uspgbox.pack_start(self.uspgbut, False, False, 0)
        self.uspgbox.pack_start(self.uspgdir, False, False, 0)

        # Defines uspg password field
        self.uspgpwd = Gtk.Entry(placeholder_text="User Key Password")
        self.uspgpwd.set_visibility(False)

        # Defines Buttons to modify settings
        self.endbox = Gtk.Box(spacing = 25)
        self.cancelbut = Gtk.Button(label="Cancel")
        self.cancelbut.connect("clicked", lambda widget: self.quitter())
        self.savebut = Gtk.Button(label="Save")
        self.savebut.connect("clicked", lambda widget: self.saver())
        self.okbut = Gtk.Button(label="Ok")
        self.okbut.connect("clicked", lambda widget: self.agreer())
        self.testbut = Gtk.Button(label="Test")
        self.testbut.connect("clicked", lambda widget: self.tester())
        self.endbox.pack_start(self.cancelbut, False, False, 0) 
        self.endbox.pack_start(self.testbut, False, False, 0)
        self.endbox.pack_start(self.savebut, False, False, 0)
        self.endbox.pack_start(self.okbut, False, False, 0)

        # Appends current settings to fields
        self.labels = SettingsWindow.getlabels()
        self.ip.set_text(self.labels["sshhost"])
        self.port.set_text(self.labels["sshport"]) 
        self.username.set_text(self.labels["sshuser"])
        self.sshdir.set_text(self.labels['messagesdirectory'])
        self.rcpgdir.set_text(self.labels['recpgpdir'])
        self.uspgdir.set_text(self.labels['usrpgpdir'])
        self.uspgpwd.set_text(self.labels['userpgppassword'])
        self.sshpwd.set_text(self.labels['sshpassword'])

        # Packs all elements into column
        self.column.pack_start(self.ip, False, False, 0)
        self.column.pack_start(self.port, False, False, 0)
        self.column.pack_start(self.username, False, False, 0)
        self.column.pack_start(self.sshdir, False, False, 0)
        self.column.pack_start(self.sshpwd, False, False, 0)
        self.column.pack_start(self.rcpglbl, False, False, 0)
        self.column.pack_start(self.rcpgbox, False, False, 0)
        self.column.pack_start(self.uspglbl, False, False, 0)
        self.column.pack_start(self.uspgbox, False, False, 0)
        self.column.pack_start(self.uspgpwd, False, False, 0)
        self.column.pack_start(self.endbox, False, False, 0)

        # Packs column into vbox and adds it to the window
        self.vbox = Gtk.VBox(spacing=0,homogeneous=False)
        self.vbox.pack_start(self.column,False,False,0)
        self.add(self.vbox)

    def getlabels():
        labels = {}
        labels['sshhost'] = o1sshhost
        labels['sshuser'] = o1sshuser
        labels['sshport'] = o1sshport
        labels['messagesdirectory'] = o1messagesdirectory
        labels['recpgpdir'] = o1recpgpdir
        labels['usrpgpdir'] = o1usrpgpdir
        labels['userpgppassword'] = o1userpgppassword
        labels['sshpassword'] = o1sshpassword
        return labels

    
    def filechooser(self,label):
        win = Gtk.Window(title=str('File picker'))

        dialog = Gtk.FileChooserDialog("Please choose a file", win,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        #win.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path=dialog.get_filename()
            label.set_text(file_path)
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()
        dialog.destroy()

    def saver(self):
        ip = str(self.ip.get_text())
        port = str(self.port.get_text())
        user = str(self.username.get_text())
        rcdir = str(self.rcpgdir.get_text())
        usdir = str(self.uspgdir.get_text())
        uspwd = str(self.uspgpwd.get_text())
        sshpwdtext = str(self.sshpwd.get_text())
        sshdirector = str(self.sshdir.get_text()) 

        testresults = masterchecker()

        contents = str('sshhost = \'%s\'\nsshuser = \'%s\'\nsshport = \'%s\'\nmessagesdirectory = \'%s\'\nrecpgpdir = \'%s\'\nusrpgpdir = \'%s\'\nuserpgppassword = \'%s\'\nsshpassword = \'%s\'\n' % (ip, user, port, sshdirector, rcdir, usdir, uspwd,sshpwdtext))

        if testresults[0] == True:
            with open(settingsdir, 'w') as file:
                file.write(contents)
            statbox = StatusWindow(content = 'Settings successfully tested and saved')
            statbox.show_all()
            o1sshhost = ip
            o1sshport = port
            o1sshuser = user
            o1rcrpgpdir = rcdir
            o1usrpgpdir = usdir
            o1usrpgppassword = uspwd
            o1sshpassword = sshpwdtext
            o1messagesdirectory = sshdirector
        else:
            statbox = StatusWindow(content = str('Aborted: incorrect settings detected (%s)' % testresults[1]))
            statbox.show_all()

    def tester(self):
        testresults = masterchecker()
        
        if testresults[0] == True:
            statbox = self.StatusWindow(content = 'Settings successfully tested and seem to be correct (keep in mind, some might still be wrong)')
            statbox.show_all()
        else:
            statbox = self.StatusWindow(content = str('Aborted: incorrect settings detected (%s)' % testresults[1]))
            statbox.show_all()

    def quitter(self):
        o = self.CancelWindow(superclass=self)
        o.show_all()

    def agreer(self):
        ip = self.ip.get_text() 
        port = self.port.get_text() 
        user = self.username.get_text()
        rcdir = self.rcpgdir.get_text()
        usdir = self.uspgdir.get_text()
        uspwd = self.uspgpwd.get_text()
        sshpwdtext = self.sshpwd.get_text()
        sshdirector = self.sshdir.get_text() 
        
        contents = str('sshhost = \'%s\'\nsshuser = \'%s\'\nsshport = \'%s\'\nmessagesdirectory = \'%s\'\nrecpgpdir = \'%s\'\nusrpgpdir = \'%s\'\nuserpgppassword = \'%s\'\nsshpassword = \'%s\'\n' % (ip, user, port, sshdirector, rcdir, usdir, uspwd,sshpwdtext))

        with open(settingsdir, "r") as file:
            filecontents = file.read()

        if filecontents == contents:
            o = StatusWindow(content = 'Succesfully exited')
            o.show_all()
            win_destroy(super())
        else:
            o = StatusWindow(content = 'Changes have not been saved, please save them or cancel')
            o.show_all()
             
    class CancelWindow(Gtk.Window):
            def __init__(self, superclass):
                super().__init__(title='AnonTexter Gtk - Status Window')

                self.connect("destroy", lambda widget: self.destroy)

                
                self.box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL,homogeneous=False)
                
                self.box.set_halign(Gtk.Align.START)

                self.row = Gtk.Box(spacing=15)
                
                self.text = Gtk.Label('Sure you want to cancel? Any unsaved changes will be reset')
                
                self.exitbutton = Gtk.Button(label="Reset my Settings")
                self.exitbutton.connect("clicked", lambda widget:super_destroy(self,superclass))

                def super_destroy(self,superclass):
                    superclass.destroy()
                    self.destroy()

                self.cancel = Gtk.Button(label = "Return to Menu")
                self.cancel.connect("clicked", lambda widget: win_destroy(self))
                
                self.row.pack_start(self.exitbutton, True, True, 0)
                self.row.pack_start(self.cancel, True, True, 0)

                self.box.pack_start(self.text, True, True, 0)
                self.box.pack_start(self.row, True, True, 0)

                self.add(self.box)

class MainWindow(Gtk.Window):
    def __init__(self):
        # Initial settings
        super().__init__(title='AnonTexter Gtk - Home')

        self.border_width=(5,5)
        
        self.vbox = Gtk.VBox(spacing=0)

        # Creation of top box
        self.topbar = Gtk.Box()
        self.topbar.set_valign(Gtk.Align.START)
        self.topbar.set_size_request(-1,5)
        self.topbar.set_hexpand(True)
        
        # Settings Button
        self.settingsbutton = Gtk.Button(label='Settings')
        self.settingsbutton.set_size_request(30,-1)
        self.settingsbutton.set_halign(Gtk.Align.START)
        self.settingsbutton.connect("clicked", self.opensettings)
        self.topbar.pack_start(self.settingsbutton, False, False, 0)

        # Refresh Button
        self.settingsbutton = Gtk.Button(label= u"\U0001F5D8")
        self.settingsbutton.set_size_request(30,-1)
        self.settingsbutton.set_halign(Gtk.Align.END)
        self.settingsbutton.connect("clicked", lambda widget: self.messagesrefresh())
        self.topbar.pack_start(self.settingsbutton, False, False, 0)

        # Chatwindow

        self.chatbar = Gtk.Box(spacing = 5)

        self.pointer = Gtk.Label('> ')

        self.entry = Gtk.Entry(placeholder_text='Enter a Message')

        self.entry.connect("activate", self.message_send)
        self.entry.set_alignment(xalign=0)
        self.entry.set_hexpand(True)

        self.chatbar.pack_start(self.pointer, False, False, 0)
        self.chatbar.pack_start(self.entry, False, True, 0)
        
        self.chatbar.set_hexpand(True)

        self.messagebox = Gtk.Box(spacing=5)
        self.messagebox.set_orientation(Gtk.Orientation.VERTICAL)
        self.messagebox.set_hexpand(True)
        self.messagebox.set_vexpand(True)

        self.chatwindow = Gtk.ScrolledWindow()
        self.chatwindow.set_hexpand(True)
        self.chatwindow.set_vexpand(True)
        self.chatwindow.set_policy(Gtk.PolicyType.ALWAYS,Gtk.PolicyType.AUTOMATIC)
        self.chatwindow.set_min_content_height(self.get_size()[1])
        self.chatwindow.add(self.messagebox)
        
        
        self.add(self.vbox)

        # Seperator
        self.seperator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.seperator.set_size_request(-1, 8)
       
        # Loading of elements into vbox
        self.vbox.pack_start(self.topbar, False, False, 0)
        self.vbox.pack_start(self.seperator, False, False, 0)
        self.vbox.pack_start(self.chatwindow, True, True, 0)
        self.vbox.pack_start(self.chatbar, False, True, 0)

        # Adding the vbox 
        self.add(self.vbox)

        self.messagesrefresh()

    
    def opensettings(self,widget):
        o = SettingsWindow()
        o.show_all()

    def message_send(self,widget):
        if masterchecker()[0] == True:
            o = self.entry.get_text()
            functions.sendmessage(o, functions.getpgp(str(o1recpgpdir)), o1sshhost, o1sshuser, o1sshport, o1sshpassword)
            self.entry.set_text('')
            adjustment = self.chatwindow.get_vadjustment()
            adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
            self.messagesrefresh()
        else:
            o = StatusWindow(content='Failed to send message, the settings are incorrect')
            o.show_all()

        
    def messagesrefresh(self):
        if masterchecker()[0] == True:
            messagelist = message_list_refresh()
            
            # Clear Messages
            for i in self.messagebox.get_children():
                self.messagebox.remove(i)
            
            # Add messages
            for i in reversed(messagelist):
                self.messagebox.pack_end(Gtk.Label(label=str('%s    %s' % (i, messagelist[i])),xalign=0), False, False, 0)

            # Display messages
            self.show_all()
        else: 
            o = StatusWindow(content='Failed to refresh messages, the settings are incorrect')
            o.show_all()


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
