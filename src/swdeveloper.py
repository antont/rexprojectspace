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
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
       
        self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero

        self.rop.RexClassName = ""
        
        #print "dev: %s---created---"%(vDeveloperInfo.login)
        
        self.sog.SetText(self.developerinfo.login,V3(0.0,1.0,0.5),1.0)
        
    
    def updateCommitData(self, vCommitData):
        pass
        ##print "updating developer vis. with: ", vNewCommit
        #update visualization also...
        
    def updateIsAtProjectSpace(self, vAtProjectSpace):
        """update visualization if necessary """
        
        #print "local id for dev: ",self.sog.LocalId
        #self.sog.LocalId.ToString()
        #actor = self.mod.GetActor("1338755245")
        ##print actor
        #actor.SetAvatarName(self.developerinfo.login)
        
        """
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
        """

        
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
            rot_lsl = LSL_Types.Quaternion(0, 0, 1, 1)
            
            #clientview = self.avatar.ControllingClient
            #self.scene.AttachObject(clientview,self.avatar.UUID.ToString(), 1,pos_lsl, rot_lsl, False)

            
            self.rexif.rexAttachObjectToAvatar(mesh_local_id.ToString(),self.avatar.UUID.ToString(), 1,pos_lsl, rot_lsl, False)
            self.timer = 0
    
    def OnNewPresenceEntered(self,vScenePresence):
        name = vScenePresence.Firstname + " " + vScenePresence.Lastname
        print "avatar entered: ", name
        
        if name == self.developerinfo.login:
            print "avatar name matched"
            self.avatar = vScenePresence
            self.timer = threading.Timer(2, self.AttachToAvatar)
            self.timer.start()  
        
        
            
    def OnPresenceLeaved(self,vScenePresenceUUID):
        if self.avatar:
            if vScenePresenceUUID == self.avatar.UUID:
                self.DropFromAvatar()
                #self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        
                #self.initVisualization()
        
                
    def DropFromAvatar(self):
        clientview = self.avatar.ControllingClient
        print "Droppig dev from avatar"
        #self.scene.DetachSingleAttachmentToGround(self.sog.RootPart.UUID,clientview)
        #self.avatar.Appearance.DetachAttachment(self.sog.UUID)
        #self.sog = 0 #for some reason sog gets deleted
        #self.rop = 0
        
            