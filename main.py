import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from functions import * 
from settings.settings import *

import os

settingsdir = str('%s/settings/settings.py' % os.path.realpath(__file__))


def win_destroy(widget):
    widget.destroy()

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
        ip = Gtk.get_text(self.ip) 
        port = Gtk.get_text(self.port)
        user = Gtk.get_text(self.username) 
        rcdir = Gtk.get_text(self.rcpgdir)
        usdir = Gtk.get_text(self.uspgdir) 
        uspwd = Gtk.get_text(self.usrpwd)
        sshpwdtext = Gtk.get_text(self.sshpwd)
        sshdirector = Gtk.get_text(self.sshdir)

        testresults = self.checker()

        contents = str('sshhost = %s\n','sshuser = %s\n','sshport = %s\n','messagesdirectory = %s\n','recpgpdir = %s\n','usrpgpdir = %s\n','userpgppassword = %s\n' % (ip, user, port, sshdirector, rcdir, usdir, uspwd))

        if testresults[0] == True:
            with open(settingsdir, 'w') as file:
                file.write(contents)
            statbox = StatusWindow(content = 'Settings successfully tested and saved')
            statbox.show_all()
        else:
            statbox = StatusWindow(content = str('Aborted: incorrect settings detected (%s)' % checker[1]))
            statbox.show_all()

    def tester(self):
        testresults = self.checker()
        
        if testresults[0] == True:
            statbox = StatusWindow(content = 'Settings successfully tested and seem to be correct (keep in mind, some might still be wrong)')
            statbox.show_all()
        else:
            statbox = StatusWindow(content = str('Aborted: incorrect settings detected (%s)' % checker[1]))
            statbox.show_all()

    def quitter(self):
        o = self.CancelWindow(superclass=self)
        o.show_all()

    def agreer(self):
        ip = self.ip.get_text() 
        port = self.port.get_text() 
        user = self.username.gettext()
        rcdir = self.rcpgdir.gettext()
        usdir = self.uspgdir.gettext()
        uspwd =self.usrpwd.gettext()
        sshpwdtext = self.sshpwd.get_text()
        sshdirector = self.sshdir.get_text()
        
        contents = str('sshhost = %s\n','sshuser = %s\n','sshport = %s\n','messagesdirectory = %s\n','recpgpdir = %s\n','usrpgpdir = %s\n','userpgppassword = %s\n' % (ip, user, port, sshdirector, rcdir, usdir, uspwd))

        with open(settingsdir, "r") as file:
            filecontents = file.read()

        if filecontents == contents:
            o = StatusWindow(contents = 'Succesfully exited')
            win_destroy(super())
        else:
            o = StatusWindow(contents = 'Changes have not been saved, please save them or cancel')
             
    class CancelWindow(Gtk.Window):
            def __init__(self, superclass):
                super().__init__(title='AnonTexter Gtk - Status Window')
                self.connect("destroy", lambda widget: self.destroy)

                
                self.box = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL,homogeneous=False)
                
                self.box.set_halign(Gtk.Align.START)

                self.row = Gtk.Box(spacing=15)
                
                self.text = Gtk.Label('Sure you want to cancel? Any changes will be reset')
                
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

    class StatusWindow(Gtk.Window):
        def __init__(self, content):
            super().__init__(title='AnonTexter Gtk - Status Window')
            self.connect("destroy", win_destroy)

            frame = Gtk.Frame(label=content)
            
            self.add(frame)

    def checker(self):
        ip = self.ip.get_text() 
        port = self.port.get_text() 
        user = self.username.gettext()
        rcdir = self.rcpgdir.gettext()
        usdir = self.uspgdir.gettext()
        uspwd =self.usrpwd.gettext()
        sshpwdtext = self.sshpwd.get_text()
        sshdirector = self.sshdir.get_text()

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
        elif functions.pgppasswordverif(functions.getpgp(usdir, uspwd)).is_correct == False:
            errors = 'Incorrect PGP password'
            counter += 1 
        elif functions.sshpasswordverif(host,user,port,sshpwdtext):
            errors = 'Incorrect SSH password'
            counter += 1 
        
        if counter == 0:
            return (True, errors)
        else:
            return (False, errors)
        
class MainWindow(Gtk.Window):
    def __init__(self):
        # Initial settings
        super().__init__(title='AnonTexter Gtk - Home')

        self.border_width=(5,5)

        # Creation of top box
        self.topbar = Gtk.Box()
        self.topbar.set_valign(Gtk.Align.START)
        self.topbar.set_size_request(-1,5)
        
        # Settings Button
        self.settingsbutton = Gtk.Button(label='Settings')
        self.settingsbutton.set_size_request(30,-1)
        self.settingsbutton.set_halign(Gtk.Align.START)
        self.settingsbutton.connect("clicked", self.opensettings)
        self.topbar.pack_start(self.settingsbutton, False, False, 0)
        
        # Seperator
        self.seperator = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        self.seperator.set_size_request(-1, 8)
       
        # Loading of elements into vbox
        self.vbox = Gtk.VBox(spacing=0)
        self.vbox.pack_start(self.topbar, False, False, 0)
        self.vbox.pack_start(self.seperator, False, False, 0)

        # Adding the vbox 
        self.add(self.vbox)
    
    def opensettings(self,widget):
        o = SettingsWindow()
        o.show_all()

win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
