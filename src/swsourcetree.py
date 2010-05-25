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

class SWSourceTree:
    
    def __init__(self, vScene, vProjectName, vBranchNames):
        print "haloo..."
        self.scene = vScene
        self.projectName = vProjectName
        self.branches = []
        self.UUID = OpenMetaverse.UUID("ac1e69a2-b56a-4cd6-bf95-360aa1dd27c4")
        
        self.bCurrentBuildFailed = False
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.rop = rexObjects.GetObject(self.UUID)
        print "mesh id___"
        print self.rop.RexMeshUUID
        
        
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
        
class SWSourceTreeBranch:
    
    def __init__(self, vScene, vBranchName, vNumberOfCommits = 0, vLatestCommit = ""):
        self.scene = vScene
        self.projectName = vProjectName
        self.numberOfCommits = vNumberOfCommits
        self.latestCommit = vLatestCommit