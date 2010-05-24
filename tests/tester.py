from versioncontrolsystem import *
from issuetracker import *
from buildbot import *

v = VersionControlSystem("naali")

#list = v.getAllCommitters()
#print list

#contributors = v.getAllContributors()
#print contributors

#branches = v.getBranches()
#print branches

#latestCommit = v.getLatestCommitForBranch()
#print latestCommit

commits = v.getCommitsForBranch()
print commits

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