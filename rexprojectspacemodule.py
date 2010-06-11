 
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

sys.path.append(os.getcwd() + "/ScriptEngines/PythonScript")
sys.path.append(os.getcwd() + "/src")

import swsourcetree
import buildbot

import swproject
import swdeveloper

import versioncontrolsystem

import rexprojectspaceutils

import commitdispatcher

import RexProjectSpaceScripts.follower
from RexProjectSpaceScripts.rexprojectspace import *
 
def SetWorld(vW):
    RexProjectSpaceModule.rexworld = vW
    

class DeveloperInfo:
    def __init__(self,vName,vLogin):
        self.name = vName
        self.login = vLogin
        self.commit = None
        self.commitcount = 0
        
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
        
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        #self.updateCommitters(self.developers)
        

        
        self.project = self.initSWProject()
        
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
        
        #self.tree = swsourcetree.Tree(self.scene, "Naali")
        #self.tree = swsourcetree.SWSourceTree(self.scene, "Naali",[])
        
        
        #self.component = swproject.Component(self.scene,V3(135.2,129.89,25.80),"",4,4)
        #self.component = swproject.SWProject(self.scene,"naali",["toni alatalo"])

        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
        
        #testing component grid
        scene.AddCommand(self, "ac","","",self.cmd_ac)
        
        scene.AddCommand(self, "bb","","",self.cmd_bb)
        
        #testing branches
        scene.AddCommand(self, "cb","","",self.cmd_cb)
        
        #testing builds
        scene.AddCommand(self, "bf","","",self.cmd_bf)
        scene.AddCommand(self, "bs","","",self.cmd_bs)
        
        #testing commits
        scene.AddCommand(self, "commit","","",self.cmd_commit)

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
   
 
###
    def resolveFilesAndFolders(self,vCommit):
        #get mod,add,remove
        files,mod,removed,added = [],[],[],[]
        try:
            mod = vCommit["modified"]
        except:
            pass
        try:
            removed = vCommit["Removed"]
        except:
            pass
        try:
            added = vCommit["added"]
        except:
            pass
          
        for m in mod:
            files.append(m["filename"]) 
        for a in added:
            files.append(a) 
        
        for r in removed:
            files.append(r)
                    

        #files.sort()       
        
        modifiedfiles = list(set(files))
        
        files = []
        folders = []
        
        for file in modifiedfiles:
            files.append(file)
            
            temp = file.split("/")
            if len(temp) > 0:
                folders.append(temp[0])
            else:
                folders.append("/")

        #print folders
        return files,folders


    def initSWProject(self):
        
        components = []
        
        #get all committers
        committers = self.vcs.getAllContributors()
        
        devs = {}
        
        for committer in committers:
            devs[committer["login"]] = DeveloperInfo("",committer["login"])
        
        commits_for_devs = {}
        
        #get all commits 
        commits = self.vcs.getCommitsForBranch()
        count = len(committers)
        temp = count

        for commit in commits:
           
            author = commit["author"]
            #for every name, insert a commit
            try:
                commits_for_devs[author["name"]]
            except:
                #print author
                #print commit["committer"]
                commits_for_devs[author["name"]] = commit
                
                count -= 1
            
            if count < 1:
                break # every one has commit
            
        #print commits_for_devs
        
        #now we have commit ids... fetch the data for all committers
        for keys,values in commits_for_devs.iteritems():
            id = values["id"]
            ci = self.vcs.getCommitInformation(id)
            c = ci["commit"]
            
            #
            
            cur = None
            #locate correct committer
            commitcount = 0
            
            for committer in committers:
                author = values["author"]

                if committer["login"] == author["login"]:# or author["name"] == committer["login"]:
                    cur = committer
  
                    dev = devs[committer["login"]]
                    dev.commitcount = cur["contributions"]
                    
                    files,dirs = self.resolveFilesAndFolders(c)
                    
                    dev.commit = commitdispatcher.Commit(committer["login"],c["message"],dirs,files)
            if cur:
                commitcount = cur["contributions"]
            
            print "number of commits: %d for developer: %s"%(commitcount,keys)
        
        swdevelopers = []
        
        for dev in devs.values():
            swdevelopers.append(swdeveloper.SWDeveloper(self.scene,dev.login,dev.commitcount,dev.commit,False))
        
        #mock components for now
        components = ["CMakeModules","CommunicationsModule","Core","DebugStatsModule","ECEditorModule",
                      "EntityComponents","EnvironmentModule","Foundation","RexLogicModule","bin"]
        
        project = swproject.SWProject(self.scene,"naali",components,swdevelopers)
        return project
### 
        
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
        
    def cmd_ac(self, *args):
        self.component.addComponent("")
        pass
    
    def cmd_bb(self, *args):
        #w = RXCore.rxactor.Actor.GetScriptClassName()
        #self.tree.addNewBranch(self,"Naali")
        self.grid = swproject.Component(self.scene,V3(135.2,129.89,25.80),"",4,4)
        
        pass
        
    def cmd_cb(self, *args):
        #try to get the tree item
        self.tree.addNewBranch(self,"")
        #list = self.scene.GetAvatars()
        #sp = list[0]

        #self.mauno.updateIsAtProjectSpace(True)
        #self.rexif.        
        
    def cmd_bs(self, *args):
        #w = RXCore.rxactor.Actor.GetScriptClassName()
        #self.tree.addNewBranch(self,"Naali")
        self.tree.setBuildSuccesfull()
        pass
    
    def cmd_bf(self, *args):
        #w = RXCore.rxactor.Actor.GetScriptClassName()
        #self.tree.addNewBranch(self,"Naali")
        self.tree.setBuildFailed()
        pass
    
    def cmd_commit(self, *args):
        cd = commitdispatcher.CommitDispatcher.dispatcherForProject("naali")
        cd.dispatchCommits( [] )
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
        
