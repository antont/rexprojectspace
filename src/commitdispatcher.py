import sys
import threading

import versioncontrolsystem
import rexprojectspacedataobjects


class CommitDispatcher:
    dispatchers = {}

    """fetches commits and passes them to developers. Can be used as a datasource
       to update ui objects..."""
    def __init__(self,vVCS):
        self.vcs = vVCS
        self.targets = {}
        self.timer = None
        self.latestcommit = "" #id of latest commit
        self.timer = threading.Timer(60.0,self.updateCommits)#once a minute
        self.timer.start()
    
    @classmethod
    def register(cls, vTarget, vProject ,vDeveloper = ""):
        """ Registers observer to commits. If no developer name is given
            all new commits are dispatched to target """
  
        cls.dispatcherForProject(vProject).targets[vDeveloper] = vTarget
        
    @classmethod
    def dispatcherForProject(cls,vProject):
        dispatcher = None
        try:
            dispatcher = cls.dispatchers[vProject]
        except:
            print "creating dispatcher for project: ", vProject
            dispatcher = cls(versioncontrolsystem.VersionControlSystem(vProject))
            cls.dispatchers[vProject] = dispatcher
            
        return dispatcher

    
    def updateCommits(self):
        """ get single commit for every developer and
        store latest commit and if commit is the same
        do not update anything """
        commits = self.vcs.getCommitsFromNetworkData(20)
        commits.reverse()
        
        if( len(commits) < 1 or commits[0]["id"] == self.latestcommit):
            #nothing to update...
            return
        
        newCommits = []
        
        for c in commits:
            if c["id"] == self.latestcommit:
                print "________id matched!!!______"
                break
            
            login = c["login"]
            
            #get detailed info also...
            ci = self.vcs.getCommitInformation(c["id"])
            
            commit = ci["commit"]
            
            devCommit = rexprojectspacedataobjects.CommitInfo(login,commit)
            newCommits.append(devCommit)
            
        self.dispatchCommits(newCommits)
        
        self.latestcommit = commits[0]["id"]
         
        #print newCommits
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60.0,self.updateCommits)#once a minute
        self.timer.start()
    
    
    def dispatchCommits(self,vCommits):
        for commit in vCommits:
            for k,v in self.targets.iteritems():
                if k == "" or k == commit.login:
                    #v(rexprojectspacedataobjects.CommitInfo("antont","new commit", ["SceneManager"], ["a","b","c"]))
                    v(commit)
                    
        
           
        