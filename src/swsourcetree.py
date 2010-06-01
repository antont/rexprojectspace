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

#UI stuff
class Tree:

    def __init__(self,vScene,vName):
        """ "Base" of the tree """
        
        self.scene = vScene
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("a56f05c7-533b-45a3-864b-d0860ae8482d") #root of tree...
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        
        self.loc = self.sog.AbsolutePosition
    
        self.tile_height = 1.0
        
        print "mesh id for tree base: ", self.rop.RexMeshUUID
        
        self.tiles = [] #from bottom to up
        #self.tiles.append(TreeTile(vScene,V3(137.65,129.87,26.2)))
        
        self.treeTop = None
        
        self.branches = []
        
    
    def addNewBranch(self,vBranchName,vParentName=""):
        """None means to add branch to main tree, otherwise add to
           other branch """         
           
        #V3(137.65,129.87,26.2)
        #self.tiles.append(TreeTile(self.scene,self.loc))
           
        #if vParentName == None:
        nbr = len(self.tiles)
        print "number of tre tiles: ", nbr
        if(nbr == 0):
            self.tiles.append(TreeTile(self.scene,self.loc))
            nbr = 1
        
        tile = self.tiles[nbr-1]
        currentPlace = tile.currentIndex
        #create branch and locate it
        branch = Branch(self.scene, vBranchName,"",TreeTile.locations[tile.currentIndex],V3(1.0,2.5,2.5),TreeTile.rotations[tile.currentIndex])
        if tile.currentIndex < len(TreeTile.locations) - 1:
            tile.currentIndex += 1
            pass
        else:
            temp = self.loc
            z = self.loc.Z + nbr*self.tile_height
            newLoc = V3(self.loc.X,self.loc.Y,z)
            print "New loc: ", newLoc
            self.tiles.append(TreeTile(self.scene,newLoc))
        
        #self.branches.append(branch)
            
class TreeTile:
    locations = [V3(136.62,129.91,27.26),V3(136.62,129.91,27.66)] #insert branch locations to here… (with normal scale, relative to tile)
    rotations = [rexprojectspaceutils.euler_to_quat(20,0,0),rexprojectspaceutils.euler_to_quat(20,0,0)] #insert branch rotations to here, with quats…

    def __init__(self,vScene,vPos):
        
        self.currentIndex = 0  #increment on add, fix after testing...
        self.scene = vScene
        self.pos = vPos
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        #upwards...
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treetile.mesh","treetile.material","tile…",rexprojectspaceutils.euler_to_quat(90,0,0),self.pos)
    
        print "mesh id for tile: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)
                      
        self.branches = []
        
    
class Branch:
    def __init__(self,vScene,vName,vParentName,vPos,vScale,vRot):
   
        self.scene = vScene
        self.parent = vParentName
        self.pos = vPos
        self.scale = vScale
        self.rot = vRot

        #upwards...
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treebranch.mesh","treebranch.material","tile…",rexprojectspaceutils.euler_to_quat(0,0,90),self.pos)
        
        print "mesh id for branch: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)

    pass    

#data
class SWSourceTree:
    
    def __init__(self, vScene, vProjectName, vBranchNames):

        self.scene = vScene
        self.projectName = vProjectName
        self.branches = []
               
        self.bCurrentBuildFailed = False
        
        #self.tree = Tree(vScene,vProjectName)
                
        #start from bottom
        for branch in vBranchNames:
            self.tree.branches.append(self.addNewBranch(branch))
        
        
    def setBuildSuccesfull(self):
        if self.bCurrentBuildFailed == True:
            #make it rain
            pass
        
        self.bCurrentBuildFailed = False
    
    def setBuildFailed(self):
        print "build failed"
        self.rop.RexClassName = "follower.Follower"
        
        if self.bCurrentBuildFailed == False:
            #make it burn
            pass
        
        self.bCurrentBuildFailed = True
        
    def addNewBranch(self,vBranchName,vParent=None):
        """None means to add branch to main tree, otherwise add to
           other branch """           
        pass        
        
class SWSourceTreeBranch:
    
    def __init__(self, vScene, vBranchName, vNumberOfCommits = 0, vLatestCommit = ""):
        self.scene = vScene
        self.projectName = vProjectName
        self.numberOfCommits = vNumberOfCommits
        self.latestCommit = vLatestCommit