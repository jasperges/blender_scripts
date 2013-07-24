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

# <pep8 compliant>

# The 'copy modifier settings' is from an addon by Sergey Sharybin.

bl_info = {
    "name": "jasperge tools",
    "description": "Assorted tools",
    "author": "jasperge",
    "version": (0, 3),
    "blender": (2, 62, 3),
    "location": "View 3D > Toolbar / View 3D - Shift + Q (gives a menu)",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"}

import bpy
import os
import glob


class OBJECT_OT_copy_modifier_settings(bpy.types.Operator):
    """Copy settings of modifiers from active object to """
    """all other selected objects."""

    bl_description = "Copy settings of modifiers from active object to all"\
            " other selected objects."
    bl_idname = "object.copy_modifier_settings"
    bl_label = "Copy Modifier Settings"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        # list of properties to be skipped
        skip_props = ("bl_rna", "name", "rna_type", "type")

        obact = context.active_object

        for ob in context.selected_objects:
            if ob == obact:
                continue

            # itterate through all modifiers of active object
            for mod in obact.modifiers:
                if mod.name not in ob.modifiers:
                    # no need to copy modifier to self
                    continue

                mod2 = ob.modifiers[mod.name]

                # copy all propeties from active object to selected
                for prop in dir(mod):
                    if prop.startswith("_") or prop in skip_props:
                        # no need to copy property
                        continue

                    attr = getattr(mod, prop)
                    setattr(mod2, prop, attr)

                # copy animation data for this modifier
                if obact.animation_data and obact.animation_data.action:
                    action = obact.animation_data.action
                    data_path = "modifiers[\"" + mod.name + "\"]"

                    for fcu in action.fcurves:
                        if fcu.data_path.startswith(data_path):
                            # create new animation data if needed
                            if not ob.animation_data:
                                ob.animation_data_create()

                            # if there's no action assigned to selected object
                            # create new one
                            if not ob.animation_data.action:
                                action_name = ob.name + "Action"
                                bpy.data.actions.new(name=action_name)
                                action2 = bpy.data.actions[action_name]
                                ob.animation_data.action = action2
                            else:
                                action2 = ob.animation_data.action

                            # delete existing curve if present
                            for fcu2 in action2.fcurves:
                                if fcu2.data_path == fcu.data_path:
                                    action2.fcurves.remove(fcu2)
                                    break

                            # create new fcurve
                            fcu2 = action2.fcurves.new(data_path=fcu.data_path,
                                index=fcu.array_index)
                            fcu2.color = fcu.color

                            # create keyframes
                            fcu2.keyframe_points.add(len(fcu.keyframe_points))

                            # copy keyframe settings
                            for x in range(len(fcu.keyframe_points)):
                                point = fcu.keyframe_points[x]
                                point2 = fcu2.keyframe_points[x]

                                point2.co = point.co
                                point2.handle_left = point.handle_left
                                point2.handle_left_type = point.handle_left_type
                                point2.handle_right = point.handle_right
                                point2.handle_right_type = point.handle_right_type

        return {'FINISHED'}


class OBJECT_OT_modifier_viewport_off(bpy.types.Operator):
    """Turn off all the modifiers (except 'ARMATURE', 'CURVE' and
     'SIMPLE_DEFORM) in the viewport."""

    bl_description = "Turn off all the modifiers (except 'ARMATURE', 'CURVE'"\
            "and 'SIMPLE_DEFORM) in the viewport."
    bl_idname = "object.modifier_viewport_off"
    bl_label = "Modifiers viewport off"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            if obj.modifiers:
                for m in obj.modifiers:
                    if m.type not in ('ARMATURE', 'CURVE', 'SIMPLE_DEFORM'):
                        m.show_viewport = False

        return {'FINISHED'}


class OBJECT_OT_modifier_viewport_on(bpy.types.Operator):
    """Turn on all the modifiers in the viewport."""

    bl_description = "Turn on all modifiers in the viewport."
    bl_idname = "object.modifier_viewport_on"
    bl_label = "Modifiers viewport on"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            if obj.modifiers:
                for m in obj.modifiers:
                    if m.type != 'ARMATURE':
                        m.show_viewport = True

        return {'FINISHED'}


class OBJECT_OT_wire_on(bpy.types.Operator):
    """Turn on the wire display option for all mesh objects."""

    bl_description = "Turn on the wire display option for all mesh objects."
    bl_idname = "object.wire_on"
    bl_label = "Wire on"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        mesh_objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        for ob in mesh_objects:
            ob.show_wire = True
            ob.show_all_edges = True

        return {'FINISHED'}


class OBJECT_OT_wire_off(bpy.types.Operator):
    """Turn off the wire display option for all mesh objects."""

    bl_description = "Turn off the wire display option for all mesh objects."
    bl_idname = "object.wire_off"
    bl_label = "Wire off"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        mesh_objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']
        for ob in mesh_objects:
            ob.show_wire = False
            ob.show_all_edges = False

        return {'FINISHED'}


class FILE_incremental_save(bpy.types.Operator):
    """Do an incremental save for the file (like in Maya).

    Saves the file with the current name, but also saves a copy in the
    incremental save folder.
    (./incrementalSave/<filename>/<filename>.xxxx.blend)
    There is no limitation for the amount of incremental save files"""

    bl_description = "Do an incremental save for the file (Maya style)."
    bl_idname = "file.incremental_save"
    bl_label = "Incremental Save"

    def execute(self, context):

        # To avoid double 'backup saving' we need to set the 'Save Versions'
        # in the user preferences to 0.
        user_prefs = context.user_preferences
        save_versions = user_prefs.filepaths.save_version  # Store for later
        user_prefs.filepaths.save_version = 0

        # Get all file and dir names.
        filepath = bpy.data.filepath
        avoid_double_save = None
        if not filepath:
            bpy.ops.wm.save_mainfile('INVOKE_DEFAULT')
            avoid_double_save = True
        workdir = os.path.dirname(filepath)
        filename = bpy.path.basename(filepath)
        filebasename = os.path.splitext(filename)[0]
        incr_save_dir = os.path.join(workdir, "incrementalSave")
        incr_save_file_dir = os.path.join(incr_save_dir, filename)

        # Create incremental save dirs if needed.
        if not os.path.isdir(incr_save_dir):
            os.mkdir(incr_save_dir)
        if not os.path.isdir(incr_save_file_dir):
            os.mkdir(incr_save_file_dir)

        # Check number of incremental save files.
        incr_files = glob.glob(os.path.join(
            incr_save_file_dir,
            "*.[bB][lL][eE][nN][dD]"
            ))
        if incr_files:
            incr_files.sort()   # Sort list, just to be sure.
            last_file_num = int(os.path.splitext(
                    incr_files[-1])[0].split(".")[-1])
            file_num = last_file_num + 1
        else:
            file_num = 0
        new_incr_filename = "%s.%.4d.blend" % (filebasename, file_num)
        new_incr_file = os.path.join(incr_save_file_dir, new_incr_filename)

        bpy.ops.wm.save_as_mainfile(
            filepath=new_incr_file,
            check_existing=False,
            compress=True,
            copy=True,
            )

        if not avoid_double_save:
            bpy.ops.wm.save_mainfile(check_existing=False)

        # Restore user preferences.
        user_prefs.filepaths.save_version = save_versions

        print("Incremental saved: {}".format(new_incr_filename))

        return {'FINISHED'}


class JaspergeToolsPanel(bpy.types.Panel):
    bl_label = "jasperge tools"
    bl_idname = "VIEW3D_PT_jasperge_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):

        layout = self.layout
        col = layout.column(align=True)
        col.label(text="File:")
        col.operator("file.incremental_save")
        col.separator()

        col.label(text="Modifiers:")
        col.operator("object.copy_modifier_settings", text="Copy Settings")
        row = col.row(align=True)
        row.operator("object.modifier_viewport_on", text="Viewport On")
        row.operator("object.modifier_viewport_off", text="Viewport Off")
        col.separator()

        col.label(text="Object:")
        row = col.row(align=True)
        row.operator("object.wire_on")
        row.operator("object.wire_off")


class JaspergeToolsMenu(bpy.types.Menu):
    bl_description = "jasperge tools menu"
    bl_idname = "VIEW3D_MT_jasperge_tools_menu"
    bl_label = "jasperge tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("file.incremental_save",
                icon='SAVE_COPY')
        layout.separator()
        layout.operator("object.copy_modifier_settings",)
        layout.operator("object.modifier_viewport_on",)
        layout.operator("object.modifier_viewport_off",)
        layout.separator()
        layout.operator("object.wire_on",
                #text="Wireframe Display On",
                icon='MESH_GRID')
        layout.operator("object.wire_off",
                #text="Wireframe Display Off",
                icon='MESH_PLANE')
        layout.separator()
        layout.operator("object.shade_smooth",
                icon='SOLID')
        layout.operator("object.shade_flat",
                icon='MESH_UVSPHERE')


jasperge_tools_keymaps = list()


def register():
    bpy.utils.register_module(__name__)
    wm = bpy.context.window_manager
    for mode in (
            "Object Mode",
            "Mesh",
            "Curve",
            "Armature",
            "Metaball",
            "Lattice",
            "Font",
            "Pose",
            "Vertex Paint",
            "Weight Paint",
            "Sculpt",
            ):
        km = wm.keyconfigs.addon.keymaps.new(name=mode)
        kmi = km.keymap_items.new("wm.call_menu", "Q", "PRESS", shift=True)
        kmi.properties.name = "VIEW3D_MT_jasperge_tools_menu"


def unregister():
    bpy.utils.unregister_module(__name__)
    wm = bpy.context.window_manager
    for km in jasperge_tools_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del jasperge_tools_keymaps[:]


if __name__ == "__main__":
    register()
