
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

from System.Collections.Generic import List as GenericList

class RexProjectSpace(RXCore.rxactor.Actor):
    
    @staticmethod
    def GetScriptClassName():
        return "rexprojectspace.RexProjectSpace"
    
    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        self.timer = self.CreateRexTimer(2,1)
        self.timer.onTimer += self.SetSpawnerInstance
            
        self.SetSpawnerInstance()
        
        
        
    def EventDestroyed(self):
        #print "rexprojectspace.RexProjectSpace EventDestroyed"
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass
    
    def SetSpawnerInstance(self):
        try:
            module = self.MyWorld.CS.World.Modules["ScriptBridgeModule"]
            module.SetWorld(self.MyWorld)
            print "spawner set!"
            self.timer = 0
            
        except:
            print "did not get RexProjectSpaceModule"
            self.timer = 0
            self.timer.Start()
            return
        

    