class SWDeveloper:

    def __init__(self, vName, vNumberOfCommits, vLatesCommit, vIsAtProjectSpace):
        self.name = vName
        self.numberOfCommits = vNumberOfCommits
        self.latesCommit = vLatesCommit
        self.isAtProjectSpace = vIsAtProjectSpace
        
    def updateCommitData(vNewCommit):
        self.numberOfCommits = self.numberOfCommits + 1
        self.latesCommit = vNewCommit
        #update visualization also...
        
    def updateIsAtProjectSpace(vAtProjectSpace):
        """update visualization if necessary """
        if self.isAtProjectSpace == False and vAtProjectSpace == True:
            pass
        else:
            pass
        self.isAtProjectSpace = vAtProjectSpace