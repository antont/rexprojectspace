
import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')
Vector3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

import rexprojectspacemodule
import rexprojectspaceutils

class RexProjectSpace(RXCore.rxactor.Actor):
    world2 = None
    
    @staticmethod
    def GetScriptClassName():
        return "rexprojectspace.RexProjectSpace"
    
    @classmethod
    def GetWorld(cls):
        print "getting world: " , cls.world2 
        return cls.world2
    
    @classmethod
    def setWorld(cls,vWorld):
        cls.world2 = vWorld
           
    
    @classmethod
    def getDeveloper(cls,vName):
        pass
        
    def getActor(self,vUUID):
        pass
    
    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        
        print "rexprojectspace.RexProjectSpace EventCreated-------------"
        RexProjectSpace.world2 = "maalima..."
        print "+++++++world: ", self.MyWorld
        
        
    def EventDestroyed(self):
        print "rexprojectspace.RexProjectSpace EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass
       