import rexprojectspaceutils
import commitdispatcher
import rexprojectspacedataobjects

import clr

import threading

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

class SWDeveloper:

    def __init__(self, vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):
        self.scene = vScene
        self.developerinfo = vDeveloperInfo
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        self.script = None
        self.timer = None
        
        sop =  vScene.GetSceneObjectPart("rps_dev_" + self.developerinfo.login)
             
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
        else:    
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
            self.scene.AddNewSceneObject(self.sog, False)
        
        scalefactor = vDeveloperInfo.commitcount
        #self.sog.RootPart.Resize(V3(0.1,0.1,0.1))
        self.sog.RootPart.Scale = V3(scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2, scalefactor*0.01 + 0.2)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
        
        #start receiving commits for project, not needed at the moment
        #commitdispatcher.CommitDispatcher.register(self.updateCommitData,"naali",self.developerinfo.login)
        
        #start observing if developers avatar enters to a region
        self.scene.EventManager.OnNewPresence += self.OnNewPresenceEntered
        print "dev: %s---created---"%(vDeveloperInfo.login)
    
    def __del__(self):
        self.scene.EventManager.OnNewPresence -= self.OnNewPresenceEntered
        
    def updateCommitData(self, vCommitData):
        pass
        #print "updating developer vis. with: ", vNewCommit
        #update visualization also...
        
        
    def updateIsAtProjectSpace(self, vAtProjectSpace):
        """update visualization if necessary """
        if self.isAtProjectSpace == False and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
                self.timer = threading.Timer(1,self.OnScriptMaybeCreated)
        elif self.isAtProjectSpace == True and vAtProjectSpace == False:
            pass
        elif self.isAtProjectSpace == True and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isAtProjectSpace == False and vAtProjectSpace == False:
            pass
        self.isAtProjectSpace = vAtProjectSpace
    
    def OnScriptMaybeCreated(self):
        #try to get script
        module = self.scene.Modules["RexProjectSpaceModule"]
        print "Local id: ", (self.sog.LocalId)
        avr = module.GetActor(self.sog.LocalId.ToString())
        if not avr:
            self.timer.stop()
            self.timer.start()
            return
            
        print "#############avatar: ", avr
        
    
    def OnNewPresenceEntered(self,vScenePresence):
        #print "avatar entered: ", vScenePresence
        name = vScenePresence.Firstname + vScenePresence.Lastname
        print name
        print self.developerinfo.login
        if name == self.developerinfo.name or name == self.developerinfo.login or self.developerinfo.login == vScenePresence.Firstname :
            #self.updateIsAtProjectSpace(True)
            if self.rop.RexClassName == "follower.Follower":
                module = self.scene.Modules["RexProjectSpaceModule"]
                print "Local id: ", (self.sog.LocalId)
                avr = module.GetActor(self.sog.LocalId.ToString())
                print "---avatar----",avr
                
            self.avatar = vScenePresence
            print "located avatar!!!"
            
            