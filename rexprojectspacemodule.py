 
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
import issuetracker

import swproject
import swdeveloper
import swissue

import versioncontrolsystem

import rexprojectspaceutils

import rexprojectspacedataobjects
import rexprojectspacenotificationcenter 
 
import time
import datetime 
import random

class RexProjectSpaceInformationShouter:
    def __init__(self, vScene):
        self.scene = vScene
        self.scriptingbridge = None
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIrcMessage += self.OnNewIRCMessage
        nc.OnNewCommit += self.OnNewCommit
        
        try:
            self.scriptingbridge = self.scene.Modules["ScriptBridgeModule"]
            print "Got bridge"
        except:
            #get it later
            self.timer = threading.Timer(5.0,self.GetBridge)
            self.timer.start()
    
    def __del__(self):
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIrcMessage += self.OnNewIRCMessage
        nc.OnNewCommit += self.OnNewCommit
        
        
    def OnNewCommit(self,vCommit):
        self.GetBridge()
        self.scriptingbridge.Actor().llShout(0,vCommit.message)
        
    def OnNewIRCMessage(self,vMessage):
        self.GetBridge()
        self.scriptingbridge.Actor().llShout(0,vMessage)
        
    
    def GetBridge(self):
        try:
            self.scriptingbridge = self.scene.Modules["ScriptBridgeModule"]
            print "Got bridge"
            self.timer = 0
        except:
            #get it later
            self.timer = threading.Timer(5.0,self.GetBridge)
    
    
