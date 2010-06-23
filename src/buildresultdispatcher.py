
import threading
import buildbot

class BuildResultDispatcher:
    dispatcherinstance = None
    
    def __init__(self):
        self.targets = []
        self.buildbot = buildbot.BuildBot()
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        
    
    @classmethod
    def register(cls, vTarget):
        """ Registers observer to commits. If no developer name is given
            all new commits are dispatched to target """
  
        cls.dispatcher().targets.append(vTarget)
        
        if len(cls.dispatcher().targets) == 1:
            cls.dispatcher().timer.start()#first one, so start
    
    @classmethod
    def dispatcher(cls):
        d = None
        if not cls.dispatcherinstance:
            print "creating dispatcher for build results: "
            cls.dispatcherinstance = cls()
        
        return cls.dispatcherinstance

    def updateBuildResults(self):
        print "building"
        builds = self.buildbot.getLatestBuilds()
        
        buildResult = True
        
        for k,v in builds.iteritems():
            if v == "success":
                print "build succesfull for: ",k
                pass
            else:
                print "build failed for: ",k
                buildResult = False
                
        self.dispatchBuildResults(buildResult)
        
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(60,self.updateBuildResults)
        self.timer.start()
        
        
    def dispatchBuildResults(self,vResult):
        for target in self.targets:
            target(vResult)
        
        
        