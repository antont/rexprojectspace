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

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

import rexprojectspaceutils

import rexprojectspacenotificationcenter
import rexprojectspacedataobjects

import swdeveloper

import rexprojectspacemodule

import clickhandler

class ComponentBase(object):
    """ Base class for composite objects """
    def __init__(self):
        pass
    
    def SetState(self,vState):
        """ Override this """
        pass
    
    def AddChild(self,vComponentBase):
        """ Composites has to implement this """
        pass
    
    def RemoveChild(self,vComponentBase):
        """ Composites has to implement this """
        pass
        

        
class File(ComponentBase):
    """ Representing a single file, can't have children. Not implemented yet..."""
    def __init__(self):
        pass
    
    def SetState(self,vState):
        """ Not implemented """
        pass
    
class Component(ComponentBase):
    """ Representing a single directory, can have children."""
        
    offset = 0.5
    
    modifiedtextureid = None
    removedtextureid = None
    addedtextureid = None
    MESHUUID = OpenMetaverse.UUID.Zero 
    
    def __init__(self,vScene,vFolderInfo,vPos,vParent,vX=1,vY=1,vScale = V3(0,0,0)):
        """ Load mesh and texture and set state as added
        """
        super(Component,self).__init__()
        
        self.name = vFolderInfo.name
        self.folderinfo = vFolderInfo
        
        self.__x = vX
        self.__y = vY
        
        self.curRow = 0
        self.curColumn = 0
        
        self.__offset = [] #offsets in x,y dimension
        self.currentIndex = 0  
        self.scene = vScene
        self.pos = vPos
        self.scale = vScale
        self.color = 0 #blue
        
        if not Component.modifiedtextureid:
            print "loading  textures"
            Component.modifiedtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/modifiedcomponent.jp2")
            Component.removedtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/removedcomponent.jp2")
            Component.addedtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/addedcomponent.jp2")
        
        sop =  vScene.GetSceneObjectPart("rps_component_" + self.name)
        self.currenttexid = Component.addedtextureid
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
             #print "Component: %s found from scene"%("rps_component_" + self.name)
        else:
            #self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos,self.scale)
            if Component.MESHUUID == OpenMetaverse.UUID.Zero:
                print "loading component mesh"
                Component.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"component.mesh","component mesh")
                
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,Component.MESHUUID,"component.material",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos,self.scale)
            
            self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
            #self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"diamond.mesh","diamond.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos,self.scale)
            
            self.sog.RootPart.Scale = V3(vX,vY,1)
            self.sog.RootPart.Name =  "rps_component_" + self.name
            
            self.scene.AddNewSceneObject(self.sog, False)

        #print "mesh id for component: ", self.rop.RexMeshUUID
        self.sog.SetText(self.name,V3(1.0,1.0,0.0),1.0)

        self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.folderinfo.url)
        
        self.modified = False
        
    def AddChild(self,vFolderInfo):

        temp = self.sog.AbsolutePosition
        p = V3(self.curColumn + temp.X + self.curColumn*Component.offset,
               self.curRow + temp.Y + self.curRow*Component.offset,
               temp.Z + 0.5)
               
        child =  Component(self.scene, vFolderInfo, p, self, 1,1,V3(0.85,0.85,0.85))
        
        #child.sog.RootPart.Scale = V3(0.85,0.85,1)
        
        if self.curColumn < self.__x - 1: 
            self.curColumn += 1
        else:
            self.curColumn = 0
            self.curRow += 1
            
        return child
            
    def SetState(self,vState):
        """ Changes texture if needed. vState can be modified,removed or added """
        print "component: ",self.name, "is at state: ",vState
        tex = self.currenttexid
        if vState == "modified":
            tex = Component.modifiedtextureid
        elif vState == "removed" or vState == "Removed":
            tex = Component.removedtextureid
        elif vState == "added":
            tex = Component.addedtextureid
        
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        self.currenttexid = tex

