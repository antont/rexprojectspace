import clr, math

clr.AddReference('OpenMetaverseTypes')
import OpenMetaverse

clr.AddReference("mscorlib.dll")
import System

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types

clr.AddReference('OpenSim.Framework')
import OpenSim.Framework

clr.AddReference('OpenSim.Region.Framework')
import OpenSim.Region.Framework

asm = clr.LoadAssemblyByName('OpenSim.Region.ScriptEngine.Shared')

import OpenMetaverse
from OpenMetaverse import Vector3 as V3

import time

import rexprojectspaceutils
import rexprojectspacedataobjects

import rexprojectspacenotificationcenter
import clickhandler

class Tree:
    """ View object that is able to create tree tiles
        when needed."""
    
    def __init__(self,vScene,vName):
        """ Load tree base and top meshes """
        
        self.tile_height = 2.5
        self.tree_base_height = 1.0
        
        self.scene = vScene
        
        self.treebase = None
        self.tiles = [] #from bottom to up
        self.branches = []
        self.treeTop = None
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        self.UUID = OpenMetaverse.UUID("e0afbfb2-fbac-4bb2-b797-915d2eaa7730") #root of tree...
        
        """
        if not self.scene.GetSceneObjectPart(self.UUID):
            #print "No tree..."
            return
        """

        if not self.scene.GetSceneObjectPart("tree_base"):
            print "No tree..."
            return
        """
        self.sog = self.scene.GetSceneObjectPart(self.UUID).ParentGroup
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        self.pos = self.sog.AbsolutePosition
        """
        
        self.sog = self.scene.GetSceneObjectPart("tree_base").ParentGroup
        self.UUID = self.sog.UUID
        self.rop = rexObjects.GetObject(self.UUID)
        self.sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        self.pos = self.sog.AbsolutePosition
        
        
        sop =  vScene.GetSceneObjectPart("rps_treebase_" + vName)
        tex = rexprojectspaceutils.load_texture(self.scene,"rpstextures/treebranch_green.jp2")
        
        if sop:
            self.treebasesog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.treebaserop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Tree: %s found from scene"%(vName)
        else:    
            self.treebasesog,self.treebaserop = rexprojectspaceutils.load_mesh(self.scene,"rpsmeshes/treebase.mesh","rpsmeshes/treebase.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
            self.treebasesog.RootPart.Name =  "rps_treebase_" + vName
            self.scene.AddNewSceneObject(self.treebasesog, False)
            self.treebasesog.AbsolutePosition = V3(self.sog.AbsolutePosition)
            #self.treebasesog.SetText("master",V3(1.0,1.0,0.0),1.0)
            
            self.treebaserop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        
        sop = None
        
        self.treetop = TopBranch(self.scene,"master")
        
        """
        sop =  vScene.GetSceneObjectPart("rps_treetop_" + vName)
        
        if sop:
            self.treetopsog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.treetoprop = rexObjects.GetObject(self.sog.RootPart.UUID)
            #print "Tree: %s found from scene"%(vName)
        else:
            temp = self.treebasesog.AbsolutePosition
            self.treetopsog,self.treetoprop = rexprojectspaceutils.load_mesh(self.scene,"rpsmeshes/treetop.mesh","rpsmeshes/treetop.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0),V3(temp.X,temp.Y,temp.Z+1))
            self.treetopsog.RootPart.Name =  "rps_treetop_" + vName
            
            self.scene.AddNewSceneObject(self.treetopsog, False)
            self.treetoprop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(tex))
        
        #print "mesh id for tree: ", self.rop.RexMeshUUID
        """
        
    def addNewBranch(self,vBranchInfo,vTexturePath,vParentName=""):
        """ Creates a new branch and a tile if needed """         
           
        nbr = len(self.tiles)
        if(nbr == 0):
            temp = self.pos
            z = temp.Z + self.tree_base_height
            self.tiles.append(TreeTile(self.scene,V3(temp.X,temp.Y,z),self.tile_height,"tile" + str(nbr)))
            nbr = 1
           
        tile = self.tiles[nbr-1]
        currentPlace = tile.currentIndex
        
        if currentPlace >= len(tile.locations):
            temp = self.pos
            z = self.pos.Z + nbr*self.tile_height + self.tree_base_height
            newLoc = V3(self.pos.X,self.pos.Y,z)
            tile = TreeTile(self.scene,newLoc,self.tile_height,str(nbr))
            self.tiles.append(tile)
            #put top in to a place
            temp = tile.sog.AbsolutePosition
            newpos = V3(temp.X,temp.Y,temp.Z+self.tile_height)
            self.treetop.sog.NonPhysicalGrabMovement(newpos)
            print "paikka: ", newpos
        
        
        branch = Branch(self.scene, vBranchInfo.name,vTexturePath,tile.locations[tile.currentIndex],V3(1.0,1.0,1.0),tile.rotations[tile.currentIndex])
        
        self.branches.append(branch)
        
        tile.currentIndex += 1
        
        return branch
        
            
class TreeTile:
    """ View class for single treetile. Knows positions and rotations/euler angles to
        branches
    """
    MESHUUID = OpenMetaverse.UUID.Zero
    TEXTUREUUID = OpenMetaverse.UUID.Zero
    
    def __init__(self,vScene,vPos,vHeight,vName):
        """ Load mesh and calculate positions and rotations to branches 
            (that may or may not be created later on).
        """
        self.currentIndex = 0  #increment on add
        self.scene = vScene
        self.pos = vPos
        self.w = 0.2
        self.height = vHeight
        #print "_______Tile height:_______",self.height
        
        self.locations = []
        for i in range(4):
            tempPos = None
            if i%2 == 0:
                tempPos = V3(self.pos.X - self.w/2, self.pos.Y,self.pos.Z + (i*self.height/4 + 0.15))
            else:
                tempPos = V3(self.pos.X + self.w/2, self.pos.Y,self.pos.Z + (i*self.height/4 + 0.15))
            self.locations.append(tempPos)
            
        self.rotations = [rexprojectspaceutils.euler_to_quat(20,0,0),
                          rexprojectspaceutils.euler_to_quat(-20,180,0),
                          rexprojectspaceutils.euler_to_quat(20,0,0)
                          ,rexprojectspaceutils.euler_to_quat(-20,180,0)] #insert branch rotations to here, with quats…

        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        sop =  vScene.GetSceneObjectPart("rps_treetile_" + vName)
        
        if sop:
            self.sog = sop.ParentGroup
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            TreeTile.MESHUUID = self.rop.RexMeshUUID.ToString()
            
        else:
            if TreeTile.MESHUUID == OpenMetaverse.UUID.Zero:
                print "loading tile mesh"
                TreeTile.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"rpsmeshes/treetile.mesh","rpsmeshes/treetile mesh")
            
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,TreeTile.MESHUUID,"rpsmeshes/treetile.material",rexprojectspaceutils.euler_to_quat(0,0,0),self.pos)
            
            if TreeTile.TEXTUREUUID == OpenMetaverse.UUID.Zero:
                TreeTile.TEXTUREUUID = rexprojectspaceutils.load_texture(self.scene,"rpstextures/treebranch_green.jp2")
            
            self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(TreeTile.TEXTUREUUID))
            self.sog.RootPart.Name =  "rps_treetile_" + vName
            ##print "mesh id for tile: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)


