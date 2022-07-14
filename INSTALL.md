### [FreeCAD](https://www.freecadweb.org)

#### Install using FreeCAD

Starting with FreeCAD 0.20, this theme is available via the [Addon manager](https://wiki.freecadweb.org/Std_AddonMgr)!

#### Install manually

Refer to [the FreeCAD wiki](https://wiki.freecadweb.org/Preference_Packs#Distributing_a_pack) for manual installation instructions.

#### Activating theme

1. Install the PreferencePack either using the [Addon manager](https://wiki.freecadweb.org/Std_AddonMgr) inside FreeCAD or [manually](https://wiki.freecadweb.org/Preference_Packs#Distributing_a_pack).

2. Activate the pack via Preferences -> General -> Preference packs -> Dracula -> Apply

3. Boom! It's working

#### FreeCAD <0.20

If you are using a FreeCAD version before 0.20 you will need to do the following:

1. Copy `dracula.qss` to `~/.FreeCAD/Gui/Stylesheets/` (Linux)
   `/Users/[YOUR_USER_NAME]/Library/Preferences/FreeCAD/Gui/Stylesheets/`
   (MacOS) or `C:/[INSTALLATION_PATH]/FreeCAD/data/Gui/Stylesheets/` (Windows)

2. Rename `Dracula.cfg` to `user.cfg` and copy to `~/.FreeCAD/` (Linux)
   `/Users/[YOUR_USER_NAME]/Library/Preferences/FreeCAD/` (MacOS) or
   `C:/[INSTALLATION_PATH]/FreeCAD/data/` (Windows). Note that will override
   any existing configuration - if you want to preserve your original
   configuration, you will need to manually merge the two `user.cfg` files

3. Boom! It's working
