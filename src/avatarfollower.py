import threading

import rxevent

import clr

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types


class AvatarFollower(object):
    def __init__(self,vScene,vSog,vNames):
        self.scene = vScene
        self.sog = vSog
        self.rop = None
        
        self.login = vNames[0]
        self.name = vNames[1]
        
        self.avatar = None
        self.bFollowing = False
            
        self.OnAvatarEntered = rxevent.RexPythonEvent()
        self.OnAvatarExited = rxevent.RexPythonEvent()
        
        rexpy = None
        
        try:
            rexpy = self.scene.Modules["RexPythonScriptModule"]
        except KeyError:
            self.rexif = None
            #print "Couldn't get a ref to RexSCriptInterface"
        
        if rexpy:    
            self.rexif = rexpy.mCSharp
        
        #start observing if developers avatar enters to a region
        self.scene.EventManager.OnNewPresence += self.OnNewPresenceEntered
        
        #start observing if developers avatar leaves region
        self.scene.EventManager.OnRemovePresence += self.OnPresenceLeaved
    
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
                else:
                    return
                    
            print "about to attach dev in to a avatar"
            mesh_local_id = self.sog.RootPart.LocalId
            
            pos_lsl = LSL_Types.Vector3(0, 0, 2)
            rot_lsl = LSL_Types.Quaternion(0, 0, 0, 1)


            #attach to skull...
            self.rexif.rexAttachObjectToAvatar(mesh_local_id.ToString(),self.avatar.UUID.ToString(), 2,pos_lsl, rot_lsl, False)
            self.timer = 0
    
    
    def OnNewPresenceEntered(self,vScenePresence):
        name = vScenePresence.Firstname + " " + vScenePresence.Lastname
        print "avatar entered: ", name
        
        if name == self.name or vScenePresence.Firstname == self.login:
            print "avatar name matched"
            self.bFollowing = True
            self.OnAvatarEntered
            
            self.avatar = vScenePresence
            self.timer = threading.Timer(2, self.AttachToAvatar)
            self.timer.start()  
            
    def OnPresenceLeaved(self,vScenePresenceUUID):
        if self.avatar:
            if vScenePresenceUUID == self.avatar.UUID:
                self.DropFromAvatar()
                self.bFollowing = True
            
                self.OnAvatarExited()
                self.avatar = 0
                
    def DropFromAvatar(self):
        clientview = self.avatar.ControllingClient
        print "Droppig dev from avatar"
        self.scene.DetachSingleAttachmentToGround(self.sog.RootPart.UUID,clientview)
        self.scene.DeleteSceneObject(self.sog,False)
        
        self.sog = 0

        
