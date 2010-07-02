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
            #print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
            self.scene.AddNewSceneObject(self.sog, False)
        
        scalefactor = vDeveloperInfo.commitcount
        #self.sog.RootPart.Resize(V3(0.1,0.1,0.1))
        self.sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
       
        self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
       
        #start observing if developers avatar enters to a region
        self.scene.EventManager.OnNewPresence += self.OnNewPresenceEntered
        
        #start observing if developers avatar leaves region
        self.scene.EventManager.OnRemovePresence += self.OnPresenceLeaved
        
        self.rop.RexClassName = ""
        
        #print "dev: %s---created---"%(vDeveloperInfo.login)
        
        self.sog.SetText(vDeveloperInfo.login,V3(0.0,1.0,0.5),1.0)
        
        
    
    def __del__(self):
        self.scene.EventManager.OnNewPresence -= self.OnNewPresenceEntered
        
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
        
    def OnNewPresenceEntered(self,vScenePresence):
        ##print "avatar entered: ", vScenePresence
        """
        name = vScenePresence.Firstname + vScenePresence.Lastname
        #print name
        #print self.developerinfo.login
        if name == self.developerinfo.name or name == self.developerinfo.login or self.developerinfo.login == vScenePresence.Firstname :
            #self.updateIsAtProjectSpace(True)
            #print "located avatar!!!"
            avatarpos = self.sog.AbsolutePosition
            for ent in self.scene.GetEntities():
                ##print ent
                if self.sog.UUID == ent.UUID:
                    #print "local matched rexmeshuuid"
                    mesh_localid = ent.LocalId
                    break

            pos = LSL_Types.Vector3(0, 0, 2) 
            self.rexif.rexAttachObjectToAvatar(mesh_localid.ToString(),
                                              vScenePresence.UUID.ToString(),
                                              42, pos, LSL_Types.Quaternion(0, 0, 0, 1), False)
                        
            self.avatar = vScenePresence
            """
            
        
        pass
            
    def OnPresenceLeaved(self,vScenePresence):
        if self.avatar:
            #print "avatart %s exited"%(vScenePresence)
            self.scene.DetachSingleAttachmentToGround(
                        self.sog.UUID,
                        self.avatar.ControllingClient)
            self.avatar = None   