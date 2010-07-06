
import clr
import random

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

import rexprojectspaceutils
import rexprojectspacedataobjects

class IssueFactory():
    
    def __init__(self,vScene,vStart,vEnd):
        """ vStart and vEnd defines a cube by start and end point. By calling
            factory function CreateIssue, this factory can create issue and position
            it inside the given cage
        """
        self.scene = vScene
        self.start = vStart
        self.end = vEnd
    
    def CreateIssue(self,vIssueData):
        issue = None
        if vIssueData.type == "Defect":
            issue =  SWBug(self.scene,vIssueData)
        else:
            issue =  SWEnhancement(self.scene,vIssueData)
            
        x = random.uniform(self.start.X,self.end.X)
        y = random.uniform(self.start.Y,self.end.Y)
        z = random.uniform(self.start.Z,self.end.Z)
        
        pos = V3(x,y,z)
        
        #should set the end position after setting the start
        issue.sog.AbsolutePosition = pos
        
        
        return issue
        
class SWIssue(object):

    def __init__(self,vScene,vIssueInfo):
        self.scene = vScene
        self.issueinfo = vIssueInfo
        self.isResponsibleAvatartAtProjectSpace = False
        self.avatar = None #rxavatar

    def LoadMeshWithTexturedMaterialAndAnimation(self,vMeshPath,vTexturePath,vMaterialPath,vSkeletonAnimPath):
        sop =  self.scene.GetSceneObjectPart("rps_issue_" + self.issueinfo.id)
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = self.scene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Issue: %s found from scene"%(self.issueinfo.id)
        else:
            rexprojectspaceutils.load_texture(self.scene,vTexturePath)
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,vMeshPath,vMaterialPath,"test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Scale = V3(0.1,0.1,0.1)
            skeleton_anim_id = rexprojectspaceutils.load_skeletonanimation(self.scene,vSkeletonAnimPath)
            self.rop.RexAnimationPackageUUID = skeleton_anim_id
            
            self.sog.RootPart.Name =  "rps_issue_" + self.issueinfo.id
            self.scene.AddNewSceneObject(self.sog, False)
    
    def start(self):
        #implemented by sub classes...
        pass
    

class SWEnhancement(SWIssue):
    def __init__(self,vScene,vIssueInfo):
        super(SWEnhancement,self).__init__(vScene,vIssueInfo)
        super(SWEnhancement,self).LoadMeshWithTexturedMaterialAndAnimation("Sphere.mesh","bug_wings_rigged_face_Sphere.jpg","Sphere.material","Sphere.skeleton")
        
        if self.sog and self.rop:
            pass
        else:
            return

    def start(self):
        self.rop.RexAnimationName = "flying_no_movement"
        
class SWBug(SWIssue):
    def __init__(self,vScene,vIssueInfo):
        super(SWBug,self).__init__(vScene,vIssueInfo)
        super(SWBug,self).LoadMeshWithTexturedMaterialAndAnimation("Sphere.mesh","bug_wings_rigged_face_Sphere.jpg","Sphere.material","Sphere.skeleton")
        
        if self.sog and self.rop:
            """
            try:
            rexpy = scene.Modules["RexPythonScriptModule"]
            except KeyError:
                self.rexif = None
                #print "Couldn't get a ref to RexSCriptInterface"
            else:
                self.rexif = rexpy.mCSharp
                self.rexif.rexSetTextureMediaURL("http://img810.imageshack.us/img810/5356/bugwingsriggedfacespher.jpg")
            """
            pass
        else:
            return
      
    def start(self):
        self.rop.RexAnimationName = "flying"    
     
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