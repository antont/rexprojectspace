import versioncontrolsystem

class Commit:
    def __init__(self,vDeveloperName,vMessage,vDirectories,vFiles):
        
        self.login = vDeveloperName
        self.message = vMessage
        self.directories = vDirectories
        self.files = vFiles

class CommitDispatcher:
    dispatchers = {}

    """fetches commits and passes them to developers. Can be used as a datasource
       to update ui objects..."""
    def __init__(self,vVCS):
        self.vcs = vVCS
        self.targets = {}
        self.timer = None
        self.latestcommit = "" #id of latest commit
    
    @classmethod
    def register(cls, vTarget, vProject ,vDeveloper = ""):
        """ Registers observer to commits. If no developer name is given
            all new commits are dispatched to target """
        if vDeveloper == "":
            pass #not implemented yet
            
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
        commits = self.vcs.getCommitsForBranch("develop")
        
        if( len(commits) < 1 or commits[0]["id"] == self.latestcommit):
            #nothing to update...
            return
        
        newCommits = []
        
        for c in commits:
            if c["id"] == self.latestcommit:
                break
                
            name = c["author"]["name"]
            
        
        self.dispatchCommits(newCommits)
        
        latestcommit = commits[0]
    
    def dispatchCommits(self,vCommits):
        for k,v in self.targets.iteritems():
            #print commits[developer]
            v(Commit("toni alatalo","new commit", ["A","B","C"], ["a","b","c"]))
           
        
           
        