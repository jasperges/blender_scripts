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
    "name": "Import object(s)",
    "author": "Jasper van Nieuwenhuizen",
    "version": (0, 1),
    "blender": (2, 6, 6),
    "location": "File > Import > Import object(s)",
    "description": "Import object(s) for use with pointcache importer",
    "warning": "wip",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"}


import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from os import path
from glob import glob

# Actual import operator.
class ImportObs(bpy.types.Operator, ImportHelper):
    '''Import object(s)'''
    bl_idname = "import_scene.obs"
    bl_label = "Import object(s)"
    bl_options = {'PRESET', 'UNDO'}
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    directory = StringProperty(maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN', 'SKIP_SAVE'})
    files = CollectionProperty(type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'})

    filename_ext = ".obj"
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    
    def execute(self, context):
        d = self.properties.directory
        fils = self.properties.files
        if not fils[0].name:
            # No files selected, getting all obj's in the directory.
            import_files = glob(path.join(d, "*.[oO][bB][jJ]"))
        else:
            # Get the full path names for the files.
            import_files = [path.join(d, f.name) for f in fils]
        if import_files:
            # Import the objects and append them to "imported_list".
            imported_objects = []
            for f in import_files:
                try:
                    bpy.ops.import_scene.obj(
                        filepath=f,
                        use_ngons=True,
                        use_edges=True,
                        use_smooth_groups=True,
                        use_split_objects=False,
                        use_split_groups=False,
                        use_groups_as_vgroups=False,
                        use_image_search=True,
                        global_clamp_size=0,
                        axis_forward='-Z',
                        axis_up='Y'
                        )
                except AttributeError:
                    raise Exception("obj importer not loaded, aborting...")
                # Rename the object.
                name = path.splitext(path.split(f)[1])[0]
                imported_object = bpy.context.selected_objects[0]
                if imported_object:
                    imported_object.name = imported_object.data.name = name
                    imported_objects.append(imported_object)
                else:
                    print("File: {0} appears to be empty...".format(f))
            # Select all imported objects and make the last one the active object.
            # The obj importer already deselects previously selected objects.
            for ob in imported_objects:
                ob.select = True
            context.scene.objects.active = imported_objects[-1]

        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportObs.bl_idname, text="Import object(s)")


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    

if __name__ == "__main__":
    register()