class Branch:
    """ View class for a single branch """
    MESHUUID = OpenMetaverse.UUID.Zero
    textures = {}  #texturepath, textureid map
    w = 1
    
    
    def __init__(self,vScene,vBranchName,vTexturePath,vPos,vScale,vRot):
        """ Load mesh and set the texture.
        """
        self.scene = vScene
        self.texturepath = vTexturePath
        self.pos = vPos
        self.scale = vScale
        self.rot = vRot
        
        self.currenttexid = OpenMetaverse.UUID.Zero
        
        if Branch.MESHUUID == OpenMetaverse.UUID.Zero:
            print "loading branch mesh"
            Branch.MESHUUID = rexprojectspaceutils.load_mesh_new(self.scene,"rpsmeshes/treebranch.mesh","rpsmeshes/treebranch mesh")
        
        sop =  vScene.GetSceneObjectPart("rps_branch_" + vBranchName)
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "branch: %s found from scene"%(vBranchName)
            Branch.MESHUUID = self.rop.RexMeshUUID.ToString()
        else:
            self.sog,self.rop = rexprojectspaceutils.bind_mesh(self.scene,Branch.MESHUUID,"rpsmeshes/treebranch.material",vRot,vPos,vScale)
            self.sog.RootPart.Name =  "rps_branch_" + vBranchName
        
        
        self.SetTexture(vTexturePath)
        self.sog.SetText(vBranchName,V3(0.0,1.0,0.0),1.0)
        ##print "mesh id for branch: ", self.rop.RexMeshUUID
        
        self.scene.AddNewSceneObject(self.sog, False)

    def SetTexture(self,vTexturePath):
        """ Loads and sets the given texture to a branch (uv-mapped) """
        texid = OpenMetaverse.UUID.Zero
        try:
            texid = Branch.textures[vTexturePath] 
        except:
            texid = rexprojectspaceutils.load_texture(self.scene,vTexturePath)
            Branch.textures[vTexturePath] = texid

        if texid != self.currenttexid and texid != OpenMetaverse.UUID.Zero:
            self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(texid))
            self.currenttexid = texid

