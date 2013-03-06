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
    "name": "Objects exporter (obj)",
    "description": "Export all (selected objects) as obj's.",
    "author": "jasperge",
    "version": (0, 8),
    "blender": (2, 6, 3),
    "location": "File > Export",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
from os import path
from time import time


def check_exporters():
    # Check if .obj exporter is enabled or try to enable it.
    try:
        bpy.ops.export_scene.obj.poll()
    except:
        try:
            bpy.ops.wm.addon_enable(module="io_scene_obj")
            print("*******\n.obj import enabled...\n*******")
        except:
            raise RuntimeError("Could not enable .obj export...")


def export_object(**kwargs):
    
    # Pull out the variables.
    ob = kwargs.setdefault("obj", bpy.context.active_object)
    objdir = kwargs.setdefault("objdir", bpy.path.abspath("//"))
    export_mats = kwargs.setdefault("export_mats", False)
    apply_modifiers = kwargs.setdefault("apply_modifiers", True)
    
    # Select only this object.
    for obj in bpy.data.objects:
        obj.select = False
    ob.select = True
    bpy.context.scene.objects.active = ob
    
    # Get the name of the object to use in the filename.
    name = bpy.path.clean_name(ob.name)
    
    # Export obj.
    filepath = path.join(objdir, "%s.obj" % name)
    bpy.ops.export_scene.obj(
        filepath=filepath,
        check_existing=True,
        use_selection=True,
        use_animation=False,
        use_mesh_modifiers=apply_modifiers,
        use_edges=True,
        use_normals=True,
        use_uvs=True,
        use_materials=export_mats,
        use_triangles=False,
        use_nurbs=False,
        use_vertex_groups=False,
        use_blen_objects=True,
        group_by_object=False,
        group_by_material=False,
        keep_vertex_order=True,
        global_scale=1,
        axis_forward='-Z',
        axis_up='Y',
        path_mode='AUTO',
        )


class ExportObjs(Operator, ExportHelper):
    """Exports all objects as .obj's."""

    bl_idname = "export_scene.objdir"
    bl_label = "Export scene (OBJ)"
    bl_options = {'PRESET'}
    
    filename_ext = ".obj"
    filter_glob = StringProperty(
        default="*.obj;*.mtl",
        options={'HIDDEN'},
        )
    
    use_selection = BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=True,
        )
    apply_modifiers = BoolProperty(
        name="Apply Modifiers",
        description="Apply the modifiers",
        default=True,
        )
    export_mats = BoolProperty(
        name="Materials",
        description="Also export the materials",
        default=False,
        )
    

    def execute(self, context):
        
        time1 = time()
        apply_modifiers = self.apply_modifiers
        export_mats = self.export_mats
        
        # Check for needed exporters:
        check_exporters()
        
        # Get a list with all the mesh objects.
        if self.use_selection:
            objects_to_export = [ob for ob in bpy.context.selected_objects]
        else:
            objects_to_export = [ob for ob in bpy.data.objects]
        
        # Get the folder.
        dirpath = path.dirname(self.filepath)
        
        for ob in objects_to_export:
            print("\n*** processing object %s (%d of %d)...\n" % (
                ob.name,
                objects_to_export.index(ob) + 1,
                len(objects_to_export)),
                )
            
            export_object(
                obj=ob,
                objdir=dirpath,
                apply_modifiers=apply_modifiers,
                export_mats=export_mats,
                )
        
        process_time = time() - time1
        minutes, seconds = divmod(process_time, 60)
        if minutes == 1:
            print("\n*** Objects export finished in %d minute and %d seconds...\n" % (int(minutes), int(seconds)))
        else:
            print("\n*** Objects export finished in %d minutes and %d seconds...\n" % (int(minutes), int(seconds)))
        
        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportObjs.bl_idname, text="Export Objects (.obj)")


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    

if __name__ == "__main__":
    register()