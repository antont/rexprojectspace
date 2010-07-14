from versioncontrolsystem import *
from issuetracker import *
from buildbot import *

import commitdispatcher
#import swdeveloper
#from swdeveloper import *

class Commit:
    def __init__(self,vDeveloperName,vMessage,vDirectories,vFiles):
        
        self.author = vDeveloperName
        self.message = vMessage
        self.directories = vDirectories
        self.files = vFiles

class DeveloperInfo:
    def __init__(self,vName,vLogin):
        self.name = vName
        self.login = vLogin
        self.commit = None
        self.commitcount = 0
        self.latestcommit = None
        

v = VersionControlSystem("naali")

def cb(vCommit):
    print vCommit.message



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


def initSWProject():
    """Mocked solution for now """
    
    components = []
    
    #get all committers
    committers = v.getAllContributors()
    #print committers[0]
    devs = []
    
    commits_for_devs = {}
    
    #get all commits 
    commits = v.getCommitsForBranch()   
    count = len(committers)
    temp = count
    
    
    coms = v.getCommitsFromNetworkData()
    print len(coms)
    coms.reverse()
    
    for commit in coms:
       
        author = commit["author"]
        #for every name, insert a commit
        try:
            commits_for_devs[author]
        except:
            #print author
            #print commit["committer"]
            commits_for_devs[author] = commit
            dev = DeveloperInfo(commit["login"])
            dev.name = commit["author"]
            
            
            dev.latestcommit = Commit(commit["login"],commit["author"],"","")
            
            devs.append(dev)
            """
            print commit["author"]
            print commit["login"]
            print commit["message"]
            print commit["id"]
            print commit["date"]
            """
            print "_______________"
            
            count -= 1
            
            for committer in committers:
            
                name = ""
                try:
                    name = committer["name"]
                except:
                    pass
    
                if committer["login"] == author or commit["login"] == committer["login"] or name == author:
                    cur = committer
                    print "commit found for: ",committer["login"]
    """            
    for commit in commits:
       
        author = commit["author"]
        #login = commit["login"]
        #for every name, insert a commit
        try:
            commits_for_devs[author["name"]]
        except:
            #print author
            #print commit["committer"]
            commits_for_devs[author["name"]] = commit
            
            count -= 1
        
        if count < 1:
            break # every one has commit
    
    #print commits_for_devs
    """
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
            
            name = ""
            try:
                name = committer["name"]
            except:
                pass

            if committer["login"] == author["login"] or author["name"] == committer["login"] or name == keys:
                cur = committer
                print "commit found for: ",committer["login"]
        if cur:
            commitcount = cur["contributions"]
        
        print "number of commits: %d for developer: %s"%(commitcount,keys)
        #myCommit = commitdispatcher.Commit(values["author"]["name"],values["message"],folders,files)
        #swdeveloper.SWDeveloper(self.scene,keys,commitcount,myCommit,False)
    #init every developer so that each has latest commits, commit count and names in place
    
    
    #project = swproject.SWProject(self.scene,"naali",components)
    return ""

###

initSWProject()

###
"""
coms = v.getCommitsFromNetworkData()

committers = v.getAllContributors()

commits_for_devs = {}

#get all commits 
count = len(committers)
temp = count

for commit in coms:
   
    author = commit["author"]
    #for every name, insert a commit
    try:
        commits_for_devs[author]
    except:
        #print author
        #print commit["committer"]
        commits_for_devs[author] = commit
        print commit["author"]
        print commit["login"]
        print commit["message"]
        print commit["id"]
        print "_______________"
        count -= 1
    
    if count < 1:
        break # every one has commit
"""
#print count    
#print commits_for_devs
 
#print v.getUserInfo("antont")
 
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

