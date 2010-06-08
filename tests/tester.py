from versioncontrolsystem import *
from issuetracker import *
from buildbot import *


def resolveFolder(vCommit):
	#print vCommit
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
	
	filesandcounts = {}
	
	for file in modifiedfiles:
		filesandcounts[file] = files.count(file)	
		
	print filesandcounts


#from swdeveloper import *

v = VersionControlSystem("naali")

#list = v.getAllCommitters()
#print list

#contributors = v.getAllContributors()
#print contributors

#branches = v.getBranches()
#print branches

### get lates commit and print modified file list

#latestCommit = v.getLatestCommitForBranch()

#commitId = latestCommit["id"]

#commitInfo = v.getCommitInformation(commitId)

commitInfo = v.getCommitInformation("8a0f0cd5b1603dca2e2a0d6f5238a6e6909bb683")


commit = commitInfo["commit"]

mod = commit["modified"]

#for m in mod:
#	print m["filename"]

resolveFolder(commit)


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

