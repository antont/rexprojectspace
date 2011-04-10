import sys
import os

sys.path.append(os.getcwd() + "/../src/")

import rexprojectspacedataobjects
import buildbot
import versioncontrolsystem
import issuetracker

class Tester:
    """ 
    Implements a tester class for data fetcher modules. This module should be
    kept free from dependencies to any non python modules and one should be able
    to run these tests in any Python env (without iron python).
    """
    
    def __init__(self):
        self.vcs = versioncontrolsystem.VersionControlSystem("naali")
        self.it = issuetracker.IssueTracker()
        self.bb = buildbot.BuildBot()

    def Run(self):
        #print self.GetBuildResult()
        print self.GetBranches()
        print self.GetAllBlobs()
        print self.GetCommitsFromNetworkData()
        print self.GetAllContributors()
        print self.GetCommitInformation()
        print self.GetCommitsForBranch()
        print self.GetIssues()
        
    def GetBuildResult(self):
        builds = self.bb.GetLatestBuilds()
        print builds
        if len(builds) > 0:
            for build in builds:
                if build.result == "success" or build.result == "failure":
                    return True
        return False
   
    def GetBranches(self):
        branches = self.vcs.GetBranches()
        found = False
        if len(branches) > 0:
            for b in branches:
                 if b.name == "master":
                    found = True
                    
        return found

    def GetAllBlobs(self):
        blobs = self.vcs.GetBlobs()
        
        b = blobs["blobs"]
        
        if(len(b)>0):
            if (b[".gitignore"]):
                return True
        
            return False
        
    def GetCommitsFromNetworkData(self):
        commits = self.vcs.GetCommitsFromNetworkData(10)

        if(len(commits) != 10):
            return False
        
        #should be oldest first...
        if commits[0]["time"] > commits[1]["time"]:
            return False
        
        return True
    

    def GetAllContributors(self):
        devs = self.vcs.GetAllContributors()
        ret = False
        
        for d in devs:
            if d["login"] == "antont":
                ret = True
                break
        
        return ret
        
    def GetCommitInformation(self):
        commits = self.vcs.GetCommitsFromNetworkData(1)
        commitid = commits[0]["id"]
        
        commit = self.vcs.GetCommitInformation(commitid)

        if commit["commit"]["id"] == commitid:
            return True
            
        return False 
        
    def GetCommitsForBranch(self):
        commits = self.vcs.GetCommitsForBranch("develop")
        
        networkcommits = self.vcs.GetCommitsFromNetworkData(1)
        
        if commits[0]["id"] == networkcommits[0]["id"]:
            return True
            
        print commits[0]["id"], networkcommits[0]["id"]
        return False
    
    def GetIssues(self):
        issues = self.it.GetIssues()
        
        ret = True
        
        for issue in issues:
        
            if issue.type != "Enhancement" and issue.type != "Defect":
                ret = False
        
        return ret
    
t = Tester()
t.Run()
