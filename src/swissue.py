
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
import clickhandler

class IssueFactory():
    """ IssueFactory can create issues and locate place them correctly (random)
        to the scene
    """
    
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
        
        self.bugs = {} #issueid,issue object dictionary
        self.enhancements = {} #issueid,issue object dictionary
        
        #uncomment this
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIssue +=  self.CreateIssue
        nc.OnIssueUpdated += self.UpdateIssue
        
    
    def __del__(self):
        #uncomment this
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewIssue -=  self.CreateIssue
        nc.OnIssueUpdated -= self.UpdateIssue
        
        
    def CreateIssue(self,vIssueData):
        """ Returns object inherited from SWIssue
        """
        
        if self.bugs.keys().count(vIssueData.id) > 0 or self.enhancements.keys().count(vIssueData.id) > 0:
            print "Found from factory: ", vIssueData.id
            return #don't create duplicatess
        
        issue = None
        #print "------the type of issue-------------:", vIssueData.type
        
        x = random.uniform(self.start.X,self.end.X)
        y = random.uniform(self.start.Y,self.end.Y)
        z = 0
        
        if vIssueData.type == "Defect":
            print "Creating bug: ", vIssueData.id
            issue =  SWBug(self.scene,vIssueData,self.spawnpos)
            
            z = random.uniform(self.start.Z,self.start.Z + (self.end.Z - self.start.Z)*0.45)
            
            self.bugs[vIssueData.id] = issue
        else:
            print "Creating enhancement: ", vIssueData.id
            issue =  SWEnhancement(self.scene,vIssueData,self.spawnpos)
            
            z = random.uniform(self.start.Z + (self.end.Z - self.start.Z)*0.55, self.end.Z)

            self.enhancements[vIssueData.id] = issue
            
        print z
        
        pos = V3(x,y,z)
        
        #should set the end position after setting the start, so that one could see the bug flying...
        issue.move(pos)

        issue.start()
        
        return issue
    
    def UpdateIssue(self,vIssueInfo):
        """ Locate correct issue and update it's data 
        """
        issue = 0
        try:
            issue = self.bugs[vIssueInfo.id]
        except:
            try:
                issue = self.enhancements[vIssueInfo.id]
            except:
                return
            
        if issue:
            issue.DataChanged(vIssueInfo)
            
class SWIssue(object):
    """ Base class for issues
    """
    
    def __init__(self,vScene,vIssueInfo,vPos):
        self.scene = vScene
        self.issueinfo = vIssueInfo
        self.isResponsibleAvatartAtProjectSpace = False
        self.avatar = None #rxavatar
        
        #feature works correctly, but does it make any sense?
        #self.follower = avatarfollower.AvatarFollower(vScene,0,[vIssueInfo.owner,vIssueInfo.owner])
        
        #self.follower.OnAvatarEntered += self.AvatarEntered
        #self.follower.OnAvatarExited += self.AvatarExited 

    def LoadMeshWithMaterialAndTextures(self,vMeshPath,vMaterialPath,vTexturePaths,vPos):
        """ Checks if scene allready has mesh with issues id... If not 
            create it. Return sceneobjectgroup and rexobjectproperties
        """
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
        
    def move(self, vTargetPos):
        """ update position """
        self.newposition = vTargetPos

    def start(self):
        #override this
        #self.follower.sog = self.sog
        pass
        
    def DataChanged(self,vNewIssueInfo):
        print "base classes data changed"
        pass
    
    

