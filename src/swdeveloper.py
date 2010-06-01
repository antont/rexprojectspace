import rexprojectspaceutils

class SWDeveloper:

    def __init__(self, vScene,vName, vNumberOfCommits, vLatesCommit, vIsAtProjectSpace, vAvatar=None):
        self.scene = vScene
        self.name = vName
        self.numberOfCommits = vNumberOfCommits
        self.latesCommit = vLatesCommit
        self.isAtProjectSpace = vIsAtProjectSpace
        self.avatar = vAvatar #rxavatar
        
        sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"Diamond.mesh","Diamond.material","test mesh data")
        self.scene.AddNewSceneObject(sog, False)
        
        self.updateIsAtProjectSpace(self.isAtProjectSpace)
        
    def updateCommitData(self, vNewCommit):
        self.numberOfCommits = self.numberOfCommits + 1
        self.latesCommit = vNewCommit
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