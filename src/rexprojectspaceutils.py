
import clr, math

clr.AddReference('OpenMetaverseTypes')
import OpenMetaverse

clr.AddReference("mscorlib.dll")
import System

from System import Array

clr.AddReference('ModularRex.RexFramework')
from ModularRex.RexFramework import IModrexObjectsProvider

clr.AddReference('OpenSim.Region.ScriptEngine.Shared')
from OpenSim.Region.ScriptEngine.Shared import LSL_Types
clr.AddReference('OpenSim.Framework')
import OpenSim.Framework
clr.AddReference('OpenSim.Region.Framework')
from OpenSim.Region.Framework.Interfaces import IRegionModule

clr.AddReference('OgreSceneImporter')
import OgreSceneImporter

clr.AddReference('RexDotMeshLoader')
from RexDotMeshLoader import DotMeshLoader

from OpenMetaverse import Vector3 as V3

import sys, os, sha

def euler_to_quat(yaw_deg, pitch_deg, roll_deg):
    # lifted & modded from Naali conversions.py
    #let's assume that the euler has the yaw,pitch and roll and they are in degrees, changing to radians
    c1 = math.cos(math.radians(yaw_deg)/2)
    c2 = math.cos(math.radians(pitch_deg)/2)
    c3 = math.cos(math.radians(roll_deg)/2)
    s1 = math.sin(math.radians(yaw_deg)/2)
    s2 = math.sin(math.radians(pitch_deg)/2)
    s3 = math.sin(math.radians(roll_deg)/2)
    ###print c1, c2, c3, s1, s2, s3
    c1c2 = c1*c2
    s1s2 = s1*s2
    w =c1c2*c3 - s1s2*s3
    x =c1c2*s3 + s1s2*c3
    y =s1*c2*c3 + c1*s2*s3
    z =c1*s2*c3 - s1*c2*s3
    
    return OpenMetaverse.Quaternion(x, y, z, w)

def load_texture(vScene,vTexturePath):
    """ Loads texture and returns texture id. This texture can be used as
        a material by inserting this texture to a rexobjectproperties' material
        dictionary
    """
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = vTexturePath
    asset.FullID = uid
    asset.Type = 0 # ?? texture??
    asset.Description = vTexturePath
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(vTexturePath))
    val = vScene.AssetService.Store(asset)
    
    return val
 
def load_skeleton_animation(vScene,vSkeletonAnimPath):
    """ Load skeleton animation and returns the id. Can be used as a skeleton anim
        by setting this id to rexobjectproperties' RexAnimationPackageUUID
    """
    #not ready
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = vSkeletonAnimPath
    asset.FullID = uid
    asset.Type = 44 # ?? skeleton anim??
    asset.Description = vSkeletonAnimPath
    
    ##print "Loading texture script: ", os.path.abspath(vSkeletonAnimPath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(vSkeletonAnimPath))
     
    val = vScene.AssetService.Store(asset)
    return asset.ID
 
def load_particle_script(vScene, particlescriptpath, description):
    """ Load skeleton animation and returns the id. Can be used as a skeleton anim
        by setting this id to rexobjectproperties' RexParticleScriptUUID
    """
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = particlescriptpath
    asset.FullID = uid
    asset.Type = 47 # ?? particle script??
    asset.Description = description
    
    ##print "Loading particle script: ", os.path.abspath(particlescriptpath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(particlescriptpath))
     
    val = vScene.AssetService.Store(asset)
    return asset.ID
    
  
