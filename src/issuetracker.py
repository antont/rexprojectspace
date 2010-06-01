import urllib
import time

class Issue:
    """ Model class for issue"""    
    def __init__(self,issueData):

        self.id = issueData[0]#do something with this...
        self.type = issueData[1]
        self.status = issueData[2]
        self.priority = issueData[3]
        self.milestone = issueData[4]
        self.owner = issueData[5]
        self.summary = issueData[6]
        self.allLabels = issueData[7]


        
class IssueTracker:
    """ Data fetcher for issue tracker type of service.
        Gets data from google code hosting issue tracking
        service and creates issue objects """
    def __init__(self):
        pass
        
    def getIssues(self):
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
                issue = Issue(issueString)
                issues.append(issue)

        return issues
