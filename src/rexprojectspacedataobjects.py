
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

        self.id = issueData[0]
        self.type = issueData[1]
        self.status = issueData[2]
        self.priority = issueData[3]
        self.milestone = issueData[4]
        self.owner = issueData[5]
        self.summary = issueData[6]
        self.allLabels = issueData[7]

class CommitInfo:
    def __init__(self,vLogin,vCommit):
        
        self.login = vLogin
        self.name = ""
        try:
            vCommit["author"]["name"]
        except:
            pass
        self.message = vCommit["message"]
        self.files,self.directories = self.resolveFilesAndFolders(vCommit)

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

        #print folders
        return files,folders

        
        