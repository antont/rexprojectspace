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

class Component:
    offset = 0.0
    
    def __init__(self,vScene,vPos,vParent,vX=1,vY=1):
        
        self.__x = vX
        self.__y = vY
        
        self.curRow = 0
        self.curColumn = 0
        
        self.__offset = [] #offsets in x,y dimension
        self.currentIndex = 0  
        self.scene = vScene
        self.pos = vPos
        
        rexObjects = self.scene.Modules["RexObjectsModule"]

        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
        self.sog.RootPart.Scale = V3(vX,vY,1)
        
        
        print "mesh id for component: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
                      
        self.branches = []
        

        
    def addChild(self):

        temp = self.sog.AbsolutePosition
        p = V3(self.curColumn + temp.X + self.curColumn*Component.offset,
               self.curRow + temp.Y + self.curRow*Component.offset,
               temp.Z + 0.5)
               
        child =  Component(self.scene, p, self, 1,1)
        
        child.sog.RootPart.Scale = V3(0.85,0.85,1)
        
        if self.curColumn < self.__x - 1: 
            self.curColumn += 1
        else:
            self.curColumn = 0
            self.curRow += 1
            
        return child
        
    
class SWProject:

    def __init__(self, vScene,vProjectName, vDevelopers):
        self.scene = vScene
        self.projectName = vProjectName
        
        self.components = {}
        self.developers = vDevelopers
        
        self.dev = swdeveloper.SWDeveloper(self.scene,"dump",0,"",False,"")
        
        #create first component representing self
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("4fad3aac-7819-42a0-86da-298b54a72791")
        
        if not self.scene.GetSceneObjectPart(self.UUID):
            print "No first sw component..."
            return
            
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        
        self.component = Component(vScene, self.sog.AbsolutePosition, None, 5,5)
        self.component.sog.RootPart.Scale = V3(0,0,0)
        
        self.addComponent("B")
        self.addComponent("A")
        
        print self.components
        
        #place developers to their initial positions...
        for dev in self.developers:
            latestcommit = dev.latesCommit
            if latestcommit != None:
                self.updateDeveloperLocationWithNewCommitData(latestcommit)
        
        #get all commits
        commitdispatcher.CommitDispatcher.register(self.updateDeveloperLocationWithNewCommitData,"naali","toni alatalo")
        
    def addComponent(self, vComponentName):
        self.components[vComponentName] = self.component.addChild()
        pass
        
    
    def updateDeveloperLocationWithNewCommitData(self, vCommit):
        
        #we know nothing about this developer
        if self.developers.count(vCommit.author) < 1:
            return
        
        print "commit directory: ",vCommit.directories[0]
        
        #locate correct component and developer
        component = self.components[vCommit.directories[0]]
        
        if not component:
            return

        print "dev target pos: ", component.sog.AbsolutePosition
        
        self.dev.sog.NonPhysicalGrabMovement(component.sog.AbsolutePosition)
        
        pass   
      
    def addDeveloper(self,vDeveloper):
        pass
 