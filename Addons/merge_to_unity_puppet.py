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
    "version": (0,2),
    "blender": (2, 6, 2),
    "location": "View3D > ObjectMode > ToolShelf",
    "description": "Combines selected planes for use as a 2D puppet in Unity",
    "warning": "Alpha; discards material and texture information",
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
 
    def create_mesh(self, verts, faces):
        mesh_data = bpy.data.meshes.new(name="UnityPuppet")
        mesh_data.from_pydata(verts, [], faces)
        return mesh_data

    def face_maker(self, total_verts):
        return [range(i,i+4) for i in range(0,total_verts,4)] 

    def execute(self, context) :
        
        # Store list of selected vertices in a [[0,1,2,3],[4,5,6,7],[8,9,10,11],...] list
        all_verts = list()
        for obj in bpy.context.selected_objects:
            loc = obj.location
            all_verts.append([vert.co+loc for vert in obj.data.vertices])
        
        # Sort the list according to the depth (user-defined) of the 0th vertex #XXX (should probably be avg. value)
        if self.axis == "0":
            all_verts.sort(key=lambda v: v[0].x, reverse=False)
        elif self.axis == "1":
            all_verts.sort(key=lambda v: v[0].y, reverse=False)
        elif self.axis == "2":
            all_verts.sort(key=lambda v: v[0].z, reverse=False)

        # Discard the depth component in a new, flat list
        final_verts = list()
        for plane_verts in all_verts:
            if self.axis == "0":
                final_verts.extend([(0.0,vert.y,vert.z) for vert in plane_verts])        
            elif self.axis == "1":
                final_verts.extend([(vert.x,0.0,vert.z) for vert in plane_verts])       
            elif self.axis == "2":
                final_verts.extend([(vert.x,vert.y,0.0) for vert in plane_verts])

        # Create a new mesh and object with the custom vertices; fill in the faces
        new_mesh = self.create_mesh(tuple(final_verts),self.face_maker(len(final_verts)))
        new_mesh.update()
        new_obj = bpy.data.objects.new("UnityPuppet", new_mesh)
        
        # Link in the object to the current scene
        context.scene.objects.link(new_obj)

        # Deselect everything but the newly created object
        for obj in bpy.context.selected_objects:
            obj.select = False
        new_obj.select = True

        return {"FINISHED"}

    def draw(self, context) :

        # Radiobutton to change the operational axis 
        row = self.layout.row()        
        row.prop(self, 'axis', expand=True)

def register():
    bpy.utils.register_class(MergeToUnityPuppet)
    bpy.utils.register_class(MergeToUnityPuppetPanel)

def unregister():
    bpy.utils.unregister_class(MergeToUnityPuppet)
    bpy.utils.register_class(MergeToUnityPuppetPanel)

if __name__ == "__main__":
    register()
