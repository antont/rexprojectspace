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

class SWIssueFactory(object):
    
    instance = None
    
    def __init__(self,vScene):
        self.scene = vScene
        
    @classmethod
    CreateIssue(vIssueData):
        issue = None
        if vIssueData.type == "Defect":
            issue =  SWBug(self.scene,vIssueData)#bug
        else:
            issue =  SWEnhacement(self.scene,vIssueData)
            
        return issue

class SWIssue(object):

    def __init__(self,vScene,vIssueInfo):
        self.scene = vScene
        self.issueinfo = vIssueInfo
        self.isResponsibleAvatartAtProjectSpace = False
        self.avatar = None #rxavatar

    def LoadMeshWithTexturedMaterialAndAnimation(self,vMeshPath,vTexturePath,vMaterialPath,vSkeletonAnimPath):
        sop =  vScene.GetSceneObjectPart("rps_issue_" + self.issueinfo.id)
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Issue: %s found from scene"%(self.issueinfo.id)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"issue.mesh","issue.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Name =  "rps_issue_" + self.issueinfo.id
            self.scene.AddNewSceneObject(self.sog, False)


class SWEnhancement(SWIssue):
    def __init__(self,vScene,vIssueInfo):
        super(SWIssue,self).__init__(vScene,vIssueInfo)
        super(SWIssue,self).LoadMeshWithTexturedMaterialAndAnimation("","","","")
        
        if self.sog and self.rop:
            pass
        else:
            return

class SWBug(SWIssue):
    def __init__(self,vScene,vIssueInfo):
        super(SWBug,self).__init__(vScene,vIssueInfo)
        super(SWBug,self).LoadMeshWithTexturedMaterialAndAnimation("","","","")
        
        if self.sog and self.rop:
            pass
        else:
            return
        
        #scalefactor = vDeveloperInfo.commitcount
        #self.sog.RootPart.Resize(V3(0.1,0.1,0.1))
        #self.sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        
    def updateIsAtProjectSpace(self, vAtProjectSpace):
        """update visualization if necessary """
        if self.isResponsibleAvatartAtProjectSpace == False and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isResponsibleAvatartAtProjectSpace == True and vAtProjectSpace == False:
            pass
        elif self.isResponsibleAvatartAtProjectSpace == True and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isResponsibleAvatartAtProjectSpace == False and vAtProjectSpace == False:
            pass
        self.isResponsibleAvatartAtProjectSpace = vAtProjectSpace