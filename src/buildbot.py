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
            build = self.proxy.getLastBuilds(platform, 1)
            build = build[0]
            result = build[6]

            t = time.gmtime(build[2])
 
            binfo = rexprojectspacedataobjects.BuildInfo(platform,result,t)
            results.append(binfo)

        return results
