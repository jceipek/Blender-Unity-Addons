# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Merge to Unity Puppet",
    "author": "Julian Ceipek",
    "version": (0,4),
    "blender": (2, 6, 2),
    "location": "View3D > ObjectMode > ToolShelf",
    "description": "Combines selected planes for use as a 2D puppet in Unity",
    "warning": "Alpha; does not preserve custom uv mapping",
    "wiki_url": "https://github.com/jceipek/Blender-Unity-Addons/wiki/Merge-to-Unity-Puppet",
    "tracker_url": "https://github.com/jceipek/Blender-Unity-Addons/issues",
    "category": "Mesh"}

import bpy
import math
import mathutils

class MergeToUnityPuppetPanel(bpy.types.Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Merge to Unity Puppet"
 
    def draw(self, context) :
        the_col = self.layout.column(align = True)
        the_col.operator("mesh.merge_to_unity_puppet", text = "Merge to Unity Puppet")


class PlaneContainer:
    def __init__(self, verts, name, materials=None, uv_maps=None):
        self.verts = verts
        self.name = name
        if materials:
            self.materials = materials
        else:
            self.materials = list()
        if uv_maps:
            self.uv_maps = uv_maps
            print(uv_maps)
        else:
            self.uv_maps = list()

    def get_depth(self, axis):
        return sum([d[axis] for d in self.verts])/len(self.verts)

    def strip_depth(self, axis):
        for v in self.verts:
            v[axis] = 0.0

class MergeToUnityPuppet(bpy.types.Operator) :
    bl_idname = "mesh.merge_to_unity_puppet"
    bl_label = "Merge to Unity Puppet"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_description = "Combine selected planes for use as a 2D puppet in Unity"

    bl_options = {'REGISTER', 'UNDO'}
 

    axis = bpy.props.EnumProperty(items=(("0", "X", "Merge relative to x-axis"),
    ("1", "Y", "Merge relative to y-axis"),("2", "Z", "Merge relative to z-axis")),
    name="Merge Axis", description="Choose the axis to use for depth information.")

    create_vert_grps = bpy.props.BoolProperty(name="Create Vertex Groups",
    description="Create a vertex group for each plane, with the name of the originating object.", default=True)

    preserve_mats = bpy.props.BoolProperty(name="Preserve Materials",
    description="Preserve the material properties of the planes. May not work with multiple textures/materials per object.", default=False) 

    def create_mesh(self, verts, faces):
        mesh_data = bpy.data.meshes.new(name="UnityPuppet")
        mesh_data.from_pydata(verts, [], faces)
        return mesh_data

    def face_maker(self, total_verts):
        return [range(i,i+4) for i in range(0,total_verts,4)] 

    def execute(self, context) :
        
        axis_int = int(self.axis)

        # Store list of planes
        all_planes = list()
        for obj in bpy.context.selected_objects:
            loc = obj.location
            all_planes.append(PlaneContainer([vert.co+loc for vert in obj.data.vertices], obj.name, materials=obj.data.materials, uv_maps=obj.data.uv_textures))
        
        # Sort the list according to the depth (user-defined) of the planes
        all_planes.sort(key=lambda plane: plane.get_depth(axis_int), reverse=False)
        # Discard the depth component in a new, flat list        
        final_verts = list()        
        for plane in all_planes:
            plane.strip_depth(axis_int)
            final_verts.extend(plane.verts)

        # Create a new mesh and object with the custom vertices; fill in the faces
        new_mesh = self.create_mesh(tuple(final_verts),self.face_maker(len(final_verts)))
        new_mesh.update()
        new_obj = bpy.data.objects.new("UnityPuppet", new_mesh)
       
        # Make vertex groups for each unique object
        if self.create_vert_grps:
            for index,plane in zip(range(0,len(all_planes)*4,4),all_planes):
                new_vert_grp = new_obj.vertex_groups.new(plane.name)
                new_vert_grp.add([index,index+1,index+2,index+3],1.0,'ADD')

        if self.preserve_mats:
            uvtex = new_obj.data.uv_textures.new()
            uvtex.name = "Unity Puppet Atlas"

            for index,plane in zip(range(len(all_planes)),all_planes):
                for mat in plane.materials:
                    if not mat.name in new_obj.data.materials:
                        new_obj.data.materials.append(mat)
                
                face = new_obj.data.faces[index]
                face.material_index = index
                #Add texture to face here, using UV editor
                try:
                    uvtex.data[index].image = plane.materials[0].texture_slots[0].texture.image
                except Exception as e:
                    print(e)
                    print("Thar be failure here")
                    pass
        # Link in the object to the current scene
        context.scene.objects.link(new_obj)

        # Deselect everything but the newly created object
        for obj in bpy.context.selected_objects:
            obj.select = False
        new_obj.select = True
        bpy.context.scene.objects.active = new_obj

        return {"FINISHED"}

    def draw(self, context) :

        # Radiobutton to change the operational axis 
        row = self.layout.row()        
        row.prop(self, 'axis', expand=True)
        col = self.layout.column()
        col.prop(self, 'create_vert_grps')
        col.prop(self, 'preserve_mats')


def register():
    bpy.utils.register_class(MergeToUnityPuppet)
    bpy.utils.register_class(MergeToUnityPuppetPanel)

def unregister():
    bpy.utils.unregister_class(MergeToUnityPuppet)
    bpy.utils.register_class(MergeToUnityPuppetPanel)

if __name__ == "__main__":
    register()
