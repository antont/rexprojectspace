import rexprojectspaceutils
import rexprojectspacedataobjects
import rexprojectspacemodule
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
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        
        self.initVisualization()
        self.newposition = self.sog.AbsolutePosition

        #start observing if developers avatar enters to a region
        self.scene.EventManager.OnNewPresence += self.OnNewPresenceEntered
        
        #start observing if developers avatar leaves region
        self.scene.EventManager.OnRemovePresence += self.OnPresenceLeaved
        
    
    def __del__(self):
        self.scene.EventManager.OnNewPresence -= self.OnNewPresenceEntered
        self.scene.EventManager.OnRemovePresence -= self.OnPresenceLeaved
    
    def initVisualization(self):
        self.sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
        
        scalefactor = self.developerinfo.commitcount
        self.sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        self.sog.SetText(self.developerinfo.login,V3(0.0,1.0,0.5),1.0)
        
    def move(self, vTargetPos):
        self.newpos = vTargetPos
        if self.avatar != None:
            dev.sog.NonPhysicalGrabMovement(vTargetPos)
        
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
    
    def AttachToAvatar(self):
        if self.avatar:
            if not self.rexif:
                try:
                    rexpy = self.scene.Modules["RexPythonScriptModule"]
                except KeyError:
                    self.rexif = None
                    #print "Couldn't get a ref to RexSCriptInterface"
                
                if rexpy:    
                    self.rexif = rexpy.mCSharp

            print "about to attach dev in to a avatar"
            mesh_local_id = self.sog.RootPart.LocalId
            
            print mesh_local_id
            
            pos_lsl = LSL_Types.Vector3(0, 0, 2)
            rot_lsl = LSL_Types.Quaternion(0, 0, 0, 1)
            
            #clientview = self.avatar.ControllingClient
            #self.scene.AttachObject(clientview,self.avatar.UUID.ToString(), 1,pos_lsl, rot_lsl, False)

            #attach to skull...
            self.rexif.rexAttachObjectToAvatar(mesh_local_id.ToString(),self.avatar.UUID.ToString(), 2,pos_lsl, rot_lsl, False)
            self.timer = 0
    
    def OnNewPresenceEntered(self,vScenePresence):
        name = vScenePresence.Firstname + " " + vScenePresence.Lastname
        print "avatar entered: ", name
        
        if name == self.developerinfo.login or vScenePresence.Firstname == self.developerinfo.login:
            print "avatar name matched"
            self.newposition = self.sog.AbsolutePosition
            self.avatar = vScenePresence
            self.timer = threading.Timer(2, self.AttachToAvatar)
            self.timer.start()  
            
    def OnPresenceLeaved(self,vScenePresenceUUID):
        if self.avatar:
            if vScenePresenceUUID == self.avatar.UUID:
                self.DropFromAvatar()
                
    def DropFromAvatar(self):
        clientview = self.avatar.ControllingClient
        print "Droppig dev from avatar"
        self.scene.DetachSingleAttachmentToGround(self.sog.RootPart.UUID,clientview)
        self.scene.DeleteSceneObject(self.sog,False)
        
        #self.avatar.Appearance.DetachAttachment(self.sog.UUID)
        self.sog = 0 #for some reason sog gets deleted
        self.rop = 0
        
        self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        self.initVisualization()
        self.move(self.newposition)
        
        
            