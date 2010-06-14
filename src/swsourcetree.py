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

import rexprojectspaceutils

#UI stuff
class Tree:

    def __init__(self,vScene,vName):
        """ "Base" of the tree """
        
        self.tile_height = 2.0
        
        self.scene = vScene
        
        self.tiles = [] #from bottom to up
        self.branches = []
        self.treeTop = None
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("fcc8a5f7-0851-4b50-bf24-8ba463dbb6aa") #root of tree...
        
        if not self.scene.GetSceneObjectPart(self.UUID):
            print "No tree..."
            return
            
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        self.pos = self.sog.AbsolutePosition
        
        print "mesh id for tree base: ", self.rop.RexMeshUUID
        
    def addNewBranch(self,vBranchName,vParentName=""):
        """None means to add branch to main tree, otherwise add to
           other branch """         
           
        nbr = len(self.tiles)
        if(nbr == 0):
            self.tiles.append(TreeTile(self.scene,self.pos))
            nbr = 1
        
        tile = self.tiles[nbr-1]
        currentPlace = tile.currentIndex
        
        if currentPlace >= len(tile.locations):
            temp = self.pos
            z = self.pos.Z + nbr*self.tile_height
            newLoc = V3(self.pos.X,self.pos.Y,z)
            tile = TreeTile(self.scene,newLoc)
            self.tiles.append(tile)
        
        #create branch and locate it
        branch = Branch(self.scene, vBranchName,"",tile.locations[tile.currentIndex],V3(1.0,1.0,1.0),tile.rotations[tile.currentIndex])
        self.branches.append(branch)
        
        tile.currentIndex += 1
        
            
class TreeTile:
    
    def __init__(self,vScene,vPos):
        
        self.currentIndex = 0  #increment on add
        self.scene = vScene
        self.pos = vPos
        self.w = 0.5
        
        self.locations = []
        for i in range(4):
            tempPos = None
            if i%2 == 0:
                tempPos = V3(self.pos.X + self.w/2 ,self.pos.Y,self.pos.Z + 0.4*(i+0.1))
            else:
                tempPos = V3(self.pos.X - self.w/2 ,self.pos.Y,self.pos.Z + 0.4*(i+0.1))
            self.locations.append(tempPos)
        
        self.rotations = [rexprojectspaceutils.euler_to_quat(20,0,0),
                          rexprojectspaceutils.euler_to_quat(-20,180,0),
                          rexprojectspaceutils.euler_to_quat(20,0,0)
                          ,rexprojectspaceutils.euler_to_quat(-20,180,0)] #insert branch rotations to here, with quats…

        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treetile.mesh","treetile.material","tile…",rexprojectspaceutils.euler_to_quat(90,0,0),self.pos)
            
        #print "mesh id for tile: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
        
class Branch:
    w = 1
    def __init__(self,vScene,vName,vParentName,vPos,vScale,vRot):
   
        self.scene = vScene
        self.parent = vParentName
        self.pos = vPos
        self.scale = vScale
        self.rot = vRot

        #upwards...
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treebranch.mesh","treebranch.material","tile…",vRot,self.pos)
        
        #print "mesh id for branch: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)

#data
class SWSourceTree:
    
    def __init__(self, vScene, vProjectName, vBranchNames):

        self.scene = vScene
        self.projectName = vProjectName
        self.branches = []
               
        self.bCurrentBuildFailed = False
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        self.tree = Tree(vScene,vProjectName)
        self.treerop = rexObjects.GetObject(self.tree.UUID)
        
        tempPos = self.tree.pos
        
        self.rainPlaceHolderSog = self.createRainPlaceHolder(V3(tempPos.X,tempPos.Y,tempPos.Z + 45))
        self.rainPlaceHolderRop = rexObjects.GetObject(self.rainPlaceHolderSog.UUID)
                
        #start from bottom
        for branch in vBranchNames:
            self.tree.branches.append(self.addNewBranch(branch))
    
    def createRainPlaceHolder(self,vPos):
        
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateBox()
        pbs.SetHeigth(1)
        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),vPos,pbs)
        
        sog.RootPart.Scale = V3(0.05,0.05,0.05)
        sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        
        self.scene.AddNewSceneObject(sog, False)
        print "placeholder position",vPos
        return sog    
        
    def setBuildSuccesfull(self):
        print "build succesfull"
        if self.bCurrentBuildFailed == True:
            #make it rain
            self.rainPlaceHolderRop.RexClassName = "sourcetree.Rain"
            #add timer so that tree burns...
            
        self.bCurrentBuildFailed = False
    
    def setBuildFailed(self):
        print "build failed"
                
        if self.bCurrentBuildFailed == False:
            #make it burn
            self.treerop.RexClassName = "sourcetree.BurningTree"
        
        self.bCurrentBuildFailed = True
        
    def addNewBranch(self,vBranchName,vParentName=""):
        """None means to add branch to main tree, otherwise add to
           other branch """
        self.tree.addNewBranch(vBranchName,vParentName)
        pass        
        
class SWSourceTreeBranch:
    
    def __init__(self, vScene, vBranchName, vNumberOfCommits = 0, vLatestCommit = ""):
        self.scene = vScene
        self.projectName = vProjectName
        self.numberOfCommits = vNumberOfCommits
        self.latestCommit = vLatestCommit