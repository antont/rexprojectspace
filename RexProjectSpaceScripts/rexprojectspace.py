
import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')
Vector3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

import rexprojectspacemodule

class RexProjectSpace(RXCore.rxactor.Actor):
    world2 = None
    
    @staticmethod
    def GetScriptClassName():
        return "rexprojectspace.RexProjectSpace"
    
    @staticmethod
    def GetWorld():
        print "getting world: " , RexProjectSpace.world2 
        return RexProjectSpace.world2
               
        
    def getActor(self,vUUID):
        pass
    
    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        if RexProjectSpace.world2 == None:
            print "setting world: ", self.MyWorld
            RexProjectSpace.world2 = "joo"
            print RexProjectSpace.world2
            print self.world2
        else:
            print "world set, : ", RexProjectSpace.world2
        print "rexprojectspace.RexProjectSpace EventCreated"
        
        rexprojectspacemodule.SetWorld("...")

    def EventDestroyed(self):
        print "rexprojectspace.RexProjectSpace EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass
       