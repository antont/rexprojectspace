import urllib
import time

import rexprojectspacedataobjects
        
class IssueTracker:
    """ Data fetcher for issue tracker.
        Gets data from google code hosting issue tracking
        service"""
    def __init__(self):
        pass
        
    def GetIssues(self):
        """ Get issues from google code hosting service by using http request
            to the naali projects csv page and parse csv data to a string and 
            create IssueInfo objects with the data. Returns list of IssueInfos
        """
        f = urllib.urlopen("http://code.google.com/p/realxtend-naali/issues/csv")
        s = f.read()
        
        issues = []
        
        issuesStringArray = s.splitlines()        
        
        for j in range(len(issuesStringArray)):                        
            if(j == len(issuesStringArray) - 1):
                pass
            elif(j == 0):
                #first object contains the csv column names, so don't
                #use it
                pass
            else:
                issueString = issuesStringArray[j][1:-1].split(',')             
                issue = rexprojectspacedataobjects.IssueInfo(issueString)
                issues.append(issue)

        return issues
