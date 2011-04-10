import naali
V3 = naali.Vector3df
import circuits

import math
import sys, os, sha
import threading

import swsourcetree
import buildbot
import issuetracker

import swproject
import swdeveloper
import swissue

import versioncontrolsystem

import rexprojectspacedataobjects
import rexprojectspacenotificationcenter

import time
import datetime
import random

class RexProjectSpaceInformationShouter:
    """
    Shouts information to the region so that all avatars can see it.
    Currently only IRC messages are shouted...
    """

    def __init__(self, vScene):
        """ Register to listen to new IRC messages """
        self.scene = vScene
        self.scriptingbridge = None

        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        #nc.OnNewIrcMessage += self.OnNewIRCMessage
        #nc.OnNewCommit += self.OnNewCommit

    def OnNewCommit(self, vCommit):
        pass #self.scriptingbridge.Actor().llShout(0, vCommit.message)

    def OnNewIRCMessage(self, vMessage):
        """ Shout message """
        #actor.llSetObjectName("irc-bot")
        #actor.llShout(0, vMessage)
        pass

class RexProjectSpace(circuits.BaseComponent):
    def __init__(self):
        circuits.BaseComponent.__init__(self)
        self.scene = None
        naali.scene.connect("SceneAdded(QString)", self.Initialise)

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
            folderinfos.append(rexprojectspacedataobjects.FolderInfo(folder, count))

        return folderinfos


    def Initialise(self, scenename):
        """ Create IssueFactory, SWTree and SWProject """

        self.removed = False
        self.scene = naali.getScene(scenename)
        # self.config = configsource

        self.developers = []

        self.vcs = versioncontrolsystem.VersionControlSystem("naali")

        projectpos = V3(131, 130, 25.2)
        issuespawnpos = V3(125, 125, 25.2)

        self.tree = self.initTree("naali")

        self.project = self.initSWProject()

        # temp = self.project.sog.AbsolutePosition
        projectpos = V3() #temp.X, temp.Y, temp.Z + 0.75)
        startpos = V3() #projectpos.X, projectpos.Y, projectpos.Z),
        endpos = V3() #projectpos.X + 9.5, projectpos.Y + 9.5, projectpos.Z + 3)
        self.issuefactory = swissue.IssueFactory(self.scene, 
                                                 startpos, endpos,
                                                 issuespawnpos)
        self.initSWIssues()

        #self.shouter = RexProjectSpaceInformationShouter(self.scene)

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
        """ Create issue objects by using issuefactory. Also initialize 
            issuedispatcher with the received data, so that dispatcher
            is able to know if issue is new...
        """

        self.issuetracker = issuetracker.IssueTracker()
        issues = self.issuetracker.GetIssues()
        issuesdict = {}
        for i in issues:
            issue = self.issuefactory.CreateIssue(i)
            issuesdict[i.id] = i

        issuedispatcher = rexprojectspacenotificationcenter.IssueDispatcher.dispatcher()
        issuedispatcher.issues = issuesdict

    def initTree(self, vProjectName):
        """ Get branches and create tree """
        branches = self.vcs.GetBranches()
        #branches = []
        tree = swsourcetree.SWSourceTree(self.scene, vProjectName, branches)
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
        print "number of devs", count
        temp = count

        #create developerinfo for every dev..
        devs = []
        for dev in committers:
            dinfo = rexprojectspacedataobjects.DeveloperInfo(dev["login"], "")
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

        #get previous 1000 commits 
        coms = self.vcs.GetCommitsFromNetworkData(1000)

        coms.reverse()#oldest first, so reverse!

        #just to make things more easier. Make notification center to notify only
        #new commits...
        commitdispatcher = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")
        commitdispatcher.latestcommit = coms[0]["id"]

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
                            #print "commit found for: ",dev.login
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
                dev.latestcommit = rexprojectspacedataobjects.CommitInfo(dev.login, empty)
                pass
            else:
                ci = self.vcs.GetCommitInformation(dev.latestcommitid)
                #print "commit id %s for dev:%s "%(dev.latestcommitid,dev.login)

                c = ci["commit"]

                devCommit = rexprojectspacedataobjects.CommitInfo(dev.login, c)
                dev.latestcommit = devCommit
                #print "---hakemistot commitissa: ", devCommit.directories

            #init every developer so that each has latest commits, commit count and names in place
            swdevs.append(swdeveloper.SWDeveloper(self.scene, dev, False))
            print "Developer's name-----%s and login:-------%s" % ( dev.name, dev.login )

        #get all the components...
        componentNames = self.getProjectRootFolders()

        project = swproject.SWProject(self.scene, "naali", componentNames, swdevs)

        return project

    def setUpTests(self):
        def addCommand(*args):
            pass

        addCommand(self, "hitMe", "", "", self.cmd_hitMe)
        addCommand(self, "organize", "", "", self.cmd_organize)

        #testing component grid
        addCommand(self, "ac", "", "", self.cmd_ac)
        addCommand(self, "modcom", "", "", self.cmd_modify)
        addCommand(self, "remcom", "", "", self.cmd_remove)
        addCommand(self, "addcom", "", "", self.cmd_add)


        #testing builds
        addCommand(self, "bf", "", "", self.cmd_bf)
        addCommand(self, "bs", "", "", self.cmd_bs)

        #testing commits
        addCommand(self, "commit", "", "", self.cmd_commit)
        addCommand(self, "commit2", "", "", self.cmd_commit2)
        addCommand(self, "blame", "", "", self.cmd_blame)#commit and fail build
        addCommand(self, "fix_blame", "", "", self.cmd_fix_blame)#commit and fail build
        addCommand(self, "commit_new_dev", "", "", self.cmd_commit_new_dev)#commit done by new dev
        addCommand(self, "commit_new_comp", "", "", self.cmd_commit_new_comp)#commit done by new dev


        #testing branches
        addCommand(self, "cb", "", "", self.cmd_cb)

        #testing issues
        addCommand(self, "bug", "", "", self.cmd_create_bug)
        addCommand(self, "enhan", "", "", self.cmd_create_en)
        addCommand(self, "changebugdata", "", "", self.cmd_change_bug_data)


        #testing developers
        addCommand(self, "developer", "", "", self.cmd_developer)

        #testing project
        addCommand(self, "project", "", "", self.cmd_project)

    def createBall(self):
        sphereRadius = 1
        sphereHeigth = 1

        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateSphere()
        pbs.SetRadius(sphereRadius)
        pbs.SetHeigth(sphereHeigth)
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
            OpenMetaverse.UUID.Random(), V3(127, 130, 26), pbs)

        texcolor = OpenMetaverse.Color4(1, 0, 0, 1)
        tex = sog.RootPart.Shape.Textures
        tex.DefaultTexture.RGBA = texcolor
        sog.RootPart.UpdateTexture(tex)
        self.scene.AddNewSceneObject(sog, False)
        sog.SetText("pallo", V3(1.0, 1.0, 0.0), 1.0)
        return sog


    def cmd_hitMe(self, *args):
        #fi = rexprojectspacedataobjects.FolderInfo("LongName4",20)
        #self.comp = swproject.Component(self.scene,fi,V3(125,125,27),None)

        import OpenMetaverse.Imaging.OpenJPEG

        import System.Drawing.Bitmap
        import System.Drawing.Color
        import System.Drawing.Graphics

        width, height = 256, 256

        bitmap = System.Drawing.Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format32bppRgb)

        graph = System.Drawing.Graphics.FromImage(bitmap);

        color = System.Drawing.SolidBrush(System.Drawing.Color.Yellow)
        graph.FillRectangle(color, 0, 0, width, height)

        myFont = System.Drawing.Font("Courier", 25, System.Drawing.FontStyle.Bold)
        myBrush = System.Drawing.SolidBrush(System.Drawing.Color.Black)
        startPoint = System.Drawing.Point(10, 10)

        layoutrect = System.Drawing.RectangleF(0, 10, 256, 45)

        #graph.DrawString("Hello world", myFont, myBrush, startPoint)
        graph.DrawString("InventoryModule", myFont, myBrush, layoutrect)

        bitmap.Save("kokeilutekstuuri.bmp")

        sog, rop = rexprojectspaceutils.load_mesh(self.scene, "rpsmeshes/component.mesh", "rpsmeshes/component.material"
                                                  , "comp")

        imageJ2000 = OpenMetaverse.Imaging.OpenJPEG.EncodeFromImage(bitmap, True);

        tex = rexprojectspaceutils.StoreBytesAsTexture(self.scene, imageJ2000)

        #return tex

        rop.RexMaterials.AddMaterial(0, OpenMetaverse.UUID(tex))


    def cmd_organize(self, *args):
        newpositions = []
        pos = V3(131, 130, 25.2)

        count = 0

        for bug in self.bugs:
            newposition = V3(pos.x(), pos.y(), pos.z() + count * 0.3)
            bug.sog.NonPhysicalGrabMovement(newposition)
            count += 1

    def clicked(self, vLocalID, vOriginalID, vOffsetPos, vRemoteClient, vSurfaceArgs):
        if vLocalID == self.testcomponent.sog.RootPart.LocalId:
            #actor = 
            print "hello"

    def cmd_ac(self, *args):
        #self.testcomponent = self.project.components.values[0]

        folderinfo = rexprojectspacedataobjects.FolderInfo("bin", 10)

        self.testcomponent = swproject.Component(self.scene, folderinfo, V3(126, 126, 25.5), None, 2, 2, V3(1, 1, 1))


    def cmd_remove(self, *args):
        self.testcomponent.SetState("removed")

    def cmd_modify(self, *args):
        self.testcomponent.SetState("modified")

    def cmd_add(self, *args):
        self.testcomponent.SetState("added")

    def cmd_cb(self, *args):
        name = "test branch" + str(random.randint(0, 1000000))
        binfo = rexprojectspacedataobjects.BranchInfo(name)
        binfo.url = "http://github.com/realxtend/naali/tree/master"
        self.tree.addNewBranches([binfo])

    def cmd_bs(self, *args):
        self.tree.setBuildSuccesfull()

    def cmd_bf(self, *args):
        self.tree.setBuildFailed()

    def cmd_commit(self, *args):
        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")

        commit = {}
        commit["message"] = "Test commit from region module, changed files from Core, tools and doc "

        commit["authored_date"] = "2010-09-23T09:54:40-07:00"
        commit["id"] = random.randint(0, 1000000)

        commit["Removed"] = []
        commit["added"] = ["doc/a.txt", "tools/b.cpp", "Core/b.cpp"]
        commit["modified"] = []

        ci = rexprojectspacedataobjects.CommitInfo("antont", commit, "antont")
        print "hakemistot: ", ci.directories
        commits = [ci]

        cd.dispatchCommits(commits)

    def cmd_commit2(self, *args):
        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")

        commit = {}
        commit["message"] = "test commit from region module , and again with a long test string...----...---..---"

        commit["authored_date"] = "2010-09-24T09:54:40-07:00"

        commit["Removed"] = ["Foundation/file2.h"]
        commit["added"] = []
        commit["modified"] = []
        commit["id"] = random.randint(0, 1000000)

        ci = rexprojectspacedataobjects.CommitInfo("antont", commit, "antont")
        print "hakemistot: ", ci.directories
        commits = [ci]
        self.project.updateDeveloperLocationWithNewCommitData(ci)

    def cmd_blame(self, *args):
        t = time.time() #Epoch time, set the new commit after this moment of time
        self.project.lastBuildTime = time.gmtime(t)

        commit = {}
        commit["message"] = "test commit from region module"

        commit["authored_date"] = "2010-09-18T09:54:40-07:00"

        commit["removed"] = ["WorldMapModule/j.j2k"]
        commit["added"] = ["WorldMapModule/help.txt"]
        commit["modified"] = []
        commit["id"] = random.randint(0, 1000000)

        ci = rexprojectspacedataobjects.CommitInfo("antont", commit, "antont")

        #locate antont
        dev = None

        for d in self.project.developers:
            if d.developerinfo.login == "antont":
                dev = d
                break

        if dev == None:
            return

        dev.developerinfo.latestcommit = ci

        print "Muutos: ", dev.developerinfo.latestcommit.date

        t = time.time() #Epoch time
        ti = time.gmtime(t)

        binfo = rexprojectspacedataobjects.BuildInfo("", "failure", ti)

        t = time.time() #Epoch time
        ti = time.gmtime(t - 1000)

        binfo_old = rexprojectspacedataobjects.BuildInfo("", "success", ti)

        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")
        commits = [ci]
        cd.dispatchCommits(commits)

        bd = rexprojectspacenotificationcenter.BuildResultDispatcher.dispatcher()
        bd.dispatchBuildResults([binfo, binfo_old])
        #self.project.buildFinished([binfo,binfo_old])

    def cmd_fix_blame(self, *args):
        t = time.time() #Epoch time, set the new commit after this moment of time
        self.project.lastBuildTime = time.gmtime(t)

        commit = {}
        commit["message"] = "test commit from region module"

        commit["authored_date"] = "2010-09-18T09:54:40-07:00"

        commit["removed"] = ["WorldMapModule/j.j2k"]
        commit["added"] = ["WorldMapModule/help.txt"]
        commit["modified"] = []
        commit["id"] = random.randint(0, 1000000)

        ci = rexprojectspacedataobjects.CommitInfo("antont", commit, "antont")

        #locate antont
        dev = None

        for d in self.project.developers:
            if d.developerinfo.login == "antont":
                dev = d
                break

        if dev == None:
            return

        dev.developerinfo.latestcommit = ci

        t = time.time() #Epoch time
        ti = time.gmtime(t)

        binfo = rexprojectspacedataobjects.BuildInfo("", "success", ti)

        t = time.time() #Epoch time
        ti = time.gmtime(t - 1000)

        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")
        commits = [ci]
        cd.dispatchCommits(commits)

        binfo_old = rexprojectspacedataobjects.BuildInfo("", "failure", ti)

        bd = rexprojectspacenotificationcenter.BuildResultDispatcher.dispatcher()
        bd.dispatchBuildResults([binfo, binfo_old])

        self.project.buildFinished([binfo, binfo_old])

    def cmd_commit_new_dev(self, *args):
        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")

        commit = {}
        commit["message"] = "test commit from region module"

        commit["authored_date"] = "2010-09-23T09:54:40-07:00"

        commit["Removed"] = ["doc/file5.h", "bin/helpme.txt"]
        commit["added"] = ["doc"]
        commit["modified"] = []
        commit["id"] = random.randint(0, 1000000)

        generated_name = str(random.randint(0, 1000000))

        ci = rexprojectspacedataobjects.CommitInfo(generated_name, commit, generated_name)

        print "hakemistot: ", ci.directories

        cd.dispatchCommits([ci])

    def cmd_commit_new_comp(self, *args):
        cd = rexprojectspacenotificationcenter.VersionControlDataDispatcher.dispatcherForProject("naali")

        commit = {}
        commit["message"] = "test commit from region module"

        commit["authored_date"] = "2010-09-23T09:54:40-07:00"

        generated_name = str(random.randint(0, 1000000))

        commit["Removed"] = []
        commit["added"] = [generated_name]
        commit["modified"] = []
        commit["id"] = random.randint(0, 1000000)

        generated_name = str(random.randint(0, 1000000))

        ci = rexprojectspacedataobjects.CommitInfo(generated_name, commit, generated_name)

        cd.dispatchCommits([ci])

    def cmd_create_bug(self, *args):
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Defect"
        issueData.owner = "maukka user"
        issueData.status = "New"
        issueData.id = str(random.randint(0, 1000000))
        issueData.url = "http://code.google.com/p/realxtend-naali/issues/detail?=9"
        bug = self.issuefactory.CreateIssue(issueData)
        self.bugid = issueData.id

        bug.start()

    def cmd_create_en(self, *args):
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Enhancement"
        issueData.owner = "maukka user"
        issueData.status = "New"
        issueData.id = str(random.randint(0, 1000000))
        issueData.url = "http://code.google.com/p/realxtend-naali/issues/detail?=24"
        bug = self.issuefactory.CreateIssue(issueData)
        self.bugid = issueData.id

        bug.start()

    def cmd_change_bug_data(self, *args):
        #resolve latest bug/issue
        empty = []
        issueData = rexprojectspacedataobjects.IssueInfo(empty)
        issueData.type = "Enhancement"
        issueData.owner = "maukka user"
        issueData.status = "Started"
        issueData.id = self.bugid

        self.issuefactory.UpdateIssue(issueData)


    def cmd_developer(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("MaukkaS", "maukka user")

        commit = {}
        commit["message"] = "test commit from region \n module with very long description \n, or is this long enough???"

        commit["authored_date"] = "2010-07-23T09:54:40-07:00"

        commit["Removed"] = ["doc", "bin"]
        commit["added"] = []
        commit["modified"] = []

        ci = rexprojectspacedataobjects.CommitInfo("MaukkaS", commit, "MaukkaS")
        dinfo.latestcommit = ci

        self.dev = swdeveloper.SWDeveloper(self.scene, dinfo, False)


    def cmd_project(self, *args):
        dinfo = rexprojectspacedataobjects.DeveloperInfo("maukka", "maukka user")
        self.dev = swdeveloper.SWDeveloper(self.scene, dinfo, False)

        self.testproject = swproject.SWProject(self.scene, "test_project", [], [self.dev])

if __name__ == '__main__':
    import mock
    scene = mock.Mock()

    m = RexProjectSpace()    
    m.Initialise(scene)
    m.PostInitialise()
