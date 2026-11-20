[app]

# Identità applicazione
title = BIOLMEDICARE - IKARO SBRW
package.name = ikarosbrw
package.domain = org.aikm.seicore

# Sorgenti e asset inclusi nell'APK
source.dir = .
source.include_exts = py,png,jpg,jpeg,json,kv,atlas
source.exclude_dirs = tests,bin,.buildozer,.ikaro_sandbox

version = 8.6

# Librerie Python core (zero pacchetti pesanti/superflui)
requirements = hostpython3==3.11.5,python3==3.11.5,kivy==2.3.0,pyjnius,android

# Asset grafici ufficiali (Icona + Presplash)
icon.filename = %(source.dir)s/B.png
presplash.filename = %(source.dir)s/B.png
presplash.color = #0D598C

# Orientamento e schermo
orientation = portrait
fullscreen = 0

# Configurazione Android SDK/NDK (obbligatoria per ML Kit v2)
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.enable_androidx = True
android.accept_sdk_license = True
android.allow_backup = True

# Motore OCR Offline Google ML Kit (modello Latin incorporato direttamente nell'APK)
# Gradle risolve automaticamente anche vision-common e play-services-tasks
android.gradle_dependencies = com.google.mlkit:text-recognition:16.0.0

# Permessi lettura/scrittura cartella ponte 'Ikaro' (Android 7 -> Android 14+)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

# Filtro logcat per eventuale debug via ADB
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 0
