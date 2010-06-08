#import swdeveloper
import versioncontrolsystem

class CommitDispatcher:
    """fetches commits and passes them to developers"""
    def __init__(self,vDevelopers,vVCS):
        self.vcs = vVCS
        self.developers = vDevelopers
        self.timer = None
        self.latestcommit = "" #id of latest commit
    
    def updateCommits(self):
        """ get single commit for every developer and
        store latest commit and if commit is the same
        do not update anything """
        commits = self.vcs.getCommitsForBranch("develop")
        
        if(commits[0]["id"] == self.latestcommit):
            #nothing to update...
            return
        
        for developer in self.developers:
            #print commits[developer]
            pass
            #developer.updateLatestCommit(commits[developer.name])
    
    def addDeveloper(self,vDeveloper):
        self.developers.append(vDeveloper)