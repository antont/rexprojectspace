
import time
def parseDate(vDateString):
    datestring = vDateString[0:len(vDateString)-6]#quite dirty, remove -xx:xx from the end
    ti = time.strptime(datestring,"%Y-%m-%dT%H:%M:%S")
    return ti    

class BuildInfo:
    def __init__(self,vPlatformName,vResult,vTime = None):
        self.platformname = vPlatformName
        self.result = vResult
        self.time = 0
        if vTime:
            self.time = parseDate(vTime)
        

class FolderInfo:
    def __init__(self,vName,vNumberOfSubFiles,vLatestCommitDate = 0 ,vNumberOfCommits=0):
        self.name = vName
        #self.latestcommitdate = parseDate(vLatestCommitDate)
        self.numberofcommits = vNumberOfCommits
        self.numberofsubfiles = vNumberOfSubFiles
    
class BranchInfo:
    def __init__(self,vName,vLatestCommitDate,vNumberOfCommits=0):
        self.name = vName
        self.numberofcommits = vNumberOfCommits
        self.latestcommitdate = parseDate(vLatestCommitDate)

class DeveloperInfo:
    def __init__(self,vLogin,vName=""):
        self.login = vLogin
        self.name = ""
        self.commitcount = 0
        self.latestcommitid = 0
        self.latescommit = None 
        
class IssueInfo:
    """ Model class for issue"""    
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
        self.type = issueData[1]
        self.status = issueData[2]
        self.priority = issueData[3]
        self.milestone = issueData[4]
        self.owner = issueData[5]
        self.summary = issueData[6]
        self.allLabels = issueData[7]

    def toString(self):
        print ("Issue object: ID:%s TYPE:%s SUMMARY:%s")%(self.id,self.type,self.summary)


    def compare(self,other):
        #print "vertailu--"
        #print "vertailu-----%s"%(other)
        #print self

        if self.id == vOther.id and self.type == vOther.type and self.status == vOther.status and self.priority == vOther.priority and self.milestone == vOther.milestone and self.owner == vOther.owner and self.summary == vOther.summary and self.allLabels == vOther.allLabels:
            return 1
        else:
            return -1 

    #__cmp__ = compare
    __str__ = toString

class CommitInfo:
    def __init__(self,vLogin,vCommit,vAuthor=""):
        
        self.login = vLogin
        self.name = vAuthor
        
        if self.name == "":
            try:
                self.name = vCommit["author"]["name"]
            except:
                pass

        self.message = vCommit["message"]
        self.files,self.directories = self.resolveFilesAndFolders(vCommit)
        datestring = vCommit["authored_date"]
        self.date = parseDate(datestring)
        #print ti
        #print self.login
        
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

        ##print folders
        return files,folders

        
        