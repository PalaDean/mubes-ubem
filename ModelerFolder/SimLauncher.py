# @Author  : Xavier Faure
# @Email   : xavierf@kth.se

import os
import sys
#add the required path
path2addgeom = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),'geomeppy')
sys.path.append(path2addgeom)
#add needed packages
import pickle5 as pickle
import copy
import shutil
#add scripts from the project as well
sys.path.append("..")
import CoreFiles.GeneralFunctions as GrlFct
import CoreFiles.LaunchSim as LaunchSim
from BuildObject.DB_Building import BuildingList
import BuildObject.DB_Data as DB_Data
import multiprocessing as mp
from subprocess import check_call

def SetParamSample(SimDir,nbruns,VarName2Change,Bounds):

    #the parameter are constructed. the oupute gives a matrix ofn parameter to change with nbruns values to simulate
    Paramfile = os.path.join(SimDir,'ParamSample.pickle')
    if SepThreads:
        Paramfile = os.path.join(os.path.dirname(SimDir), 'ParamSample.pickle')
        if os.path.isfile(Paramfile):
            with open(Paramfile, 'rb') as handle:
                ParamSample = pickle.load(handle)
        else:
            ParamSample = GrlFct.getParamSample(VarName2Change,Bounds,nbruns)
            if nbruns>1:
                with open(Paramfile, 'wb') as handle:
                    pickle.dump(ParamSample, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        Paramfile = os.path.join(SimDir,'ParamSample.pickle')
        if os.path.isfile(Paramfile):
            with open(Paramfile, 'rb') as handle:
                ParamSample = pickle.load(handle)
        else:
            ParamSample = GrlFct.getParamSample(VarName2Change, Bounds, nbruns)
            if nbruns > 1:
                with open(Paramfile, 'wb') as handle:
                    pickle.dump(ParamSample, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return ParamSample

def LaunchOAT(MainInputs,ParamVal,currentRun):
    print('Launched')
    # lets prepare the commande lines
    virtualenvline = os.path.normcase('C:\\Users\\xav77\Envs\\UBEMGitTest\Scripts\\python.exe')
    # virtualenvline = virtualenvline+'\n'

    scriptpath = os.path.normcase('C:\\Users\\xav77\Documents\FAURE\prgm_python\\UrbanT\Eplus4Mubes\MUBES_UBEM\CoreFiles')
    cmdline = [virtualenvline, os.path.join(scriptpath, 'CaseBuilder_OAT.py')]
    for key in MainInputs.keys():
        cmdline.append('-'+key)
        if type(MainInputs[key]) == str:
            cmdline.append(MainInputs[key])
        else:
            cmdline.append(str(MainInputs[key]))
    cmdline.append('-ParamVal')
    cmdline.append(str(ParamVal))
    cmdline.append('-currentRun')
    cmdline.append(str(currentRun))
    # cmdline = [virtualenvline, os.path.join(scriptpath, 'CaseBuilder_OAT.py'), '-FirstRun', '-SimDir', SimDir,
    #            '-PathInputFiles', PathInputFile, '-nbcase', str(nbBuild),'-VarName2Change',VarName2Change,'-ParamVal',ParamVal]
    check_call(cmdline)#,stdout=open(os.devnull, "w"))


if __name__ == '__main__' :

######################################################################################################################
########        MAIN INPUT PART     ##################################################################################
######################################################################################################################
#The Modeler have to fill in the following parameter to define his choices

# CaseName = 'String'                   #name of the current study (the ouput folder will be renamed using this entry)
# BuildNum = [1,2,3,4]                  #list of numbers : number of the buildings to be simulated (order respecting the
#                                       geojsonfile), if empty, all building in the geojson file will be considered
# VarName2Change = ['String','String']  #list of strings: Variable names (same as Class Building attribute, if different
#                                       see LaunchProcess 'for' loop for examples)
# Bounds = [[x1,y1],[x2,y2]]            #list of list of 2 values  :bounds in which the above variable will be allowed to change
# NbRuns = 1000                         #number of run to launch for each building (all VarName2Change will have automotaic
#                                       allocated value (see sampling in LaunchProcess)
# CPUusage = 0.7                        #factor of possible use of total CPU for multiprocessing. If only one core is available,
#                                       this value should be 1
# SepThreads = False / True             #True = multiprocessing will be run for each building and outputs will have specific
#                                       folders (CaseName string + number of the building. False = all input files for all
#                                       building will be generated first, all results will be saved in one single folder
#                                       This options is to be set to True only for several simulation over one building
# CreateFMU = False / True             #True = FMU are created for each building selected to be computed in BuildNum
#                                       #no simulation will be run but the folder CaseName will be available for the FMUSimPlayground.py
# CorePerim = False / True             #True = create automatic core and perimeter zonning of each building. This options increases in a quite
#                                       large amount both building process and simulation process.
#                                       It can used with either one zone per floor or one zone per heated or none heated zone
#                                       building will be generated first, all results will be saved in one single folder
# FloorZoning = False / True            True = thermal zoning will be realized for each floor of the building, if false, there will be 1 zone
#                                       for the heated volume and, if present, one zone for the basement (non heated volume
## PlotBuilding = False / True          #True = after each building (and before the zoning details (setZoneLevel) the building will
#                                       be plotted for viisuaal check of geometrie and thermal zoning. It include the shadings
# PathInputFile = 'String'              #Name of the PathFile containing the paths to the data and to energyplus application (see ReadMe)
# OutputsFile = 'String'               #Name of the Outfile with the selected outputs wanted and the associated frequency (see file's template)
# ZoneOfInterest = 'String'             #Text file with Building's ID that are to be considered withoin the BuildNum list, if '' than all building in BuildNum will be considered

    with open('Ham2Simu4Calib_Last2complete.txt') as f: #'Ham2Simu4Calib_Last.txt') as f:
        FileLines = f.readlines()
    Bld2Sim = []
    for line in FileLines:
        Bld2Sim.append(int(line))

    CaseName = 'CalibHamm_Bld31'
    BuildNum = [31]#Bld2Sim
    VarName2Change = ['AirRecovEff','IntLoadCurveShape','wwr','EnvLeak','setTempLoL','AreaBasedFlowRate','WindowUval','WallInsuThick','RoofInsuThick']
    Bounds = [[0.5,0.9],[1,5],[0.2,0.4],[0.5,1.6],[18,22],[0.35,1],[0.7,2],[0.1,0.3],[0.2,0.4]]
    NbRuns = 200
    CPUusage = 0.8
    SepThreads = True
    CreateFMU = False
    CorePerim = False
    FloorZoning = True
    PlotBuilding = False
    PathInputFile = 'HammarbyLast.txt'#'Pathways_Template.txt'
    OutputsFile = 'Outputs.txt'
    ZoneOfInterest = ''

######################################################################################################################
########     LAUNCHING MULTIPROCESS PROCESS PART     #################################################################
######################################################################################################################

    # reading the pathfiles and the geojsonfile
    keyPath = GrlFct.readPathfile(PathInputFile)
    epluspath = keyPath['epluspath']
    DataBaseInput = GrlFct.ReadGeoJsonFile(keyPath)
    BuildNum2Launch = [i for i in range(len(DataBaseInput['Build']))]
    if BuildNum:
        BuildNum2Launch = BuildNum
    if os.path.isfile(os.path.join(os.getcwd(), ZoneOfInterest)):
        NewBuildNum2Launch = []
        Bld2Keep = GrlFct.ReadZoneOfInterest(os.path.join(os.getcwd(), ZoneOfInterest), keyWord='50A Uuid')
        for bldNum, Bld in enumerate(DataBaseInput['Build']):
            if Bld.properties['50A_UUID'] in Bld2Keep and bldNum in BuildNum2Launch:
                NewBuildNum2Launch.append(bldNum)
        BuildNum2Launch = NewBuildNum2Launch
    if not BuildNum2Launch:
        print('Sorry, but no building matches with the requirements....Please, check your ZoneOfInterest')
    else:

        FigCenter = []
        LogFile=[]
        CurrentPath = os.getcwd()

        for idx,nbBuild in enumerate(BuildNum2Launch):
            #First, lets create the folder for the building and simulation processes
            SimDir,LogFile1 = GrlFct.CreateSimDir(CurrentPath,CaseName,SepThreads,nbBuild,idx,LogFile,Refresh=False)
            LogFile1.close() #this file was define by the olde way of doing things
            os.remove(os.path.join(SimDir, 'Build_' + str(nbBuild) + '_Logs.log'))
            Paramfile = os.path.join(os.path.dirname(SimDir), 'ParamSample.pickle')
            newpath = 'C:\\Users\\xav77\Documents\\FAURE\\prgm_python\\UrbanT\\Eplus4Mubes\\MUBES_SimResults\\ComputedElem4Calibration'
            Paramfile = os.path.join(newpath, 'Bld31_WeeklyCovarCalibratedSample.pickle')
            with open(Paramfile, 'rb') as handle:
                 ParamSample = pickle.load(handle)
            import numpy as np
            ParamSample = np.array(ParamSample)
            #ParamSample = SetParamSample(SimDir, NbRuns, VarName2Change, Bounds)

            if idx-200<len(DataBaseInput['Build']):
                MainInputs = {}
                MainInputs['FirstRun'] = True
                MainInputs['CorePerim'] = CorePerim
                MainInputs['FloorZoning'] = FloorZoning
                MainInputs['CreateFMU'] = CreateFMU
                MainInputs['TotNbRun'] = NbRuns
                MainInputs['OutputsFile'] = OutputsFile
                MainInputs['SimDir'] = SimDir
                MainInputs['PathInputFiles'] = PathInputFile
                MainInputs['nbBuild'] = nbBuild
                MainInputs['ParamVal'] = ParamSample[0, :]
                MainInputs['VarName2Change'] = VarName2Change
                LaunchOAT(MainInputs,ParamSample[0, :],idx)
                MainInputs['FirstRun'] = False
                nbcpu = max(mp.cpu_count() * CPUusage, 1)
                pool = mp.Pool(processes=int(nbcpu))  # let us allow 80% of CPU usage
                for i in range(1,len(ParamSample)):
                    pool.apply_async(LaunchOAT, args=(MainInputs,ParamSample[i, :],i+idx))
                pool.close()
                pool.join()
                #getting through the mainfunction above :LaunchProcess() each building sees its idf done in a row within this function
                # try:
                #     epluspath,NewCentroid = LaunchProcess(SimDir,DataBaseInput,LogFile,idx,keyPath,nbBuild,CorePerim,FloorZoning,
                #             VarName2Change,Bounds,NbRuns,SepThreads,CreateFMU,FigCenter,PlotBuilding,OutputsFile)
                # except:
                #     msg = '[ERROR] There was an error on this building, process aborted\n'
                #     print(msg[:-1])
                #     GrlFct.Write2LogFile(msg, LogFile)
                #     GrlFct.Write2LogFile('##############################################################\n', LogFile)
                #     os.chdir(CurrentPath)
                #if choicies is done, once the building is finished parallel computing is launched for this one
                if SepThreads and not CreateFMU:
                    try:
                        LogFile.close()
                    except:
                        pass
                    file2run = LaunchSim.initiateprocess(SimDir)
                    newlist2run = []
                    for file in file2run:
                        if not os.path.isfile(os.path.join(SimDir, 'Sim_Results', file[:-4] + '.pickle')):
                            newlist2run.append(file)
                    file2run = newlist2run
                    nbcpu = max(mp.cpu_count()*CPUusage,1)
                    pool = mp.Pool(processes=int(nbcpu))  # let us allow 80% of CPU usage
                    for i in range(len(file2run)):
                        pool.apply_async(LaunchSim.runcase, args=(file2run[i], SimDir, epluspath))
                    pool.close()
                    pool.join()
                    #GrlFct.SaveCase(SimDir,SepThreads,CaseName,nbBuild)
            else:
                print('All buildings in the input file have been treated.')
                print('###################################################')
                break
        # if choicies is done, once the building is finished parallel computing is launched for all files
        if not SepThreads and not CreateFMU:
            try:
                LogFile.close()
            except:
                pass
            file2run = LaunchSim.initiateprocess(SimDir)
            nbcpu = max(mp.cpu_count()*CPUusage,1)
            pool = mp.Pool(processes=int(nbcpu))  # let us allow 80% of CPU usage
            for i in range(len(file2run)):
                pool.apply_async(LaunchSim.runcase, args=(file2run[i], SimDir, epluspath))
            pool.close()
            pool.join()
            #GrlFct.SaveCase(SimDir, SepThreads,CaseName,nbBuild)
        #lets supress the path we needed for geomeppy
        # import matplotlib.pyplot as plt
        # plt.show()
        sys.path.remove(path2addgeom)