def load_mesh(scene, meshpath, materialpath, description, rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30), scale=V3(1, 1, 1)):
    """ Loads mesh and gets related RexObjectProperties instance and sets materials to it (ie. to the mesh)
        return SceneObjectGroup and RexObjectProperties
    """
    uid = OpenMetaverse.UUID.Random()
    
    asset = OpenSim.Framework.AssetBase()
    asset.Name = "George"
    asset.FullID = uid
    asset.Type = 43 # ??
    asset.Description = description
    
    ##print "Loading mesh: ", os.path.abspath(meshpath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(meshpath))
     
    scene.AssetService.Store(asset)
    root_avatar_uuid = scene.RegionInfo.MasterAvatarAssignedUUID
    
    ###print "avatar uid:", root_avatar_uuid
    
    sceneobjgroup = scene.AddNewPrim(
        root_avatar_uuid, root_avatar_uuid,
        pos, rot, OpenSim.Framework.PrimitiveBaseShape.CreateBox())
    rexObjects = scene.Modules["RexObjectsModule"]
    sceneobjgroup.RootPart.Scale = scale
    robject = rexObjects.GetObject(sceneobjgroup.RootPart.UUID)
    ###print "root uuid", sceneobjgroup.RootPart.UUID
    robject.RexMeshUUID = asset.FullID
    robject.RexDrawDistance = 256
    robject.RexCastShadows = True
    robject.RexDrawType = 1;
    robject.RexCollisionMeshUUID = asset.FullID;
   
    matdata = open(materialpath).read()
    
    matparser = OgreSceneImporter.OgreMaterialParser(scene)
    
    rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
        matdata)

    mat2uuid = dict(mat2uuid)
    
    if not rc:
        return
    
    matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
    
    if errors:
        print "errors while loading mesh: ", errors
    
    #print mat2uuid
    
    for i, mname in enumerate(matnames):
        #print mname
        #print mat2uuid[mname]
        robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
        
    return sceneobjgroup, robject        

def load_material_from_string(scene,materialpath,description):
    """ Loads mesh and gets related RexObjectProperties instance and sets material to it (ie. to the mesh)
        return SceneObjectGroup and RexObjectProperties
    """
    print "hello"
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = description
    asset.FullID = uid
    asset.Type = 0 # ?? texture??
    asset.Description = description
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(materialpath))
    val = scene.AssetService.Store(asset)
    print "hello...", val
    return val

def load_mesh_new(scene, meshpath, description):
    mesh_uuid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Type = 43
    asset.FullID = mesh_uuid 
    asset.Description = description
    asset.Data = System.IO.File.ReadAllBytes(meshpath)
    val = scene.AssetService.Store(asset)
    #return asset.FullID.ToString()
    return val
    
#from oukautils
def bind_mesh(scene, mesh_assetidstr, materialpath,
                              rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30),
                              scale=V3(1, 1, 1)):
    
        #print "binding mesh ", mesh_assetidstr, "of type ", type(mesh_assetidstr)
        print mesh_assetidstr
        asset = scene.AssetService.Get(mesh_assetidstr)
        #asset = mesh_assetidstr
        root_avatar_uuid = scene.RegionInfo.MasterAvatarAssignedUUID
        
        print "binding..."
        sceneobjgroup = scene.AddNewPrim(
                root_avatar_uuid, root_avatar_uuid,
                pos, rot, OpenSim.Framework.PrimitiveBaseShape.CreateBox())
            
        sceneobjgroup.RootPart.Scale = scale
        
        
        print "scaled..."
        rexObjects = scene.Modules["RexObjectsModule"]
        robject = rexObjects.GetObject(sceneobjgroup.RootPart.UUID)
        
        #print "root uuid", sceneobjgroup.RootPart.UUID
        robject.RexMeshUUID = asset.FullID
        robject.RexDrawDistance = 256
        robject.RexCastShadows = True
        robject.RexDrawType = 1;
        robject.RexCollisionMeshUUID = asset.FullID;
        
        if materialpath != "":
            
            matdata = open(materialpath).read()
            matparser = OgreSceneImporter.OgreMaterialParser(scene)
            rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
                    matdata)
            mat2uuid = dict(mat2uuid)
            #print "mat-uuid dict:", mat2uuid
            if not rc:
                raise MaterialParsingError("material parsing failed")
        
            matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
            for i, mname in enumerate(matnames):
                robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
                #print "material added:", mname
        
        return sceneobjgroup, robject
    
def StoreBytesAsTexture(vScene,vBytes):
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = "tekstuuri"
    asset.FullID = uid
    asset.Type = 0 # ?? texture??
    asset.Description = "tekstuuri"
    asset.Data = vBytes
    val = vScene.AssetService.Store(asset)
    
    return val
    
    
#not used    
def load_and_send_urltexture(vScene,vSog,vRop,vUrl):
    if vSog and vRop and vScene:
        try:
            am = vScene.Modules["AssetMediaURLModule"]
        except KeyError:
            print "module not found"
            return
        
        id = vSog.RootPart.Shape.Textures.DefaultTexture.TextureID
        am.SetAssetData(id, vUrl, 1)
        vRop.RexMaterials.AddMaterial(0,id)
        
        am.SendMediaURLtoAll(id)
