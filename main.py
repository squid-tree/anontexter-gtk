import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from functions import * 
from settings.settings import *

def win_destroy(widget):
    widget.destroy()

class SettingsWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title='Anontexter Gtk - Settings')
        self.connect("destroy", win_destroy)

        self.column = Gtk.Box(spacing=5, orientation=Gtk.Orientation.VERTICAL,homogeneous=False)
        self.column.set_halign(Gtk.Align.START)
        
        self.ip = Gtk.Entry(placeholder_text="Ip Address of Server")

        self.port = Gtk.Entry(placeholder_text="Server Port")

        self.username = Gtk.Entry(placeholder_text="Server User")
       
        
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

        self.column.pack_start(self.ip, False, False, 0)
        self.column.pack_start(self.port, False, False, 0)
        self.column.pack_start(self.username, False, False, 0)
        self.column.pack_start(self.rcpglbl, False, False, 0)
        self.column.pack_start(self.rcpgbox, False, False, 0)
        self.column.pack_start(self.uspglbl, False, False, 0)
        self.column.pack_start(self.uspgbox, False, False, 0)

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
