
import clr, math

clr.AddReference('OpenMetaverseTypes')
import OpenMetaverse

clr.AddReference("mscorlib.dll")
import System

from System import Array

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types
clr.AddReference('OpenSim.Framework')
import OpenSim.Framework
clr.AddReference('OpenSim.Region.Framework')
from OpenSim.Region.Framework.Interfaces import IRegionModule

clr.AddReference('OgreSceneImporter')
import OgreSceneImporter

clr.AddReference('RexDotMeshLoader')
from RexDotMeshLoader import DotMeshLoader

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types


from OpenMetaverse import Vector3 as V3

import sys, os, sha
import threading
class ScriptBridgeModule(IRegionModule):
    autoload = True
    instance = None
    
    def Initialise(self, scene, configsource):
     
        print "Initialise from bridge"
        
        self.removed = False
        self.scene = scene
        self.config = configsource
        self.world = None
        self.actor = None
        
        try:
            rexpy = self.scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            #print "Couldn't get a ref to RexSCriptInterface"
        
        if rexpy:
            print "spawning actor"
            self.rexif = rexpy.mCSharp
            #pos = self.sog.AbsolutePosition
            pos_lsl = LSL_Types.Vector3(125,125,25)
            self.rexif.SpawnActor(pos_lsl,0,False,"rexprojectspace.RexProjectSpace")

        
    def PostInitialise(self):
        #print "postinit..."
        pass

    def Close(self):
        #print self, 'close'
        pass
    
    def getname(self):
        return self.__class__.__name__

    Name = property(getname)

    def isshared(self):
        return False

    IsSharedModule = property(isshared)
    
    def onFrameUpdate(self):
        pass
    
    def Actor(self):
        print "hello"
        if not self.actor:
            self.actor = self.SpawnActor("rxactor.Actor",V3(120,120,120))
            print self.actor
        return self.actor
    
    def SetWorld(self,vWorld):
        print "--------world set-------"
        self.world = vWorld
        
    def SpawnActor(self,vClassName,pos):   
        pos_lsl = LSL_Types.Vector3(125,125,25)
        localid = self.rexif.SpawnActor(pos_lsl,0,False,vClassName)
        actor = self.GetActorWithLocalID(localid)
        #print actor
        return actor
        
    def GetActorWithLocalID(self,vLocalID):
        return self.world.GetActorByLocalID(vLocalID)
    