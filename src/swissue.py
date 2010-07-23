
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
import avatarfollower

import rexprojectspacenotificationcenter

class IssueFactory():
    
    def __init__(self,vScene,vStart,vEnd,vSpawnPosition = V3(125,125,25)):
        """ vStart and vEnd defines a cube by start and end point. vSpawnPosition defines 
            a single point in scene that will be used a spawn position for spawned issues.
            By calling factory function CreateIssue, this factory can create issue and position
            it inside the given cage
        """
        self.scene = vScene
        self.start = vStart
        self.end = vEnd
        
        self.spawnpos = vSpawnPosition
        
        self.issues = {} #issueid,issue object dictionary
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIssue +=  self.CreateIssue
        nc.OnIssueUpdated += self.UpdateIssue
    
    def __del__(self):
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIssue -=  self.CreateIssue
        nc.OnIssueUpdated -= self.UpdateIssue
    
    def CreateIssue(self,vIssueData):
        
        
        if self.issues.keys().count(vIssueData.id) > 0:
            print "Found from factory: ", vIssueData.id
            return #don't create duplicatess
        
        issue = None
        print "------the type of issue-------------:", vIssueData.type
        if vIssueData.type == "Defect":
            print "Creating bug: ", vIssueData.id
            issue =  SWBug(self.scene,vIssueData,self.spawnpos)
        else:
            print "Creating enhancement: ", vIssueData.id
            issue =  SWEnhancement(self.scene,vIssueData,self.spawnpos)
        
        self.issues[vIssueData.id] = issue
        
        x = random.uniform(self.start.X,self.end.X)
        y = random.uniform(self.start.Y,self.end.Y)
        z = random.uniform(self.start.Z,self.end.Z)
        
        pos = V3(x,y,z)
        
        #should set the end position after setting the start, so that one could see the bug flying...
        issue.move(pos)
        
        self.issues[vIssueData.id] = issue
        
        issue.start()
        
        return issue
    
    def UpdateIssue(self,vIssueInfo):
        issue = 0
        try:
            issue = self.issues[vIssueInfo.id]
        except:
            return
            
        if issue:
            issue.DataChanged(vIssueInfo)
            
class SWIssue(object):

    def __init__(self,vScene,vIssueInfo,vPos):
        self.scene = vScene
        self.issueinfo = vIssueInfo
        self.isResponsibleAvatartAtProjectSpace = False
        self.avatar = None #rxavatar
        
        self.follower = avatarfollower.AvatarFollower(vScene,0,[vIssueInfo.owner,vIssueInfo.owner])
        
        self.follower.OnAvatarEntered += self.AvatarEntered
        self.follower.OnAvatarExited += self.AvatarExited 

    def LoadMeshWithMaterialAndTextures(self,vMeshPath,vMaterialPath,vTexturePaths,vPos):
        sop =  self.scene.GetSceneObjectPart("rps_issue_" + self.issueinfo.id)
        sog = 0
        rop = 0  
        if sop:
            sog = sop.ParentGroup
            rexObjects = self.scene.Modules["RexObjectsModule"]
            rop = rexObjects.GetObject(sog.RootPart.UUID)
            print "Issue: %s found from scene"%(self.issueinfo.id)
        else:
            
            sog,rop = rexprojectspaceutils.load_mesh(self.scene,vMeshPath,vMaterialPath,"test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0),vPos,V3(0.1,0.1,0.1))
            
            i = 1
            for texture in vTexturePaths:
                tex = rexprojectspaceutils.load_texture(self.scene,texture)
                rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
                i = i + 1
            sog.RootPart.Name =  "rps_issue_" + self.issueinfo.id
            self.scene.AddNewSceneObject(sog, False)
        
        return sog,rop
    
    def AvatarEntered(self):
        """ Override if needed """
        print "avatar entered"
        self.newposition = self.sog.AbsolutePosition
    
    def AvatarExited(self):
        """ Override if needed """
        self.sog.AbsolutePosition = self.newposition
        #create visualization again, since follower destroys sog...
        #self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"diamond.mesh","diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        #self.follower.sog = self.sog 
        
        #self.initVisualization(self.sog)
        #self.move(self.newposition)
        
    def move(self, vTargetPos):
        self.newposition = vTargetPos

    def start(self):
        #override this
        self.follower.sog = self.sog
        
    def DataChanged(self,vNewIssueInfo):
        print "base classes data changed"
        pass
    
    

class SWEnhancement(SWIssue):
    def __init__(self,vScene,vIssueInfo,vPos):
        super(SWEnhancement,self).__init__(vScene,vIssueInfo,vPos)
        
        vMaterialPath = "enhgenerated.material"
        
        self.sog,self.rop = super(SWEnhancement,self).LoadMeshWithMaterialAndTextures("bugi.mesh",vMaterialPath,["rpstextures/bugi_green.jp2"],vPos)
        skeleton_anim_id = rexprojectspaceutils.load_skeletonanimation(self.scene,"bug.skeleton")
        self.rop.RexAnimationPackageUUID = skeleton_anim_id
        self.issueinfo = vIssueInfo
        
    def start(self):
        super(SWEnhancement,self).start()
        self.rop.RexAnimationName = "flying"
        self.selectAnimation()
        
    def DataChanged(self,vNewIssueInfo):
        self.issueinfo = vNewIssueInfo
        self.selectAnimation()
        
    def move(self, vTargetPos):
        super(SWEnhancement,self).move(vTargetPos)
        self.sog.AbsolutePosition = vTargetPos
    
    def selectAnimation(self):
        if self.issueinfo.status == "new":
            print "new bug"
            self.rop.RexAnimationName = "flying"
        
        elif self.issueinfo.status == "started":
            print "started bug"
            self.rop.RexAnimationName = "flying_with_movement"
            
        else:
            pass
            #self.rop.RexAnimationName = "idle"
    
    
class SWBug(SWIssue):
    def __init__(self,vScene,vIssueInfo,vPos):
        super(SWBug,self).__init__(vScene,vIssueInfo,vPos)
        
        vMaterialPath = "enhgenerated.material"
        
        self.sog,self.rop = super(SWBug,self).LoadMeshWithMaterialAndTextures("bugi.mesh",vMaterialPath,["rpstextures/bugi_red.jp2"],vPos)
        skeleton_anim_id = rexprojectspaceutils.load_skeletonanimation(self.scene,"bug.skeleton")
        self.rop.RexAnimationPackageUUID = skeleton_anim_id
        self.issueinfo = vIssueInfo
        
    def start(self):
        super(SWBug,self).start()
        #self.rop.RexAnimationName = "flying"    
        self.selectAnimation()
        
        
    def DataChanged(self,vNewIssueInfo):
        self.issueinfo = vNewIssueInfo
        self.selectAnimation()
        
    def move(self, vTargetPos):
        super(SWBug,self).move(vTargetPos)
        self.sog.AbsolutePosition = vTargetPos
    
    def selectAnimation(self):
        print "hello: ", self.issueinfo.status
        if self.issueinfo.status == "new":
            print "new bug"
            self.rop.RexAnimationName = "flying"
        
        elif self.issueinfo.status == "started":
            print "bug started"
            self.rop.RexAnimationName = "flying_with_movement"
            
        else:
            pass
            #self.rop.RexAnimationName = "idle"
    
    