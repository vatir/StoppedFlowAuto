
if __name__ == '__main__':
    FolderRoot = 'E:\PyProjects\StopFlow\Data\TestingSets'
    #FolderRoot = 'C:\Users\Koan\Documents\PyProjects\StopFlow\TempData\Seq4uM'
    
    #FolderRoot = 'Z:\\5 2 2014\\' # 1 uM
    #FolderRoot = 'Z:\\5 5 2014\\' # 4 uM
    from os import walk
    Holder = []
    for Entry in walk(FolderRoot):
        Holder.append(Entry)
    
    from DataImport import *

    Files = []
    for File in Holder[0][2]:
        print File
        Files.append(CDSA(DSA(FolderRoot, File)))

    from matplotlib import pylab
    import numpy

    Folder = FolderRoot
    Chan1Avg = []
    Chan1HV = []
    Chan1SD = []
    Chan2Avg = []
    Chan2HV = []
    Chan2SD = []
    Wavelength = []
    StartTime = []
    IS1 = []
    IS2 = []
    #print "C1HV, C1Avg, C1SD, C2HV, C2Avg, C2SD"
    InitialTime = Files[0].InitialTimeStamp
    
    for File in Files: # # 1 uM
    #for File in Files[6:-2]: # 4 uM
        CurrentTime = File.InitialTimeStamp
        StartTime.append(CurrentTime - InitialTime)
        C1HV = float(File.Properties['HT (Absorbance channel)'][1])
        C2HV = float(File.Properties['HT (Fluorescence channel)'][1])
        C1.apend(list(File.AllData()[0]))
        C2.apend(list(File.AllData()[1]))

        V1 = numpy.array(File.AllData()[0])
        V2 = numpy.array(File.AllData()[1])
        T = File.Time
        UB = 9.5
        if max(V1) > UB:
            Last1 = numpy.argmax(V1 > 9.5)-1
        else:
            Last1 = numpy.argmin(V1 != 0.0)-1

        if max(V2) > UB:
            Last2 = numpy.argmax(V2 > 9.5)-1
        else:
            Last2 = numpy.argmin(V2 != 0.0)-1

        EI = 1000
        if Last1 > EI : Last1 = EI
        EI = 400
        if Last2 > EI : Last2 = EI
        #print max(V1)
        #print max(V2)
        #print numpy.argmin(V2 != 0.0)
        #print numpy.argmax(V2 > 9.5)
        #print Last1
        #print Last2

        print "%f : %f"%(T[Last1]-T[0],T[Last2]-T[0])
        print V1[0]
        print V2[0]
        IS1.append(((V1[Last1]-V1[0])/(T[Last1]))/(C2HV**8.150))
        IS2.append(((V2[Last2]-V2[0])/(T[Last2]))/(C1HV**9.096))
        #IS1.append(((V1[Last1]-V1[0])/(T[Last1])))
        #IS2.append(((V2[Last2]-V2[0])/(T[Last2])))

        #IS1.append(((V1[Last1]-V1[0])/(T[Last1]))/(C2HV))
        #IS2.append(((V2[Last2]-V2[0])/(T[Last2]))/(C1HV))
        #IS1.append(((V1[Last1]-V1[0])/(T[Last1])))
        #IS2.append(((V2[Last2]-V2[0])/(T[Last2])))

        Chan1HV.append(File.Properties['HT (Absorbance channel)'][1])
        Chan2HV.append(File.Properties['HT (Fluorescence channel)'][1])
        Wavelength.append(File.Wavelength[0])
        #print File.Properties['HT (Absorbance channel)'][1]
        #print File.Properties['HT (Fluorescence channel)'][1]
        Chan1Avg.append(numpy.mean(File.AllData()[0]))
        Chan2Avg.append(numpy.mean(File.AllData()[1]))

        Chan1SD.append(numpy.std(File.AllData()[0]))
        Chan2SD.append(numpy.std(File.AllData()[1]))
        #print numpy.mean(File.AllData()[0])
        #print numpy.mean(File.AllData()[1])
        #print numpy.mean(File.AllData()[0])
        #print numpy.mean(File.AllData()[1])
        print "%f, %f, %f, %f, %f, %f, %f" % (Wavelength[-1], float(C1HV), float(C1Avg), float(C1SD), float(C2HV), float(C2Avg), float(C2SD))
    #pylab.plot(Chan1HT, Chan1SD)
    #pylab.plot(Chan2HT, Chan2SD)
    
    IS1 = numpy.array(IS1)
    IS2 = numpy.array(IS2)
    IS1 = (IS1-(IS1[0]))
    IS1 = IS1/abs(IS1[-1])
    IS2 = (IS2-(IS2[0]))
    IS2 = IS2/abs(IS2[-1])

    pylab.plot(StartTime, IS1, marker="+")
    pylab.plot(StartTime, IS2, marker="o")
    pylab.show()

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