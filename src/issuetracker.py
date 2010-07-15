import urllib
import time

import rexprojectspacedataobjects
        
class IssueTracker:
    """ Data fetcher for issue tracker type of service.
        Gets data from google code hosting issue tracking
        service"""
    def __init__(self):
        pass
        
    def GetIssues(self):
        f = urllib.urlopen("http://code.google.com/p/realxtend-naali/issues/csv")
        s = f.read()
        
        issues = []
        
        issuesStringArray = s.splitlines()        
        
        for j in range(len(issuesStringArray)):                        
            if(j == len(issuesStringArray) - 1):
                pass
            elif(j == 0):
                pass
            else:
                issueString = issuesStringArray[j][1:-1].split(',')             
                issue = rexprojectspacedataobjects.IssueInfo(issueString)
                issues.append(issue)

        return issues
