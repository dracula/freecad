### [FreeCAD](https://www.freecadweb.org)

#### Install using Git

If you are a git user, you can install the theme and keep up to date by cloning the repo:

    $ git clone https://github.com/dracula/freecad.git

#### Install manually

Download using the [GitHub .zip download](https://github.com/dracula/freecad/archive/master.zip) option and unzip them.

#### Activating theme

1. Copy `dracula.qss` to `~/.FreeCAD/Gui/Stylesheets/` (Linux)
   `/Users/[YOUR_USER_NAME]/Library/Preferences/FreeCAD/Gui/Stylesheets/`
   (MacOS) or `C:/[INSTALLATION_PATH]/FreeCAD/data/Gui/Stylesheets/` (Windows)

2. Copy `user.cfg` to `~/.FreeCAD/` (Linux)
   `/Users/[YOUR_USER_NAME]/Library/Preferences/FreeCAD/Gui/Stylesheets/`
   (MacOS) or `C:/[INSTALLATION_PATH]/FreeCAD/data/` (Windows). Note that will
   override any existing configuration - if you want to preserve your original
   configuration, you will need to manually merge the two `user.cfg` files

3. Boom! It's working
