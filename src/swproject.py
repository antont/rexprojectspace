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

import commitdispatcher

import swdeveloper

import rexprojectspacemodule

class Component:
    offset = 0.0
    
    def __init__(self,vScene,vName,vPos,vParent,vX=1,vY=1):
        
        self.name = vName
        
        self.__x = vX
        self.__y = vY
        
        self.curRow = 0
        self.curColumn = 0
        
        self.__offset = [] #offsets in x,y dimension
        self.currentIndex = 0  
        self.scene = vScene
        self.pos = vPos
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        """
        comp = vScene.GetSceneObjectPart(self.name)
        
        if comp:
            "Found component:%s from scene"%(self.name)
            self.sog = comp
        else:
            self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
            self.sog.RootPart.Scale = V3(vX,vY,1)
        """
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
        self.sog.RootPart.Scale = V3(vX,vY,1)
        
        
        print "mesh id for component: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
                      
        self.branches = []
        

        
    def addChild(self,vComponentName):

        temp = self.sog.AbsolutePosition
        p = V3(self.curColumn + temp.X + self.curColumn*Component.offset,
               self.curRow + temp.Y + self.curRow*Component.offset,
               temp.Z + 0.5)
               
        child =  Component(self.scene, vComponentName, p, self, 1,1)
        
        child.sog.RootPart.Scale = V3(0.85,0.85,1)
        
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
        
        #self.dev = swdeveloper.SWDeveloper(self.scene,"dump",0,"",False,"")
        
        #create first component representing self
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("4fad3aac-7819-42a0-86da-298b54a72791")
        
        if not self.scene.GetSceneObjectPart(self.UUID):
            print "No first sw component..."
            return
            
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        
        self.component = Component(vScene, "naali_root_component" , self.sog.AbsolutePosition, None, 5,5)
        self.component.sog.RootPart.Scale = V3(0,0,0)
        
        for componentname in vComponents:
            self.addComponent(componentname)
        
        print self.components
        
        #place developers to their initial positions...
        for dev in self.developers:
            latestcommit = dev.latesCommit
            if latestcommit != None or latestcommit == "":
                print latestcommit 
                self.updateDeveloperLocationWithNewCommitData(latestcommit)
        
        #get all commits
        #commitdispatcher.CommitDispatcher.register(self.updateDeveloperLocationWithNewCommitData,"naali","toni alatalo")
        
    def addComponent(self, vComponentName):
        self.components[vComponentName] = self.component.addChild(vComponentName)
        self.components[vComponentName].sog.RootPart.Name =  vComponentName
        pass
        
    
    def updateDeveloperLocationWithNewCommitData(self, vCommit):
        
        #we know nothing about this developer
        committer = None
        for dev in self.developers:
            print "%s developer and %s committer "%(dev.name,vCommit.author)
            if dev.name == vCommit.author:
                committer = dev
                break
        
        if committer == None:
            print "no committer"
            return
        
        print "commit directory: ",vCommit.directories[0]
        
        #locate correct component and developer
        component = None
        try:
            component = self.components[vCommit.directories[0]]
        except:
            print "No component named: ", vCommit.directories[0]
            return
        
        if not component:
            print "No component found from project"
            return
        
        print "____________dev target pos________: ", component.sog.AbsolutePosition
        
        committer.sog.NonPhysicalGrabMovement(component.sog.AbsolutePosition)
        
        pass   
      
    def addDeveloper(self,vDeveloper):
        pass
 