 
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

clr.AddReference('OgreSceneImporter')
import OgreSceneImporter

clr.AddReference('RexDotMeshLoader')
from RexDotMeshLoader import DotMeshLoader

from OpenMetaverse import Vector3 as V3

import sys, os, sha
import threading

import swsourcetree
import buildbot

import swproject
import swdeveloper

import versioncontrolsystem

class RexProjectSpace(IRegionModule):
    autoload = True
    
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
        return sog    
    
    
    def Initialise(self, scene, configsource):
        
        self.removed = False
        self.scene = scene
        self.config = configsource
        
        self.developers = []
        
        self.buildbot = buildbot.BuildBot()
        
        branches = []
        self.tree = swsourcetree.SWSourceTree(scene,"Naali",branches)
        
        self.updateBuildResults()
        
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        self.updateCommitters(self.developers)
        
        self.project = self.initSWProject()
        
        try:
            rexpy = scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            print "Couldn't get a ref to RexSCriptInterface"
        else:
            self.rexif = rexpy.mCSharp
        
        ball = self.createBall()

        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        #self.updateTimer = threading.Timer(1.0,self.updateProjectSpace)
        #self.updateTimer.start()
        
        scene.AddCommand(self, "hitMe","","",self.cmd_hitMe)
    
    def updateBuildResults(self):
        builds = self.buildbot.getLatestBuilds()
        
        buildResult = True
        
        for k,v in builds.iteritems():
            if v == "success":
                pass
            else:
                buildResult = False
                
        if buildResult == True:
            self.tree.setBuildSuccesfull()
        else:
            self.tree.setBuildFailed()
    
    def initSWProject(self):
        """Mocked solution for now """
        
        components = []
        component.append(SWComponent("Application"))
        component.append(SWComponent("AssetModule"))
    
        project = SWProjext("naali",components)
    
        return project
        
        
    def updateCommitters(self,vCommitters):
        """ Committers from github """
        contributors = self.vcs.getAllContributors()
        
        for value in contributors:
            login = value["login"]
            nbrOfCommits = value["contributions"]
            vCommmitters.append(SWDeveloper(login,nbrOfCommits,"",False))

    
    def cmd_hitMe(self, *args):
        #try to get the tree item
        print "hello"
        self.tree.setBuildFailed()

    
    def updateProjectSpace(self):

        
    
        self.updateTimer = threading.Timer(30.0,self.updateProjectSpace)
        self.updateTimer.start()       
        
        pass

    def PostInitialise(self):
        print self, 'post-initialise'

    def Close(self):
        print self, 'close'

    def getname(self):
        return self.__class__.__name__

    Name = property(getname)

    def isshared(self):
        return False

    IsSharedModule = property(isshared)
        
    def onFrameUpdate(self):
        pass
        

def load_mesh(scene, meshpath, materialpath, description, rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30), scale=V3(1, 1, 1)):
    mesh_uuid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase(mesh_uuid, "George")
    asset.Type = 43 # ??
    asset.Description = description
    asset.Data = System.IO.File.ReadAllBytes(meshpath)
    scene.AssetService.Store(asset)
    root_avatar_uuid = scene.RegionInfo.MasterAvatarAssignedUUID
    
    sceneobjgroup = scene.AddNewPrim(
        root_avatar_uuid, root_avatar_uuid,
        pos, rot, OpenSim.Framework.PrimitiveBaseShape.CreateBox())
    rexObjects = scene.Modules["RexObjectsModule"]
    sceneobjgroup.RootPart.Scale = scale
    robject = rexObjects.GetObject(sceneobjgroup.RootPart.UUID)
    print "root uuid", sceneobjgroup.RootPart.UUID
    robject.RexMeshUUID = asset.FullID
    robject.RexDrawDistance = 256
    robject.RexCastShadows = True
    robject.RexDrawType = 1;
    robject.RexCollisionMeshUUID = asset.FullID;
    matdata = open(materialpath).read()
    matparser = OgreSceneImporter.OgreMaterialParser(scene)
    rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
        matdata)
    mat2uuid = dict(mat2uuid)
    print "mat-uuid dict:", mat2uuid
    if not rc:
        print "material parsing failed"
        return

    matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
    print list(matnames)
    for i, mname in enumerate(matnames):
        robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
        print "material added:", mname
    return sceneobjgroup, robject        
        
 