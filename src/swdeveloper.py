import rexprojectspaceutils
import commitdispatcher

class SWDeveloper:

    def __init__(self, vScene,vName, vNumberOfCommits, vLatesCommit, vIsAtProjectSpace, vAvatar=None):
        print "dev---created---"
        self.scene = vScene
        self.name = vName
        self.numberOfCommits = vNumberOfCommits
        self.latesCommit = vLatesCommit
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        
        self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
        self.sog.RootPart.Name =  vName
        self.scene.AddNewSceneObject(self.sog, False)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)

        
        #start receiving commits for project
        commitdispatcher.CommitDispatcher.register(self.updateCommitData,"naali",self.name)
        
    def updateCommitData(self, vNewCommit):
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