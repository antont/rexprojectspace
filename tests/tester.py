import sys
import os

sys.path.append(os.getcwd() + "/../src/")

import rexprojectspacedataobjects
import buildbot
import versioncontrolsystem
import issuetracker

class Tester:
    def __init__(self):
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        self.it = issuetracker.IssueTracker()
        self.bb = buildbot.BuildBot()

    def Run(self):
        print self.GetBuildResult()
        print self.GetBranches()
        
    def GetBuildResult(self):
        builds = self.bb.GetLatestBuilds()
        print builds
        if len(builds) > 0:
            for build in builds:
                if build.result == "success" or build.result == "failure":
                    return True
        return False
        
    def GetIssues(self):
        issues = self.it.GetIssues()
        pass
    
    def GetLatestCommit(self):
        pass
    
    def GetBranches(self):
        branches = self.vcs.GetBranches()
        found = False
        if len(branches) > 0:
            for b in branches:
                 if b.name == "master":
                    found = True
                    
        return found

    def GetAllBlobs(self):
        pass
    
    def GetCommitsForBranch(self):
        pass
    
    def GetCommitForDeveloper(self):
        pass
    
t = Tester();
t.Run()