class SWProject:
    """ Controller class for software projects that knows of it's developers,
        components and compilation results of the source code. """
        
    def __init__(self, vScene,vProjectName, vComponents, vDevelopers):
        """ Create projects components and resolve latest developer
            and update components and developers visualizations respectively
        """
        
        self.scene = vScene
        self.projectName = vProjectName
        
        self.components = {}
        self.developers = vDevelopers
        
        #map developers to the components, so that project knows where developers
        #are
        self.componentsAndDevelopersDict = {}
        
        #will contain developers that could have caused a build break
        self.blameList = []
        
        self.lastBuildTime = 0
        self.bLatestBuildFailed  = False
        
        self.latestcommitter = None
        #print "-----------------",self.developers[0].developerinfo.login
        
        if len(self.developers) > 0:
            self.latestcommitter = self.developers[0]
            self.latestcommitter = self.resolveLatestCommitter()
            self.latestcommitter.updateIsLatestCommitter(True)
        
        #create first component representing self
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("41cb4157-80e1-45d4-b2a1-fb1ea3f9c303")
        
        
        
        if not self.scene.GetSceneObjectPart("first_component"):
            print "No first sw component..."
            return
        
        self.sog = self.scene.GetSceneObjectPart("first_component").ParentGroup
        self.rop = rexObjects.GetObject(self.sog.UUID)
        
        
        #if not self.scene.GetSceneObjectPart(self.UUID):
        #    print "No first sw component..."
        #    return
            
        #self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        #self.rop = rexObjects.GetObject(self.UUID)
        
        rootfolder = rexprojectspacedataobjects.FolderInfo("naali_root_component",0)
        
        self.component = Component(vScene, rootfolder, self.sog.AbsolutePosition, None, 6,6,V3(0,0,0))
        self.component.sog.RootPart.Scale = V3(0,0,0)
        
        self.componentsAndDevelopersDict["naali_root_component"] = []
        
        for component in vComponents:
            self.addComponent(component)
            
        #place developers to their initial positions...
        for dev in self.developers:
            latestcommit = dev.developerinfo.latestcommit
            if latestcommit != None or latestcommit != "":
                #print latestcommit 
                self.updateDeveloperLocationWithNewCommitData(latestcommit,False)
        
        self.visualizeLatestCommitModifications()
        
        #get all commits
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnNewCommit += self.updateDeveloperLocationWithNewCommitData
        
        nc.OnBuild += self.buildFinished
        
    def __del__(self):
        """ """
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnNewCommit -= self.updateDeveloperLocationWithNewCommitData
    
    def visualizeLatestCommitModifications(self):
        """ Update components that are modified by latest commit """
        if self.latestcommitter:
            
            #unset previous modified
            for component in self.components.values():
                component.SetState("added")#return to default
                
            #change every components color that was mod,added or removed
            #within a latest commit
            for item in self.latestcommitter.developerinfo.latestcommit.directories:
                #locate component
                print item
                component = self.components[item]
                #perhaps one day we might tell component/file if
                #it was removed,added or modified, but now we have
                #only root level folders...
                component.SetState("modified")
    
    def resolveLatestCommitter(self):
        """ """
        devs = self.sortDevelopers(self.developers)
        latestcommmitter = devs[len(devs)-1]
        return latestcommmitter
    
    def addComponent(self, vComponent):
        """ Adds component to the project root folder """
        self.componentsAndDevelopersDict[vComponent.name] = []
        c = self.component.AddChild(vComponent)
        
        self.components[vComponent.name] = c
        #visualize components "size" and modified date
        """
        tempscale = c.sog.RootPart.Scale
        scale = max(0.4,vComponent.numberofsubfiles/25)
        scale = min(scale,1)
        c.sog.RootPart.Scale = V3(scale,scale,tempscale.Z)
        """
        return c

    def updateDeveloperLocationWithNewCommitData(self, vCommit, vMakeCurrent = True):
        """ Position developer on top of component that was modified by the 
            developer. If component was new, then create a new component."""
        #locate developer
        committer = None
        for dev in self.developers:
            if dev.developerinfo.login == vCommit.login or dev.developerinfo.name == vCommit.name:
                committer = dev
                break
        
        #we know nothing about this developer
        if committer == None:
            print "no committer with login:%s and name:%s, must be a new developer.(message:%s) "%(vCommit.login,vCommit.name,vCommit.message)
            
            developerinfo = rexprojectspacedataobjects.DeveloperInfo(vCommit.login,vCommit.name)
            developerinfo.latestcommit = vCommit
            committer = swdeveloper.SWDeveloper(0,self.scene,developerinfo,False)
            
        #there is no way to know for sure if the commit has been set to dev
        #before this, so set it...
        committer.developerinfo.latestcommit = vCommit
        
        #locate correct component 
        component = None
        
        if len(vCommit.directories) > 0:
            
            print "commit directory: ",vCommit.directories[0]
            
            try:
                component = self.components[vCommit.directories[0]]
            except:
                print "No component named:%s  , must be a new component"%(vCommit.directories[0])
                folder = rexprojectspacedataobjects.FolderInfo(vCommit.directories[0],0)#new directory
                component = self.addComponent(folder)
                
            #remove developer from previous componenent, k is component name and c lists developers to
            #component named k... 
            for k,c in self.componentsAndDevelopersDict.iteritems():
                if c.count(committer)>0:
                    c.remove(committer)
                    #devs = c
                    previouscomponentsdevs = c
                    
                    #rearrange devs
                    h = 0
                    for j in range(len(previouscomponentsdevs)):
                        print "removed dev"
                        dev = previouscomponentsdevs[j]
                        h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
                        h += 0.2
                        
                        comp = self.components[k]#get component instance from dict
                        
                        pos = comp.sog.AbsolutePosition
                        devPos = V3(pos.X,pos.Y,pos.Z + h)
                        dev = previouscomponentsdevs[j]
                        dev.move(devPos)
                        
                    print "developer: ", committer , "removed from ", self.components[k].name
                    break #developer can be only in one component at the same time
        else:
            component = self.component #no directories, so put dev into "container component"
        
        devs = self.componentsAndDevelopersDict[component.name]
        devs.append(committer)
            
        devs = self.sortDevelopers(devs)
        #for d in devs:
        #    print d.latestcommit.date
        
        h = 0
        for j in range(len(devs)):
            dev = devs[j]
            pos = component.sog.AbsolutePosition
            devPos = V3(pos.X,pos.Y,pos.Z + h)
            
            dev.move(devPos)
            
            h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
            h += 0.2
        
        #finally set latest committer if wanted
        if vMakeCurrent == True:
            
            self.latestcommitter.updateIsLatestCommitter(False)
            
            self.latestcommitter = committer
            
            #so, these commits are processed at runtime, not at initializing phase
            #update also the developervisualization
            self.latestcommitter.developerinfo.commitcount += 1
            self.latestcommitter.developerinfo.latestcommit = vCommit
            self.latestcommitter.developerinfo.latestcommitid = vCommit.id

            self.latestcommitter.updateVisualization()
            
            #print "developer %s is current committer"%(self.latestcommitter.developerinfo.login)
            self.latestcommitter.updateIsLatestCommitter(True)
            
            self.visualizeLatestCommitModifications()
            print "new test..."
            
    from operator import itemgetter,attrgetter
    def sortDevelopers(self,vDevelopers):
        """ sort developers based on their commit date, so that newest is at the top
        """
        vDevelopers.sort(self.compareCommitDates)
        #for d in vDevelopers:
        #    print d.developerinfo.login ," committed on : ",d.developerinfo.latestcommit.date
        return vDevelopers
    
    def compareCommitDates(self,x,y):
        return cmp(x.developerinfo.latestcommit.date,y.developerinfo.latestcommit.date)
 
    def buildFinished(self,vBuilds):
        """ Handle build notifications by creating a blame list containing
            developers that might have broken the build. """
        bResult = True
        
        if len(vBuilds) < 1:
            return
        
        build = vBuilds[0]
        
        if build.result != "success":
            bResult = False
            
        if bResult == False:
            if self.bLatestBuildFailed == True:
                #don't update blamelist, because build was allready failing...
                return
            else:
                bLatestBuildFailed = True
                latestSuccess = vBuilds[1]
                 
                #make blamelist
                for d in self.developers:
                    if d.developerinfo.latestcommit.date > latestSuccess.time:
                        print "dev added to blamelist: ", d.developerinfo.login
                        self.blameList.append(d)
                        
                self.visualizeBlameListMembers()
        else:
            self.bLatestBuildFailed = False
            self.unsetBlameListMemberVisualizations()
            self.blameList = []
            
        self.lastBuildTime = build.time
       
    def visualizeBlameListMembers(self):
        """ Tell developers that they might have broken the build """
        for d in self.blameList:
            d.updateDidBrakeBuild(True)
    
    def unsetBlameListMemberVisualizations(self):
        """ Tell developers that the build is ok. """
        for d in self.blameList:
            d.updateDidBrakeBuild(False)
 