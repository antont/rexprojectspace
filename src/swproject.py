import swdeveloper

class SWProject:

    def __init__(self, vProjectName, vDevelopers):
        self.projectName = vProjectName
        self.components = []
        self.developers = vDevelopers
        
    def addComponent(self, vComponentName):
        pass
    
    def newCommitForDeveloper(self, vDeveloper):
        #locate correct component
        #parameter holds all the necessary data            
        pass   
    
    def createComponentVisualization(self,vComponent):
        """ Dynamically added components """
        pass
      
class SWComponent:

    def __init__(self, vComponentName):
        self.componentName = vComponentName
        self.commmitters = []
    
    def addDeveloper(self,vDeveloper):
        pass
        
    def removeDeveloper(self,vDeveloper):
        pass