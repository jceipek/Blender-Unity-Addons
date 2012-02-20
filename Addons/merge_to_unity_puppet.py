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
    "version": (0,1),
    "blender": (2, 6, 2),
    "location": "View3D > ObjectMode > ToolShelf",
    "description": "Combines selected planes for use as a 2D puppet in Unity",
    "warning": "Alpha; discards material and texture information",
    "wiki_url": "https://github.com/jceipek/Blender-Unity-Addons/wiki/Merge-to-Unity-Puppet",
    "tracker_url": "git@github.com:jceipek/Blender-Unity-Addons.git",
    "category": "Mesh"}

'''
A quick hack to make puppet creation for Unity easier.
Simply arrange all planes in the x,y plane and change the z offset so
that the planes are layered correctly. This script will then
generate a new mesh with all of the planes merged and with the z
coordinate discarded. They will be in the correct order when
Unity renders them.
'''

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
    bl_options = {'REGISTER', 'UNDO'}
 
 
    def create_mesh(self, verts, faces):
        mesh_data = bpy.data.meshes.new(name="UnityPuppet")
        mesh_data.from_pydata(verts, [], faces)
        return mesh_data

    def face_maker(self, x):
        y = 0
        while x > 0:
            yield [i for i in range(y,y+4)]
            x-=4
            y+=4
 
    def invoke(self, context, event) :
        
        all_verts = list()
        for obj in bpy.context.selected_objects:
            loc = obj.location
            all_verts.append([vert.co+loc for vert in obj.data.vertices])
        
        all_verts.sort(key=lambda v: v[0].z, reverse=False)
        final_verts = list()
        for plane_verts in all_verts:
            final_verts.extend([(vert.x,vert.y,0.0) for vert in plane_verts])        
        
        new_mesh = self.create_mesh(tuple(final_verts),list(self.face_maker(len(final_verts))))
        new_mesh.update()
        new_obj = bpy.data.objects.new("UnityPuppet", new_mesh)
        
        context.scene.objects.link(new_obj)
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MergeToUnityPuppet)
    bpy.utils.register_class(MergeToUnityPuppetPanel)

def unregister():
    bpy.utils.unregister_class(MergeToUnityPuppet)
    bpy.utils.unregister_class(MergeToUnityPuppetPanel)

if __name__ == "__main__":
    register()
