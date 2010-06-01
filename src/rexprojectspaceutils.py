
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


def setWorld(vWorld):
    pass

def world():
    pass

def euler_to_quat(yaw_deg, pitch_deg, roll_deg):
    # lifted & modded from Naali conversions.py
    #let's assume that the euler has the yaw,pitch and roll and they are in degrees, changing to radians
    c1 = math.cos(math.radians(yaw_deg)/2)
    c2 = math.cos(math.radians(pitch_deg)/2)
    c3 = math.cos(math.radians(roll_deg)/2)
    s1 = math.sin(math.radians(yaw_deg)/2)
    s2 = math.sin(math.radians(pitch_deg)/2)
    s3 = math.sin(math.radians(roll_deg)/2)
    #print c1, c2, c3, s1, s2, s3
    c1c2 = c1*c2
    s1s2 = s1*s2
    w =c1c2*c3 - s1s2*s3
    x =c1c2*s3 + s1s2*c3
    y =s1*c2*c3 + c1*s2*s3
    z =c1*s2*c3 - s1*c2*s3
    
    return OpenMetaverse.Quaternion(x, y, z, w)
    
def load_mesh(scene, meshpath, materialpath, description, rot=OpenMetaverse.Quaternion(0, 0, 0, 1), pos=V3(128, 128, 30), scale=V3(1, 1, 1)):
    uid = OpenMetaverse.UUID.Random()
    
    asset = OpenSim.Framework.AssetBase()
    asset.Name = "George"
    asset.FullID = uid
    asset.Type = 43 # ??
    asset.Description = description
    
    print "Loading mesh: ", os.path.abspath(meshpath)
    
    asset.Data = System.IO.File.ReadAllBytes(os.path.abspath(meshpath))
     
    scene.AssetService.Store(asset)
    #root_avatar_uuid = scene.RegionInfo.MasterAvatarAssignedUUID
    list = scene.GetAvatars()
    if len(list) > 0:
        sp = list[0]
    else:
        print "No avatar, can't upload assets..."
    root_avatar_uuid = sp.UUID
    
    print "avatar uid:", root_avatar_uuid
    
    sceneobjgroup = scene.AddNewPrim(
        root_avatar_uuid, root_avatar_uuid,
        pos, rot, OpenSim.Framework.PrimitiveBaseShape.CreateBox())
    rexObjects = scene.Modules["RexObjectsModule"]
    sceneobjgroup.RootPart.Scale = scale
    robject = rexObjects.GetObject(sceneobjgroup.RootPart.UUID)
    print "root uuid", sceneobjgroup.RootPart.UUID
    robject.RexMeshUUID = asset.FullID
    robject.RexDrawDistance = 256
    robject.RexCastShadows = True
    robject.RexDrawType = 1;
    robject.RexCollisionMeshUUID = asset.FullID;
   
    matdata = open(materialpath).read()
    
    #print matdata
    matparser = OgreSceneImporter.OgreMaterialParser(scene)
    rc, mat2uuid, mat2texture = matparser.ParseAndSaveMaterial(
        matdata)
    mat2uuid = dict(mat2uuid)
    print "mat-uuid dict:", mat2uuid
    if not rc:
        print "material parsing failed"
        return
    
    matnames, errors = DotMeshLoader.ReadDotMeshMaterialNames(asset.Data)
    for i, mname in enumerate(matnames):
        robject.RexMaterials.AddMaterial(i, mat2uuid[mname])
        print "material added:", mname
        
    return sceneobjgroup, robject        

        
 