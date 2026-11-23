[app]
title = AIKMGE N1 Ton
package.name = aikmgeton
package.domain = org.sbrwge
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 3.0.0

requirements = python3,kivy,pyjnius,android
orientation = portrait
fullscreen = 0

services = Bmsmonitor:service.py:foreground:sticky

# Pure-Sandbox Air-Gap: ZERO INTERNET, ZERO WAKE_LOCK, ZERO ADB/ROOT
android.permissions = FOREGROUND_SERVICE,FOREGROUND_SERVICE_DATA_SYNC,POST_NOTIFICATIONS,ACCESS_WIFI_STATE,CHANGE_WIFI_STATE,ACCESS_NETWORK_STATE,WRITE_SETTINGS
android.add_src = src_java
p4a.hook = p4a_hook.py

android.api = 33
android.minapi = 26
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.release_artifact = aab
android.allow_backup = False

[buildozer]
log_level = 2
warn_on_root = 0