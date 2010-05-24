class SWProject:

    def __init__(self, vProjectName):
        self.projectName = vProjectName
        self.components = []
        
    def addComponent(self, vComponentName):
        pass
    
    def newCommitForDeveloper(self, vDeveloper, vCommit):
        #locate correct component            
        pass
        
class SWComponent:

    def __init__(self, vComponentName):
        self.componentName = vComponentName
        self.commmitters = []        