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
from bpy.props import (StringProperty,
                       CollectionProperty,
                       EnumProperty,
                       BoolProperty)
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
    directory = StringProperty(
            maxlen=1024,
            subtype='DIR_PATH',
            options={'HIDDEN', 'SKIP_SAVE'})
    files = CollectionProperty(
            type=bpy.types.OperatorFileListElement,
            options={'HIDDEN', 'SKIP_SAVE'})

    filename_ext = ".obj"
    filter_glob = StringProperty(default="*.obj", options={'HIDDEN'})
    replace_existing = BoolProperty(
            name="Overwrite existing objects",
            description="Overwrite objects already present in the scene",
            default=True)
    material_options = EnumProperty(
            name="Materials",
            items=[("scene",
                    "Scene",
                    "Use the materials that are now assigned to the objects "\
                    "(if they already exist), else don't assign materials"),
                   ("obj",
                    "From file",
                    "Use the materials from the OBJ"),
                   ("ignore",
                    "No Materials",
                    "Don't assign materials")],
            description="Select which materials to use for the imported models",
            default="scene")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        col.prop(self, "replace_existing")
        col.separator()
        col.prop(self, "material_options")

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
                imported_objects.append(import_file(f))
            # Select all imported objects and make the last one the active object.
            # The obj importer already deselects previously selected objects.
            for ob in imported_objects:
                ob.select = True
            context.scene.objects.active = imported_objects[-1]

        return {'FINISHED'}

    # Helper functions
    def import_file(self, f):
        '''
        Imports an obj file and returns the name of the object
        '''
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
                axis_up='Y')
        except AttributeError:
            self.report({'ERROR'}, "obj importer not loaded, aborting...")
            # raise Exception("obj importer not loaded, aborting...")
            return {'CANCELLED'}

        return rename_object(self, f)

    def rename_object(self, f):
        '''
        Renames the object according to the file name and returns the name
        '''
        name = path.splitext(path.split(f)[1])[0]
        imported_object = bpy.context.selected_objects[0]
        if imported_object:
            imported_object.name = imported_object.data.name = name
        else:
            print("File: {f} appears to be empty...".format(f=f))


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
