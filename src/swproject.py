import naali
V3 = naali.Vector3df

import rexprojectspacenotificationcenter
import rexprojectspacedataobjects
import swdeveloper
import rexprojectspacemodule

from rexprojectspaceutils import new_mesh

class ComponentBase(object):
    """ Base class for composite objects """
    def __init__(self):
        pass
    
    def SetState(self,vState):
        """ Override this """
        pass
    
    def AddChild(self,vComponentBase):
        """ Composites has to implement this """
        pass
    
    def RemoveChild(self,vComponentBase):
        """ Composites has to implement this """
        pass
        

        
class File(ComponentBase):
    """ Representing a single file, can't have children. Not implemented yet..."""
    def __init__(self):
        pass
    
    def SetState(self,vState):
        """ Not implemented """
        pass
    
class Component(ComponentBase):
    """ Representing a single directory, can have children."""
        
    offset = 0.75
    
    modifiedtextureid = None
    removedtextureid = None
    addedtextureid = None
    MESHUUID = "component.mesh"
    MATERIAL = "component.material"
    
    def __init__(self,vScene,vFolderInfo,vPos,vParent,vX=1,vY=1,vScale = V3(0,0,0)):
        """ Load mesh and texture and set state as added
        """
        super(Component,self).__init__()
        
        self.name = vFolderInfo.name
        self.folderinfo = vFolderInfo
        
        self.__x = vX
        self.__y = vY
        
        self.curRow = 0
        self.curColumn = 0
        
        self.__offset = [] #offsets in x,y dimension
        self.currentIndex = 0  
        self.scene = vScene
        self.pos = vPos
        self.scale = vScale
        self.color = 0 #blue

        self.modifiedtextureid, self.removedtextureid,self.addedtextureid = None,None,None
        
        entname = "Component-%s" % self.name
        ent = vScene.GetEntityByNameRaw(entname)
        #self.currenttexid = Component.addedtextureid
        # self.addedtextureid = self.CreateTexture(self.name,System.Drawing.Color.Black,System.Drawing.Color.SkyBlue)
        
        self.currenttexid = "" #self.addedtextureid
        
        if ent:
        #     #self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
            print "Component: %s found from scene" % ("rps_component_" + self.name)
            self.ent = ent
        else:
            print "loading component mesh"
            new_mesh(self.scene, Component.MESHUUID, Component.MATERIAL, entname,
                     V3(), self.pos, self.scale)
            
        #     self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(self.currenttexid))
            
        #     self.sog.RootPart.Scale = V3(vX,vY,1)
        #     self.sog.RootPart.Name =  "rps_component_" + self.name
            
        #     self.scene.AddNewSceneObject(self.sog, False)

        # #print "mesh id for component: ", self.rop.RexMeshUUID
        # #self.sog.SetText(self.name,V3(1.0,1.0,0.0),1.0)

        # self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.folderinfo.url)
        
        # self.modified = False
        
    def AddChild(self,vFolderInfo):

        temp = self.pos
        p = V3(self.curColumn + temp.x() + self.curColumn * Component.offset,
               self.curRow + temp.y() + self.curRow * Component.offset,
               temp.z() + 0.5)
               
        child =  Component(self.scene, vFolderInfo, p, self, 1,1,V3(0.9,0.9,0.9))
        
        #child.sog.RootPart.Scale = V3(0.85,0.85,1)
        
        if self.curColumn < self.__x - 1: 
            self.curColumn += 1
        else:
            self.curColumn = 0
            self.curRow += 1
            
        return child
            
    def SetState(self,vState):
        """ Changes texture if needed. vState can be modified,removed or added """
        #print "component: ",self.name, "is at state: ",vState
        tex = self.currenttexid
        temp = self.currenttexid
        
        # if vState == "modified":
        #     if not self.modifiedtextureid:
        #         self.modifiedtextureid = self.CreateTexture(self.name,System.Drawing.Color.Black,System.Drawing.Color.Yellow)
            
        #     tex = self.modifiedtextureid
        # elif vState == "removed" or vState == "Removed":
        #     if not self.removedtextureid:
        #         self.removedtextureid = self.CreateTexture(self.name,System.Drawing.Color.Black,System.Drawing.Color.Red)
            
        #     tex = self.removedtextureid
        # elif vState == "added":
        #     tex = self.addedtextureid
        
        # if tex != temp:
        #     self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))

        self.currenttexid = tex
        
    # def CreateTexture(self,vText,vTextColor,vBackgroundColor):

    #     width,height = 256,256
        
    #     bitmap = System.Drawing.Bitmap(width,height,System.Drawing.Imaging.PixelFormat.Format32bppRgb)
        
    #     bgbrush = System.Drawing.SolidBrush(vBackgroundColor)
        
    #     graph = System.Drawing.Graphics.FromImage(bitmap);
    #     graph.FillRectangle(bgbrush, 0, 0, width, height)

    #     textFont = System.Drawing.Font("Courier", 25, System.Drawing.FontStyle.Bold)
    #     textBrush = System.Drawing.SolidBrush(vTextColor)
    #     layoutrect = System.Drawing.RectangleF(0,10,256,45)
    #     text = ""

    #     if len(vText) > 11:
    #         text = vText[0:11]
    #         text = text + "..."
    #     else:
    #         text = vText
            
    #     graph.DrawString(text, textFont, textBrush, layoutrect)

    #     imageJ2000 = OpenMetaverse.Imaging.OpenJPEG.EncodeFromImage(bitmap, True);
        
    #     tex = rexprojectspaceutils.StoreBytesAsTexture(self.scene,imageJ2000)

    #     return tex
    
