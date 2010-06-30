
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

#to be removed
def load_texture(vScene,vTexturePath):
    #not ready
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = vTexturePath
    asset.FullID = uid
    asset.Type = 0 # ?? texture??
    asset.Description = vTexturePath
    
    ##print "Loading texture script: ", os.path.abspath(vTexturePath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(vTexturePath))
     
    val = vScene.AssetService.Store(asset)
    return asset.ID
 
 

def load_texture_with_uuid(vScene,vTexturePath,vUUID=-1):
    
    if(vUUID != -1):
        uid = vUUID
    else:
        uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = vTexturePath
    asset.FullID = uid
    asset.Type = 0 # ?? texture??
    asset.Description = vTexturePath
    
    ##print "Loading texture script: ", os.path.abspath(vTexturePath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(vTexturePath))
     
    val = vScene.AssetService.Store(asset)
    return asset.ID

 
def load_skeletonanimation(vScene,vSkeletonAnimPath):
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
    #not ready
    uid = OpenMetaverse.UUID.Random()
    asset = OpenSim.Framework.AssetBase()
    asset.Name = particlescriptpath
    asset.FullID = uid
    asset.Type = 47 # ?? particle script??
    asset.Description = description
    
    ##print "Loading particle script: ", os.path.abspath(particlescriptpath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(particlescriptpath))
     
    val = scene.AssetService.Store(asset)
    return asset.ID
    
    
def store_mesh(scene, meshpath):
    uid = OpenMetaverse.UUID.Random()
    
    asset = OpenSim.Framework.AssetBase()
    asset.Name = "George"
    asset.FullID = uid
    asset.Type = 43 # ??
    asset.Description = description
    
    ##print "Loading mesh: ", os.path.abspath(meshpath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(meshpath))
     
    scene.AssetService.Store(asset)
    
    return asset.FullID
    
"""
def bind_mesh(scene, sceneobjgroup , materialpath, description, rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30), scale=V3(1, 1, 1)):


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
    
    ###print matdata
    matparser = OgreSceneImporter.OgreMaterialParser(scene)
    rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
        matdata)
    mat2uuid = dict(mat2uuid)
    ##print "mat-uuid dict:", mat2uuid
    if not rc:
        ##print "material parsing failed"
        return
    
    matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
    for i, mname in enumerate(matnames):
        robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
        ###print "material added:", mname
        
    return sceneobjgroup, robject 
"""
    
def load_mesh(scene, meshpath, materialpath, description, rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30), scale=V3(1, 1, 1)):
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
    newString = matdata
    #newString = newString.replace("bug_wings_rigged_face_Sphere","1234565")
    
    ###print newString
    
    #modify all the material scripts so that instead of filepaths for textures,
    #there is reference to the uuid of the texture
    
    
    
    ###print matdata
    matparser = OgreSceneImporter.OgreMaterialParser(scene)
    rctempp, mat2uuidtemp, mat2texturetemp = matparser.ParseAndSaveMaterial(
        matdata)
        
    mat2texturetemp = dict(mat2texturetemp)
    ##print mat2texturetemp
    
    for k,v in enumerate(mat2texturetemp):
        ##print mat2texturetemp[v]
        
        path = v.ToString()
        ##print path
        load_texture_with_uuid(scene,path,mat2texturetemp[v].ToString())
        newString = newString.replace(path,mat2texturetemp[v].ToString())
    
    ###print newString
    
    rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
        matdata)

    mat2uuid = dict(mat2uuid)
    
    ###print mat2texture
    
    ##print "mat-uuid dict:", mat2uuid
    if not rc:
        ##print "material parsing failed"
        return
    
    matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
    for i, mname in enumerate(matnames):
        robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
        ##print "material added:", mname
        
    return sceneobjgroup, robject        

        
 