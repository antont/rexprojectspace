import rexprojectspaceutils
import commitdispatcher

class SWDeveloper:

    def __init__(self, vScene,vDeveloperInfo, vIsAtProjectSpace ,vAvatar = None):
        self.scene = vScene
        self.developerinfo = vDeveloperInfo
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        
        self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        self.sog.RootPart.Name =  self.developerinfo.login
        self.scene.AddNewSceneObject(self.sog, False)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
        
        #start receiving commits for project, not needed at the moment
        #commitdispatcher.CommitDispatcher.register(self.updateCommitData,"naali",self.developerinfo.login)
        print "dev: %s---created---"%(vDeveloperInfo.login)
        
    def updateCommitData(self, vCommitData):
        pass
        #print "updating developer vis. with: ", vNewCommit
        #update visualization also...
        
        
    def updateIsAtProjectSpace(self, vAtProjectSpace):
        """update visualization if necessary """
        if self.isAtProjectSpace == False and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isAtProjectSpace == True and vAtProjectSpace == False:
            pass
        elif self.isAtProjectSpace == True and vAtProjectSpace == True:
            if not self.rop.RexClassName == "follower.Follower":
                self.rop.RexClassName = "follower.Follower"
        elif self.isAtProjectSpace == False and vAtProjectSpace == False:
            pass
        self.isAtProjectSpace = vAtProjectSpace