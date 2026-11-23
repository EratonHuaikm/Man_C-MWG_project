[app]
requirements = python3,kivy,pyjnius,ailu_core
p4a.local_recipes = ./p4a_recipes
android.release_artifact = aab
android.api = 35
android.minapi = 21
android.ndk = 27c
android.ndk_api = 21
android.archs = arm64-v8a
source.exclude_dirs = tests, bin, venv, p4a_recipes, .buildozer, __pycache__
presplash.filename = icon_wolf.png
android.presplash_color = #05170F
icon.filename = icon_wolf.png
icon.adaptive_foreground.filename = icon_wolf.png
icon.adaptive_background.filename = icon_wolf.png
title = AiLU API Sentinel
package.name = ailusentinel
package.domain = org.ailu
source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,kv,json
source.include_patterns = *.png,*.jpg,*.jpeg,*.webp,*.kv
version = 2.3.0
orientation = portrait
fullscreen = 0
android.adaptive_icon_background_color = #050C12
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.sdk = 34
android.private_storage = True
android.copy_libs = 1
android.allow_backup = False
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.enable_androidx = True
android.wakelock = False
p4a.branch = develop
p4a.bootstrap = sdl2
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1


