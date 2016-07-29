'''
Stop flow data import module for the importation of standard dsa files.
'''
import numpy as np

def ConvertRelativePath(Folder):
    '''
    Converts a path relative to SMD/DATA to abs path.
    '''
    from os import path
    from re import search
    import sys, os, inspect
    if '__file__' not in locals():
        __file__ = inspect.getframeinfo(inspect.currentframe())[0]

    CurPath = os.path.abspath(__file__)

    while os.path.split(CurPath)[1].lower() != 'stopflow':
        CurPath = os.path.split(CurPath)[0]
        Path = os.path.split(CurPath)[0]
        if os.path.split(CurPath)[1]=='':
            break
    else:
        Path = path.split(CurPath)[0]
    
    return os.path.join(Path, 'StopFlow\\'+Folder+'\\')

class DSA(list):
    """
    DSA
    Inherits: list
    Applied Photophysics ".dsa" file format import helper. 

    FullFileName: Original Filename with Path
    Date: File mtimestamp
    mtime: Modified Time
    """
    def __init__(self, Folder, Filename, *args, **kargs):
        super(DSA, self).__init__(*args, **kargs)
        self.FileName = Filename
        self.FolderName= Folder
        if ":" in Folder:
            if Folder[-1] != '\\':
                self.FullFileName = Folder + "\\" + Filename
            else:
                self.FullFileName = Folder + Filename
        else:
            self.FullFileName = ConvertRelativePath(Folder) + Filename
        import os
        self.mtime = os.path.getmtime(self.FullFileName)
        import datetime
        self.Date = datetime.datetime.fromtimestamp(self.mtime)

        with open(self.FullFileName, 'rb') as InputFilehandle:
            for Line in InputFilehandle:
                self.append(Line)