class SWEnhancement(SWIssue):
    """ SWIssue subclass representing a software enhancement proposal
    """
    TEXTUREUUID = OpenMetaverse.UUID.Zero 
    MESHUUID = OpenMetaverse.UUID.Zero 
    def __init__(self,vScene,vIssueInfo,vPos):
        """ Load mesh and animation package
        """
        super(SWEnhancement,self).__init__(vScene,vIssueInfo,vPos)
        self.issueinfo = vIssueInfo
        
        if SWEnhancement.MESHUUID == OpenMetaverse.UUID.Zero:
            print "loading enhancement mesh"
            SWEnhancement.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"rpsmeshes/bugi.mesh","issue mesh")
        
        sop =  vScene.GetSceneObjectPart("rps_issue_" + self.issueinfo.id)
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "enhancement: %s found from scene"%(self.issueinfo.id)
            SWEnhancement.MESHUUID = self.rop.RexMeshUUID.ToString()
        else:
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,SWEnhancement.MESHUUID,"rpsmeshes/enhgenerated.material",rexprojectspaceutils.euler_to_quat(0,0,0),vPos,V3(0.1,0.1,0.1))
            self.sog.RootPart.Name =  "rps_issue_" + self.issueinfo.id
        
        if SWEnhancement.TEXTUREUUID == OpenMetaverse.UUID.Zero:
            SWEnhancement.TEXTUREUUID = rexprojectspaceutils.load_texture(self.scene,"rpstextures/bugi_green.jp2")
        
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(SWEnhancement.TEXTUREUUID))
        
        skeleton_anim_id = rexprojectspaceutils.load_skeleton_animation(self.scene,"bug.skeleton")
        self.rop.RexAnimationPackageUUID = skeleton_anim_id
        
        self.rop.RexParticleScriptUUID = rexprojectspaceutils.load_particle_script(vScene,"rpsparticles/spark_green.particle","")
        self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.issueinfo.url)
        
        
    def start(self):
        """ Choose animation
        """
        super(SWEnhancement,self).start()
        
        self.selectAnimation()
        
    def DataChanged(self,vNewIssueInfo):
        """ Choose animation
        """
        self.issueinfo = vNewIssueInfo
        self.selectAnimation()
        
    def move(self, vTargetPos):
        """ update location
        """
        super(SWEnhancement,self).move(vTargetPos)
        self.sog.AbsolutePosition = vTargetPos
    
    def selectAnimation(self):
        """ Choose animation by evaluating status of the enhancement
        """
        print "enhan status: ", self.issueinfo.status
        if self.issueinfo.status == "New":
            self.rop.RexAnimationName = "flying"
        
        elif self.issueinfo.status == "Started":
            print "started bug"
            self.rop.RexAnimationName = "flying_with_movement"
            
        else:
            pass
            #self.rop.RexAnimationName = "idle"
            
        self.rop.RexAnimationRate = 4.0

class SWBug(SWIssue):
    """ SWIssue subclass representing a software bug
    """
    MESHUUID = OpenMetaverse.UUID.Zero
    TEXTUREUUID = OpenMetaverse.UUID.Zero
    def __init__(self,vScene,vIssueInfo,vPos):
        """ Load mesh and animation package
        """
        super(SWBug,self).__init__(vScene,vIssueInfo,vPos)
        self.issueinfo = vIssueInfo
         
        if SWBug.MESHUUID == OpenMetaverse.UUID.Zero:
            print "loading enhancement mesh"
            SWBug.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"rpsmeshes/bugi.mesh","issue mesh")
        
        sop =  vScene.GetSceneObjectPart("rps_issue_" + self.issueinfo.id)
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "bug: %s found from scene"%(self.issueinfo.id)
            SWBug.MESHUUID = self.rop.RexMeshUUID.ToString()
        else:
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,SWBug.MESHUUID,"rpsmeshes/enhgenerated.material",rexprojectspaceutils.euler_to_quat(0,0,0),vPos,V3(0.1,0.1,0.1))
            self.sog.RootPart.Name =  "rps_issue_" + self.issueinfo.id
        
        if SWBug.TEXTUREUUID == OpenMetaverse.UUID.Zero:
            SWBug.TEXTUREUUID = rexprojectspaceutils.load_texture(self.scene,"rpstextures/bugi_red.jp2")

        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(SWBug.TEXTUREUUID))
        
        skeleton_anim_id = rexprojectspaceutils.load_skeleton_animation(self.scene,"bug.skeleton")
        self.rop.RexAnimationPackageUUID = skeleton_anim_id
        
        self.rop.RexParticleScriptUUID = rexprojectspaceutils.load_particle_script(vScene,"rpsparticles/spark_red.particle","")
        self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.issueinfo.url)
        
    def start(self):        
        """ Choose animation
        """
        super(SWBug,self).start()  
        self.selectAnimation()
        
    def DataChanged(self,vNewIssueInfo):        
        """ Choose animation
        """
        self.issueinfo = vNewIssueInfo
        self.selectAnimation()
        
    def move(self, vTargetPos):
        """ Update location
        """
        
        super(SWBug,self).move(vTargetPos)
        self.sog.AbsolutePosition = vTargetPos
    
    def selectAnimation(self):
        """ Choose animation by evaluating status of the enhancement
        """
        print "bugin status: ", self.issueinfo.status
        
        if self.issueinfo.status == "New":
            self.rop.RexAnimationName = "flying"
        
        elif self.issueinfo.status == "Started":
            print "bug started"
            self.rop.RexAnimationName = "flying_with_movement"
            
        else:
            pass
            #self.rop.RexAnimationName = "idle"
            
        self.rop.RexAnimationRate = 4.0