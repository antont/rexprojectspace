import urllib
try:
    import json
except:
    import simplejson as json

import time
import rexprojectspacedataobjects

class VersionControlSystem:
    """Represent a version control system for a single GitHub project.
    Data is gathered with GitHub JSON -api.
    Tries to cache data, so every function call does not 
    necessarily cause network traffic""" 
    
    def __init__(self,projectName):
        self.projectName = projectName
    
        
    def GetBranches(self):
        """Returns all branches as a list of BranchInfo objects.
           BranchInfo objects have names and latest commit dates set"""

        branches = []
        url = "http://github.com/api/v2/json/repos/show/realXtend/%s/branches"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()

        br = json.loads(s)
        for k,v in br.iteritems():
            for keys,values in v.iteritems():    
                commits = self.GetCommitsForBranch(keys)
                latestcommit,date = 0,0
                if len(commits) > 0:
                    latestcommit = commits[0]
                    date = latestcommit["authored_date"]

                b = rexprojectspacedataobjects.BranchInfo(keys,date)
                branches.append(b)  
                print b.latestcommitdate
        return branches    
    
    def GetBlobs(self,vPath = "http://github.com/api/v2/json/blob/all/realxtend/naali/develop"):
        """ Gets blobs from github
        """
        url = vPath
        f = urllib.urlopen(url)
        s = f.read()
        
        jsonstring = json.loads(s)
        
        return jsonstring
        
    
    def GetCommitsFromNetworkData(self, vNbrOfCommits):
        """ Gets a vNbrOfCommits amount of commits from the github network data. 
            Returns commits as list of dicts, contents directly from github"""
        url = "http://github.com/realxtend/%s/network_meta"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()
            
        jsonstring = json.loads(s)
        nethash = jsonstring["nethash"]
        end = len(jsonstring["dates"])

        url = "http://github.com/realxtend/%s/network_data_chunk?nethash=%s&start=%s&end=%s"%(self.projectName,nethash,str(end - vNbrOfCommits),str(end-1))

        f = urllib.urlopen(url)
        s = f.read()

        jsonstring = json.loads(s)
        commits = jsonstring["commits"]
        
        return commits    
    
    def GetAllContributors(self):
        """Returns all contributors as a dictionary without duplicate entries.
           Dictionary holds names as keys and number of contributions as values"""
        
        if(time.localtime().tm_min > self.contributorsFetchedTime):
            self.contributorsFetchedTime = time.localtime().tm_min
        url = "http://github.com/api/v2/json/repos/show/realXtend/%s/contributors"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()
        
        jsonString = json.loads(s)
       
        contributors = jsonString["contributors"]
        
        return contributors
    
    def GetCommitInformation(self,vId):
        """ Returns information about specific github commit as a dictionary. """
        url = "http://github.com/api/v2/json/commits/show/realxtend/naali/%s"%(vId)  
        f = urllib.urlopen(url)
        s = f.read()
        commit = json.loads(s)
        
        #make it a commit info
        
        return commit
   
   
    def GetCommitsForBranch(self,branch="develop"):
        """Returns latest commits as a dictionary holding all the data that
           GitHub provides"""

        url = "http://github.com/api/v2/json/commits/list/realXtend/naali/%s"%(branch)
        f = urllib.urlopen(url)
        s = f.read()

        allCommits = json.loads(s)#ordered, newest is the first one
        
        commits = allCommits["commits"]
        return commits       
   
    
    ###### NOT USED

    def GetCommitsForFile(self,vFileName):
        url = "http://github.com/api/v2/json/commits/list/realxtend/naali/develop/%s"%(vFileName)  
        f = urllib.urlopen(url)
        s = f.read()
        commits = json.loads(s)

        return commits
       
    def GetLatestCommitForBranch(self,branch="develop"):
        """Returns latest commit as a dictionary holding all the data that
            GitHub provides"""

        latestCommitForBranch
        url = "http://github.com/api/v2/json/commits/list/realXtend/naali/%s"%(branch)
        f = urllib.urlopen(url)
        s = f.read()

        allCommits = json.loads(s)#ordered, newest is the first one
        
        commit = allCommits["commits"][0]
        
        return commit   
    
    def GetAllCommitters(self):
        """Returns all commmitters as a list without duplicate entries"""
        authors = []
        url = "http://github.com/api/v2/json/commits/list/realXtend/%s/master"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()
        
        committers = json.loads(s)
        for k,v in committers.iteritems():
            for a in v:
                author = {}
                author = a["author"]
                authors.append(author["name"])

        self.authors = list(set(authors))
    
        return self.authors
    

    
