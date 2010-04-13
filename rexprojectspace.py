 
import clr, math

clr.AddReference('OpenMetaverseTypes')
import OpenMetaverse

clr.AddReference("mscorlib.dll")
import System

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types
clr.AddReference('OpenSim.Framework')
import OpenSim.Framework
clr.AddReference('OpenSim.Region.Framework')
from OpenSim.Region.Framework.Interfaces import IRegionModule

from OpenMetaverse import Vector3 as V3

import sys, os, sha
import threading

import buildbot
import issuetracker

class RexProjectSpace(IRegionModule):
    autoload = True

    def Initialise(self, scene, configsource):
        """ Create issuetracker and build bot and start the
        timer that trickers scene updates """
        self.removed = False
        self.scene = scene
        self.config = configsource

        try:
            rexpy = scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            print "Couldn't get a ref to RexSCriptInterface"
        else:
            self.rexif = rexpy.mCSharp
        
        self.bot = buildbot.BuildBot(scene,V3(133.00,124.00,24.92))
        
        self.tracker = issuetracker.IssueTracker("realxtend-naali",scene,V3(129, 129, 25.279))

        self.updateTimer = threading.Timer(60.0,self.updateProjectSpace)
        self.updateTimer.start()

    def updateProjectSpace(self):
        """update the project space once a minute"""
        self.bot.updateData()
        self.bot.updateVisualization()
                
        self.tracker.updateData()
        self.tracker.updateVisualization()
        
        self.updateTimer = None
        self.updateTimer = threading.Timer(60.0,self.updateProjectSpace)
        self.updateTimer.start()
        pass

    def PostInitialise(self):
        print self, 'post-initialise'

    def Close(self):
        print self, 'close'

    def getname(self):
        return self.__class__.__name__

    Name = property(getname)

    def isshared(self):
        return False

    IsSharedModule = property(isshared)

    def cmd_mesh(self, modname, args):
        print self, "running cmd_mesh"
        self.make_textmesh(None, args[0])
        
    def onFrameUpdate(self):
        pass