class SWProject:
    """ Controller class for software projects that knows of it's developers,
        components and compilation results of the source code. """
        
    def __init__(self, vScene,vProjectName, vComponents, vDevelopers):
        """ Create projects components and resolve latest developer
            and update components and developers visualizations respectively
        """
        
        self.scene = vScene
        self.projectName = vProjectName
        
        self.components = {}
        self.developers = vDevelopers
        
        #map developers to the components, so that project knows where developers
        #are
        self.componentsAndDevelopersDict = {}
        
        #will contain developers that could have caused a build break
        self.blameList = []
        
        self.lastBuildTime = 0
        self.bLatestBuildFailed  = False
        
        self.latestcommitter = None
        #print "-----------------",self.developers[0].developerinfo.login
        
        if len(self.developers) > 0:
            #self.latestcommitter = self.developers[0]
            self.latestcommitter = self.resolveLatestCommitter()
            self.latestcommitter.updateIsLatestCommitter(True)
        
        #create first component representing self
        self.ent = self.scene.GetEntityByNameRaw("swproject")
        
        rootfolder = rexprojectspacedataobjects.FolderInfo("/",0)
        
        self.pos = self.ent.placeable.transform.position()
        self.component = Component(vScene, rootfolder, self.pos, None, 6,6, self.pos)
        self.components["/"] = self.component
        self.componentsAndDevelopersDict["/"] = []
        
        for component in vComponents:
            self.addComponent(component)
            
        #place developers to their initial positions...
        for dev in self.developers:
            latestcommit = dev.developerinfo.latestcommit
            if latestcommit != None or latestcommit != "":
                #print latestcommit 
                self.updateDeveloperLocationWithNewCommitData(latestcommit,False)
        
        self.visualizeLatestCommitModifications()
        
        #get all commits
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        # nc.OnNewCommit += self.updateDeveloperLocationWithNewCommitData
        
        # nc.OnBuild += self.buildFinished
        
    def __del__(self):
        """ """
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnNewCommit -= self.updateDeveloperLocationWithNewCommitData
    
    def visualizeLatestCommitModifications(self):
        """ Update components that are modified by latest commit """
        if self.latestcommitter:
            
            #unset previous modified
            for component in self.components.values():
                component.SetState("added")#return to default
                
            #change every components color that was mod,added or removed
            #within a latest commit
            for item in self.latestcommitter.developerinfo.latestcommit.directories:
                #locate component, there is a change that this is not on a map yet...
                print item
                try:
                    component = self.components[item]
                except KeyError:
                    print "RexProjectSpace: unknown component in commit -- possibly a new dir in a branch, and different branch used as reference:", item, "not in:", self.components.keys()
                #perhaps one day we might tell component/file if
                #it was removed,added or modified, but now we have
                #only root level folders...
                component.SetState("modified")
    
    def resolveLatestCommitter(self):
        """ """
        devs = self.sortDevelopers(self.developers)
        latestcommmitter = devs[len(devs)-1]
        return latestcommmitter
    
    def addComponent(self, vComponent):
        """ Adds component to the project root folder """
        self.componentsAndDevelopersDict[vComponent.name] = []
        c = self.component.AddChild(vComponent)
        
        self.components[vComponent.name] = c
        #visualize components "size" and modified date
        """
        tempscale = c.sog.RootPart.Scale
        scale = max(0.4,vComponent.numberofsubfiles/25)
        scale = min(scale,1)
        c.sog.RootPart.Scale = V3(scale,scale,tempscale.Z)
        """
        return c

    def updateDeveloperLocationWithNewCommitData(self, vCommit, vMakeCurrent = True):
        """ Position developer on top of component that was modified by the 
            developer. If component was new, then create a new component."""
        #locate developer
        committer = None
        for dev in self.developers:
            if dev.developerinfo.login == vCommit.login or dev.developerinfo.name == vCommit.name:
                committer = dev
                break
        
        #we know nothing about this developer
        if committer == None:
            print "no committer with login:%s and name:%s, must be a new developer.(message:%s) "%(vCommit.login,vCommit.name,vCommit.message)
            
            developerinfo = rexprojectspacedataobjects.DeveloperInfo(vCommit.login,vCommit.name)
            developerinfo.latestcommit = vCommit
            committer = swdeveloper.SWDeveloper(self.scene,developerinfo,False)
            
        #there is no way to know for sure if the commit has been set to dev
        #before this, so set it...
        committer.developerinfo.latestcommit = vCommit
        
        #locate correct component 
        component = None
        
        print "---hakemistot commitissa___projekti: ", vCommit.directories
        
        if len(vCommit.directories) > 0:
            
            #print "commit directory: ",vCommit.directories[0]
            for i in range(0,len(vCommit.directories)):
                try:
                    component = self.components[vCommit.directories[i]]
                except:
                    print "No component named:%s  , must be a new component"%(vCommit.directories[0])
                    folder = rexprojectspacedataobjects.FolderInfo(vCommit.directories[0],0)#new directory
                    component = self.addComponent(folder)
                    
            component = self.components[vCommit.directories[0]]  
            #remove developer from previous componenent, k is component name and c lists developers to
            #component named k... 
            for k,c in self.componentsAndDevelopersDict.iteritems():
                if c.count(committer)>0:
                    c.remove(committer)
                    #devs = c
                    previouscomponentsdevs = c
                    
                    #rearrange devs
                    h = 0
                    for j in range(len(previouscomponentsdevs)):
                        print "removed dev"
                        dev = previouscomponentsdevs[j]
                        # h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
                        # h += 0.2
                        
                        comp = self.components[k]#get component instance from dict
                        
                        # pos = comp.sog.AbsolutePosition
                        # devPos = V3(pos.X,pos.Y,pos.Z + h)
                        dev = previouscomponentsdevs[j]
                        # dev.move(devPos)
                        
                    print "developer: ", committer , "removed from ", self.components[k].name
                    break #developer can be only in one component at the same time
        else:
            component = self.component #no directories, so put dev into "container component"
        
        devs = self.componentsAndDevelopersDict[component.name]
        devs.append(committer)
            
        devs = self.sortDevelopers(devs)
        #for d in devs:
        #    print d.latestcommit.date
        
        h = 0
        for j in range(len(devs)):
            dev = devs[j]
            # pos = component.sog.AbsolutePosition
            # devPos = V3(pos.X,pos.Y,pos.Z + h)
            
            # dev.move(devPos)
            
            # h += dev.sog.RootPart.Scale.Z * swdeveloper.SWDeveloper.HEIGHT
            # h += 0.2
        
        #finally set latest committer if wanted
        if vMakeCurrent == True:
            
            print "Ennen updatea: ", self.latestcommitter.developerinfo.login
            
            self.latestcommitter.updateIsLatestCommitter(False)
            
            self.latestcommitter = committer
            
            #so, these commits are processed at runtime, not at initializing phase
            #update also the developervisualization
            self.latestcommitter.developerinfo.commitcount += 1
            self.latestcommitter.developerinfo.latestcommit = vCommit
            self.latestcommitter.developerinfo.latestcommitid = vCommit.id

            self.latestcommitter.updateVisualization()
            
            #print "developer %s is current committer"%(self.latestcommitter.developerinfo.login)
            self.latestcommitter.updateIsLatestCommitter(True)
            
            self.visualizeLatestCommitModifications()
            print "jalkeen updaten: ", self.latestcommitter.developerinfo.login
            
    from operator import itemgetter,attrgetter
    def sortDevelopers(self,vDevelopers):
        """ sort developers based on their commit date, so that newest is at the top
        """
        devs = vDevelopers
        devs.sort(self.compareCommitDates)
        #for d in devs:
        #    print d.developerinfo.login ," committed on : ",d.developerinfo.latestcommit.date
        return devs
    
    def compareCommitDates(self,x,y):
        return cmp(x.developerinfo.latestcommit.date,y.developerinfo.latestcommit.date)
 
    def buildFinished(self,vBuilds):
        """ Handle build notifications by creating a blame list containing
            developers that might have broken the build. """
        print "Build finished..."
        bResult = True
        
        if len(vBuilds) < 1:
            return
        
        build = vBuilds[0]
        
        if build.result != "success":
            bResult = False
            
        if bResult == False:
            if self.bLatestBuildFailed == True:
                #don't update blamelist, because build was allready failing...
                return
            else:
                bLatestBuildFailed = True
                latestSuccess = vBuilds[1]
                print "edellinen onnistunut: ",latestSuccess.time 
                #make blamelist
                for d in self.developers:
                    if d.developerinfo.latestcommit.date > latestSuccess.time:
                        print "dev added to blamelist: ", d.developerinfo.login
                        self.blameList.append(d)
                        
                self.visualizeBlameListMembers()
        else:
            self.bLatestBuildFailed = False
            self.unsetBlameListMemberVisualizations()
            self.blameList = []
            
        self.lastBuildTime = build.time
       
    def visualizeBlameListMembers(self):
        """ Tell developers that they might have broken the build """
        for d in self.blameList:
            d.updateDidBrakeBuild(True)
    
    def unsetBlameListMemberVisualizations(self):
        """ Tell developers that the build is ok. """
        for d in self.blameList:
            d.updateDidBrakeBuild(False)
 
