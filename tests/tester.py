from versioncontrolsystem import *
from issuetracker import *
from buildbot import *


#from swdeveloper import *

v = VersionControlSystem("naali")

#list = v.getAllCommitters()
#print list

#contributors = v.getAllContributors()
#print contributors

#branches = v.getBranches()
#print branches

### get lates commit and print modified file list

latestCommit = v.getLatestCommitForBranch()

commitId = latestCommit["id"]

commitInfo = v.getCommitInformation(commitId)


commit = commitInfo["commit"]

mod = commit["modified"]

for m in mod:
	print m["filename"]


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

