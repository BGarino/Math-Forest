[app]
title = Math-Forest
package.name = mathforest
package.domain = org.mathforest
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ogg,mp3,ttf,json,sqlite3
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd,pillow,sqlite3
orientation = portrait
osxwindow_icon = assets/images/icon.png
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
[buildozer]
log_level = 2
warn_on_root = 1
