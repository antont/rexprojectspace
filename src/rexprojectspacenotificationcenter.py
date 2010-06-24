import sys
import threading

import rxevent

import rexprojectspacedataobjects

class RexProjectSpaceNotificationCenter:
    """ Clusters all the dispatcher classes in to a single
        easily usable class. Users can subscribe in to events
        that they are interested in and provide their callback/delegate
        functions.
    """    
    instances = {}

    @classmethod
    def NotificationCenter(cls,vProjectName):
        """ Singleton interface to notification center class.
            Ensures that there is only one instance for a project """
        nc = None
        try:
            nc = cls.instances[vProjectName]
        except:
            print "creating notification center for project: ", vProjectName
            nc = cls(vProjectName)
            cls.instances[vProjectName] = nc
            
        return nc 

    def __init__(self,vProjectName):
        """ start listening to all coming events that are related to 
            a project."""
        
        CommitDispatcher.register(self.NewCommit,vProjectName)
        
        BuildResultDispatcher.register(self.NewBuild)

        IssueDispatcher.registerOnNewIssues(self.NewIssue)
        IssueDispatcher.registerOnIssueUpdated(self.IssueUpdated)
           
        self.OnNewCommit = rxevent.RexPythonEvent()
        
        self.OnNewIssue = rxevent.RexPythonEvent()
        self.OnIssueUpdated = rxevent.RexPythonEvent()
        
        self.OnBuild = rxevent.RexPythonEvent()
        
    def NewCommit(self,vCommit):
        print "---commit----"
        self.OnNewCommit(vCommit)
        
    def NewBuild(self,vBuild):
        print "---build----"
        self.OnBuild(vBuild)
        
    def NewIssue(self,vIssue):
        print "---new issue----"
        self.OnNewIssue(vIssue)
        
    def IssueUpdated(self,vIssue):
        print "---issue updated----"
        self.OnIssueUpdated(vIssue)

########


import versioncontrolsystem

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
#####

import buildbot

class BuildResultDispatcher:
    dispatcherinstance = None
    
    def __init__(self):
        self.targets = []
        self.buildbot = buildbot.BuildBot()
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        
    
    @classmethod
    def register(cls, vTarget):
        """ Registers observer to commits. If no developer name is given
            all new commits are dispatched to target """
  
        cls.dispatcher().targets.append(vTarget)
        
        if len(cls.dispatcher().targets) == 1:
            cls.dispatcher().timer.start()#first one, so start
    
    @classmethod
    def dispatcher(cls):
        d = None
        if not cls.dispatcherinstance:
            print "creating dispatcher for build results: "
            cls.dispatcherinstance = cls()
        
        return cls.dispatcherinstance

    def updateBuildResults(self):
        print "building"
        builds = self.buildbot.getLatestBuilds()
        
        buildResult = True
        
        for k,v in builds.iteritems():
            if v == "success":
                print "build succesfull for: ",k
                pass
            else:
                print "build failed for: ",k
                buildResult = False
                
        self.dispatchBuildResults(buildResult)
        
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        self.timer.start()
        
        
    def dispatchBuildResults(self,vResult):
        for target in self.targets:
            target(vResult)
            
#####

import issuetracker

class IssueDispatcher:
    instance = None
    
    def __init__(self):
        self.issuetracker = issuetracker.IssueTracker()
        self.newIssueTargets = []
        self.issueUpdatedTargets = []
        
        self.timer = threading.Timer(10,self.updateIssues)
        self.issues = {}
    
    @classmethod
    def registerOnNewIssues(cls, vTarget):

        cls.dispatcher().newIssueTargets.append(vTarget)
        
        if len(cls.dispatcher().issueUpdatedTargets) == 0 and len(cls.dispatcher().newIssueTargets) == 1:
            cls.dispatcher().timer.start()#first one, so start
    @classmethod
    def registerOnIssueUpdated(cls, vTarget):
        """ Registers observer to commits. If no developer name is given
            all new commits are dispatched to target """
  
        cls.dispatcher().issueUpdatedTargets.append(vTarget)
        
        if len(cls.dispatcher().issueUpdatedTargets) == 1 and len(cls.dispatcher().newIssueTargets) == 0:
            cls.dispatcher().timer.start()#first one, so start
    
    
    @classmethod
    def dispatcher(cls):
        d = None
        if not cls.instance:
            print "creating dispatcher for issues: "
            cls.instance = cls()
        
        return cls.instance

    def updateIssues(self):
        print "getting issues"
        issues = self.issuetracker.getIssues()
        
        
        for i in issues:
            issue = None
            try:
                issue = self.issues[i.id]
                
                #check if data has changed
                if issue.status == i.status and issue.owner == i.owner and issue.priority == i.priority: 
                    
                    pass
                else:
                    #notify that data has changed
                    for target in self.issueUpdatedTargets:
                        target(i)
            except:
                self.issues[i.id] = i
                
                #notify that there was a new issue
                for target in self.newIssueTargets:
                    target(i)

        
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(10,self.updateIssues)
        self.timer.start()
        