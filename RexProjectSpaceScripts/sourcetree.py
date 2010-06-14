import RXCore.rxactor
import RXCore.rxavatar
import sys
import clr

import random
import math

import rexprojectspaceutils

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')
Vector3 = asm.OpenSim.Region.ScriptEngine.Shared.LSL_Types.Vector3

class BurningTree(RXCore.rxactor.Actor):
    @staticmethod
    def GetScriptClassName():
        return "sourcetree.BurningTree"

    def EventCreated(self):
        super(self.__class__,self).EventCreated()
        
        id = rexprojectspaceutils.load_particle_script("myfire.particle")
        self.SetRexParticleScriptUUID(id)
        
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
        
        id = rexprojectspaceutils.load_particle_script("snow.particle")
        self.SetRexParticleScriptUUID(id)
        
        print "sourcetree.Rain EventCreated"

    def EventDestroyed(self):
        print "sourcetree.Rain EventDestroyed"
        self.SetRexParticleScriptUUID("")
        
        super(self.__class__,self).EventDestroyed()

    def EventTouch(self,vAvatar):
        pass      