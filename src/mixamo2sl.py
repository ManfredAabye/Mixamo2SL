import os
import sys
import collada
import numpy as np

def triangulate_faces(faces):
    triangles = []
    for face in faces:
        if len(face) == 3:
            triangles.append(face)
        elif len(face) == 4:
            # Split quad into two triangles
            triangles.append([face[0], face[1], face[2]])
            triangles.append([face[0], face[2], face[3]])
        else:
            # Handle polygon with more than 4 vertices (naive fan triangulation)
            for i in range(1, len(face) - 1):
                triangles.append([face[0], face[i], face[i + 1]])
    return triangles

def load_mtl(filename):
    materials = {}
    current_material = None

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('newmtl'):
                current_material = line.split()[1].strip()
                materials[current_material] = {}
            elif current_material:
                if line.startswith('Kd'):
                    materials[current_material]['diffuse'] = [float(x) for x in line.split()[1:]]
                elif line.startswith('map_Kd'):
                    materials[current_material]['texture'] = line.split()[1].strip()

    return materials

def convert_obj_to_dae(input_file, output_file, mtl_file=None):
    mesh = collada.Collada()
    vertices = []
    normals = []
    faces = []
    materials = {}
    current_material = None

    if mtl_file:
        materials = load_mtl(mtl_file)

    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append([float(x) for x in line.strip().split()[1:]])
            elif line.startswith('vn '):
                normals.append([float(x) for x in line.strip().split()[1:]])
            elif line.startswith('f '):
                face = []
                for vertex in line.strip().split()[1:]:
                    index = vertex.split('/')[0]
                    face.append(int(index) - 1)
                faces.append(face)
            elif line.startswith('usemtl'):
                current_material = line.split()[1].strip()

    # Convert lists to numpy arrays
    vertices = np.array(vertices)
    normals = np.array(normals)
    faces = triangulate_faces(faces)
    faces = np.array(faces)

    # Create the Collada geometry
    vertices_source = collada.source.FloatSource("vertices", vertices, ('X', 'Y', 'Z'))
    sources = [vertices_source]
    if normals.size > 0:
        normals_source = collada.source.FloatSource("normals", normals, ('X', 'Y', 'Z'))
        sources.append(normals_source)

    geom = collada.geometry.Geometry(mesh, "geometry0", "geometry0", sources)

    # Create the polygons
    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', "#vertices")
    if normals.size > 0:
        input_list.addInput(1, 'NORMAL', "#normals")

    triset = geom.createTriangleSet(faces, input_list)
    geom.primitives.append(triset)
    mesh.geometries.append(geom)

    if current_material and current_material in materials:
        mat = materials[current_material]
        effect = collada.material.Effect("effect0", [], "phong", diffuse=mat['diffuse'])
        mat = collada.material.Material("material0", current_material, effect)
        mesh.effects.append(effect)
        mesh.materials.append(mat)
        bind_mat = collada.scene.MaterialNode("materialref", mat, inputs=[])
        triset.material = bind_mat

    # Create a scene
    node = collada.scene.Node("node0", children=[collada.scene.GeometryNode(geom)])
    myscene = collada.scene.Scene("myscene", [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    # Write the DAE file
    mesh.write(output_file)

def read_bone_names(file):
    with open(file, 'r') as f:
        bones = [line.strip() for line in f.readlines()]
    return bones

def write_bone_names(file, bones):
    with open(file, 'w') as f:
        for bone in bones:
            f.write(bone + '\n')

def list_bones_from_obj(input_file):
    bones = []
    with open(input_file, 'r') as f:
        for line in f:
            if 'bone' in line:
                bone_name = line.split()[1]
                bones.append(bone_name)
    return bones

def rename_bones(obj_file, input_bones, output_bones):
    for i, bone in enumerate(input_bones):
        if bone in input_bones:
            bone_index = input_bones.index(bone)
            new_name = output_bones[bone_index]
            # Rename logic for the bone in obj_file
            # Pseudocode: replace bone name in obj_file with new_name
    pass

def calculate_weights(input_file):
    pass

def convert_and_rename(input_obj, output_dae, input_bones_file, output_bones_file, mtl_file=None):
    print("Converting OBJ to DAE...")
    convert_obj_to_dae(input_obj, output_dae, mtl_file)
    print("Renaming bones...")
    input_bones = read_bone_names(input_bones_file)
    output_bones = read_bone_names(output_bones_file)
    rename_bones(output_dae, input_bones, output_bones)
    calculate_weights(output_dae)
    output_dae_renamed = input_obj.replace(".obj", ".m2sl.dae")
    os.rename(output_dae, output_dae_renamed)
    print(f"File renamed to: {output_dae_renamed}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mixamo2sl.py <input_obj_file> [<mtl_file>]")
        sys.exit(1)
    
    input_obj = sys.argv[1]
    mtl_file = sys.argv[2] if len(sys.argv) == 3 else None

    print(f"Input OBJ file: {input_obj}")

    output_dae = "temporary_output.dae"
    input_bones_file = "inputbones.ini"
    output_bones_file = "outputbones.ini"
    get_bones_file = "getbones.ini"

    print("Listing bones from OBJ file...")
    bones = list_bones_from_obj(input_obj)
    write_bone_names(get_bones_file, bones)

    print("Converting and renaming bones...")
    convert_and_rename(input_obj, output_dae, input_bones_file, output_bones_file, mtl_file)
