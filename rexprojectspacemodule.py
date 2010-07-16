 
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
import rexprojectspacenotificationcenter 
 
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
        sog.SetText("pallo",V3(1.0,1.0,0.0),1.0)
        return sog    
    
    
    def getProjectRootFolders(self):  
        j = self.vcs.GetBlobs()
        
        allFilesAndFolders = j.values()
        
        folders = []    
        temp = []
        folderinfos = []
        
        allFilesAndFolders = allFilesAndFolders[0]
        
        for item in allFilesAndFolders:
            
            t = item.split("/")
            if len(t) > 1:
                
                folders.append(t[0])
                
        temp = folders
        folders = list(set(folders))
        folders.sort()
      
        #now count sub items
        for folder in folders:
            count = temp.count(folder)
            folderinfos.append(rexprojectspacedataobjects.FolderInfo(folder,count))
        
        return folderinfos
    
    
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
            #print "Couldn't get a ref to RexSCriptInterface"
        else:
            self.rexif = rexpy.mCSharp
        
        ball = self.createBall()

        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.rop = rexObjects.GetObject(ball.UUID)
        self.rop.RexClassName = "rexprojectspace.RexProjectSpace"
        
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        
        #self.tree = self.initTree("naali")
        self.project = self.initSWProject()

        projectpos = V3(131,130,25.2)
        issuespawnpos = V3(125,125,25.2)
        self.issuefactory = swissue.IssueFactory(self.scene,V3(projectpos.X,projectpos.Y,projectpos.Z),V3(projectpos.X+6,projectpos.Y+6,projectpos.Z + 2),issuespawnpos)
    
        self.setUpTests()
        
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

    
    def initTree(self,vProjectName):
        
        branches = self.vcs.GetBranches()
        self.tree = swsourcetree.SWSourceTree(self.scene,vProjectName,branches)

    def initSWProject(self):
          
        components = []
        
        #get all committers
        committers = self.vcs.GetAllContributors()
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
            
            print "%s has %s commits and name is:%s"%(dev["login"],dev["contributions"],name)
        
        commits_for_devs = {}
        
        #get previous 500 commits 
        coms = self.vcs.GetCommitsFromNetworkData(500)
        
        coms.reverse()#oldest first, so reverse!
        
        for commit in coms:
           
            author = commit["author"]
            #for every name, insert a commit
            try:
                commits_for_devs[author]
            except:
                ##print author
                ##print commit["committer"]
                commits_for_devs[author] = commit
                """
                #print commit["author"]
                #print commit["login"]
                #print commit["message"]
                #print commit["id"]
                #print commit["date"]
                """
                #print "_______________"
                
                
                
                #match committer to some dinfo
                for dev in devs:
                    if dev.name == author or dev.login == commit["login"]  or dev.login == author:
                        dev.latestcommitid = commit["id"]
                        print "commit found for: ",dev.login
                        count -= 1
                        
            if count < 1:
                #print "everyone has commits"
                break
          
        #now we have commit ids... fetch the data for all committers
        #and create swdevelopers...
        swdevs = []
        for dev in devs:
            if dev.latestcommitid == 0:
                continue #no commit
            
            ci = self.vcs.GetCommitInformation(dev.latestcommitid)
            #print "commit id %s for dev:%s "%(dev.latestcommitid,dev.login)
            
            c = ci["commit"]
           
            devCommit = rexprojectspacedataobjects.CommitInfo(dev.login,c)
            dev.latestcommit = devCommit
            
            #init every developer so that each has latest commits, commit count and names in place
            swdevs.append(swdeveloper.SWDeveloper(self,self.scene,dev,False))
           
        #get all the components...
        """
        components = ["Core","Foundation","Interfaces","RexCommon","SceneManager","OgreRenderingModule"
                      "Application","RexLogicModule","SupportModules","AssetModule","UiModule","HttpUtilities"
                      "RpcUtilities","ProtocolUtilities","EnvironmentModule","TextureDecoderModule","ProtocolModuleOpenSim",
                      "ProtocolModuleTaiga","EntityComponents","bin","doc","QtInputModule"]
        """
        
        """
        components = ["Application","RexLogicModule","SupportModules","AssetModule","UiModule","HttpUtilities"
                      "RpcUtilities","ProtocolUtilities","EnvironmentModule"]
        """
        
        """
        components = ["Core","Foundation","RpcUtilities"]
        """
        
        """
        components = ["Core","Foundation","RpcUtilities","ProtocolUtilities","EnvironmentModule","TextureDecoderModule","ProtocolModuleOpenSim",
                      "ProtocolModuleTaiga","EntityComponents","bin","doc","QtInputModule"]
        """
        
        components = self.getProjectRootFolders()
        
        project = swproject.SWProject(self.scene,"naali",components,swdevs)
        
        return project

    def mesh_follow_avatar(self, avatar_presence, mesh_part, pos=V3(1.5, 0, 1),
        rot=OpenMetaverse.Quaternion(0, 0, 0, 1)):
        #mesh_local_id = self.get_mesh_local_id(mesh_part)
        
        lid = 0
        for ent in self.scene.GetEntities():
            if self.bug.UUID == ent.UUID:
                #print "found local id"
                lid = ent.LocalId
                
        mesh_local_id = lid
        pos_lsl = LSL_Types.Vector3(0, 0, 2)
        rot_lsl = LSL_Types.Quaternion(0, 0, 0, 1)
        ##print 'rot offset before attach', mesh_part.RotationOffset
        self.rexif.rexAttachObjectToAvatar(mesh_local_id.ToString(),
        avatar_presence.UUID.ToString(),
        28, pos_lsl, rot_lsl, False)
        mesh_part.ParentGroup.UpdateGroupPosition(pos)

        mesh_part.ParentGroup.UpdateGroupRotationR(rot)
        #print "attach done"   
    
    def setUpTests(self):
        
        scene = self.scene
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
        
        #testing component grid
        scene.AddCommand(self, "ac","","",self.cmd_ac)
        scene.AddCommand(self, "modcom","","",self.cmd_modify)
        scene.AddCommand(self, "remcom","","",self.cmd_remove)
        scene.AddCommand(self, "addcom","","",self.cmd_add)
        
       
        #testing builds
        scene.AddCommand(self, "bf","","",self.cmd_bf)
        scene.AddCommand(self, "bs","","",self.cmd_bs)
        
        #testing commits
        scene.AddCommand(self, "commit","","",self.cmd_commit)
    
        #testing branches
        scene.AddCommand(self, "cb","","",self.cmd_cb)
        
        #testing issues
        scene.AddCommand(self, "bug","","",self.cmd_create_bug)
        scene.AddCommand(self, "enhan","","",self.cmd_create_en)

        #testing developers
        scene.AddCommand(self, "developer","","",self.cmd_developer)
        
        #testing project
        scene.AddCommand(self, "project","","",self.cmd_project)
        
    
    def cmd_hitMe(self, *args):
        #try to get the tree item
        #self.tree.setBuildFailed()
        sog,rop = rexprojectspaceutils.load_mesh(self.scene,"diamond.mesh","diamond.material","test mesh data")
        
        #load texture
        tex = rexprojectspaceutils.load_texture(self.scene,"rpstextures/diamond_blue.jp2")
        rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))

        self.scene.AddNewSceneObject(sog, False)

        
    def cmd_ac(self, *args):
        self.testcomponent = swproject.Component(self.scene, "test_component_11" , V3(126,126,25.5), None, 2,2,V3(1,1,1))
    
    def cmd_remove(self, *args):
        self.testcomponent.SetState("removed") 

    def cmd_modify(self, *args):
        self.testcomponent.SetState("modified")
        
    def cmd_add(self, *args):
        self.testcomponent.SetState("added")
        
        
    def cmd_cb(self, *args):
        self.tree.addNewBranch(self,"new branch from region module")
        
    def cmd_bs(self, *args):
        self.tree.setBuildSuccesfull()
        
    def cmd_bf(self, *args):
        self.tree.setBuildFailed()
        
    def cmd_commit(self, *args):
        
        cd = rexprojectspacenotificationcenter.CommitDispatcher.dispatcherForProject("naali")
        
        commit = {}
        commit["message"] = "test commit from region module"
        
        commit["authored_date"] = "2010-07-01T09:54:40-07:00"
        
        commit["removed"] = []
        commit["added"] = []
        commit["modified"] = ["bin"]
        
        ci = rexprojectspacedataobjects.CommitInfo("antont",commit,"antont")
        
        commits = [commit]
        
        cd.dispatchCommits( commits )
    
    def cmd_create_bug(self, *args):

        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Defect"
        issueData.owner = "maukka user"
        issueData.id = str(random.randint(0,1000000))
        bug =  self.issuefactory.CreateIssue(issueData)
        bug.start()
        
    def cmd_create_en(self, *args):
        
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Enhancement"
        issueData.owner = "maukka user"
        issueData.id = str(random.randint(0,1000000))
        bug =  self.issuefactory.CreateIssue(issueData)
        bug.start()
        print bug
    
    def cmd_developer(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("maukka","maukka user")
        self.dev = swdeveloper.SWDeveloper(self,self.scene,dinfo,False)
        
        
    def cmd_project(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("maukka","maukka user")
        self.dev = swdeveloper.SWDeveloper(self,self.scene,dinfo,False)
    
        self.testproject = swproject.SWProject(self.scene,"test_project",[],[self.dev])
    
    def onFrameUpdate(self):
        pass
     
    #to scripting bridge ---------------------
    
    def SpawnDeveloper(self,vDevLoc):
        """Returs the actual script instance!!! """
        pos = LSL_Types.Vector3(120, 120, 26)
        localId = self.spawner.SpawnActor(pos,0,False,"developer.Developer")
        developer = self.world.GetActorByLocalID(localId)
        #print "script instance: ",developer
        return developer
    
    def SetRexWorld(self,vWorld):
        #print "it's alive"
        self.world = vWorld
    
    def GetActor(self, vId):
        if not self.world:
            #print "no world set!!!!!______"
            return None
        
        actor = self.spawner.MyWorld.GetActorByLocalID(vId)
            
        #actor = self.world.GetActorByLocalID(vId)
        #print actor
        
        return actor
    
    def SetSpawner(self,vRexProjectSpace):
        #print "spawner set-------"
        self.spawner = vRexProjectSpace
        
        
        def Spawner(self):
            return spawner
            
        def SpawnScriptInstance(self,vPyClass):
            id = 0
            return id
    
    ####
        
        