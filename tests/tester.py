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
        self.GetBuildResult()
        
    def GetBuildResult(self):
        builds = self.bb.GetLatestBuilds()
        print builds
        if len(builds) > 0:
            print builds[0].result
            if build.result == "success" or build.result == "failure":
                return True
        return False
        
    def GetIssues(self):
        pass
    
    def GetLatestCommit(self):
        pass
    
    def GetBranches(self):
        pass

    def GetAllBlobs(self):
        pass
    
    def GetCommitsForBranch(self):
        pass
    
    def GetCommitForDeveloper(self):
        pass
    
t = Tester();
t.Run()