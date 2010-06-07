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

import swdeveloper

class Component:
    offset = 0.2
    
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
        
        #upwards...
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"component.mesh","component.material","comp",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
        self.sog.RootPart.Scale = V3(vX,vY,1)
        
        print "mesh id for component: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
                      
        self.branches = []
        
    def addChild(self):
        print "111"
        temp = self.sog.AbsolutePosition
        p = V3((1+self.curColumn) + temp.X + Component.offset,(1+self.curRow) + temp.Y + Component.offset,temp.Z)
        print "aaaa"
        child =  Component(self.scene, p, self, 1,1)
        print "bbbb"
        child.sog.RootPart.Scale = V3(1,1,1)
        print "ccc"
        self.curColumn += 1
        
    
class SWProject:

    def __init__(self, vScene,vProjectName, vDevelopers):
        self.scene = vScene
        self.projectName = vProjectName
        self.components = []
        self.developers = vDevelopers
        
        #create first component representing self
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("f5255b3a-3955-40ef-b890-247b831d3245") #root of tree...
        
        if not self.scene.GetSceneObjectPart(self.UUID):
            print "No first sw component..."
            return
            
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        
    def addComponent(self, vComponentName):
        pass
    
    def newCommitForDeveloper(self, vDeveloper):
        #locate correct component
        #parameter holds all the necessary data            
        pass   
    
    def createComponentVisualization(self,vComponent):
        """ Dynamically added components """
        pass
      
class SWComponent:

    def __init__(self, vComponentName):
        self.componentName = vComponentName
        self.commmitters = []
    
    def addDeveloper(self,vDeveloper):
        pass
        
    def removeDeveloper(self,vDeveloper):
        pass