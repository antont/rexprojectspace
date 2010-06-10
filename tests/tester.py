from versioncontrolsystem import *
from issuetracker import *
from buildbot import *

import commitdispatcher
import swdeveloper

def resolveFilesAndFolders(vCommit):
    #get mod,add,remove
    files,mod,removed,added = [],[],[],[]
    try:
        mod = vCommit["modified"]
    except:
        pass
    try:
        removed = vCommit["Removed"]
    except:
        pass
    try:
        added = vCommit["added"]
    except:
        pass
      
    for m in mod:
        files.append(m["filename"]) 
    for a in added:
        files.append(a) 
    
    for r in removed:
        files.append(r)
                

    #files.sort()       
    
    modifiedfiles = list(set(files))
    
    files = []
    folders = []
    
    for file in modifiedfiles:
        files.append(file)
        
        temp = file.split("/")
        if len(temp) > 0:
            folders.append(temp[0])
        else:
            folders.append("/")

    #print folders
    return files,folders

#from swdeveloper import *

v = VersionControlSystem("naali")

def cb(vCommit):
    print vCommit.message


def initSWProject():
    """Mocked solution for now """
    
    components = []
    
    
    #get all committers
    committers = v.getAllContributors()
    print committers
    
    commits_for_devs = {}
    
    #get all commits 
    commits = v.getCommitsForBranch()
    count = len(committers)
    temp = count
    for commit in commits:
        
        author = commit["author"]
        try:
            commits_for_devs[author["name"]]
        except:
            commits_for_devs[author["name"]] = commit
            count -= 1
        
        if count < 1:
            break # every one has commit
        
    #now we have commit ids... fetch the data for all committers
    for keys,values in commits_for_devs.iteritems():
        id = values["id"]
        ci = v.getCommitInformation(id)
        c = ci["commit"]
        
        files,folders = resolveFilesAndFolders(c)
        
        cur = None
        #locate correct committer
        commitcount = 0
        
        for committer in committers:
            author = values["author"]
            if committer["login"] == author["login"]:
                cur = committer
        if cur:
            commitcount = cur["contributions"]
        
        print "number of commits: %d for developer: %s"%(commitcount,keys)
        #commitdispatcher.Commit(values["author"]["name"],values["message"],folders,files)
    
    #init every developer so that each has latest commits, commit count and names in place
    
    
    #project = swproject.SWProject(self.scene,"naali",components)
    return ""

###
initSWProject()
    
### test commit dispatching
"""
cd = commitdispatcher.CommitDispatcher.dispatcherForProject("naali")


cd.targets["TestUser"] = cb

cd.updateCommits()

cd.dispatchCommits([])
"""

"""
list = v.getAllCommitters()
print list
"""

"""
contributors = v.getAllContributors()
print contributors
"""

"""
branches = v.getBranches()
print branches
"""

### get lates commit and print modified file list
"""
latestCommit = v.getLatestCommitForBranch()
commitId = latestCommit["id"]
commitInfo = v.getCommitInformation(commitId)
"""

### test resolver folder
"""
commitInfo = v.getCommitInformation("8a0f0cd5b1603dca2e2a0d6f5238a6e6909bb683")
commit = commitInfo["commit"]
resolveFolder(commit)
"""

"""
commits = v.getCommitsForBranch()
print commits
"""

########
"""
tracker = IssueTracker()
issues = tracker.getIssues()
print issues[5].owner
"""

####
"""
bb = BuildBot()
results = bb.getLatestBuilds()
#print results
"""

####
"""
committers = v.getAllContributors()
print committers

for value in committers:
    #print value.keys()
    #login = value["login"]
    print value
    #print "%s has %d commits"%(login,value["contributions"])
"""  

####

