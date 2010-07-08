import rexprojectspaceutils
import rexprojectspacedataobjects
import rexprojectspacemodule
import avatarfollower

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

    HEIGHT = 1.0

    def __init__(self, vMod,vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):

        self.mod = vMod
        self.scene = vScene
        self.developerinfo = vDeveloperInfo
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        self.script = None
        self.skeleton_anim_id = 0
        
        try:
            rexpy = self.scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            #print "Couldn't get a ref to RexSCriptInterface"
        
        if rexpy:    
            self.rexif = rexpy.mCSharp
        
        sop =  vScene.GetSceneObjectPart("rps_dev_" + self.developerinfo.login)
        sog = 0
        rop = 0
        if sop:
            sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            rop = rexObjects.GetObject(sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            sog,rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        
        self.initVisualization(sog)
        self.newposition = sog.AbsolutePosition
        
        self.follower = avatarfollower.AvatarFollower(vScene,sog,[vDeveloperInfo.login,vDeveloperInfo.name])
        
        self.sog = sog
        self.rop = rop
        self.follower.OnAvatarEntered += self.AvatarEntered
        self.follower.OnAvatarExited += self.AvatarExited
    
    def __del__(self):
        self.scene.EventManager.OnNewPresence -= self.OnNewPresenceEntered
        self.scene.EventManager.OnRemovePresence -= self.OnPresenceLeaved
    
    def initVisualization(self,sog):
        sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
        
        scalefactor = self.developerinfo.commitcount
        sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        sog.SetText(self.developerinfo.login,V3(0.0,1.0,0.5),1.0)
        
    def updateCommitData(self, vCommitData):
        pass
        ##print "updating developer vis. with: ", vNewCommit
        #update visualization also...
    
    def updateIsLatestCommitter(self,vIsLatestCommitter):
        if vIsLatestCommitter:
            if self.skeleton_anim_id != OpenMetaverse.UUID.Zero:
                self.skeleton_anim_id = rexprojectspaceutils.load_skeletonanimation(self.scene,"Diamond.skeleton")
            self.rop.RexAnimationPackageUUID = self.skeleton_anim_id
            self.rop.RexAnimationName = "jump"
        else:
            self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
    
    def AvatarEntered(self):
        self.newposition = self.sog.AbsolutePosition
    
    def AvatarExited(self):
        
        #create visualization again, since follower destroys sog...
        self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        self.follower.sog = self.sog 
        
        self.initVisualization(self.sog)
        self.move(self.newposition)
        
    def move(self, vTargetPos):
        self.newposition = vTargetPos
        if self.follower.bFollowing:
            self.sog.NonPhysicalGrabMovement(vTargetPos)
            