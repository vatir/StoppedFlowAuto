
if __name__ == '__main__':
    FolderRoot = 'C:\\Users\\Koan\\Documents\\PyProjects\\StopFlow\\TempData\\'
    from os import walk
    Holder = []
    for Entry in walk(FolderRoot):
        Holder.append(Entry)
    
    from DataImport import *
    Files = {}
    for Dir in Holder[1:]:
        Folder = Dir[0]
        Files[Folder] = []
        for File in Dir[2]:
            Files[Folder].append(CDSA(DSA(Folder, File)))

    from matplotlib import pylab
    import numpy

    for Folder in Files.keys():
        print Folder
        Chan1Avg = []
        Chan1HV = []
        Chan1SD = []
        Chan2Avg = []
        Chan2HV = []
        Chan2SD = []
        Wavelength = []
        print "C1HV, C1Avg, C1SD, C2HV, C2Avg, C2SD"
        for File in Files[Folder]:
            C1HV = File.Properties['HT (Absorbance channel)'][1]
            C2HV = File.Properties['HT (Fluorescence channel)'][1]
            C1Avg = numpy.mean(File.AllData()[0])
            C2Avg = numpy.mean(File.AllData()[1])
            C1SD = numpy.std(File.AllData()[0])
            C2SD = numpy.std(File.AllData()[1])

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
        
        pylab.plot(Chan1HV, Chan1Avg, marker="+")
        pylab.plot(Chan2HV, Chan2Avg, marker="o")
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