class RexProjectSpaceModule(IRegionModule):
    autoload = True

    def getProjectRootFolders(self):
        """ Gets all the blobs from version control and
            parses the data so that the root folders
            of the projects repository can be listed withot
            duplicate entries and returns it. """
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
        """ Create IssueFactory, SWTree and SWProject """
        
        self.removed = False
        self.scene = scene
        self.config = configsource

        self.developers = []
        
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        
        projectpos = V3(131,130,25.2)
        issuespawnpos = V3(125,125,25.2)
        
        #self.tree = self.initTree("naali")
        self.project = self.initSWProject()
        
        self.issuefactory = swissue.IssueFactory(self.scene,V3(projectpos.X,projectpos.Y,projectpos.Z),V3(projectpos.X+6,projectpos.Y+6,projectpos.Z + 2),issuespawnpos)
        #self.initSWIssues()
        #self.scene.EventManager.OnObjectGrab += self.clicked;
        
        self.shouter = RexProjectSpaceInformationShouter(self.scene)
        
        self.setUpTests()
        
    def PostInitialise(self):
        #print "postinit..."
        pass
    
    
    def Close(self):
        #print self, 'close'
        #self.scene.EventManager.OnObjectGrab -= self.clicked;
        pass
    
    def getname(self):
        return self.__class__.__name__

    Name = property(getname)

    def isshared(self):
        return False

    IsSharedModule = property(isshared)
    
    def onFrameUpdate(self):
        pass
    
    def initSWIssues(self):
        """ Create issue objects by using issuefactory. """
        self.issuetracker = issuetracker.IssueTracker()
        issues = self.issuetracker.getIssues()
        for i in issues:
            issue = self.issuefactory.CreateIssue(i)
            
    def initTree(self,vProjectName):
        """ Get branches and create tree """
        branches = self.vcs.GetBranches()
        #branches = []
        tree = swsourcetree.SWSourceTree(self.scene,vProjectName,branches)
        return tree
        
    def initSWProject(self):
        """ 1. Get all the contributors to a github project
            2. Resolve latest commit to as many contributors
               as possible
            3. Resolve github projects repository's root folder's
               directories
            4. Create SWProject with the help of previous informations
        """
        components = []
        
        #get all committers
        committers = self.vcs.GetAllContributors()
        count = len(committers)
        print "number of devs",count
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
        
        #get previous 1500 commits 
        coms = self.vcs.GetCommitsFromNetworkData(1000)
        
        coms.reverse()#oldest first, so reverse!
        
        for commit in coms:
           
            author = commit["author"]
            #for every name, insert a commit
            try:
                commits_for_devs[author]
            except:
                
                #match committer to some dinfo
                for dev in devs:
                    if dev.name == author or dev.login == commit["login"]  or dev.login == author:
                        if dev.latestcommitid == 0:
                            dev.latestcommitid = commit["id"]
                            print "commit found for: ",dev.login
                            count -= 1
                            break
            if count < 1:
                #print "everyone has commits"
                break
          
        #now we have commit ids... fetch the data for all committers
        #and create swdevelopers...
        swdevs = []
        for dev in devs:
            if dev.latestcommitid == 0:
                #no commit
                empty = []
                dev.latestcommit = rexprojectspacedataobjects.CommitInfo(dev.login,empty)
                pass
            else:
                ci = self.vcs.GetCommitInformation(dev.latestcommitid)
                #print "commit id %s for dev:%s "%(dev.latestcommitid,dev.login)
                
                c = ci["commit"]
               
                devCommit = rexprojectspacedataobjects.CommitInfo(dev.login,c)
                dev.latestcommit = devCommit
            
            #init every developer so that each has latest commits, commit count and names in place
            swdevs.append(swdeveloper.SWDeveloper(self.scene,dev,False))
            print "Developer-----", dev.name
            
        #get all the components...
        componentNames = self.getProjectRootFolders()
        
        project = swproject.SWProject(self.scene,"naali",componentNames,swdevs)
        
        return project

    def setUpTests(self):
        
        scene = self.scene
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
        scene.AddCommand(self, "organize","","",self.cmd_organize)
        
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
        scene.AddCommand(self, "commit2","","",self.cmd_commit2)
        scene.AddCommand(self, "blame","","",self.cmd_blame)#commit and fail build
        scene.AddCommand(self, "commit_new_dev","","",self.cmd_commit_new_dev)#commit done by new dev
        scene.AddCommand(self, "commit_new_comp","","",self.cmd_commit_new_comp)#commit done by new dev
        
    
        #testing branches
        scene.AddCommand(self, "cb","","",self.cmd_cb)
        
        #testing issues
        scene.AddCommand(self, "bug","","",self.cmd_create_bug)
        scene.AddCommand(self, "enhan","","",self.cmd_create_en)
        scene.AddCommand(self, "changebugdata","","",self.cmd_change_bug_data)

        
        #testing developers
        scene.AddCommand(self, "developer","","",self.cmd_developer)
        
        #testing project
        scene.AddCommand(self, "project","","",self.cmd_project)
    
    def cmd_hitMe(self, *args):
        self.shouter.OnNewCommit("")
        """
        self.bugs = []
        
        for i in range(0,5):
            empty = []
            issueData = rexprojectspacedataobjects.IssueInfo(empty)
            
            issueData.type = "Enhancement"
            issueData.owner = "maukka user"
            issueData.status = "new"
            issueData.summary = "enhancement made by test user..."
            issueData.id = str(random.randint(0,1000000))
            bug =  self.issuefactory.CreateIssue(issueData)
            self.bugid = issueData.id
            self.bugs.append(bug)
            bug.start()
        """
    def cmd_organize(self, *args):
        
        newpositions = []
        pos = V3(131,130,25.2)
        
        count = 0
        
        for bug in self.bugs:
            newposition = V3(pos.X,pos.Y,pos.Z + count*0.3)
            bug.sog.NonPhysicalGrabMovement(newposition)
            count += 1
    
    def clicked(self,vLocalID,vOriginalID, vOffsetPos, vRemoteClient, vSurfaceArgs):
        if vLocalID == self.testcomponent.sog.RootPart.LocalId:
            #actor = 
            print "hello"
    
    def cmd_ac(self, *args):
        #self.testcomponent = self.project.components.values[0]
        
        folderinfo = rexprojectspacedataobjects.FolderInfo("bin",10)
        
        self.testcomponent = swproject.Component(self.scene,folderinfo, V3(126,126,25.5), None, 2,2,V3(1,1,1))
        
        
    def cmd_remove(self, *args):
        self.testcomponent.SetState("removed") 

    def cmd_modify(self, *args):
        self.testcomponent.SetState("modified")
        
    def cmd_add(self, *args):
        self.testcomponent.SetState("added")
        
    def cmd_cb(self, *args):
        name = "test branch" + str(random.randint(0,1000000))
        binfo = rexprojectspacedataobjects.BranchInfo(name)
        binfo.url = "http://github.com/realxtend/naali/tree/master"
        self.tree.addNewBranches([binfo])
        
    def cmd_bs(self, *args):
        self.tree.setBuildSuccesfull()
        
    def cmd_bf(self, *args):
        self.tree.setBuildFailed()
        
    def cmd_commit(self, *args):
        
        cd = rexprojectspacenotificationcenter.CommitDispatcher.dispatcherForProject("naali")
        
        commit = {}
        commit["message"] = "test commit from region module with very long description, or is this long enough???"
        
        commit["authored_date"] = "2010-07-23T09:54:40-07:00"
        
        commit["Removed"] = ["doc","bin"]
        commit["added"] = []
        commit["modified"] = []
        
        ci = rexprojectspacedataobjects.CommitInfo("antont",commit,"antont")
        print "hakemistot: ", ci.directories
        commits = [ci]
        
        cd.dispatchCommits( commits )
    
    def cmd_commit2(self, *args):
        
        cd = rexprojectspacenotificationcenter.CommitDispatcher.dispatcherForProject("naali")
        
        commit = {}
        commit["message"] = "test commit from region module"
        
        commit["authored_date"] = "2010-07-24T09:54:40-07:00"
        
        commit["Removed"] = ["Foundation"]
        commit["added"] = []
        commit["modified"] = []
        
        ci = rexprojectspacedataobjects.CommitInfo("antont",commit,"antont")
        print "hakemistot: ", ci.directories
        commits = [ci]
        self.project.updateDeveloperLocationWithNewCommitData(ci)
        
    def cmd_blame(self, *args):
        
        t = time.time() #Epoch time, set the new commit after this moment of time
        self.project.lastBuildTime = time.gmtime(t)
        
        commit = {}
        commit["message"] = "test commit from region module"
        
        commit["authored_date"] = "2010-07-31T09:54:40-07:00"
        
        commit["removed"] = ["bin"]
        commit["added"] = ["doc"]
        commit["modified"] = []
        
        ci = rexprojectspacedataobjects.CommitInfo("antont",commit,"antont")

        #locate antont
        dev =  None
        
        for d in self.project.developers:
            if d.developerinfo.login == "antont":
                dev = d
                break
                
        if dev == None:
            return
        
        
        dev.developerinfo.latestcommit = ci
        
        t = time.time() #Epoch time
        ti = time.gmtime(t)
        
        binfo = rexprojectspacedataobjects.BuildInfo("",False,ti)
        
        self.project.buildFinished([binfo])
        
    def cmd_commit_new_dev(self, *args):
        
        cd = rexprojectspacenotificationcenter.CommitDispatcher.dispatcherForProject("naali")
        
        commit = {}
        commit["message"] = "test commit from region module"
        
        commit["authored_date"] = "2010-07-23T09:54:40-07:00"
        
        commit["Removed"] = ["doc","bin"]
        commit["added"] = []
        commit["modified"] = []
        
        generated_name = str(random.randint(0,1000000))
        
        ci = rexprojectspacedataobjects.CommitInfo(generated_name,commit,generated_name)
        
        cd.dispatchCommits( [ci] )
    
    def cmd_commit_new_comp(self, *args):
        
        cd = rexprojectspacenotificationcenter.CommitDispatcher.dispatcherForProject("naali")
        
        commit = {}
        commit["message"] = "test commit from region module"
        
        commit["authored_date"] = "2010-07-23T09:54:40-07:00"
        
        generated_name = str(random.randint(0,1000000))
        
        commit["Removed"] = [generated_name]
        commit["added"] = []
        commit["modified"] = []
        
        generated_name = str(random.randint(0,1000000))
        
        ci = rexprojectspacedataobjects.CommitInfo(generated_name,commit,generated_name)
        
        cd.dispatchCommits( [ci] )
    
    def cmd_create_bug(self, *args):

        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Defect"
        issueData.owner = "maukka user"
        issueData.status = "new"
        issueData.id = str(random.randint(0,1000000))
        issueData.url = "http://code.google.com/p/realxtend-naali/issues/detail?=9"
        bug =  self.issuefactory.CreateIssue(issueData)
        self.bugid = issueData.id
        
        bug.start()
        
    def cmd_create_en(self, *args):
        
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Enhancement"
        issueData.owner = "maukka user"
        issueData.status = "new"
        issueData.id = str(random.randint(0,1000000))
        issueData.url = "http://code.google.com/p/realxtend-naali/issues/detail?=24"
        bug =  self.issuefactory.CreateIssue(issueData)
        self.bugid = issueData.id
        
        bug.start()
        
    def cmd_change_bug_data(self, *args):
        #resolve latest bug/issue
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Enhancement"
        issueData.owner = "maukka user"
        issueData.status = "started"
        issueData.id = self.bugid
        
        self.issuefactory.UpdateIssue(issueData)
        
    
    def cmd_developer(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("ma2sfddass2","maukka user")
        
        commit = {}
        commit["message"] = "test commit from region \n module with very long description \n, or is this long enough???"
        
        commit["authored_date"] = "2010-07-23T09:54:40-07:00"
        
        commit["Removed"] = ["doc","bin"]
        commit["added"] = []
        commit["modified"] = []
        
        ci = rexprojectspacedataobjects.CommitInfo("maukka_tester",commit,"maukka_tester")
        dinfo.latestcommit = ci
        
        self.dev = swdeveloper.SWDeveloper(self.scene,dinfo,False)
        
        
    def cmd_project(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("maukka","maukka user")
        self.dev = swdeveloper.SWDeveloper(self.scene,dinfo,False)
    
        self.testproject = swproject.SWProject(self.scene,"test_project",[],[self.dev])
