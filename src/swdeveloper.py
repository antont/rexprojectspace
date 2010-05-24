class SWDeveloper:

    def __init__(self, vName, vIsAtProjectSpace,vNumberOfCommits, vLatesCommit):
        self.name = vName
        self.numberOfCommits = vNumberOfCommits
        self.latesCommit = vLatesCommit
        self.isAtProjectSpace = vIsAtProjectSpace
        
    def updateCommitData(vNewCommit):
        self.numberOfCommits = self.numberOfCommits + 1
        self.latesCommit = vNewCommit
        #update visualization also...