class CDSA(object):
    def __init__(self, RawData):
        self.OrigRawData = RawData
        self.Sequential = False
        self.SetKeywords()
        self.SetProperties()
        self.SetFlags()
        self.SetTime()
        self.LoadDSA(RawData)

    def SetTime(self):
        self.TimeDate = str(self.OrigRawData[1]).rstrip('\r\n')
        import datetime, time
        try:
            self.TimeDate = datetime.datetime.strptime(self.TimeDate,"%a %b %d %H:%M:%S %Y")
        except ValueError:
            self.TimeDate = datetime.datetime.fromtimestamp(self.OrigRawData.mtime)
    @property
    def StartTime(self):
        import numpy as np
        import datetime as dt
        LastRecordedIndex = 0
        for d in self.AllData():
            Index = np.argmax(np.array(d) == 0.0)
            if Index > LastRecordedIndex: LastRecordedIndex = Index
        if LastRecordedIndex > 0:
            LastRecordedTime = self.Time[LastRecordedIndex]
        else:
            LastRecordedTime = self.Time[-1]
        return self.TimeDate - dt.timedelta(seconds=LastRecordedTime)
    def SetKeywords(self):
        self.Keywords = {}
        self.Keywords['Remarks'] = ""
        self.Keywords['Properties'] = ""
        self.Keywords['Dimensions'] = ""
        self.Keywords['History'] = ""
    def SetProperties(self):
        self.Properties = {}
        self.Properties['Temperature'] = ""
        self.Properties['Time per point'] = ""
        self.Properties["Sample period"] = ""
        self.Properties["Samples per point"] = ""
        self.Properties["HT (Fluorescence channel)"] = ""
        self.Properties["HT (Absorbance channel)"] = ""
    def SetFlags(self):
        self.Flags = {}
        self.Flags["Fluorescence"] = ""
        self.Flags["Time"] = ""
        self.Flags["Wavelength"] = ""
        self.Flags["Repeat"] = ""
        self.Flags["Channel"] = ""
        self.Flags["Absorbance"] = ""
        self.Flags["Count"] = ""
    def UpdateKeyword(self, i, Line, RawData):
        import re
        Target = re.match("^(?P<Keyword>[\w ]*):.*",Line)
        if not(Target is None):
            if Target.group("Keyword") in self.Keywords.keys():
                self.Keywords[Target.group("Keyword")] = (i, int(RawData[i+1]))
                return True
        else:
            return False
    def UpdateProperty(self, i, Line, RawData):
        import re
        Target = re.match("^\#(?P<Property>[\w ()]*): (?P<Value>[\w\. ]*)\s*",Line)
        if not(Target is None):
            if Target.group("Property") in self.Properties.keys():
                self.Properties[Target.group("Property")] = (i, Target.group("Value"))
            return True
        else:
            return False
    def UpdateFlag(self, i, Line, RawData):
        import re
        Target = re.match("^(?P<Flag>\w*)\s(?P<Values>.*)$",Line)
        if not(Target is None):
            if Target.group("Flag") in self.Flags.keys():
                try:
                    self.Flags[Target.group("Flag")] = (i, map(str.strip,Target.group("Values").split('-')), int(RawData[i+1]))
                except:
                    self.Flags[Target.group("Flag")] = (i, map(str.strip,Target.group("Values").split('-')), "")
            return True
        else:
            return False
    def LoadDSA(self, RawData):
        for (i, Line) in enumerate(RawData):
            self.UpdateKeyword(i, Line, RawData)
            self.UpdateProperty(i, Line, RawData)
            self.UpdateFlag(i, Line, RawData)
        return True
    @property
    def RawData(self):
        return self.OrigRawData
    @property
    def Type(self):
        if (self.Spec) and (self.Kin):
            return "Spectrum-Kinetics"
        if (self.Spec):
            return "Spectrum"
        if (self.Kin):
            return "Kinetics"
    @property
    def Fired(self):
        if "trigger" in self.Flags["Time"][1]:
            return True
        return False
    @property
    def Oversampled(self):
        if "ovs" in self.Flags["Time"][1]:
            return True
        return False
    @property
    def X(self):
        if self.TimeLength > 1:
            return self.Time
        if self.WavelengthLength > 1:
            return self.Wavelength

    def AllData(self):
        # Find First line of the data traces
        DataStart = []
        for x in ["Wavelength", "Repeat", "Channel"]:
            try:
                DataStart.append(self.Flags[x][0])
            except:
                pass
        DataStart = max(DataStart)+5
        DataEnd = self.Keywords["History"][0] # Last line of the possible data traces

        Data = []
        for line in self.RawData[DataStart:DataEnd]:
            Cur = map(str.strip,line.split(","))
            if len(Cur) > 1:
                Cur = map(float,Cur)
            if len(Cur)>1:
                Data.append(Cur)
        Data = Data[:self.RepeatCount*self.ChannelCount] # Remove trailing data lines
        if self.Sequential:
            SeqData = []
            for i in range(self.ChannelCount):
                SeqData.append([])
                for n in range(self.RepeatCount):
                    SeqData[i].extend(Data[(i)*self.RepeatCount+(n)])
            Data = SeqData
        return Data
    def DataNames(self):
        Data = self.AllData()
        Names = []
        Repeats = self.RepeatCount
        for chan in self.Channel:
            if (self.Spec):
                if (Repeats > 0) and not self.Sequential:
                    for i in range(Repeats):
                        Names.append("C" + str(chan) + ": R"+str(i+1))
                else:
                    Names.append("C" + str(chan))
            if (self.Kin):
                if (Repeats > 0) and not self.Sequential:
                    for i in range(Repeats):
                        Names.append("C" + str(chan) + ": R"+str(i+1))
                else:
                    Names.append("C" + str(chan))
            #if (self.Spec) and (self.Kin):
            #    import numpy as np
            #    Names = [[Names[:len(Names)/2]],Names[len(Names)/2:]]
            #    Names = list(np.ravel([Names],order="F"))

        if len(Data) != len(Names):
            print \
