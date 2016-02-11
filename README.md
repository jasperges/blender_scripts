## blender_scripts

### Various addons and scripts for Blender 3D


#### io_import_mc

*WIP*

Addon to import Maya Cache files (.xml + .mc) files.
Only geometry caches are supported (ChannelInterpretation="positions").
It tries to match the channel names with the objects in the scene. If e.g. the
channel name is "my_nice_meshShape" then it looks if the object "my_nice_mesh"
exists.

Todo:

* Add support for cachetype 'OneFilePerFrame'.
* Make the settings in the import file browser work (they are ignored at the
  moment).
* Use the 'self.report' for proper error and info messages.

___

#### add_curve_wires

Creates (hanging) wires between two objects. You can create them between the
selected faces and have them connect faces with the same material.

Todo:

* Cleanup.
* Maybe improve/add stuff.

___

#### io_export_objects

Export (the selected) objects as .obj's to a chosen directory.

___

#### io_import_caches

Import geometry caches (only .pc2 and .mdd at the moment). It tries to match
the name from a cache file with an object (e.g. 'my_mesh.pc2' > 'my_mesh').
If you select/choose one or more cache files, only these will be imported. If
you don't select any files, all cache files in the directory will be imported.
You can choose if you want to import them as shapekeys or use the 'Mesh Cache'
modifier (default and recommended).

Todo:

* Settings (for re-timing) of the cache(s)
    - modifier: set all settings for the modifier in the import file browser.
    - shapekeys: specify frame offset, scale and interpolation
* Only import cache(s) for the selected object(s) (for convenience).

___

#### io_import_objects

Import all or only the selected .obj files. If you select one or more .obj
files, only these will be imported. If you don't select/choose any file,
all files in the directory will be imported.

Todo:

* Allow user to set the settings for the importer.
* Support more file formats.

___

#### io_import_pc2

Import .pc2 pointcache file as shapekeys. You have to select a mesh object for
which to import the pointcache.

Todo:

* Add more options (scale and interpolation).

___

#### jasperge_tools

_Removed. Now has it's own [repository](https://github.com/jasperges/jasperge-tools)._

___

#### space_view3d_curve_select_tool

This tool adds the ability to quickly select the previous, next, first or last point of a curve. Bezier curves and nurbs curves are both supported. Also curves with more than one spline. Especially for complicated curves it can be handy to 'step through the points'. The same as you can 'step through' the hierarchy of objects and bone chains.

You can access this in several ways when you are in 'EDIT MODE' of a curve:

* The tool panel, under Curve Tools -> Selection
* The 'select' menu
* Hotkeys: <kbd>[</kbd> and <kbd>]</kbd> to select the previous or next point and <kbd>shift</kbd> + <kbd>ctrl</kbd> + <kbd>[</kbd> and <kbd>shift</kbd> + <kbd>ctrl</kbd> + <kbd>]</kbd> to select the first or last point.

Also added shortcuts for the existing `curve.select_previous()` and `curve.select_next()` operators. These operators _add_ the previous or next point to the selection, instead of replacing the selection. Hotkeys added are <kbd>shift</kbd> + <kbd>[</kbd> and <kbd>shift</kbd> + <kbd>]</kbd>, to make it consistent.


Todo:

* See if it's possible to make the selected point also the active point.
