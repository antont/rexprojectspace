 
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
sys.path.append(os.getcwd() + "/ScriptEngines/PythonScript/RXCore")
sys.path.append(os.getcwd() + "/src")

import swsourcetree
import buildbot

import swproject
import swdeveloper
import swissue

import versioncontrolsystem

import rexprojectspaceutils

import RexProjectSpaceScripts.follower
from RexProjectSpaceScripts.rexprojectspace import *
 
import RexProjectSpaceScripts.rexprojectspace 

import rexprojectspacedataobjects
 
class RexProjectSpaceModule(IRegionModule):
    autoload = True
    rexworld = ""
    
    def SpawnDeveloper(self,vDevLoc):
        """Returs the actual script instance!!! """
        pos = LSL_Types.Vector3(120, 120, 26)
        localId = self.spawner.SpawnActor(pos,0,False,"developer.Developer")
        developer = self.world.GetActorByLocalID(localId)
        print "script instance: ",developer
        return developer
    
    def SetRexWorld(self,vWorld):
        print "it's alive"
        self.world = vWorld
    
    def GetActor(self, vId):
        if not self.world:
            print "no world set!!!!!______"
            return None
        
        actor = self.spawner.MyWorld.GetActorByLocalID(vId)
            
        #actor = self.world.GetActorByLocalID(vId)
        print actor
        
        return actor
    
    def SetSpawner(self,vRexProjectSpace):
        print "spawner set-------"
        self.spawner = vRexProjectSpace
        
    
    def Spawner(self):
        return spawner
        
    def SpawnScriptInstance(self,vPyClass):
        id = 0
        return id
    
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
        self.world = None
        self.developers = []
        self.spawner = None
        
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
        
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
        
        #self.bug,self.bugrop = rexprojectspaceutils.load_mesh(self.scene,"Bug.mesh","Bug.material","bug...")
        
        #------------ how to create bug
        
        #get bug factory
        
        #create a bug with bug data from the factory ()
        
        #"start" the bug
        
        #------------
        
        
        #------------ how to load the bug
        
        #load/store texture
        
        #load mesh with material
        
        #load/store .skeleton
        
        #start animation
        
        #self.bug,self.bugrop = rexprojectspaceutils.load_mesh(self.scene,"Sphere.mesh","Sphere.material","bug...")
        
        """
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Defect"
        bug = swissue.CreateIssue(self.scene,issueData)
        """
        
        #--------------
        
        #return
        
        self.buildbot = buildbot.BuildBot()
        
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        branches = self.vcs.getBranches()
        self.tree = swsourcetree.SWSourceTree(scene,"Naali",branches)
        
        #testing branches
        scene.AddCommand(self, "cb","","",self.cmd_cb)
        #self.updateCommitters(self.developers)
        
        return
        
        self.project = self.initSWProject()
        
        #return
        
        #self.updateBuildResults()
        
        
        #testing component grid
        scene.AddCommand(self, "ac","","",self.cmd_ac)
        
        scene.AddCommand(self, "bb","","",self.cmd_bb)
        
        
        
        #testing builds
        scene.AddCommand(self, "bf","","",self.cmd_bf)
        scene.AddCommand(self, "bs","","",self.cmd_bs)
        
        #testing commits
        scene.AddCommand(self, "commit","","",self.cmd_commit)
    
    def PostInitialise(self):
        print "postinit..."
        pass
    
    def initSWProject(self):
          
        components = []
        
        #get all committers
        committers = self.vcs.getAllContributors()
        count = len(committers)
        temp = count
        
        #create developerinfo for every dev..
        devs = []
        for dev in committers:
            dinfo = rexprojectspacedataobjects.DeveloperInfo(dev["login"],"")
            dinfo.commitcount = dev["contributions"]
            name = ""
            try:
                name = dev["name"]
            except:
                pass
            dinfo.name = name
            devs.append(dinfo)
            
            #print "%s has %s commits and name is:%s"%(dev["login"],dev["contributions"],name)
        
        commits_for_devs = {}
        
        #get previous 500 commits 
        coms = self.vcs.getCommitsFromNetworkData(500)
        
        coms.reverse()#oldest first, so reverse!
        
        for commit in coms:
           
            author = commit["author"]
            #for every name, insert a commit
            try:
                commits_for_devs[author]
            except:
                #print author
                #print commit["committer"]
                commits_for_devs[author] = commit
                """
                print commit["author"]
                print commit["login"]
                print commit["message"]
                print commit["id"]
                print commit["date"]
                """
                print "_______________"
                
                
                
                #match committer to some dinfo
                for dev in devs:
                    if dev.name == author or dev.login == commit["login"]  or dev.login == author:
                        dev.latestcommitid = commit["id"]
                        print "commit found for: ",dev.login
                        count -= 1
                        
            if count < 1:
                print "everyone has commits"
                break
          
        #now we have commit ids... fetch the data for all committers
        #and create swdevelopers...
        swdevs = []
        for dev in devs:
            if dev.latestcommitid == 0:
                continue #no commit
            
            ci = self.vcs.getCommitInformation(dev.latestcommitid)
            print "commit id %s for dev:%s "%(dev.latestcommitid,dev.login)
            
            c = ci["commit"]
            
            #files,folders = rexprojectspaceutils.resolveFilesAndFolders(c)
            #message = c["message"]
            #devCommit = commitdispatcher.CommitInfo(dev.login,message,folders,files)
            devCommit = rexprojectspacedataobjects.CommitInfo(dev.login,c)
            dev.latestcommit = devCommit
            
            #init every developer so that each has latest commits, commit count and names in place
            swdevs.append(swdeveloper.SWDeveloper(self,self.scene,dev,False))
            #try with scripts
            #swdevs.append(self.SpawnDeveloper(dev))
        
        #get all the components...
        components = ["Core","Foundation","Interfaces","RexCommon","SceneManager","OgreRenderingModule"
                      "Application","RexLogicModule","SupportModules","AssetModule","UiModule","HttpUtilities"
                      "RpcUtilities","ProtocolUtilities","EnvironmentModule","TextureDecoderModule","ProtocolModuleOpenSim",
                      "ProtocolModuleTaiga","EntityComponents","bin","doc"]
        
        project = swproject.SWProject(self.scene,"naali",components,swdevs)
        
        #update developers status information
        for dev in swdevs:
            dev.updateIsAtProjectSpace(False)
        
        return project

 
    def updateCommitters(self,vCommitters):
        """ Committers from github """
        contributors = self.vcs.getAllContributors()
        
        for value in contributors:
            login = value["login"]
            nbrOfCommits = value["contributions"]
            vCommitters.append(swdeveloper.SWDeveloper(self.scene,login,nbrOfCommits,"",False))

    def mesh_follow_avatar(self, avatar_presence, mesh_part, pos=V3(1.5, 0, 1),
        rot=OpenMetaverse.Quaternion(0, 0, 0, 1)):
        #mesh_local_id = self.get_mesh_local_id(mesh_part)
        
        lid = 0
        for ent in self.scene.GetEntities():
            if self.bug.UUID == ent.UUID:
                print "found local id"
                lid = ent.LocalId
                
        mesh_local_id = lid
        pos_lsl = LSL_Types.Vector3(0, 0, 2)
        rot_lsl = LSL_Types.Quaternion(0, 0, 0, 1)
        #print 'rot offset before attach', mesh_part.RotationOffset
        self.rexif.rexAttachObjectToAvatar(mesh_local_id.ToString(),
        avatar_presence.UUID.ToString(),
        28, pos_lsl, rot_lsl, False)
        mesh_part.ParentGroup.UpdateGroupPosition(pos)

        mesh_part.ParentGroup.UpdateGroupRotationR(rot)
        print "attach done"   
   
    def cmd_hitMe(self, *args):
        #try to get the tree item
        #self.tree.setBuildFailed()
        #sog,rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data")
        #self.scene.AddNewSceneObject(sog, False)
        #print rexprojectspaceutils.world()
        #print self.GetActor("2549818162")
        #sog,rop = rexprojectspaceutils.load_mesh(self.scene,"Bug.mesh","Bug.material","bug...")
        
        #dev = self.SpawnDeveloper(V3(120,120,24))
        """dinfo = rexprojectspacedataobjects.DeveloperInfo("antont","")
        lid = 0
        for ent in self.scene.GetEntities():
            if self.bug.UUID == ent.UUID:
                print "found local id"
                lid = ent.LocalId
        dev = self.spawner.MyWorld.GetActorByLocalID(lid)
        print dev
        #dev.SetDeveloperInfo(self.scene,sog,dinfo)
        """
        avatar = self.scene.GetScenePresences()[0]
            
        
        self.mesh_follow_avatar(avatar,self.bug)
        
    def cmd_ac(self, *args):
        self.component.addComponent("")
        pass
    
    def cmd_bb(self, *args):
        #w = RXCore.rxactor.Actor.GetScriptClassName()
        #self.tree.addNewBranch(self,"Naali")
        #self.grid = swproject.Component(self.scene,V3(135.2,129.89,25.80),"",4,4)
        
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
        #cd = commitdispatcher.CommitDispatcher.dispatcherForProject("naali")
        #cd.dispatchCommits( [] )
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
        
