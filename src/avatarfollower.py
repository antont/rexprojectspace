import threading
import clr

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types

import rxevent

class AvatarFollower(object):
    """ Listens to opensim's avatar entered/exited events and 
        reports those events. Also attaches given SceneObjectGroup
        when avatar enters and Detaches SceneObjectGroup to the ground
        when avatar exits
    """
    def __init__(self,vScene,vSog,vNames):
        """ Start listen to opensim events
        """
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
        """ Attaches object to avatars skull... """
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
        """ Calls AttachToAvatar after 2 seconds, attaching objects
            while handling OnNewPresence event from opensim
            did not work.
        """
        name = vScenePresence.Firstname + " " + vScenePresence.Lastname
        print "avatar entered: ", name
        
        if name == self.name or vScenePresence.Firstname == self.login:
            print "avatar name matched"
            self.bFollowing = True
            self.OnAvatarEntered()
            
            self.avatar = vScenePresence
            self.timer = threading.Timer(2, self.AttachToAvatar)
            self.timer.start()  
            
    def OnPresenceLeaved(self,vScenePresenceUUID):
        """ Drops attachement from the avatar and Call observers 
            callback function to handle avatar exit 
        """
        if self.avatar:
            if vScenePresenceUUID == self.avatar.UUID:
                self.DropFromAvatar()
                self.bFollowing = False
            
                self.OnAvatarExited()
                self.avatar = 0
                
    def DropFromAvatar(self):
        """ Drop attachement from the avatar.
        """
        clientview = self.avatar.ControllingClient
        print "Droppig dev from avatar"
        #self.scene.DetachSingleAttachmentToGround(self.sog.RootPart.UUID,clientview)
        #self.scene.DeleteSceneObject(self.sog,False)
        self.sog.DetachToGround()
