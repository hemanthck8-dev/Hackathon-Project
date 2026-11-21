[app]

# (str) Title of your application
title = MediCare

# (str) Package name
package.name = medicare

# (str) Package domain (needed for android/ios packaging)
package.domain = org.medicare

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty for all files)
source.include_exts = py,png,jpg,kv,atlas,db

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,sqlite3,pillow

# (str) Supported orientation (landscape, sensorLandscape, portrait, sensorPortrait, all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API, should be as high as possible
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android SDK version to use
android.sdk = 33

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (list) Permissions
android.permissions = INTERNET, RECEIVE_BOOT_COMPLETED, VIBRATE, WAKE_LOCK, POST_NOTIFICATIONS, SCHEDULE_EXACT_ALARM, SET_ALARM

# (str) presplash background color (for android toolchain)
android.presplash_color = #2196F3

# (str) Adaptive icon of the application (used if search.hierarchical_icons is true)
# icon.filename = %(source.dir)s/data/icon.png

# (str) Presplash screen image
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) Android add-on JAR files
#android.add_jars = foo.jar

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (str) python-for-android branch to use
p4a.branch = master

# (str) OUYA Console category. Should be one of GAME or APP
# android.ouya.category = GAME

# (str) Filename of the Android logcat filter to use
# android.logcat_filters = *:S python:D

# (str) Android logcat only display log for activity's pid
# android.logcat_pid_only = False

# (str) Android additional adb arguments
# android.adb_args = -H host.docker.internal

# (int) overrides automatic versionCode computation
# android.numeric_version = 1

# (bool) Use --hierarchical mode for ANT
# (default is False)
# android.use_src_clsas_resource = False

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