class TopBranch:
    def __init__(self,vScene,vBranchName):
        sop =  vScene.GetSceneObjectPart("rps_treetop_" + vBranchName)
        self.scene = vScene
        self.currenttexid = OpenMetaverse.UUID.Zero
        self.textures = {}
        
        if sop:
            self.sog = sop.ParentGroup
            rexObjects = vScene.Modules["RexObjectsModule"]
            self.rop = rexObjects.GetObject(self.sog.RootPart.UUID)
            print "branch: %s found from scene"%(vBranchName)
            
        else:
            self.sog,self.rop = rexprojectspaceutils.load_mesh(self.scene,"rpsmeshes/treetop.mesh","rpsmeshes/treetop.material","test mesh data",rexprojectspaceutils.euler_to_quat(0,0,0))
            self.sog.RootPart.Name =  "rps_treetop_" + vBranchName
        
        
        #self.SetTexture(vTexturePath)
        self.sog.SetText(vBranchName,V3(0.0,1.0,0.0),1.0)
        
    def SetTexture(self,vTexturePath):
        """ Loads and sets the given texture to a branch (uv-mapped) """
        texid = OpenMetaverse.UUID.Zero
        try:
            texid = self.textures[vTexturePath] 
        except:
            texid = rexprojectspaceutils.load_texture(self.scene,vTexturePath)
            self.textures[vTexturePath] = texid

        if texid != self.currenttexid and texid != OpenMetaverse.UUID.Zero:
            self.rop.RexMaterials.AddMaterial(0,OpenMetaverse.UUID(texid))
            self.currenttexid = texid
            
