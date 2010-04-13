
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
import OpenSim.Framework
clr.AddReference('OpenSim.Region.Framework')
from OpenSim.Region.Framework.Interfaces import IRegionModule

from OpenMetaverse import Vector3 as V3

import sys, os, sha

import urllib

sphereRadius = 0.025
sphereHeigth = 0.05

class Issue(object):
    """ Issue objects represents a single issue
    Holds all the data related to a particular
    issue """
    def __init__(self,scene, position):
        self.scene = scene
        self.position = position
        
class Bug(Issue):
    """ Visualizes a single bug,  
    (but does not hold any data, because it is not
    needed currently)"""
    def __init__(self,scene, position):
        super(Bug, self).__init__(scene, position)
        self.visualization = self.createVisualization()
        
    def createVisualization(self):
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateSphere()
        pbs.SetRadius(sphereRadius)
        pbs.SetHeigth(sphereHeigth)        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),self.position,pbs)

        texcolor = OpenMetaverse.Color4(1, 0, 0, 1)
        tex = sog.RootPart.Shape.Textures
        tex.DefaultTexture.RGBA = texcolor
        sog.RootPart.UpdateTexture(tex)
        self.scene.AddNewSceneObject(sog, False)
        return sog
        
class Enhancement(Issue):
    """ Visualizes a single enhancement
    (but does not hold any data, because it is not
    needed currently)"""    
    def __init__(self,scene, position):
        super(Enhancement,self).__init__(scene, position)
        self.visualization = self.createVisualization()
        
    def createVisualization(self):
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateSphere()
        pbs.SetRadius(sphereRadius)
        pbs.SetHeigth(sphereHeigth)
        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),self.position,pbs)

        texcolor = OpenMetaverse.Color4(1, 1, 0, 1)
        tex = sog.RootPart.Shape.Textures
        tex.DefaultTexture.RGBA = texcolor
        sog.RootPart.UpdateTexture(tex)
        self.scene.AddNewSceneObject(sog, False)
        return sog                 

class IssueTracker:
    """ IssueTracker object visualizes the data received from the 
    issue tracker used by the realXtend project. IssueTracker
    object is interested in number of bugs and number of
    enhancements. """
    def __init__(self,name,scene, position):
        self.projectName = name
        self.scene = scene
        self.position = position
        
        self.sphereRadius = 0.025
        self.sphereHeigth = 0.05
        
        self.issuesPos = V3(129, 128.5, 25.279)
        self.enhancementPos = V3(129, 129.5, 25.279) 
        self.bugCount = -1
        self.enhancementCount = -1
        self.updateData()
        
        self.text  = str(self.bugCount) + " issues and " + str(self.enhancementCount) + " enhancements"
        
        self.bugs = []
        self.enhancements = []        
        
        self.visualization = self.createVisualization()
        self.scene.AddNewSceneObject(self.visualization, False)

    def createVisualization(self):
        """creates visualization based on issue count.  (More issues -> more objects)"""
        
        vis = self.createIssueContainer(self.text,self.position)
        
        #create bug objects        
        for i in range(self.bugCount):
            newZValue = 2*i*sphereHeigth + self.position.Z
            pos = V3(self.issuesPos.X,self.issuesPos.Y,newZValue)            
            self.bugs.append(Bug(self.scene,pos))

        #create enhancement objects
        for j in range(self.enhancementCount):
            newZValue = 2*j*sphereHeigth + self.position.Z
            pos = V3(self.enhancementPos.X,self.enhancementPos.Y,newZValue)
            self.enhancements.append(Enhancement(self.scene,pos))
            
        return vis

    def createIssueContainer(self,name,position):
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateSphere()
        pbs.SetRadius(1)
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),position,pbs)
        sog.SetText(name,V3(1.0,1.0,0.0),1.0)
        sog.Name = name
        
        texcolor = OpenMetaverse.Color4(0, 0, 1, 1)
        tex = sog.RootPart.Shape.Textures
        tex.DefaultTexture.RGBA = texcolor
        sog.RootPart.UpdateTexture(tex)
        
        return sog
        
    def update(self):
        self.updateData()
        self.updateVisualization()        
        
    def updateData(self):
        """gets bug count from google code hosting service and stores bug count to
        bugCount.(hopefully temporary solution and will be replaced with 
        Google data apis)"""
        
        f = urllib.urlopen("http://code.google.com/p/realxtend-naali/issues/csv")
        s = f.read()
        self.bugCount = s.count("Type-Defect")
        self.enhancementCount = s.count("Type-Enhancement")        
    
    def updateVisualization(self):
        if len(self.bugs) == self.bugCount:
            pass
        elif len(self.bugs) < self.bugCount:
            #add bug objects
            topBugZValue = 2*self.bugs.count()*sphereHeigth + self.position.Z
            for i in range(self.bugCount - self.bugs.count()):
                newZValue = 2*(i + 1)*sphereHeigth + topBugZValue
                pos = V3(self.issuesPos.X,self.issuesPos.Y,newZValue)            
                self.bugs.append(Bug(self.scene,pos))
            
        elif len(self.bugs) > self.bugCount:
            count = len(self.bugs)
            for i in range(count - self.bugCount):
                bugToRemove = self.bugs.pop()
                self.scene.DeleteSceneObject(bugToRemove,true)
    
        if len(self.enhancements) == self.enhancementCount:
            pass

        elif len(self.enhancements) < self.enhancementCount:
            #add enhancement objects
            topEnhancementZValue = 2*self.bugs.count()*sphereHeigth + self.position.Z
            for i in range(self.enhancementCount - self.enhancements.count()):
                newZValue = 2*(i + 1)*sphereHeigth + topEnhancementZValue
                pos = V3(self.enhancementPos.X,self.enhancementPos.Y,newZValue)            
                self.enhancements.append(Enhancement(self.scene,pos))
            
        elif len(self.enhancements) > self.enhancementCount:
            count = len(self.enhancements)
            for i in range(count - self.enhancementCount):
                enhancementToRemove = self.bugs.pop()
                self.scene.DeleteSceneObject(enhancementToRemove,true)

    
           
    