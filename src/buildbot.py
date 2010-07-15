import urllib
import time
import datetime
import xmlrpclib

import rexprojectspacedataobjects
        
class BuildBot:
    """ Data fetcher for build bot type of service.
        Gets data from build bot running on remote server
    """
    def __init__(self):
        self.proxy = xmlrpclib.ServerProxy("http://www.playsign.fi:8010/xmlrpc/")

    def GetLatestBuilds(self):
        """Returns list of BuildInfo objects"""
        
        buildPlatforms = []
        results = []
        
        try:
            buildPlatforms = self.proxy.getAllBuilders()
        except:
            pass
           
            #print "exception in buildbot xmlrpc"
        
        for platform in buildPlatforms:
            result = self.proxy.getLastBuildResults(platform)
            #time = 
            binfo = rexprojectspacedataobjects.BuildInfo(platform,result)
            results.append(binfo)

        return results

    def GetBuildsForDay(vDate):
        """Argument is give as datetime.date object.
           Each Build is returned as a tuple in the form:: 
           (buildername, buildnumber, build_end, branchname, revision, 
           results, text)"""
        #start = time.
        #builds = self.proxy.getAllBuildsInInterval(start,stop)
        #return builds
        pass
