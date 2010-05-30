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

V3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

#UI stuff
class Tree:

    def __init__(self,vName):
        """ "Base" of the tree """
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("ac1e69a2-b56a-4cd6-bf95-360aa1dd27c4") #root of tree...
        self.rop = rexObjects.GetObject(self.UUID)
    
        print "mesh id___"
        print self.rop.RexMeshUUID
        
        self.tiles = [] #from bottom to up
        #tiles.append(TreeTile())
        
        self.treeTop = None
        
        self.branches = []
        
    
    def addNewBranch(self,vBranchName,vParentName=None):
        """None means to add branch to main tree, otherwise add to
           other branch """           
        if vParentName == None:
            nbr = len(self.tiles)
            tile = self.tiles[nbr]
            currentPlace = tile.currentIndex
            #create branch and locate it
            branch = Branch(vBranchName,None,currentPlace,V3(1,1,1),V3(0,0,0))
            if tile.currentIndex < len(tile.locations):
                tile.currentIndex += 1
            else:
                self.tiles.append(TreeTile)
            
            self.branches.append(branch)
            
class TreeTile:
    def __init__(self,vPos):
        locations = [] #insert branch locations to here… (with normal scale)
        currentIndex = 0 #increment on add...
        self.pos = vPos
        
        rexObjects = self.scene.Modules["RexObjectsModule"]        
        
        self.sog, self.rop = rexprojectspaceutils.load_mesh(self.scene,"treetile.mesh","treetile.material","tile…",OpenMetaverse.Quaternion(0,0,0,1),self.pos)
        #rexObjects.GetObject(self.UUID)
    
        print "mesh id___"
        print self.rop.RexMeshUUID
                      
        self.branches = []
        
    
class Branch:
    def __init__(self,vName,vParentName,vPos,vScale,vRot):
    
        """ "Branch" of the tree """
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("ac1e69a2-b56a-4cd6-bf95-360aa1dd27c4") #branch of tree...
        self.rop = rexObjects.GetObject(self.UUID)
        self.parent = vParent
        
        print "mesh id___"
        print self.rop.RexMeshUUID


    pass    

#data
class SWSourceTree:
    
    def __init__(self, vScene, vProjectName, vBranchNames):
        print "haloo..."
        self.scene = vScene
        self.projectName = vProjectName
        self.branches = []
               
        self.bCurrentBuildFailed = False
        
        self.tree = Tree()
                
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