import naali
V3 = naali.Vector3df

def new_mesh(scene, meshpath, materialpath, description, rot=V3(0, 0, 0), pos=V3(0, 0, 0), scale=V3(1, 1, 1)):
    """Creates a new scene entity with the components to show a mesh, and sets a material for it.
       Returns the created entity.
    """

    ent = scene.CreateEntityRaw(scene.NextFreeId(), ["EC_Placeable", "EC_Mesh", "EC_Name"])
    ent.SetName(description)

    ent.mesh.SetMeshRef(meshpath)

    #ent.mesh.materials = [materialpath]

    #these setters don't apparently work :o
    #t = ent.placeable.transform
    # t.SetRot(rot)
    # r.SetPos(pos)
    # t.SetScale(scale)
    # ent.placeable.transform = t
    ent.placeable.Translate(pos)

    return ent