"""
Error in Number of Data Traces
Expected number does not match number estimated from the data traits: 
Look for miscalculations or new type of data file being used.
"""
        return Names


    @property
    def X_Label(self): 
        if (self.Spec):
            return "Wavelength (nm)"
        if (self.Kin):
            return "Time (s)"

    @property
    def Y_Label(self): 
        return "Voltage (V)"

    @property
    def Y(self): 
        return self.RawData

    def TraceNum(self, Num=0, Channel=None):
        if Num > self.RepeatCount:
            return False
        return True
    @property
    def Single(self):
        if self.RepeatCount==1:
            return True
        return False
    @property
    def RepeatCount(self):
        try:
            return int(self.OrigRawData[self.Flags["Repeat"][0]+1])
        except:
            return 1
    @property
    def Channel(self):
        try:
            return map(str.strip,self.OrigRawData[self.Flags["Channel"][0]+2].split(","))
        except:
            return False
    @property
    def ChannelCount(self):
        try:
            return len(self.Channel)
        except:
            return False
    @property
    def Time(self):
        try:
            SingleTimeSet = map(float,map(str.strip,self.OrigRawData[self.Flags["Time"][0]+2].split(",")))
            if self.Sequential:
                SequentialTimeSet = []
                for i in range(self.RepeatCount):
                    SequentialTimeSet.extend(map(lambda x: x + SingleTimeSet[-1]*(i),SingleTimeSet))
                return SequentialTimeSet
            else:
                return SingleTimeSet
        except:
            return 0.0
    @property
    def InitialTimeStamp(self):
        import time
        return time.mktime(self.StartTime.timetuple())

    @property
    def TimeLength(self):
        try:
            return self.Flags["Time"][2]
        except:
            return False
    @property
    def Wavelength(self):
        try:
            return map(float,map(str.strip,self.OrigRawData[self.Flags["Wavelength"][0]+2].split(",")))
        except:
            return False
    @property
    def WavelengthLength(self):
        try:
            return self.Flags["Wavelength"][2]
        except:
            return False
    @property
    def Length(self):
        #return max(self.WavelengthLength, self.TimeLength)
        return len(self.AllData()[0])

    @property
    def Spec(self):
        try:
            return self.WavelengthLength>1
        except:
            return False
    @property
    def Kin(self):
        try:
            return self.Flags["Time"][2]>1
        except:
            return False
    @property
    def Remarks(self):
        List = []
        Start,Length = self.Keywords["Remarks"]
        for i in range(Length):
            List.append(self.OrigRawData[Start+i+2].rstrip('\r\n'))
        return List

