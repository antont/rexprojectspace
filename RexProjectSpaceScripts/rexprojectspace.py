
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
    
    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        
        try:
            module = self.MyWorld.CS.World.Modules["RexProjectSpaceModule"]
        except:
            return
            
        print "________Module",module
        module.SetRexWorld(self.MyWorld)
        module.SetSpawner(self)
        
    def EventDestroyed(self):
        print "rexprojectspace.RexProjectSpace EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass
       