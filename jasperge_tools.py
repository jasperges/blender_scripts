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

# TODO: - Expand load_post handler to try to get the version number and padding
#         from the filename
#       - Properly add rename to menu (immediately presenting options)
#       - Properly add update version to menu (immediately presenting options)
#       - Add confirmation to overwrite file if file already exists for version update.


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

import os
import shutil
import glob
import re
import bpy
from bpy.app.handlers import persistent
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty


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
                            fcu2 = action2.fcurves.new(
                                data_path=fcu.data_path,
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
    """Turn off all the modifiers (except 'ARMATURE', 'CURVE',
       'MIRROR' and 'SIMPLE_DEFORM) in the viewport."""

    bl_description = "Turn off all the modifiers (except 'ARMATURE', 'CURVE'"\
        ", 'MIRROR' and 'SIMPLE_DEFORM) in the viewport."
    bl_idname = "object.modifier_viewport_off"
    bl_label = "Modifiers viewport off"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            if obj.modifiers:
                for m in obj.modifiers:
                    if m.type not in ('ARMATURE',
                                      'CURVE',
                                      'MIRROR',
                                      'SIMPLE_DEFORM'):
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


class OBJECT_OT_modifier_mirror_toggle(bpy.types.Operator):
    """Turn on/off the 'MIRROR' modifiers for all objects in the viewport."""

    bl_description = "Turn on/off the 'MIRROR' modifiers for all objects in the viewport."
    bl_idname = "object.modifier_mirror_toggle"
    bl_label = "Mirror on"
    bl_space_type = 'VIEW_3D'

    use_mirror = BoolProperty(
        name="Mirror",
        description="Choose to turn mirror modifier on or off",
        default=True)

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            if obj.modifiers:
                for m in obj.modifiers:
                    if m.type == 'MIRROR':
                        m.show_viewport = self.use_mirror

        return {'FINISHED'}


class OBJECT_OT_modifier_boolean_toggle(bpy.types.Operator):
    """Turn on/off the 'BOOLEAN' modifiers for all objects in the viewport."""

    bl_description = "Turn on/off the 'BOOLEAN' modifiers for all objects in the viewport."
    bl_idname = "object.modifier_boolean_toggle"
    bl_label = "Boolean on"
    bl_space_type = 'VIEW_3D'

    use_boolean = BoolProperty(
        name="Boolean",
        description="Choose to turn boolean modifier on or off",
        default=True)

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            if obj.modifiers:
                for m in obj.modifiers:
                    if m.type == 'BOOLEAN':
                        m.show_viewport = self.use_boolean

        return {'FINISHED'}


class OBJECT_OT_modifier_expand(bpy.types.Operator):
    """Expand or collapse all modifier options."""

    bl_description = "Expand or collapse all modifier options."
    bl_idname = "object.modifier_expand"
    bl_label = "Expand/Collapse modifier options"

    expand = BoolProperty(
        name="Expand",
        description="Expand or collapse options (True/False",
        default=True)

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            try:
                for m in obj.modifiers:
                    m.show_expanded = self.expand
            except AttributeError:
                pass

        # force refresh of properties panel
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()

        return {'FINISHED'}


class OBJECT_OT_modifier_subsurf_optimal(bpy.types.Operator):
    """Turn on/off optimal display for all subsurf modifiers."""

    bl_description = "Turn on optimal display for all subsurf modifiers."
    bl_idname = "object.modifier_optimal_subsurf"
    bl_label = "Optimal display"

    use_optimal = BoolProperty(
        name="Optimal",
        description="Use optimal display or not (True/False)",
        default=True)

    def execute(self, context):
        objects = bpy.data.objects
        for obj in objects:
            try:
                for m in obj.modifiers:
                    if m.type == 'SUBSURF':
                        m.show_only_control_edges = self.use_optimal
            except AttributeError:
                pass

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

        # bpy.ops.wm.save_as_mainfile(
        #     filepath=new_incr_file,
        #     check_existing=False,
        #     compress=True,
        #     copy=True,
        #     )

        if not avoid_double_save:
            # Copy current saved blend file to incremental folder
            shutil.copy2(filepath, new_incr_file)
            # Save the current (modified) blend file
            bpy.ops.wm.save_mainfile(check_existing=False)

        # Restore user preferences.
        user_prefs.filepaths.save_version = save_versions

        print("Incremental saved: {}".format(new_incr_filename))

        return {'FINISHED'}


class FILE_update_version(bpy.types.Operator):
    """Update the version of the filename and the render path.

    E.g.: filename: my_blend_file_v010.blend -> my_blend_file_v011.blend
          render output: //render/v010/xxx -> //render/v011/xxx"""

    bl_description = "Update the version of the filename and the render path."
    bl_idname = "file.update_version"
    bl_label = "Update version"

    version = IntProperty(
        name="Version",
        description="The new version number for the file",
        default=1,
        min=1)

    padding = IntProperty(
        name="Padding",
        description="The padding of the version number",
        default=2,
        min=1)

    def version_to_string(self, version, padding):
        return "v{v:0{p}d}".format(v=version, p=padding)

    def update_filename(self):
        version = self.version
        padding = self.padding
        blend_path = bpy.data.filepath
        blend_dir = os.path.dirname(blend_path)
        blend_file = os.path.basename(blend_path)
        version_str = self.version_to_string(version, padding)
        new_blend_file = version_str.join(re.split(r"v\d+", blend_file))
        new_blend_path = os.path.join(blend_dir, new_blend_file)
        bpy.ops.wm.save_as_mainfile(filepath=new_blend_path, compress=True)

    def update_renderpath(self):
        version = self.version
        padding = self.padding
        render_path = bpy.context.scene.render.filepath
        version_str = self.version_to_string(version, padding)
        new_render_path = version_str.join(re.split(r"v\d+", render_path))
        bpy.context.scene.render.filepath = new_render_path

    def execute(self, context):
        wm = bpy.context.window_manager
        self.version = wm.jasperge_tools_settings.version
        self.padding = wm.jasperge_tools_settings.padding
        self.update_filename()
        self.update_renderpath()

        # Add version number and padding to first scene in file
        bpy.data.scenes[0]["jasperge_tools_file_version"] = self.version
        bpy.data.scenes[0]["jasperge_tools_file_version_padding"] = self.padding

        return {'FINISHED'}


class OBJECT_OT_hash_rename(bpy.types.Operator):
    """Hash rename all selected objects."""

    bl_description = "Hash rename all selected objects."
    bl_idname = "object.hash_rename"
    bl_label = "Hash rename"
    bl_space_type = 'VIEW_3D'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object

    new_name = StringProperty(
        name="New name",
        description="The new name for the objects. Use #-es to insert "
                    "numbering. The amount of #-es determines the padding.",
        default="")

    start_number = IntProperty(
        name="Start",
        description="Start the numbering with this number.",
        default=1,
        min=0)

    def parse_new_name(self, new_name):
        """
        parse_new_name(string new_name) -> string new_name

            Parses the new_name string and return a string that can directly be
            used in the renaming process.

            string new_name - the new name to use for the objects
        """

        m = re.search(r"#+", new_name)
        if not m:
            return new_name
        else:
            replace_string = "".join(("{i:0", str(len(m.group())), "d}"))
            new_name = "".join((new_name[:m.start()],
                                replace_string,
                                new_name[m.end():]))
            new_name = self.parse_new_name(new_name)
            return new_name

    def execute(self, context):
        wm = bpy.context.window_manager
        self.new_name = wm.jasperge_tools_settings.new_name
        self.start_number = wm.jasperge_tools_settings.start_number
        new_name = self.parse_new_name(self.new_name)
        for i, obj in enumerate(context.selected_objects):
            obj.name = new_name.format(i=i + self.start_number)

        return {'FINISHED'}

    # def invoke(self, context, event):
    #     wm = context.window_manager

    #     return wm.invoke_props_popup(self, event)


class SetNormalAngle(bpy.types.Operator):
    """Set the normal angle of the selected objects and turn on auto smooth"""
    bl_idname = "object.jaspergetools_set_normal_angle"
    bl_label = "Set normal angle"
    bl_options = {'REGISTER', 'UNDO'}

    normal_angle = FloatProperty(
        name="Angle",
        default=40,
        min=0,
        max=180)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        wm = bpy.context.window_manager
        self.normal_angle = wm.jasperge_tools_settings.normal_angle
        for obj in bpy.context.selected_objects:
            bpy.ops.object.shade_smooth()
            try:
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = radians(self.normal_angle)
            except AttributeError:
                pass
        return {'FINISHED'}


class HideRelationshipLines(bpy.types.Operator):
    """Hide relationship lines in every 3D View"""
    bl_idname = "wm.jaspergetools_hide_relationship_lines"
    bl_label = "Hide relationship lines"

    def execute(self, context):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.show_relationship_lines = False
        return {'FINISHED'}


class ShowRelationshipLines(bpy.types.Operator):
    """Show relationship lines in every 3D View"""
    bl_idname = "wm.jaspergetools_show_relationship_lines"
    bl_label = "Show relationship lines"

    def execute(self, context):
        for screen in bpy.data.screens:
            for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.show_relationship_lines = True
        return {'FINISHED'}


class JaspergeToolsSettings(bpy.types.PropertyGroup):
    new_name = StringProperty(
        name="New name",
        description="The new name for the objects. Use #-es to insert "
                    "numbering. The amount of #-es determines the padding.",
        default="")

    start_number = IntProperty(
        name="Start",
        description="Start the numbering with this number.",
        default=1,
        min=0)

    version = IntProperty(
        name="Version",
        description="The new version number for the file",
        default=1,
        min=1)

    padding = IntProperty(
        name="Padding",
        description="The padding of the version number",
        default=2,
        min=1)

    normal_angle = FloatProperty(
        name="Angle",
        default=40,
        min=0,
        max=180)


class JaspergeToolsPanel(bpy.types.Panel):
    bl_label = "jasperge tools"
    bl_idname = "VIEW3D_PT_jasperge_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'

    def draw(self, context):

        layout = self.layout
        wm = bpy.context.window_manager

        # File options
        box = layout.box()
        col = box.column(align=False)
        col.label(text="File:")
        col.operator("file.incremental_save")
        col.separator()
        col = box.column(align=True)
        row = col.row(align=True)
        row.prop(wm.jasperge_tools_settings, "version")
        row.prop(wm.jasperge_tools_settings, "padding")
        col.operator("file.update_version")

        # Modifier options
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Modifiers:")
        col.operator("object.copy_modifier_settings", text="Copy Settings")
        row = col.row(align=True)
        row.operator("object.modifier_viewport_on", text="Viewport On")
        row.operator("object.modifier_viewport_off", text="Viewport Off")
        row = col.row(align=True)
        row.operator("object.modifier_mirror_toggle",
                     text="Mirror On").use_mirror = True
        row.operator("object.modifier_mirror_toggle",
                     text="Mirror Off").use_mirror = False
        row = col.row(align=True)
        row.operator("object.modifier_boolean_toggle",
                     text="Boolean On").use_boolean = True
        row.operator("object.modifier_boolean_toggle",
                     text="Boolean Off").use_boolean = False
        row = col.row(align=True)
        row.operator("object.modifier_expand",
                     text="Expand options").expand = True
        row.operator("object.modifier_expand",
                     text="Collapse options").expand = False
        row = col.row(align=True)
        row.operator("object.modifier_optimal_subsurf",
                     text="Optimal display").use_optimal = True
        row.operator("object.modifier_optimal_subsurf",
                     text="Non-optimal display").use_optimal = False

        # Object options
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Object:")
        row = col.row(align=True)
        row.operator("object.wire_on")
        row.operator("object.wire_off")
        row = col.row(align=True)
        row.operator("object.jaspergetools_set_normal_angle")
        row.prop(wm.jasperge_tools_settings, "normal_angle")

        # Renaming options
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Rename:")
        col.prop(wm.jasperge_tools_settings, "new_name")
        col.prop(wm.jasperge_tools_settings, "start_number")
        col.operator("object.hash_rename", "Rename")

        # General options
        box = layout.box()
        col = box.column(align=True)
        col.label(text="General:")
        # row = col.row(align=True)
        row = col.split(.5, align=True)
        row.label(text="Relationship lines:")
        row.operator("wm.jaspergetools_show_relationship_lines", text="On")
        row.operator("wm.jaspergetools_hide_relationship_lines", text="Off")


class JaspergeToolsMenu(bpy.types.Menu):
    bl_description = "jasperge tools menu"
    bl_idname = "VIEW3D_MT_jasperge_tools_menu"
    bl_label = "jasperge tools"

    def draw(self, context):
        layout = self.layout
        layout.operator("file.incremental_save",
                        icon='SAVE_COPY')
        # layout.operator("file.update_version")
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
        layout.separator()
        # layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("object.hash_rename", "Rename")


@persistent
def update_jasperge_settings(context):
    wm = bpy.context.window_manager
    jt_settings = wm.jasperge_tools_settings
    jt_settings.version = bpy.data.scenes[0].get(
        "jasperge_tools_file_version", 1)
    jt_settings.padding = bpy.data.scenes[0].get(
        "jasperge_tools_file_version_padding", 2)


jasperge_tools_keymaps = list()


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.jasperge_tools_settings = bpy.props.PointerProperty(type=JaspergeToolsSettings)
    wm = bpy.context.window_manager
    for mode in ("Object Mode",
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
    bpy.app.handlers.load_post.append(update_jasperge_settings)


def unregister():
    bpy.utils.unregister_module(__name__)
    wm = bpy.context.window_manager
    for km in jasperge_tools_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del jasperge_tools_keymaps[:]
    del bpy.types.WindowManager.jasperge_tools_settings
    # Remove load_post handler
    for h in bpy.app.handlers.load_post:
        if h.__name__ == "update_jasperge_settings":
            bpy.app.handlers.load_post.remove(h)


if __name__ == "__main__":
    register()
