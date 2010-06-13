import urllib
try:
    import json
except:
    import simplejson as json

import time

class VersionControlSystem:
    """Represent a version control system for a single GitHub project.
    Data is gathered with GitHub JSON -api.
    Tries to cache data, so every function call does not 
    necessarily cause network traffic"""    
    def __init__(self,projectName):
        self.projectName = projectName
    
        self.committersFetchedTime = 0
        self.authors = []
        
        self.contributorsFetchedTime = 0
        self.contributors = []

        self.branchesFetchedTime = 0
        self.branches = []
        
        self.latestCommitForBranchFetchedTime = {};
        self.latestCommitForBranch = {}
        
        self.commitsForBranchFetchedTime = {};
        self.commitsForBranch = {}

        pass
    
    def getUserInfo(self,vLogin):
        url = "http://github.com/api/v2/json/user/show/%s"%(vLogin)
        f = urllib.urlopen(url)
        s = f.read()
        
        jsonstring = json.loads(s)
        
        user = jsonstring["user"]
        user = user["user"]
        
        return user
        
    
    def getCommitsFromNetworkData(self):
        """ Gets a huge amount of commits from the github network data. """
        url = "http://github.com/realxtend/%s/network_meta"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()
            
        jsonstring = json.loads(s)
        nethash = jsonstring["nethash"]
        end = len(jsonstring["dates"])
        #print jsonstring["dates"]
        #print "end date: ", end
        url = "http://github.com/realxtend/%s/network_data_chunk?nethash=%s&start=%s&end=%s"%(self.projectName,nethash,str(end - 500),str(end-1))
        #print url
        f = urllib.urlopen(url)
        s = f.read()
        #print s
        jsonstring = json.loads(s)
        commits = jsonstring["commits"]
        
        return commits    
        
    def getAllCommitters(self):
        """Returns all commmitters as a list without duplicate entries"""
        if(time.localtime().tm_min > self.committersFetchedTime):
            self.committersFetchedTime = time.localtime().tm_min
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
    
    def getUserInfo(self,vLogin):
        """ Returns information about specific github user """
        url = "http://github.com/api/v2/json/user/show/%s"%(vLogin)  
        f = urllib.urlopen(url)
        s = f.read()
        user = json.loads(s)

        return user
    
    def getAllContributors(self):
        """Returns all contributors as a dictionary without duplicate entries.
           Dictionary holds names as keys and number of contributions as values"""
        
        if(time.localtime().tm_min > self.contributorsFetchedTime):
            self.contributorsFetchedTime = time.localtime().tm_min
        url = "http://github.com/api/v2/json/repos/show/realXtend/%s/contributors"%(self.projectName)
        f = urllib.urlopen(url)
        s = f.read()
        
        jsonString = json.loads(s)
       
        contributors = jsonString["contributors"]
       
        self.contributors = contributors

        return self.contributors
    
        
    def getBranches(self):
        """Returns all branches as a list without duplicate entries"""
        if(time.localtime().tm_min > self.branchesFetchedTime):
            self.branchesFetchedTime = time.localtime().tm_min 
            branches = []
            url = "http://github.com/api/v2/json/repos/show/realXtend/%s/branches"%(self.projectName)
            f = urllib.urlopen(url)
            s = f.read()

            br = json.loads(s)
            for k,v in br.iteritems():
                for keys,values in v.iteritems():    
                    branches.append(keys)  
                           
            self.branches = list(set(branches))            
    
        return self.branches
    
    def getLatestCommitForBranch(self,branch="develop"):
        """Returns latest commit as a dictionary holding all the data that
            GitHub provides"""

        t = 0
        
        try:
            t = self.latestCommitForBranchFetchedTime[branch]
        except:
            pass
            
        if(time.localtime().tm_min > t ):
            
            url = "http://github.com/api/v2/json/commits/list/realXtend/naali/%s"%(branch)
            f = urllib.urlopen(url)
            s = f.read()
    
            allCommits = json.loads(s)#ordered, newest is the first one
            
            commit = allCommits["commits"][0]
            self.latestCommitForBranch[branch] = commit
            
        return self.latestCommitForBranch[branch]
  
    def getCommitInformation(self,vId):
        """ Returns information about specific github commit as a dictionary """
        url = "http://github.com/api/v2/json/commits/show/realxtend/naali/%s"%(vId)  
        f = urllib.urlopen(url)
        s = f.read()
        commit = json.loads(s)

        return commit
        
    def getCommitsForBranch(self,branch="develop"):
        """Returns latest commits as a dictionary holding all the data that
           GitHub provides"""

        t = 0
        
        try:
            t = self.commitsForBranchFetchedTime[branch]
        except:
            pass
            
        if(time.localtime().tm_min > t ):
            
            url = "http://github.com/api/v2/json/commits/list/realXtend/naali/%s"%(branch)
            f = urllib.urlopen(url)
            s = f.read()
    
            allCommits = json.loads(s)#ordered, newest is the first one
            
            commits = allCommits["commits"]
            self.commitsForBranch[branch] = commits
            
        return self.commitsForBranch[branch]            
        
    def getNumberOfCommitsForDay(self,day):
        pass    
        
    def getLatestCommitForCommitter(self,committer):
        pass    
                
    def getCommitsAfterTimeStamp(self,time):
        pass
        
    def getNumberOfCommitsInBranch(self):
        pass
    
    
