
import time
def parseDate(vDateString):
    """ Parse time from string of type 2010-07-23T09:54:40-07:00
        GitHub formats time with this format...
        Return python time object
    """
    datestring = vDateString[0:len(vDateString)-6]#quite dirty, remove -xx:xx from the end
    ti = time.strptime(datestring,"%Y-%m-%dT%H:%M:%S")
    return ti    

class BuildInfo:
    """ Data class for build related information
    """
    def __init__(self,vPlatformName,vResult,vTime = None):
        self.platformname = vPlatformName
        self.result = vResult
        self.time = vTime
        
        

class FolderInfo:
    """ Data class for folder (related to software project) information
    """
    def __init__(self,vName,vNumberOfSubFiles,vLatestCommitDate = 0 ,vNumberOfCommits=0):
        self.name = vName
        #self.latestcommitdate = parseDate(vLatestCommitDate)
        self.numberofcommits = vNumberOfCommits
        self.numberofsubfiles = vNumberOfSubFiles
        self.url = "http://github.com/realxtend/naali/tree/develop/%s/"%(self.name)
    
class BranchInfo:
    """ Data class for version control branch related information
    """
    def __init__(self,vName,vLatestCommitDate = 0,vNumberOfCommits=0):
        self.name = vName
        self.numberofcommits = vNumberOfCommits
        self.latestcommitdate = 0
        if vLatestCommitDate != 0:
            self.latestcommitdate = parseDate(vLatestCommitDate)
        else:
            self.latestcommitdate = time.gmtime(time.time())
            
        self.url = "http://github.com/realxtend/naali/tree/%s/"%(self.name)
            
class DeveloperInfo:
    """ Data class for github developer related information
    """
    def __init__(self,vLogin,vName=""):
        self.login = vLogin
        self.name = ""
        self.commitcount = 0
        self.latestcommitid = 0
        self.latescommit = None
        self.url = "http://github.com/%s/"%(self.login)
        
class IssueInfo:
    """ Data class for issue related information
    """    
    def __init__(self,issueData):

        self.id = ""
        self.type = ""
        self.status = ""
        self.priority = ""
        self.milestone = ""
        self.owner = ""
        self.summary = ""
        self.allLabels = ""
        
        if len(issueData) < 8:
            return
        
        self.id = issueData[0].strip('"')
        #print self.id
        self.type = issueData[1].strip('"')
        self.status = issueData[2].strip('"')
        self.priority = issueData[3].strip('"')
        self.milestone = issueData[4].strip('"')
        self.owner = issueData[5].strip('"')
        self.summary = issueData[6].strip('"')
        self.allLabels = issueData[7].strip('"')
        
        self.url = "http://code.google.com/p/realxtend-naali/issues/detail?id=%s"%(self.id)

    def toString(self):
        print ("Issue object: ID:%s TYPE:%s SUMMARY:%s")%(self.id,self.type,self.summary)

class CommitInfo:
    """ Data class for commit (github) related information
    """
    def __init__(self,vLogin,vCommit,vAuthor=""):
        """ Parses data out from vCommit string received from github
        """
        self.login = vLogin
        self.name = vAuthor
        self.files,self.directories = [],[]
        self.removed = []
        self.added = []
        self.modified = []
        self.id = -1
        
        if self.name == "":
            try:
                self.name = vCommit["author"]["name"]
            except:
                pass

        self.message = ""
        self.date = ""
        
        try:
            self.id = vCommit["id"]
            datestring = vCommit["authored_date"]
            self.message = vCommit["message"]
            self.files,self.directories = self.resolveFilesAndFolders(vCommit)
            self.date = parseDate(datestring)
        except:
            pass
        
    def resolveFilesAndFolders(self,vCommit):
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
            self.modified.append(m["filename"])
            
        for a in added:
            files.append(a)
            self.added.append(a)
        
        for r in removed:
            files.append(r)
            self.removed.append(r)
                   

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
        #leave no duplicates
        folders = list(set(folders))
        
        return files,folders

        
        