import threading
class SWSourceTree:
    """ Controller part of the tree """
    
    def __init__(self, vScene, vProjectName, vBranchInfos):
        """ Create view objects by using vBranchInfos list and register to
            branch and build related notifications"""
            
        self.scene = vScene
        self.projectName = vProjectName
        self.branches = {} #holds name branch pairs...
        self.branchinfos = {} #holds name branchinfo pairs...
        self.clickhandlers = [] # to hold reference to the created click handlers
        
        self.bCurrentBuildFailed = False

        self.commitsThreshold = 60*60*24*30 # about 1 month
        
        self.timer = threading.Timer(120,self.onCommitTimer)
        
        rexObjects = self.scene.Modules["RexObjectsModule"]
        
        self.tree = Tree(vScene,vProjectName)
        self.treerop = rexObjects.GetObject(self.tree.UUID)
        
        tempPos = self.tree.pos
        
        self.rainPlaceHolderSog = self.createRainPlaceHolder(V3(tempPos.X,tempPos.Y,tempPos.Z + 45))
        self.rainPlaceHolderRop = rexObjects.GetObject(self.rainPlaceHolderSog.UUID)
        
        self.rainparticleid = rexprojectspaceutils.load_particle_script(self.scene,"rpsparticles/rain.particle","")
        self.fireparticleid = rexprojectspaceutils.load_particle_script(self.scene,"rpsparticles/fire.particle","")

        self.addNewBranches(vBranchInfos)
        
        masterbranch = None
        
        for b in vBranchInfos:
            if b.name == "master":
                masterbranch = b
                break
        
        if masterbranch:
            self.clickhandlers.append(clickhandler.URLOpener(self.scene,self.tree.treetop.sog,self.tree.treetop.rop,masterbranch.url))
            #self.tree.treetop.sog.SetText("master",V3(0.0,1.0,0.0),1.0)

        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        
        nc.OnBuild += self.updateBuildResult
        
        nc.OnBranchesUpdated += self.updateBranches
        nc.OnNewBranches += self.addNewBranches
        
        self.timer.start()

    def __del__(self):
        """ unregister """
        nc = rexprojectspacenotificationcenter.RexProjectSpaceNotificationCenter.NotificationCenter(self.projectName)
        nc.OnBuild -= self.updateBuildResult

    def createRainPlaceHolder(self,vPos):
        """ Creates box that will be used as a rains starting 
            point, sort of."""
        
        pbs = OpenSim.Framework.PrimitiveBaseShape.CreateBox()
        pbs.SetHeigth(1)
        
        sog = OpenSim.Region.Framework.Scenes.SceneObjectGroup(
        OpenMetaverse.UUID.Random(),vPos,pbs)
        
        sog.RootPart.Scale = V3(0.05,0.05,0.05)
        sog.RootPart.UpdateRotation(rexprojectspaceutils.euler_to_quat(0,0,90))
        
        self.scene.AddNewSceneObject(sog, False)
        #print "placeholder position",vPos
        return sog    
        
    def updateBuildResult(self,vBuilds):
        """ Handle build notifications """
        res = True
        build = vBuilds[0]
        if build.result != "success":
            res = False
        
        if res == True:
            self.setBuildSuccesfull()
        else:
            self.setBuildFailed()
        
    
    def setBuildSuccesfull(self):
        """ If build was broken, make it rain """
        if self.bCurrentBuildFailed == True:
            self.rainPlaceHolderRop.RexParticleScriptUUID = self.rainparticleid
            self.buildresultparticletimer = threading.Timer(5,self.onBuildResultParticleTimer)
            self.buildresultparticletimer.start()
            
        self.bCurrentBuildFailed = False
    
    def setBuildFailed(self):
        """ If this was the first failing build in a row,
            set the tree on fire. """
        if self.bCurrentBuildFailed == False:
            self.treerop.RexParticleScriptUUID = self.fireparticleid
        self.bCurrentBuildFailed = True
        
    def addNewBranches(self,vBranchInfos,vParentName=""):
        """vParentName == None means to add branch to main tree, otherwise add to
           other branch. Call tree views addNewBranch to add new branch view.
           Evaluate latest commit date and choose color/
           texture based on that
           """
           
        today = time.gmtime(time.time())
        tday = time.time()
            
        for branch in vBranchInfos:
            bname = branch.name.strip()
            
            if self.branches.keys().count(branch.name) > 0:
                continue #not new
            
            if bname == "master":
                texpath = "rpstextures/treebranch_green.jp2"
                if tday - self.commitsThreshold > time.mktime(branch.latestcommitdate):
                    texpath = "rpstextures/treebranch_rust.jp2" 
                
                self.tree.treetop.SetTexture(texpath)
                print "tree tops texture", texpath
                continue
            
            #Evaluate latest commit data and create branch
            texpath = "rpstextures/treebranch_green.jp2"
            
            if tday - self.commitsThreshold > time.mktime(branch.latestcommitdate):
                texpath = "rpstextures/treebranch_rust.jp2"            
            
            
            b = self.tree.addNewBranch(branch,texpath,vParentName)
            b.rop.RexClassName = "sourcetree.BranchScaler"
            
            self.clickhandlers.append(clickhandler.URLOpener(self.scene,b.sog,b.rop,branch.url))
            
            self.branches[branch.name] = b
            self.branchinfos[branch.name] = branch
            
            #self.clickhandler = clickhandler.URLOpener(self.scene,self.sog,self.rop,self.issueinfo.url)
            
    def updateBranches(self,branches):
        """ Handle branch update notification by changing texture if needed
        """
        texpath = "rpstextures/treebranch_green.jp2"
        
        for branch in branches:
            try:
                b = self.branches[branch.name]
                
                b.SetTexture(texpath)
                
                bi = self.branchinfos[branch.name]
                bi.latestcommitdate = branch.latestcommitdate
                
            except:
                if branch.name == "master":
                    self.tree.treetop.SetTexture(texpath)
                    
    def onCommitTimer(self):
        """ Check if some branch has been too long without commits
            so that the texture has to be changed"""
        today = time.gmtime(time.time())
        tday = time.time()
        
        texpath = "rpstextures/treebranch_rust.jp2"            
        
        for branch in self.branchinfos.values():
            
            if tday - self.commitsThreshold > time.mktime(branch.latestcommitdate):
                try:
                    b = self.branches[branch.name]
                    b.SetTexture(texpath)
                except:
                    pass
                    
        self.timer.cancel()
        self.timer = 0
        
        self.timer = threading.Timer(120,self.onCommitTimer)
        self.timer.start()
        
        
    def onBuildResultParticleTimer(self):
        """ called after succesfull build, stops the rain and fire """
        print "---timer...---"
        
        self.treerop.RexParticleScriptUUID = OpenMetaverse.UUID.Zero
        self.rainPlaceHolderRop.RexParticleScriptUUID = OpenMetaverse.UUID.Zero
        
        self.buildresultparticletimer = 0
     