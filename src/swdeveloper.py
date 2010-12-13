import rexprojectspaceutils
import rexprojectspacedataobjects
import rexprojectspacemodule
import scriptbridgemodule
import avatarfollower
import rexprojectspacenotificationcenter
import clickhandler

import clr

import threading

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types

def material(vTextureId):
    return """
material Template/TransparentTexture
 {
   technique
   {
     pass
     {
       lighting off
       scene_blend alpha_blend
       depth_write off
 
       texture_unit
       {
         %s
         alpha_op_ex source1 src_manual src_texture 0.8      
       }
     }
   }
 }
"""%(vTextureId)  
  
class SWDeveloper:
    """ Class representing a software developer
    """
    greentextureid = 0
    redtextureid = 0
    
    HEIGHT = 0.85
    MESHUUID = OpenMetaverse.UUID.Zero
    SKELETON_ANIM_ID = OpenMetaverse.UUID.Zero

    def __init__(self,vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):
        """ Load mesh and animation package. Create avatar follower that registers
            to listen to state changes related to opensim avatar enter/exit events
        """

        self.scene = vScene
        self.developerinfo = vDeveloperInfo
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        self.script = None
        self.skeleton_anim_id = OpenMetaverse.UUID.Zero
        
        
        if SWDeveloper.greentextureid == 0:
            SWDeveloper.greentextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devgreen.jp2")
            SWDeveloper.redtextureid = rexprojectspaceutils.load_texture(self.scene,"rpstextures/devred.jp2")
        
        self.currenttexid = SWDeveloper.greentextureid
        
        sop =  vScene.GetSceneObjectPart("rps_dev_" + self.developerinfo.login)
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "Developer: %s found from scene"%(self.developerinfo.login)
            SWDeveloper.MESHUUID = self.rop.RexMeshUUID.ToString()
            
        else:
            if SWDeveloper.MESHUUID == OpenMetaverse.UUID.Zero:
                print "loading dev mesh"
                SWDeveloper.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"rpsmeshes/diamond.mesh","developer mesh")
                
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,SWDeveloper.MESHUUID,"rpsmeshes/diamond.material",OpenMetaverse.Quaternion(0, 0, 0, 1), V3(128, 128, 30),
                                                                V3(0.5, 0.5, 0.5))
            
            """
            mat = material(SWDeveloper.greentextureid)
            FILE = open("matgen.material","w")
            FILE.write(mat)
            FILE.close()
            
            uuid  = rexprojectspaceutils.load_material_from_string(self.scene,"matgen.material","devmat")
            print "uidi", uuid
            self.rop.RexMaterials.AddMaterial(1,OpenMetaverse.UUID(SWDeveloper.greentextureid))
            self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(uuid))
            """
            
            self.initVisualization(self.sog)
        if self.developerinfo.login == "":
            self.developerinfo.login = self.developerinfo.name
            
        self.SetText(self.developerinfo.login + " : "  + self.developerinfo.latestcommit.message)        
        
        self.newposition = self.sog.AbsolutePosition
        self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
        self.rop.RexAnimationName = ""
        
        self.follower = avatarfollower.AvatarFollower(vScene,self.sog,[vDeveloperInfo.login,vDeveloperInfo.name])

        self.follower.OnAvatarEntered += self.AvatarEntered
        self.follower.OnAvatarExited += self.AvatarExited
        
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter("naali")
        nc.OnNewCommit += self.OnNewCommit
        
        self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.developerinfo.url)
        
    def initVisualization(self,sog):
        """ Choose scale based on commit count and set opensim sceneobjectgroups
            text to be developers login...
        """
        sog.RootPart.Name =  "rps_dev_" + self.developerinfo.login
        #sog.RootPart.Scale = V3(0.2, 0.2,  0.2)
        self.updateVisualization()
        print "Current texture id_____",self.currenttexid
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))

    def updateVisualization(self):
        """ Updates scale based on commit count 
        """
        scale = self.sog.RootPart.Scale
        scalefactor = self.developerinfo.commitcount
        
        if scalefactor > 100:
            scalefactor = 100
        elif scalefactor < 50:
            scalefactor = 50
            
        self.sog.RootPart.Scale = V3(scalefactor*0.01,scalefactor*0.01,scalefactor*0.01)
    
    def updateIsLatestCommitter(self,vIsLatestCommitter):
        """ Change animation
        """
        if vIsLatestCommitter:
            #self.skeleton_anim_id = rexprojectspaceutils.load_skeleton_animation(self.scene,"diamond.skeleton")
            
            #self.rop.RexAnimationPackageUUID = self.skeleton_anim_id
            self.rop.RexAnimationName = "jump"
        else:
            self.rop.RexAnimationPackageUUID = OpenMetaverse.UUID.Zero
    
    def updateDidBrakeBuild(self,vDidBrakeBuild):
        """ Change texture if you brake the build 
        """
        print "developer did brake build?"
        if vDidBrakeBuild == True and self.currenttexid == SWDeveloper.redtextureid:
            return
        elif vDidBrakeBuild == False and self.currenttexid == SWDeveloper.greentextureid:
            return
        
        tex = self.currenttexid
        if vDidBrakeBuild:
            tex =  SWDeveloper.redtextureid
        else:
            tex =  SWDeveloper.greentextureid
           
        self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        self.currenttexid = tex
        
    
    def AvatarEntered(self):
        """ Store current position, so that we remember where to
            go when avatar exits """
        self.newposition = self.sog.AbsolutePosition
    
    def AvatarExited(self):
        """ Move developer to a place where it was before avatar entered
            or if position was updated (because of new commit, for example)
            move to a new location
        """
        self.move(self.newposition)
        
    def move(self, vTargetPos):
        self.newposition = vTargetPos
        if self.follower.bFollowing == False:
            self.sog.NonPhysicalGrabMovement(vTargetPos)
    
    def OnNewCommit(self,vCommit):
        #print "Login: ", vCommit.login
        if vCommit.login == self.developerinfo.login:
            #so, these commits are processed at runtime, not at initializing phase
            #update also the developervisualization
            """
            self.developerinfo.commitcount += 1
            self.developerinfo.latestcommit = vCommit
            self.developerinfo.latestcommitid = vCommit.id
            
            self.updateVisualization()
            """
            self.SetText(self.developerinfo.login + " : "  + vCommit.message)
    
    def SetText(self,text):
        """ Sets sceneobjectgroups text to be the text. In case of
            long string add some line breaks"""
        
        line_length = 25
        temp = ""
        if len(text) > 75:
            temp = text[0:72]#max 3 lines
            temp = temp + "..."
        else:
            temp = text
        
        
        if len(temp) > line_length:
            #print "splitting lines"
            linecount = int(len(temp)/line_length) 
            charcount = len(temp)
            #print "line count: ", linecount
            #print "with char count: ", charcount
            
            
            splitted = temp.split(" ")
            index = 0
            count = 0
 
            for i in range(1,linecount):
                cur = i*line_length
                #must not split words!
                #locate nearest space char
                l = temp.find(" ",cur,len(temp))
                temp = temp[:l] + "\n" + temp[l:]
            
            #print temp
        
        self.sog.SetText(temp,V3(0.0,1.0,0.5),1.0)
    