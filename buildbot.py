
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
import threading

import xmlrpclib

class BuildPlatform:
    """BuildPlatform object visualizes status of a single
    build platform. These objects are not responsible 
    for fetching the data."""
    def __init__(self,name,position):
        self.numberOfSuccesfulBuilds = 0
        self.numberOfFailedBuilds = 0
        self.name = name
        self.status = None
        self.visualization = self.createVisualization(position)

    def createVisualization(self,position):
        """creates vis. for a single build platform"""
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),position,
        OpenSim.Framework.PrimitiveBaseShape.CreateBox())
        sog.RootPart.Scale = V3(0.3, 0.3, 2)        
        sog.SetText(self.name,V3(1.0,1.0,0.0),1.0)
        return sog
        
    def updateVisualization(self):
        tex = self.visualization.RootPart.Shape.Textures
        if self.status == "success":
            texcolor = OpenMetaverse.Color4(0, 1, 0, 1)
            tex.DefaultTexture.RGBA = texcolor
            self.visualization.RootPart.UpdateTexture(tex)
            self.visualization.RootPart.Scale = V3(0.3, 0.3, 1)
        else:
            texcolor = OpenMetaverse.Color4(1, 0, 0, 1)
            tex.DefaultTexture.RGBA = texcolor
            self.visualization.RootPart.UpdateTexture(tex)
            self.visualization.RootPart.Scale = V3(0.3, 0.3, 1) 
            
class BuildBot:
    """ BuildBot object visualizes the actual build bot and communicates
    with the build bot (running on remote server) by using xmlrpc-api. 
    Hosts all the build platforms
    and updates their visualizations when needed. """
    
    def __init__(self,scene,position):
        self.scene = scene
        self.buildPlatformPositions = [V3(133.207,123.5,25.500),V3(133.282,124.5,25.500)]
        self.visualization = self.createVisualization(position)
        self.scene.AddNewSceneObject(self.visualization, False)
        
        self.proxy = xmlrpclib.ServerProxy("http://www.playsign.fi:8010/xmlrpc/")
        self.buildPlatforms = self.createBuildPlatforms()
        self.updateData()
        
        for key,value in self.buildPlatforms.iteritems():
            self.scene.AddNewSceneObject(value.visualization, False)
        
        self.updateVisualization()

    def createBuildPlatforms(self):
        builds = self.proxy.getAllBuilders()
        platforms = {}
        for index,buildName in enumerate(builds):
            platforms[buildName] = BuildPlatform(buildName,self.buildPlatformPositions[index])
        return platforms

    def createVisualization(self,position):
        """ creates vis. for build bot (but not for the build platforms)"""
        pos = position
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateBox()
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),pos,pbs)
        sog.RootPart.Scale = V3(1.5, 2.2, 0.5)
        sog.SetText("Build bot @ http://www.playsign.fi:8010",V3(1.0,1.0,0.0),1.0)
        sog.Name = "BuildBot"
        return sog

    def update(self):
        self.updateData()
        self.updateVisualization()

    def updateData(self):
        """fetches new data from the build bot using xmlrpc api"""
        for k,v in self.buildPlatforms.iteritems():
            v.status = self.proxy.getLastBuildResults(k)
    
    def updateVisualization(self):
        """updates the color"""
        for key,value in self.buildPlatforms.iteritems():
            tex = value.visualization.RootPart.Shape.Textures
            if value.status == "success":
                texcolor = OpenMetaverse.Color4(0, 1, 0, 1)
                tex.DefaultTexture.RGBA = texcolor
                value.visualization.RootPart.UpdateTexture(tex)
            else:
                texcolor = OpenMetaverse.Color4(1, 0, 0, 1)
                tex.DefaultTexture.RGBA = texcolor
                value.visualization.RootPart.UpdateTexture(tex)
