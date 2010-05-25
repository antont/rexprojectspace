 
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

import swsourcetree
import buildbot

class RexProjectSpace(IRegionModule):
    autoload = True
    
    def createBall(self):
        sphereRadius = 0.025
        sphereHeigth = 0.05
        
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateSphere()
        pbs.SetRadius(sphereRadius)
        pbs.SetHeigth(sphereHeigth)        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),V3(127,130,26),pbs)

        texcolor = OpenMetaverse.Color4(1, 0, 0, 1)
        tex = sog.RootPart.Shape.Textures
        tex.DefaultTexture.RGBA = texcolor
        sog.RootPart.UpdateTexture(tex)
        self.scene.AddNewSceneObject(sog, False)
        return sog    
    
    
    def Initialise(self, scene, configsource):
        
        self.removed = False
        self.scene = scene
        self.config = configsource
        
        self.buildbot = buildbot.BuildBot()
        
        branches = []
        self.tree = swsourcetree.SWSourceTree(scene,"Naali",branches)
        
        self.updateBuildResults()
        
        try:
            rexpy = scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            print "Couldn't get a ref to RexSCriptInterface"
        else:
            self.rexif = rexpy.mCSharp
        
        ball = self.createBall()

        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        #self.updateTimer = threading.Timer(1.0,self.updateProjectSpace)
        #self.updateTimer.start()
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
    
    def updateBuildResults(self):
        builds = self.buildbot.getLatestBuilds()
        
        buildResult = True
        
        for k,v in builds.iteritems():
            if v == "success":
                pass
            else:
                buildResult = False
                
        if buildResult == True:
            self.tree.setBuildSuccesfull()
        else:
            self.tree.setBuildFailed()
    
    def cmd_hitMe(self, *args):
        #try to get the tree item
        print "hello"
        self.tree.setBuildFailed()

    
    def updateProjectSpace(self):

        
    
        self.updateTimer = threading.Timer(30.0,self.updateProjectSpace)
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
        
    def onFrameUpdate(self):
        pass
 