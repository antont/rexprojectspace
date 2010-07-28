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
    
    greentextureid = 0
    redtextureid = 0
    
    HEIGHT = 1.0

    def __init__(self, vMod,vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):

        self.mod = vMod
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

        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"diamond.mesh","diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.initVisualization(sog)
            
        if SWDeveloper.greentextureid == 0:
            SWDeveloper.greentextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devgreen.jp2")
            SWDeveloper.redtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devred.jp2")
        
        self.currenttexid = SWDeveloper.greentextureid

        self.newposition = self.sog.AbsolutePosition
        self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
        self.rop.RexAnimationName = ""
        
        self.follower = avatarfollower.AvatarFollower(vScene,self.sog,[vDeveloperInfo.login,vDeveloperInfo.name])

        self.follower.OnAvatarEntered += self.AvatarEntered
        self.follower.OnAvatarExited += self.AvatarExited
    
    def __del__(self):
        self.scene.EventManager.OnNewPresence -= self.OnNewPresenceEntered
        self.scene.EventManager.OnRemovePresence -= self.OnPresenceLeaved
    
    def initVisualization(self,sog):
        sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
        sog.RootPart.Scale = V3(0.2, 0.2,  0.2)
        self.updateVisualization()
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
        
        sog.SetText(self.developerinfo.login,V3(0.0,1.0,0.5),1.0)
        
    def updateVisualization(self):
        scale = self.sog.RootPart.Scale
        scalefactor = self.developerinfo.commitcount
        self.sog.RootPart.Scale = V3(scale.X + scalefactor*0.02,scale.Y + scalefactor*0.02,scale.Z + scalefactor*0.02)

        
        print "updating developer vis. with: ", str(scalefactor)
        #update visualization also...
    
    def updateIsLatestCommitter(self,vIsLatestCommitter):
        if vIsLatestCommitter:
            self.skeleton_anim_id = rexprojectspaceutils.load_skeletonanimation(self.scene,"diamond.skeleton")
            
            self.rop.RexAnimationPackageUUID = self.skeleton_anim_id
            self.rop.RexAnimationName = "jump"
        else:
            self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
    
    def updateDidBrakeBuild(self,vDidBrakeBuild):
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
        self.newposition = self.sog.AbsolutePosition
    
    def AvatarExited(self):
        
        self.follower.sog = self.sog 
        
        # self.initVisualization(self.sog)
        self.move(self.newposition)
        
    def move(self, vTargetPos):
        self.newposition = vTargetPos
        if self.follower.bFollowing == False:
            self.sog.NonPhysicalGrabMovement(vTargetPos)
            