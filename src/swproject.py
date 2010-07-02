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

class Component:
    offset = 1.0
    
    def __init__(self,vScene,vName,vPos,vParent,vX=1,vY=1,vScale = V3(0,0,0)):
        
        self.name = vName
        
        self.__x = vX
        self.__y = vY
        
        self.curRow = 0
        self.curColumn = 0
        
        self.__offset = [] #offsets in x,y dimension
        self.currentIndex = 0  
        self.scene = vScene
        self.pos = vPos
        self.scale = vScale
        
        sop =  vScene.GetSceneObjectPart("rps_component_" + self.name)
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Component: %s found from scene"%("rps_component_" + self.name)
        else:    
            self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos,self.scale)
            #self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos,self.scale)
            
            self.sog.RootPart.Scale = V3(vX,vY,1)
            self.sog.RootPart.Name =  "rps_component_" + self.name
            
            self.scene.AddNewSceneObject(self.sog, False)
        
        #print "mesh id for component: ", self.rop.RexMeshUUID
        self.sog.SetText(self.name,V3(1.0,1.0,0.0),1.0)
        
    def addChild(self,vComponentName):

        temp = self.sog.AbsolutePosition
        p = V3(self.curColumn + temp.X + self.curColumn*Component.offset,
               self.curRow + temp.Y + self.curRow*Component.offset,
               temp.Z + 0.5)
               
        child =  Component(self.scene, vComponentName, p, self, 1,1,V3(0.85,0.85,0.85))
        
        #child.sog.RootPart.Scale = V3(0.85,0.85,1)
        
        if self.curColumn < self.__x - 1: 
            self.curColumn += 1
        else:
            self.curColumn = 0
            self.curRow += 1
            
        return child
        
    
class SWProject:

    def __init__(self, vScene,vProjectName, vComponents, vDevelopers):
        self.scene = vScene
        self.projectName = vProjectName
        
        self.components = {}
        self.developers = vDevelopers
        
        #map developers to the components, so that project knows where developers
        #are
        self.componentsAndDevelopersDict = {}
        
        
        self.latestcommitter = None
        #print "-----------------",self.developers[0].developerinfo.login
        
        if len(self.developers) > 0:
            self.latestcommitter = self.developers[0]            
            self.latestcommitter = self.resolveLatestCommitter()
            print "-----------------",self.latestcommitter.developerinfo.login
        
        #create first component representing self
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("df53f4d4-1bb8-43b0-8590-41482fd5a49a")
        
        if not self.scene.GetSceneObjectPart(self.UUID):
            print "No first sw component..."
            return
            
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        
        self.component = Component(vScene, "naali_root_component" , self.sog.AbsolutePosition, None, 6,6,V3(0,0,0))
        self.component.sog.RootPart.Scale = V3(0,0,0)
        
        self.componentsAndDevelopersDict["naali_root_component"] = [self.component]
        
        for componentname in vComponents:
            self.componentsAndDevelopersDict[componentname] = []
            self.addComponent(componentname)
        
        ##print self.components
        
        #place developers to their initial positions...
        for dev in self.developers:
            latestcommit = dev.developerinfo.latestcommit
            if latestcommit != None or latestcommit != "":
                #print latestcommit 
                self.updateDeveloperLocationWithNewCommitData(latestcommit)
        
        #get all commits
        #commitdispatcher.CommitDispatcher.register(self.updateDeveloperLocationWithNewCommitData,self.projectName ,"")
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnNewCommit += self.updateDeveloperLocationWithNewCommitData
        
        #versioncontroldatadispatcher.VersionControlDataDispatcher.dispatcherForProject(self.projectName)
        
    def __del__(self):
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnNewCommit -= self.updateDeveloperLocationWithNewCommitData
        
    def resolveLatestCommitter(self):
        
        for dev in self.developers:
            if dev.developerinfo.latestcommit:
                if dev.developerinfo.latestcommit.date > self.latestcommitter.developerinfo.latestcommit.date:
                    print dev.developerinfo.latestcommit.date
                    self.latestcommitter = dev
                    
        return self.latestcommitter
    
    def addComponent(self, vComponentName):
        self.components[vComponentName] = self.component.addChild(vComponentName)
        self.components[vComponentName].sog.RootPart.Name =  vComponentName
        return self.components[vComponentName]
        
    
    def updateDeveloperLocationWithNewCommitData(self, vCommit):
        
        #locate developer
        committer = None
        for dev in self.developers:
            if dev.developerinfo.login == vCommit.login or dev.developerinfo.name == vCommit.name:
                committer = dev
                
                #unset anim or other visualization for prev latest committer
                #self.latestcommitter
                
                #set the dev as latest commmitter and visualize it
                #committer
                break
        
        #we know nothing about this developer
        if committer == None:
            print "no committer with login:%s and name:%s, must be a new developer.(message:%s) "%(vCommit.login,vCommit.name,vCommit.message)
            """
            developerinfo = rexprojectspacedataobjects.DeveloperInfo(vCommit.login,vCommit.name)
            developerinfo.latestcommit = vCommit
            committer = swdeveloper.SWDeveloper(0,self.scene,developerinfo,false)
            """
            return
            
        #locate correct component 
        component = None
        
        if len(vCommit.directories) > 0:
            
            #print "commit directory: ",vCommit.directories[0]
            
            try:
                component = self.components[vCommit.directories[0]]
            except:
                #print "No component named:%s  , must be a new component"%(vCommit.directories[0])
                #component = self.addComponent(vCommit.directories[0])
                pass
                
            if not component:
                #print "No component found from project"
                return
                
            devs = self.componentsAndDevelopersDict[component.name]
            devs.append(committer)
            
            #remove developer from previous componenent
            """
            previouscomponent = None
            for c in self.componentsAndDevelopersDict.values():
                if c.count(committer)>0:
                    c.remove(c.index(committer))
                    previouscomponent = c
                    break
            
            #rearrange devs...not done
            h = 0
            for j in range(len(previouscomponent)):
                dev = devs[j]
                h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
                h += 0.2
                
                devPos = V3(pos.X,pos.Y,pos.Z + h)
                
                committer.sog.NonPhysicalGrabMovement(pos)
            """
        else:
            component = self.component #no directories, so put dev into "container component"
                
        #print "____________dev target pos________: ", component.sog.AbsolutePosition
        
        pos = component.sog.AbsolutePosition
        
        
        #stack developers, so they dont collide ...
        devs = self.componentsAndDevelopersDict[component.name]
        
        h = 0
        for j in range(len(devs)-1):
            dev = devs[j]
            h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
            h += 0.2
            
        devPos = V3(pos.X,pos.Y,pos.Z + h)
        pos = devPos
        
        committer.sog.NonPhysicalGrabMovement(pos)

    def addDeveloper(self,vDeveloper):
        pass
 