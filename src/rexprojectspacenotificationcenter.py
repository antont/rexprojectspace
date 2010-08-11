import sys
import threading

import rxevent

import rexprojectspacedataobjects

class RexProjectSpaceNotificationCenter:
    """ Clusters all the dispatcher classes in to a single
        easily usable class (Facade class). Users can subscribe in to events
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
            nc = cls(vProjectName)
            cls.instances[vProjectName] = nc
            
        return nc 

    def __init__(self,vProjectName):
        """ start listening to all coming events that are related to 
            a project."""
        
        VersionControlDataDispatcher.registerAsCommitListener(self.NewCommit,vProjectName)
        VersionControlDataDispatcher.registerAsNewBranchesListener(self.NewBranches,vProjectName)
        VersionControlDataDispatcher.registerAsBranchesUpdatedListener(self.BranchesUpdated,vProjectName)
        
        BuildResultDispatcher.register(self.NewBuild)
        
        IssueDispatcher.registerOnNewIssues(self.NewIssue)
        IssueDispatcher.registerOnIssueUpdated(self.IssueUpdated)
        
        IrcMessageDispatcher.registerOnNewMessage(self.NewIrcMessage)
        
        #vcs
        self.OnNewCommit = rxevent.RexPythonEvent()
        self.OnNewCommitter = rxevent.RexPythonEvent()
        self.OnBranchesUpdated = rxevent.RexPythonEvent()
        self.OnNewBranches = rxevent.RexPythonEvent()
        
        
        #issue tracking system
        self.OnNewIssue = rxevent.RexPythonEvent()
        self.OnIssueUpdated = rxevent.RexPythonEvent()
        
        #build bot
        self.OnBuild = rxevent.RexPythonEvent()
        
        #irc bot
        self.OnNewIrcMessage = rxevent.RexPythonEvent()
        
    def NewCommit(self,vCommit):
        ##print "---commit----"
        self.OnNewCommit(vCommit)
        
    def BranchesUpdated(self,branches):
        ##print "---new branch---"
        self.OnBranchesUpdated(branches)
    
    def NewBranches(self,branches):
        ##print "---new branch---"
        self.OnNewBranches(branches)

    def NewBuild(self,vBuild):
        ##print "---build----"
        self.OnBuild(vBuild)
        
    def NewIssue(self,vIssue):
        #print "---new issue----, ", vIssue
        self.OnNewIssue(vIssue)
        
    def IssueUpdated(self,vIssue):
        #print "---issue updated----"
        self.OnIssueUpdated(vIssue)
        
    def NewIrcMessage(self,vMessage):
        self.OnNewIrcMessage(vMessage)

########


import versioncontrolsystem

class VersionControlDataDispatcher:
    """fetches commits and passes them to listeners.
    """
    
    dispatchers = {}

    def __init__(self,vVCS):
        """ Set up timer and start it
        """
        self.vcs = vVCS
        self.targets = {}
        self.latestcommit = 0
        
        self.branches = {}
        self.newbranchlisteners = []
        self.branchupdatedlisteners = []
        
        
        self.timer = None
        self.latestcommit = "" #id of latest commit
        self.timer = threading.Timer(10.0,self.update)#once a minute
        self.timer.start()
    
    @classmethod
    def registerAsNewBranchesListener(cls, vTarget, vProject):
        """ Registers observer to observe new branches """
  
        cls.dispatcherForProject(vProject).newbranchlisteners.append(vTarget)
    
    @classmethod
    def registerAsBranchesUpdatedListener(cls, vTarget, vProject):
        """ Registers observer to observe changes in branches, used
            to notify about new commits"""
  
        cls.dispatcherForProject(vProject).branchupdatedlisteners.append(vTarget)
    
    @classmethod
    def registerAsCommitListener(cls, vTarget, vProject ,vDeveloper = ""):
        """ Registers observer to commits. Note: all commits are dispatched to all
            listeners, developer specific listener not implemented yet."""
  
        cls.dispatcherForProject(vProject).targets[vDeveloper] = vTarget
        
    @classmethod
    def dispatcherForProject(cls,vProject):
        """ Returns dispatcher for given project, singeleton instance
        """
        dispatcher = None
        try:
            dispatcher = cls.dispatchers[vProject]
        except:
            ##print "creating dispatcher for project: ", vProject
            dispatcher = cls(versioncontrolsystem.VersionControlSystem(vProject))
            cls.dispatchers[vProject] = dispatcher
            
        return dispatcher

    
    def update(self):
        """ Get single commit for every developer and
        store latest commit and if commit is the same
        do not update anything. Get also branch related informations, such as
        latest commits to the branches and check if there is new branches """
        
        commits = self.vcs.GetCommitsFromNetworkData(20)
        commits.reverse()
        
        if( len(commits) < 1 or commits[0]["id"] == self.latestcommit):
            pass
    
        else:   
            self.latestcommit = commits[0]["id"]
            
            newCommits = []
            
            for c in commits:
                if c["id"] == self.latestcommit:
                    ##print "________id matched!!!______"
                    break
                
                login = c["login"]
                print "login: ", login
                
                author = ""
                
                try:
                    author = c["author"]
                except:
                    pass
                    
                print "author: ", author
                
                #get detailed info also...
                ci = self.vcs.GetCommitInformation(c["id"])
                
                commit = ci["commit"]
                
                
                devCommit = rexprojectspacedataobjects.CommitInfo(login,commit,author)
                newCommits.append(devCommit)
                
            self.dispatchCommits(newCommits)
            
        branches = self.vcs.GetBranches()
        newBranches = []
        
        if len(branches) != len(self.branches.keys()):
            #we have (a) new branch(es), locate it and dispatch that as a new branch
            for b in branches:
                try:
                    br = self.branches[b.name]
                except:
                    #must be new
                    self.branches[b.name] = b
                    newBranches.append(b)
            
        self.dispatchNewBranches(newBranches)
        
        updatedBranches = []
        
        for b in branches:
            try:
                br = self.branches[b.name]
                if br.latestcommitdate != b.latestcommitdate:
                    #there has to be a new commit...
                    updatedBranches.append(b)
            
            except:
                #must be something wrong here, just updated branches...
                pass
    
        self.dispatchNewBranches(updatedBranches)
        
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60.0,self.update)#once a minute
        self.timer.start()
    
    def dispatchNewBranches(self,branches):
        """ Notify listeners about new branches """
        for listener in self.newbranchlisteners:
            listener(branches)
    
    def dispatchUpdatedBranches(self,branches):
        """ Notify listeners about branch updates """
        for listener in self.branchupdatedlisteners:
            listener(branches)
    
    
    def dispatchCommits(self,vCommits):
        """ Notify listeners about new commits. Dispatch only to listeners
            that wants to receive all commits or only commits related to 
            a single developer """
        for commit in vCommits:
            for k,v in self.targets.iteritems():
                if k == "" or k == commit.login:
                    v(commit)
#####

import buildbot

class BuildResultDispatcher:
    """ Fetches build related information from the build bot
    """
    
    dispatcherinstance = None
    
    def __init__(self):
        """ Create buildbot and update timer
        """
        self.targets = []
        self.buildbot = buildbot.BuildBot()
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        
    
    @classmethod
    def register(cls, vTarget):
        """ Registers observer to build. Start timer if first listener
            registers
        """
  
        cls.dispatcher().targets.append(vTarget)
        
        if len(cls.dispatcher().targets) == 1:
            cls.dispatcher().timer.start()#first one, so start
    
    @classmethod
    def dispatcher(cls):
        """ Return singleton dispatcher instance
        """
        d = None
        if not cls.dispatcherinstance:
            ##print "creating dispatcher for build results: "
            cls.dispatcherinstance = cls()
        
        return cls.dispatcherinstance

    def updateBuildResults(self):
        """ Get build information from build bot and dispatch results
        """
        builds = self.buildbot.GetLatestBuilds()
        self.dispatchBuildResults(builds)
        
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        self.timer.start()
        
        
    def dispatchBuildResults(self,vBuilds):
        """ Dispatch results to listeners
        """
        for target in self.targets:
            target(vBuilds)
            
#####

import issuetracker

class IssueDispatcher:
    """ Fetches issues from issuetracker and dispatches them to the listeners
    """
    instance = None
    
    def __init__(self):
        """ Create issuetracker and update timer
        """
        self.issuetracker = issuetracker.IssueTracker()
        self.newIssueTargets = []
        self.issueUpdatedTargets = []
        
        self.timer = threading.Timer(30,self.updateIssues)
        self.issues = {}
    
    @classmethod
    def registerOnNewIssues(cls, vTarget):
        """ Register listener to new issues and start update 
            timer if first listener
        """
        cls.dispatcher().newIssueTargets.append(vTarget)
        
        if len(cls.dispatcher().issueUpdatedTargets) == 0 and len(cls.dispatcher().newIssueTargets) == 1:
            cls.dispatcher().timer.start()#first one, so start
            
    @classmethod
    def registerOnIssueUpdated(cls, vTarget):
        """ Registers listener to issue updates and start update 
            timer if first listener"""
  
        cls.dispatcher().issueUpdatedTargets.append(vTarget)
        
        if len(cls.dispatcher().issueUpdatedTargets) == 1 and len(cls.dispatcher().newIssueTargets) == 0:
            cls.dispatcher().timer.start()#first one, so start
    
    
    @classmethod
    def dispatcher(cls):
        """ Return singleton class instance
        """
        d = None
        if not cls.instance:
            ##print "creating dispatcher for issues: "
            cls.instance = cls()
        
        return cls.instance

    def updateIssues(self):
        """ Update issues related information by getting new issues and
            checking if existing issues have been updated
        """
        issues = self.issuetracker.GetIssues()
        
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
                #print "new issue with id: ", i.id 
                #notify that there was a new issue
                for target in self.newIssueTargets:
                    #print "new bug from dispatcher: ", self.issues[i.id]
                    target(self.issues[i.id])

        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60,self.updateIssues)
        self.timer.start()
        
        
#####

import ircbot

class IrcMessageDispatcher:
    """ Not used
    """
    dispatcherinstance = None
    
    def __init__(self):
        self.targets = []
        self.ircbot = ircbot.IrcBot(self.OnMessage)
        print "created irc bot"
        
    @classmethod
    def registerOnNewMessage(cls, vTarget):
        """ Registers observer to new irc messages"""  
        cls.dispatcher().targets.append(vTarget)
        
    @classmethod
    def dispatcher(cls):
        d = None
        if not cls.dispatcherinstance:
            cls.dispatcherinstance = cls()
            cls.dispatcherinstance.ircbot.start()
        
        return cls.dispatcherinstance

    def OnMessage(self,vMessage):
        print "irc message: ", vMessage
        for target in self.targets:
            target(vMessage)            
#####        
        
        