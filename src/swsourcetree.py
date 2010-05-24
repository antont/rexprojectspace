class SWSourceTree:
    
    def __init__(self, vProjectName, vBranchNames):
        self.projectName = vProjectName
        self.branches = []

class SWSourceTreeBranch:
    
    def __init__(self, vBranchName, vNumberOfCommits = 0, vLatestCommit = ""):
        self.projectName = vProjectName
        self.numberOfCommits = vNumberOfCommits
        self.latestCommit = vLatestCommit