if __name__ == "__main__":
#    Data = DSA('C:\Users\Koan\Dropbox\Proteasome Project\Stopped Flow Data', "4 uM in flow cell0001.dsa")
    
    #Data = DSA('Data', "Lamp Testing0015.dsa")
    #Data = DSA('Data', "Lamp Testing0008.dsa")
    #Data = DSA('Data', "Spec0052 Buffer.dsa")
    #Data = DSA('Data', "Spec0054 Sub Only.dsa")
    #CData1 = CDSA(Data)

    #print CData1.Remarks
    #print CData1.Keywords
    #print CData1.Properties
    #print CData1.Flags
    #print CData1.Type
    #print CData1.Spec
    #print CData1.Kin

    #print len(CData1.AllData())
    #print CData1.DataNames()


    #import matplotlib.pyplot as mp
    #for x in CData1.AllData():
    #    try:
    #        mp.plot(CData1.X, x)
    #    except:
    #        pass

    # Testing of Long Run Plotting
    from StorageArray import ChannelizedArray
    Files = []


    File = "Startup and Stability Test0001.dsa"
    Folder = 'C:\Users\Koan\Dropbox\Proteasome Project\Stopped Flow Data\\4 1 2014'

    File = "Lamp Testing0024.dsa"

    Folder = 'C:\Users\Koan\Dropbox\Proteasome Project\Stopped Flow Data\\3 17 2014'
    
    # Post-filter change run (Ext 325 nm)

    #File = "Lamp Testing0027.dsa"
    #Files.append([Folder, File])
    #File = "Lamp Testing0028.dsa"
    #Files.append([Folder, File])
    #File = "Lamp Testing0029.dsa"
    #Files.append([Folder, File])

    Folder = 'C:\Users\Koan\Dropbox\Proteasome Project\Stopped Flow Data\\3 17 2014'
    ## (Ext 340 nm)

    File = "Lamp Testing0021.dsa"
    Files.append([Folder, File])
    File = "Lamp Testing0022.dsa"
    Files.append([Folder, File])
    
    # (Ext 343 nm) Temperature: 36.77 C
    # Abs 510.9V
    # Flu 378.4V
    # Both Mono set to 0.25 mm

    #File = "Lamp Testing0040.dsa"
    #Files.append([Folder, File])
    #File = "Lamp Testing0041.dsa"
    #Files.append([Folder, File])
    #File = "Lamp Testing0042.dsa"
    #Files.append([Folder, File])
    #File = "Lamp Testing0043.dsa"
    #Files.append([Folder, File])

    #

    #File = "Lamp Testing0066.dsa"
    #Files.append([Folder, File])

    #File = "Lamp Testing0069.dsa"
    #Files.append([Folder, File])

    SmoothPlots = True
    NormPlots = True

    RemoveZeroes = True
    
    DataSets = []
    TotalLength = 0

    NonZero = []

    for file in Files:
        print file[1]

        DataSets.append(CDSA(DSA(file[0], file[1])))
        TotalLength += DataSets[-1].TimeLength
        DataSets[-1].Sequential = True
        
    PlotData = DataSets[0] # Set data for general values

    print "Total Length: %i" % int(TotalLength)
    TraceCount = len(PlotData.AllData())
    PlotChannels = ChannelizedArray(TotalLength, TraceCount, 'float64')
    Time = []
    import numpy as np
    for data in DataSets:
        print data.Time[-1]
        print data.StartTime
        print data.TimeDate
        TDelta = (data.StartTime - DataSets[0].StartTime).total_seconds()
        print "Time Delta from first file: %f" % float(TDelta)
        Time = np.hstack((Time ,np.array(data.Time) + TDelta))
        for i in range(TraceCount):
            Name = str(data.DataNames()[i])
            PlotChannels.ChangeColName('Channel_'+str(i+1), Name)

    for i in range(TraceCount):
        DataStart = 0
        for data in DataSets:
            DataEnd = len(data.AllData()[0]) + DataStart
            InsertData = np.array(data.AllData()[i], dtype='float64')
            Name = str(data.DataNames()[i])
            PlotChannels[Name][DataStart:DataEnd] = InsertData
            DataStart = DataEnd


    #PlotData= CDSA(DSA('Data', File))
    #print len(PlotData.Time)

    #NonZeroLength = sum(NonZero)
    #NonZero.extend(np.array(DataSets[-1].AllData()) > 0.0)
    #print "Non Zero Length: %i" % int(NonZeroLength)

    #NonZero = np.array(PlotData.AllData()[0]) > 0.0
    #Length = sum(NonZero)
    
    if RemoveZeroes:
        NonZero = np.zeros(TotalLength)

        for Name in PlotChannels.keys():
            NonZero = (PlotChannels[Name] + NonZero ) > 0.0

        Time = Time[NonZero]

        TempChannels = ChannelizedArray(sum(NonZero), TraceCount, "float64")
        for i, Name in enumerate(PlotChannels.keys()):
            TempChannels.ChangeColName(TempChannels.keys()[i], Name)
            TempChannels[Name] = PlotChannels[Name][NonZero]
        PlotChannels = TempChannels
        print "Nonzero Entries: %i"%sum(NonZero)

    SaveData = True
    # Save Raw Data
    if SaveData:
        OutputData = Time
        for Name in PlotChannels.keys():
            OutputData = np.vstack((OutputData, PlotChannels[Name]))

    from Common.Helpers import *

    # Smooth
    if SmoothPlots:
        for Name in PlotChannels.keys():
            #PlotChannels[Name] = Smooth(PlotChannels[Name],20.0,25)
            PlotChannels[Name] = Smooth(PlotChannels[Name],5.0,25)
            if SaveData:
                OutputData = np.vstack((OutputData, PlotChannels[Name]))

    # Norm
    if NormPlots:
        for Name in PlotChannels.keys():
            PlotChannels[Name] = PlotChannels[Name] - min(PlotChannels[Name])
            PlotChannels[Name] = PlotChannels[Name]/max(PlotChannels[Name])

            if SaveData:
                OutputData = np.vstack((OutputData, PlotChannels[Name]))

    FullFileName = "Data.csv"
    with open(FullFileName, 'wb') as Filehandle:
        np.savetxt(Filehandle, OutputData.T, delimiter=", ")

    PlotChannels.ChangeColName('C1', "AMC")
    PlotChannels.ChangeColName('C3', "Suc-LLVY-AMC")

    #PlotChannels.ChangeColName('C1', "450LP")
    #PlotChannels.ChangeColName('C3', "377/50")

    #from matplotlib import pylab
    #pylab.polyfit
    #i = Time > 1500.0
    #fit = pylab.polyfit(Time[i],PlotChannels["Suc-LLVY-AMC"][i],1)
    #fit_fn = pylab.poly1d(fit)
    #pylab.plot(Time,PlotChannels["Suc-LLVY-AMC"], 'yo', Time, fit_fn(Time), '--k')
    #pylab.show()

    print "\nPlotting: Point Count: %i" % len(Time)
    import Display as D
    X = np.array(PlotData.X, dtype='float64')
    D.ForkDisplay(Time,
            PlotChannels,
            Title="Proteasome Cleavage of Suc-LLVY-AMC",
            XAxis=PlotData.X_Label,
            YAxis="Fluorescence Intensity (AU)")

    '''
    File = "Lamp Testing0008.dsa"
    PlotData = CDSA(DSA('Data', File))


    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title=File,
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)
    '''


    """
    # Testing of Sequentially Combined Plotting
    from StorageArray import ChannelizedArray

    File = "Lamp Testing0015.dsa"
    PlotData = CDSA(DSA('Data', File))

    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title=File,
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)

    File = "Lamp Testing0008.dsa"
    PlotData = CDSA(DSA('Data', File))


    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title=File,
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)
    """

    """
    # Testing of Plotting
    from StorageArray import ChannelizedArray

    File = "Lamp Testing0015.dsa"
    PlotData = CDSA(DSA('Data', File))

    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title=File,
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)

    File = "Lamp Testing0008.dsa"
    PlotData = CDSA(DSA('Data', File))


    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title=File,
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)
    """

    """
    # Plot Spectra

    from StorageArray import ChannelizedArray

    PlotData = CDSA(DSA('Data', "Spec0054 Sub Only.dsa"))

    Length = PlotData.Length
    TraceCount = len(PlotData.AllData())
    Testing = ChannelizedArray(Length, TraceCount, 'float64')

    for i in range(TraceCount):
        Name = "Substrate: " + str(PlotData.DataNames()[i])
        Testing.ChangeColName('Channel_'+str(i+1), Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')
    
    PlotData = CDSA(DSA('Data', "Spec0052 Buffer.dsa"))

    TraceCount = len(PlotData.AllData())
    for i in range(TraceCount):
        Name = "Buffer: " + str(PlotData.DataNames()[i])
        Testing = Testing.AddCol(Name)
        Testing[Name] = np.array(PlotData.AllData()[i][::-1], dtype='float64')

    print "\nPlotting: Point Count: %i" % Length
    import Display as D
    X = np.array(PlotData.X[::-1], dtype='float64')
    D.ForkDisplay(X,
            Testing,
            Title="Substrate/Buffer Spectrum Comparison",
            XAxis=PlotData.X_Label,
            YAxis=PlotData.Y_Label)
    """

    #import matplotlib.pyplot as mp
    #for x in CData1.AllData():
    #    try:
    #        mp.plot(CData1.X, x)
    #    except:
    #        pass

    #mp.show()

    ## Timestamp testing
    #print CData1.TimeDate
    #print CData2.TimeDate
    #print (CData2.TimeDate - CData1.TimeDate).total_seconds() # Time diffrence in seconds between two timestamps
    
    