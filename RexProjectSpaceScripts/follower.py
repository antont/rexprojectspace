import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

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
        self.MyWorld.MyEventManager.onAddPresence += self.OnAvatarEntered
        print "follower id: ",self.Id
        act = self.MyWorld.GetActorByLocalID(self.Id)
        print "_______________",act
        
        print "follower.Follower EventCreated"

    def EventDestroyed(self):
        print "follower.Follower EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        print vAvatar
        self.llShout(0,"Following avatar")
        self.AgentId = vAvatar.AgentId
        
        print "followers id: ",self.Id
        
        posvec = Vector3(0, 0, 0) #should add some offset...
        point = 42
        self.AttachObjectToAvatar(vAvatar.AgentId,point,posvec)
    
    def SetAvatarName(self,vAvatarName):
        self.avatarname = vAvatarName
    
    def OnAvatarEntered(self,vAvatar):
        print "++++++++++++++avatar+++++++++++:",vAvatar.GetFullName()
    