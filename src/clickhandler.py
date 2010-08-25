import clr
import scriptbridgemodule

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework


class URLOpener:
    """ Simple utility class to handle clicks and open given url """
    def __init__(self,vScene,sog,rop,vUrl):
        """ Create new actor if needed """
        self.scene = vScene
        self.sog = sog
        self.url = vUrl
        self.mod = None
        self.scene.EventManager.OnObjectGrab += self.clicked;
        
        if rop.RexClassName == "":
            print "create new actor"
            rop.RexClassName = "rxactor.Actor"

    def clicked(self,vLocalID,vOriginalID, vOffsetPos, vRemoteClient, vSurfaceArgs):
        """ Handler for opensim touch event, check if correct item was touched
            and then open url"""
        if vLocalID == self.sog.RootPart.LocalId:
            print "click to URL:", self.url
            if not self.mod:
                try:
                    self.mod = self.scene.Modules["ScriptBridgeModule"]
                    print "Got bridge module...", self.mod
                except:
                    return
                
            actor = self.mod.GetActorWithLocalID(str(self.sog.LocalId))
            print "Actor: ", actor
            if actor:
                actor.llLoadURL(str(vRemoteClient.AgentId),"Openingn URL: %s"%(self.url),self.url)
                print "hello"
        