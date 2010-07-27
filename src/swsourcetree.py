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
import OpenSim.Region.Framework

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

import time

import rexprojectspaceutils
import rexprojectspacedataobjects

import rexprojectspacenotificationcenter

#UI stuff
class Tree:

    def __init__(self,vScene,vName):
        """ "Base" of the tree """
        
        self.tile_height = 2.5
        self.tree_base_height = 1.0
        
        self.scene = vScene
        
        self.treebase = None
        self.tiles = [] #from bottom to up
        self.branches = []
        self.treeTop = None
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("e0afbfb2-fbac-4bb2-b797-915d2eaa7730") #root of tree...
        
        """
        if not self.scene.GetSceneObjectPart(self.UUID):
            #print "No tree..."
            return
        """

        if not self.scene.GetSceneObjectPart("tree_base"):
            #print "No tree..."
            return
        """
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        self.pos = self.sog.AbsolutePosition
        """
        
        self.sog = self.scene.GetSceneObjectPart("tree_base").ParentGroup
        self.UUID = self.sog.UUID
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        self.pos = self.sog.AbsolutePosition
        
        
        sop =  vScene.GetSceneObjectPart("rps_treebase_" + vName)
        
        if sop:
            self.treebasesog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.treebaserop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Tree: %s found from scene"%(vName)
        else:    
            self.treebasesog,self.treebaserop = rexprojectspaceutils.load_mesh(self.scene,"treebase.mesh","treebase.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
            self.treebasesog.RootPart.Name =  "rps_treebase_" + vName
            self.scene.AddNewSceneObject(self.treebasesog, False)
            self.treebasesog.AbsolutePosition = V3(self.sog.AbsolutePosition)
            self.treebasesog.SetText("master",V3(1.0,1.0,0.0),1.0)
        
        sop = None
        
        sop =  vScene.GetSceneObjectPart("rps_treetop_" + vName)
        
        if sop:
            self.treetopsog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.treetoprop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Tree: %s found from scene"%(vName)
        else:
            temp = self.treebasesog.AbsolutePosition
            self.treetopsog,self.treebaserop = rexprojectspaceutils.load_mesh(self.scene,"treetop.mesh","treetop.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0),V3(temp.X,temp.Y,temp.Z+1))
            self.treetopsog.RootPart.Name =  "rps_treetop_" + vName
            self.scene.AddNewSceneObject(self.treetopsog, False)
        
        #print "mesh id for tree: ", self.rop.RexMeshUUID

    def addNewBranch(self,vBranchInfo,vParentName=""):
        """None means to add branch to main tree, otherwise add to
           other branch """         
           
        nbr = len(self.tiles)
        if(nbr == 0):
            temp = self.pos
            z = temp.Z + self.tree_base_height
            self.tiles.append(TreeTile(self.scene,V3(temp.X,temp.Y,z),self.tile_height))
            nbr = 1
        
        tile = self.tiles[nbr-1]
        currentPlace = tile.currentIndex
        
        if currentPlace >= len(tile.locations):
            temp = self.pos
            z = self.pos.Z + nbr*self.tile_height + self.tree_base_height
            newLoc = V3(self.pos.X,self.pos.Y,z)
            tile = TreeTile(self.scene,newLoc,self.tile_height)
            self.tiles.append(tile)
            #put top in to a place
            temp = tile.sog.AbsolutePosition
            self.treetopsog.NonPhysicalGrabMovement(V3(temp.X,temp.Y,temp.Z+self.tile_height))
        
        #Evaluate latest commit data and create branch
        today = time.gmtime(time.time())
        tday = time.time()
        texpath = "rpstextures/treebranch_green.jp2"
        
        if tday - 60*60*24*60 > time.mktime(vBranchInfo.latestcommitdate):
            texpath = "rpstextures/treebranch_rust.jp2"
        
        branch = Branch(self.scene, vBranchInfo.name,texpath,tile.locations[tile.currentIndex],V3(1.0,1.0,1.0),tile.rotations[tile.currentIndex])
        
        self.branches.append(branch)
        
        tile.currentIndex += 1
        
        return branch
        
            
class TreeTile:
    
    def __init__(self,vScene,vPos,vHeight):
        
        self.currentIndex = 0  #increment on add
        self.scene = vScene
        self.pos = vPos
        self.w = 0
        self.height = vHeight
        print "_______Tile height:_______",self.height
        
        self.locations = []
        for i in range(4):
            tempPos = None
            if i%2 == 0:
                tempPos = V3(self.pos.X, self.pos.Y + self.w/2,self.pos.Z + (i*self.height/4 + 0.15))
            else:
                tempPos = V3(self.pos.X, self.pos.Y - self.w/2,self.pos.Z + (i*self.height/4 + 0.15))
            self.locations.append(tempPos)
            
        self.rotations = [rexprojectspaceutils.euler_to_quat(20,0,0),
                          rexprojectspaceutils.euler_to_quat(-20,180,0),
                          rexprojectspaceutils.euler_to_quat(20,0,0)
                          ,rexprojectspaceutils.euler_to_quat(-20,180,0)] #insert branch rotations to here, with quats…

        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treetile.mesh","treetile.material","tile…",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
            
        ##print "mesh id for tile: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
        
class Branch:
    w = 1
    def __init__(self,vScene,vBranchName,vTexturePath,vPos,vScale,vRot):
   
        self.scene = vScene
        self.texturepath = vTexturePath
        self.pos = vPos
        self.scale = vScale
        self.rot = vRot

        #upwards...
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treebranch.mesh","treebranch.material","tile…",vRot,self.pos,V3(0,0,0))
        tex = rexprojectspaceutils.load_texture(self.scene,vTexturePath)
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        self.sog.SetText(vBranchName,V3(0.0,1.0,0.0),1.0)
        ##print "mesh id for branch: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)

#data
class SWSourceTree:
    
    def __init__(self, vScene, vProjectName, vBranchInfos):

        self.scene = vScene
        self.projectName = vProjectName
        self.branches = {} #holds name branch pairs...
               
        self.bCurrentBuildFailed = False
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        self.tree = Tree(vScene,vProjectName)
        self.treerop = rexObjects.GetObject(self.tree.UUID)
        
        tempPos = self.tree.pos
        
        self.rainPlaceHolderSog = self.createRainPlaceHolder(V3(tempPos.X,tempPos.Y,tempPos.Z + 45))
        self.rainPlaceHolderRop = rexObjects.GetObject(self.rainPlaceHolderSog.UUID)
                
        #start from bottom
        for branch in vBranchInfos:
            b = self.addNewBranch(branch)
            #self.tree.branches.append(b)
            
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        
        nc.OnBuild += self.updateBuildResult
        nc.OnBranchesChanged += self.addNewBranch
        
    def __del__(self):
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnBuild -= self.updateBuildResult
        
    
    def createRainPlaceHolder(self,vPos):
        
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateBox()
        pbs.SetHeigth(1)
        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),vPos,pbs)
        
        sog.RootPart.Scale = V3(0.05,0.05,0.05)
        sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        
        self.scene.AddNewSceneObject(sog, False)
        #print "placeholder position",vPos
        return sog    
        
    def updateBuildResult(self,vBuilds):
        res = True
        for build in vBuilds:
            if build.result != "success":
                res = False
                break
            
        if res == True:
            self.setBuildSuccesfull()
        else:
            self.setBuildFailed()
        
    
    def setBuildSuccesfull(self):
        if self.bCurrentBuildFailed == True:
            #make it rain
            self.rainPlaceHolderRop.RexClassName = "sourcetree.Rain"
            #add timer so that tree burns...
            
        self.bCurrentBuildFailed = False
    
    def setBuildFailed(self):
        if self.bCurrentBuildFailed == False:
            #make it burn
            self.treerop.RexClassName = "sourcetree.BurningTree"
        
        self.bCurrentBuildFailed = True
        
    def addNewBranch(self,vBranchInfo,vParentName=""):
        """None means to add branch to main tree, otherwise add to
           other branch. Evaluate latest commit date and choose color/
           texture based on that (not done)"""
        #print vBranchInfo
        if self.branches.keys().count(vBranchInfo.name) > 0:
            return
            
        b = self.tree.addNewBranch(vBranchInfo,vParentName)
        b.rop.RexClassName = "sourcetree.BranchScaler"        
        self.branches[vBranchInfo.name] = b
        
class SWSourceTreeBranch:
    """ Not needed... Perhaps later... """
    def __init__(self, vScene, vBranchName, vNumberOfCommits = 0, vLatestCommit = ""):
        self.scene = vScene
        self.projectName = vProjectName
        self.numberOfCommits = vNumberOfCommits
        self.latestCommit = vLatestCommit