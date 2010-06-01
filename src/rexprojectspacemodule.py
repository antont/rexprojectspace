 
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

from OpenMetaverse import Vector3 as V3

import sys, os, sha
import threading

import swsourcetree
import buildbot

import swproject
import swdeveloper

import versioncontrolsystem

import rexprojectspaceutils

sys.path.append(os.getcwd() + "/ScriptEngines/PythonScript")

import RexProjectSpaceScripts.follower
from RexProjectSpaceScripts.rexprojectspace import *
 
def SetWorld(vW):
    RexProjectSpaceModule.rexworld = vW
    
    
class RexProjectSpaceModule(IRegionModule):
    autoload = True
    rexworld = ""
    
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
        
        RexProjectSpaceModule.rexworld = ""
        self.removed = False
        self.scene = scene
        self.config = configsource
        
        self.developers = []
        
        self.buildbot = buildbot.BuildBot()
        
        branches = []
        #self.tree = swsourcetree.SWSourceTree(scene,"Naali",branches)
        #self.updateBuildResults()
        
        #self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        #self.updateCommitters(self.developers)
        #self.project = self.initSWProject()
        
        try:
            rexpy = scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            print "Couldn't get a ref to RexSCriptInterface"
        else:
            self.rexif = rexpy.mCSharp
        
        ball = self.createBall()

        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.rop = rexObjects.GetObject(ball.UUID)
        self.rop.RexClassName = "rexprojectspace.RexProjectSpace"
        
        
        #self.updateTimer = threading.Timer(1.0,self.updateProjectSpace)
        #self.updateTimer.start()
        
        self.tree = swsourcetree.Tree(self.scene, "Naali")
        
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
        scene.AddCommand(self, "aa","","",self.cmd_aa)
        scene.AddCommand(self, "bb","","",self.cmd_bb)
        
    
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
    
    def initSWProject(self):
        """Mocked solution for now """
        
        components = []
        components.append(swproject.SWComponent("Application"))
        components.append(swproject.SWComponent("AssetModule"))
    
        project = swproject.SWProject("naali",components)
    
        return project
        
        
    def updateCommitters(self,vCommitters):
        """ Committers from github """
        contributors = self.vcs.getAllContributors()
        
        for value in contributors:
            login = value["login"]
            nbrOfCommits = value["contributions"]
            vCommitters.append(swdeveloper.SWDeveloper(self.scene,login,nbrOfCommits,"",False))

    
    def cmd_hitMe(self, *args):
        #try to get the tree item
        #self.tree.setBuildFailed()
        #sog,rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data")
        #self.scene.AddNewSceneObject(sog, False)
        self.mauno = swdeveloper.SWDeveloper(self.scene,"Mauno User",10,None,False)
        
    def cmd_aa(self, *args):
        #try to get the tree item
        #list = self.scene.GetAvatars()
        #sp = list[0]

        self.mauno.updateIsAtProjectSpace(True)
        #self.rexif.
        
    def cmd_bb(self, *args):
        #w = RXCore.rxactor.Actor.GetScriptClassName()
        self.tree.addNewBranch(self,"Naali")
        print "haalll"
        pass
        
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
        
