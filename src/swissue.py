import rexprojectspaceutils
import commitdispatcher

import clr

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

import rexprojectspacedataobjects

class SWIssue:

    def __init__(self, vScene,vIssueInfo):
        self.scene = vScene
        self.issueinfo = vIssueInfo
        self.isResponsibleAvatartAtProjectSpace = False
        self.avatar = None #rxavatar
        
        sop =  vScene.GetSceneObjectPart("rps_issue_" + self.issueinfo.login)
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Issue: %s found from scene"%(self.issueinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"issue.mesh","issue.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Name =  "rps_issue_" + self.issueinfo.login
            self.scene.AddNewSceneObject(self.sog, False)
        
        scalefactor = vDeveloperInfo.commitcount
        #self.sog.RootPart.Resize(V3(0.1,0.1,0.1))
        self.sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
        
        #start receiving commits for project, not needed at the moment
        #commitdispatcher.CommitDispatcher.register(self.updateCommitData,"naali",self.developerinfo.login)
        print "dev: %s---created---"%(vDeveloperInfo.login)
        
    def updateCommitData(self, vCommitData):
        pass
        #print "updating developer vis. with: ", vNewCommit
        #update visualization also...
        
        
    def updateIsAtProjectSpace(self, vAtProjectSpace):
        """update visualization if necessary """
        if self.isAtProjectSpace == False and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isAtProjectSpace == True and vAtProjectSpace == False:
            pass
        elif self.isAtProjectSpace == True and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isAtProjectSpace == False and vAtProjectSpace == False:
            pass
        self.isAtProjectSpace = vAtProjectSpace