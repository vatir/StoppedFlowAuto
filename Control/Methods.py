from . import ConfigOptions
from pywinauto.application import Application
import time

class Window(object):
    def __init__(self):
        super(Window, self).__init__()

    def CommandComplete(self):
        #time.sleep(0.1)
        self.TopWindow.Wait('ready')
        self.TopWindow.SetFocus()

    def Connect(self, Path):
        try:
            app = Application().Connect(path=Path)
            self.TopWindow = app.top_window_()
        except:
            app = Application().Start(Path)
            self.TopWindow = app.top_window_()
        self.CommandComplete()

    def CheckBox(self, Title, State=True):
        Item = self.TopWindow[Title]
        if Item.GetCheckState() != State:
            Item.Click()
        self.CommandComplete()

    def SetValue(self, Title, Value):
        Item = self.TopWindow[Title]
        Item.SetText(str(Value))
        self.CommandComplete()

    def SetComboBox(self, Title, Value):
        Item = self.TopWindow[Title]
        Item.Select(Value)
        self.CommandComplete()
    
    def MenuSelect(self, Title):
        Item = self.TopWindow.MenuItem(Title)
        Item.Select()
        self.CommandComplete()


class ControlWindow(Window):
    def __init__(self, *args, **k_args):
        super(ControlWindow, self).__init__()
        self.Connect(ConfigOptions.ControlPath)
        self.SetToDefault()

    def SetToDefault(self):
        self.SetModeVoltage()
        self.SetEx()
        self.SetAbsorbanceChannel()
        self.SetFluorescence()
        self.SetFlu1HV()
        self.SetFlu2HV()

    def SetModeVoltage(self):
        Item = self.SetComboBox(u'SignalComboBox', u'Voltage')

    def SetEx(self, Wavelength=ConfigOptions.ExWavelength):
        self.SetValue(u'Wavelength (nm)Edit', Wavelength)

    def SetAbsorbanceChannel(self):
        self.CheckBox(u'&AbsorbanceCheckBox')

    def SetFluorescence(self):
        self.CheckBox(u'&FluorescenceCheckBox')

    def SetFlu1HV(self, Value = ConfigOptions.Flu1HV):
        self.SetValue(u'FluorescenceEdit', Value)

    def SetFlu2HV(self, Value = ConfigOptions.Flu2HV):
        self.SetValue(u'Abs. / Flu. 2Edit', Value)

    def StartViewer(self):
        Item = self.TopWindow.MenuItem(u'&View->&Pro-Data Viewer...')
        Item.Select()
        self.CommandComplete()
        return ViewerWindow()

class ViewerWindow(Window):
    def __init__(self, *args, **k_args):
        super(ViewerWindow, self).__init__()
        self.Connect(ConfigOptions.ViewerPath)
        self.SetToDefault()

    def SetToDefault(self):
        self.SetToWorkingDir()

    def ConnectToCommand(self):
        Item = self.TopWindow.MenuItem(u'&Preferences->Go On-line...')
        Item.Select()
        app = Application().Connect(title=r"Connect...")
        app.top_window_().OK.Click()

    def SetAlwaysOnTop(self):
        self.MenuSelect(u'&View->&Always On Top')

    def SetToWorkingDir(self):
        self.MenuSelect(u'&Directory->Bac&k to Working Directory')
