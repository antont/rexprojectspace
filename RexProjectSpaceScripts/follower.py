import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

import rexprojectspaceutils

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')
Vector3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

class Follower(RXCore.rxactor.Actor):
    @staticmethod
    def GetScriptClassName():
        return "follower.Follower"

    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        self.va= "abcd"
        self.avatarname = ""
        
        self.llSetScale(Vector3(1,1,1))
        self.llSetStatus(16,1)
        self.SetRexDrawType(1)
        
        #uuid = rexprojectspaceutils.load_mesh_new(self.MyWorld,"Diamond.mesh")
        #self.SetRexMeshUUID(OpenMetaverse.UUID(uuid))
            
        #self.MyWorld.MyEventManager.onAddPresence += self.OnAvatarEntered
        print "follower id: ",self.Id
        #act = self.MyWorld.GetActorByLocalID(self.Id)
        
        #print "_______________",act
        print "follower mesh uuid: ", self.GetRexMeshUUID()
        
        self.timer = self.CreateRexTimer(2,1)
        self.timer.onTimer += self.GetModule
        self.timer.Start()
        
        print "follower.Follower EventCreated"
    
    def GetModule(self):
        try:
            module = self.MyWorld.CS.World.Modules["RexProjectSpaceModule"]
            self.module = module
            print "module set"
            #self.timer = 0
            
            #now get the data related to this script instance
            self.avatarname = module.GetData(self.GetRexMeshUUID())
            print self.avatarname
            
        except:
            print "did not get RexProjectSpaceModule"
            #self.timer = 0
            self.timer.Start()
            
            return
    
    def SetScene(self,vScene):
        self.scene = vScene
        
    def SetUUIDAndAvatarName(self,vMeshUUID,vAvatarName):
        
        print "Follower::avatar name set to ", vAvatarName
        
        self.avatarname = vAvatarName
        self.llSetScale(Vector3(1,1,1))
        self.llSetStatus(16,1)
        self.SetRexDrawType(1)
        self.SetRexMeshUUID(vMeshUUID.ToString())
    
    def EventDestroyed(self):
        print "follower.Follower EventDestroyed"
        print "follower id: ",self.Id
        #self.MyWorld.MyEventManager.onAddPresence -= self.OnAvatarEntered
        
        #this object should be temporary, so we need to delete this manually
        try:
            rexpy = self.scene.Modules["RexPythonScriptModule"]
            rexif = rexpy.mCSharp
            #rexif.DestroyActor(self.Id)
            print "destroyed"
        except KeyError:
            self.rexif = None
        
        super(self.__class__,self).EventDestroyed()
        
        
    def EventTouch(self,vAvatar):
        #print vAvatar
        self.llShout(0,"Following avatar")
        name = vAvatar.GetFullName()
        print "avatar entered: ",name, " and followers name is: ",self.avatarname
        #if name == self.avatarname:
        print "match"
        posvec = Vector3(0, 1, 2) #should add some offset...
        point = 2
        self.AttachObjectToAvatar(vAvatar.AgentId,point,posvec)

    def SetAvatarName(self,vAvatarName):
        self.avatarname = vAvatarName
    
    def OnAvatarEntered(self,vAvatar):
        
        name = vAvatar.GetFullName()
        print "avatar entered: ",name, " and followers name is: ",self.avatarname
        if name == self.avatarname:
            print "match"
            posvec = Vector3(0, 0, 1) #should add some offset...
            point = 2
            self.AttachObjectToAvatar(vAvatar.AgentId,point,posvec)
            