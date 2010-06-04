import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')
Vector3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

class BurningTree(RXCore.rxactor.Actor):
    @staticmethod
    def GetScriptClassName():
        return "sourcetree.BurningTree"

    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        self.SetRexParticleScriptUUID("8cb876e0-6a42-4826-b2ca-84fce34ccecf")
        
        print "sourcetree.BurningTree EventCreated"

    def EventDestroyed(self):
        print "sourcetree.BurningTree EventDestroyed"
        self.SetRexParticleScriptUUID("")
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass

        
class Rain(RXCore.rxactor.Actor):
    @staticmethod
    def GetScriptClassName():
        return "sourcetree.Rain"

    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        self.SetRexParticleScriptUUID("c0401b49-8335-46d5-b3f1-7aa0f964eb65")
        
        print "sourcetree.Rain EventCreated"

    def EventDestroyed(self):
        print "sourcetree.Rain EventDestroyed"
        self.SetRexParticleScriptUUID("")
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass      