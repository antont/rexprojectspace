import urllib
import time
import datetime
import xmlrpclib

import rexprojectspacedataobjects
        
class BuildBot:
    """ Data fetcher for build bot service.
        Gets data from build bot running on remote server 
        by using XMLRPC
    """
    def __init__(self):
        """ Create server proxy """
        self.proxy = xmlrpclib.ServerProxy("http://www.playsign.fi:8010/xmlrpc/")

    def GetLatestBuilds(self):
        """
        Returns list of BuildInfo objects containing results and a timestamp,
        in case of failing build, the also the latest succesfull build 
        will be returned. In case of succesfull build, the latest failing build
        will also be returned
        """
        
        buildPlatforms = []
        results = []
        
        try:
            buildPlatforms = self.proxy.getAllBuilders()
        except:
            pass
            print "exception in buildbot xmlrpc"
        
        for platform in buildPlatforms:
            build = self.proxy.getLastBuilds(platform, 1)
            
            if not build:
                continue
            
            build = build[0]
            result = build[6]
            print "tulos:", build
                  
            t = time.gmtime(build[2])
 
            binfo = rexprojectspacedataobjects.BuildInfo(platform,result,t)
            results.append(binfo)
            
            index = 1
            count = 10
            bNoMoreBuilds = False
            
            if result != "success":
                
                while result != "success" and bNoMoreBuilds == False:
                    temp = index
                    #print "---getting new build---"
                    builds = self.proxy.getLastBuilds(platform, count)
                    for i in range(temp,count):
                        try:
                            build = builds[i]
                        except:
                            #no more builds
                            print "No more builds"
                            results.append(rexprojectspacedataobjects.BuildInfo(platform,result))
                            bNoMoreBuilds = True
                            break
                            
                        result = build[6]
                        if result != "success":
                            count = count + 10
                            index = index + 1
                            continue
                            
                        t = time.gmtime(build[2])
             
                        binfo = rexprojectspacedataobjects.BuildInfo(platform,result,t)
                        results.append(binfo)
                        break
            else:
                while result != "failure" and  bNoMoreBuilds == False:
                    temp = index
                    #print "---getting new build---"
                    builds = self.proxy.getLastBuilds(platform, count)
                    for i in range(temp,count):
                        
                        try:
                            build = builds[i]
                        except:
                            #no more builds
                            print "No more builds"
                            results.append(rexprojectspacedataobjects.BuildInfo(platform,result))
                            bNoMoreBuilds = True
                            break
                        
                        result = build[6]
                        if result != "failure":
                            count = count + 10
                            index = index + 1
                            continue
                            
                        t = time.gmtime(build[2])
             
                        binfo = rexprojectspacedataobjects.BuildInfo(platform,result,t)
                        results.append(binfo)
                        break              
            
        print results
        
        return results
