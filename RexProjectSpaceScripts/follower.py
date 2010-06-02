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
        
        print "follower.Follower EventCreated"

    def EventDestroyed(self):
        print "follower.Follower EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        
        self.llShout(0,"Following avatar")
        self.AgentId = vAvatar.AgentId
        posvec = Vector3(0, 1, 2) #should add some offset...
        point = 42
        self.AttachObjectToAvatar(vAvatar.AgentId,point,posvec)
        self.set
        