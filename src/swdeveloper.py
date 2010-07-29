import rexprojectspaceutils
import rexprojectspacedataobjects
import rexprojectspacemodule
import avatarfollower
import rexprojectspacenotificationcenter

import clr

import threading

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types

class SWDeveloper:
    """ Class representing a software developer
    """
    greentextureid = 0
    redtextureid = 0
    
    HEIGHT = 1.0

    def __init__(self,vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):
        """ Load mesh and animation package. Create avatar follower that registers
            to listen to state changes related to opensim avatar enter/exit events
        """

        self.scene = vScene
        self.developerinfo = vDeveloperInfo
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        self.script = None
        self.skeleton_anim_id = OpenMetaverse.UUID.Zero
        
        try:
            rexpy = self.scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            #print "Couldn't get a ref to RexSCriptInterface"
        
        if rexpy:    
            self.rexif = rexpy.mCSharp
        
        sop =  vScene.GetSceneObjectPart("rps_dev_" + self.developerinfo.login)
        self.currenttexid = SWDeveloper.greentextureid
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"diamond.mesh","diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.initVisualization(self.sog)
            
        if SWDeveloper.greentextureid == 0:
            SWDeveloper.greentextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devgreen.jp2")
            SWDeveloper.redtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devred.jp2")
        
        self.newposition = self.sog.AbsolutePosition
        self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
        self.rop.RexAnimationName = ""
        
        self.follower = avatarfollower.AvatarFollower(vScene,self.sog,[vDeveloperInfo.login,vDeveloperInfo.name])

        self.follower.OnAvatarEntered += self.AvatarEntered
        self.follower.OnAvatarExited += self.AvatarExited
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        #nc.OnNewCommit += self.updateCommitText
        nc.OnNewIrcMessage += self.OnNewIRCMessage
    
    def initVisualization(self,sog):
        """ Choose scale based on commit count and set opensim sceneobjectgroups
            text to be developers login...
        """
        sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
        sog.RootPart.Scale = V3(0.2, 0.2,  0.2)
        self.updateVisualization()
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
        
        self.SetText(self.developerinfo.login)
        
    def updateVisualization(self):
        """ Updates scale based on commit count 
        """
        scale = self.sog.RootPart.Scale
        scalefactor = self.developerinfo.commitcount
        self.sog.RootPart.Scale = V3(scale.X + scalefactor*0.02,scale.Y + scalefactor*0.02,scale.Z + scalefactor*0.02)
    
    def updateIsLatestCommitter(self,vIsLatestCommitter):
        """ Change animation
        """
        if vIsLatestCommitter:
            self.skeleton_anim_id = rexprojectspaceutils.load_skeleton_animation(self.scene,"diamond.skeleton")
            
            self.rop.RexAnimationPackageUUID = self.skeleton_anim_id
            self.rop.RexAnimationName = "jump"
        else:
            self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
    
    def updateDidBrakeBuild(self,vDidBrakeBuild):
        """ Change texture if you brake the build 
        """
        if vDidBrakeBuild and self.currenttexid == SWDeveloper.redtextureid:
            return
        elif vDidBrakeBuild == False and self.currenttexid == SWDeveloper.greentextureid:
            return
        
        tex = self.currenttexid
        if vDidBrakeBuild:
            tex =  SWDeveloper.redtextureid
        else:
            tex =  SWDeveloper.greentextureid
           
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        self.currenttexid = tex
        
    
    def AvatarEntered(self):
        """ Store current position, so that we remember where to
            go when avatar exits """
        self.newposition = self.sog.AbsolutePosition
    
    def AvatarExited(self):
        """ Move developer to a place where it was before avatar entered
            or if position was updated (because of new commit, for example)
            move to a new location
        """
        self.move(self.newposition)
        
    def move(self, vTargetPos):
        self.newposition = vTargetPos
        if self.follower.bFollowing == False:
            self.sog.NonPhysicalGrabMovement(vTargetPos)
    
    def OnNewIRCMessage(self,vMessage):
        """ Display new IRC message
        """
        text = vMessage
        self.SetText(text)
    
    def SetText(self,text):
        """ Sets sceneobjectgroups text to be text... """
        self.sog.SetText(text,V3(0.0,1.0,0.5),1.0)
    