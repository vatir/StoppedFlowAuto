if __name__ == '__main__':
    Dir = 'E:\PyProjects\StopFlow\TempData'
    #FolderRoot = '{}\\TempData\Seq0 5uM'.format(Dir)
    #Output = open("0 5uM.csv", "w")
    FolderRoot = '{}\Seq1uMB2'.format(Dir)
    Output = open("1uMB2.csv", "w")
    #FolderRoot = '{}\Seq1uM'.format(Dir)
    #Output = open("1uM.csv", "w")
    #FolderRoot = '{}\Seq4uM'.format(Dir)
    #Output = open("4uM.csv", "w")

    SubInitialConc = 50e-6

    from os import walk
    Holder = []
    for Entry in walk(FolderRoot):
        Holder.append(Entry)
    
    from DataImport import *

    Files = []
    for File in Holder[0][2]:
        #print File
        Files.append(CDSA(DSA(FolderRoot, File)))

    from matplotlib import pylab
    import numpy

    Folder = FolderRoot

    Output.write('"","Time","V","s0","Type","Group","HV","StartTime", \"Set\"'+"\n")

    InitialTime = Files[0].InitialTimeStamp
    H = {}
    CV = {}
    GroupNumber = 0
    SetNumber = 0
    for File in Files:
        Length = File.TimeLength
        CurrentTime = File.InitialTimeStamp
        DataCollectionTime = (CurrentTime - InitialTime)*np.ones(Length)
        H["p"] = float(File.Properties['HT (Absorbance channel)'][1])*np.ones(Length)
        H["s"] = float(File.Properties['HT (Fluorescence channel)'][1])*np.ones(Length)

        CV["s"] = numpy.array(File.AllData()[0])
        CV["p"] = numpy.array(File.AllData()[1])
        SetNumber += 1
        for Chan in ["s", "p"]:
            GroupNumber += 1
            try:
                Time = np.hstack([Time, File.Time])
                V = np.hstack([V, CV[Chan]])
                s0 = np.hstack([s0, SubInitialConc*np.ones(Length)])
                Type = np.hstack([Type, [Chan,]*Length])
                Group = np.hstack([Group, GroupNumber*np.ones(Length)])
                HV = np.hstack([HV, H[Chan]])
                StartTime = np.hstack([StartTime, DataCollectionTime])
                Set = np.hstack([Set, SetNumber*np.ones(Length)])

            except:
                Time = File.Time
                V = CV[Chan]
                s0 = SubInitialConc*np.ones(Length)
                Type = [Chan,]*Length
                Group = GroupNumber*np.ones(Length)
                HV = H[Chan]
                StartTime = DataCollectionTime
                Set = SetNumber*np.ones(Length)

        #print "%f, %f, %f, %f, %f, %f, %f" % (Wavelength[-1], float(C1HV), float(C1Avg), float(C1SD), float(C2HV), float(C2Avg), float(C2SD))

    
    
    
    for x in range(len(Time)):
        Output.write("%i, %f, %f, \"%s\", \"%s\", %i, %3.3f, %i, %i" % (x+1, float(Time[x]), float(V[x]), str(s0[x]), Type[x], int(Group[x]), float(HV[x]), int(StartTime[x]), int(Set[x]))+"\n")

    Output.close()
    
        
    #from StorageArray import ChannelizedArray

    """
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
    """