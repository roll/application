#!/bin/sh
# File to create the DMG file using create-dmg tool and notarize it.
#
# It is intended to work on Github Actions and so it might not be the most optimized
# workflow for executing it locally (because of the secrets required for code sign
# and notarizing)
#
# This script expects 6 secrets:
#  - CSC_LINK: A base64 encoded p12 certificate.
#  - CSC_KEY_PASSWORD: The password used to encrypt the p12 certificate
#  - APPLE_TEAM_ID: This is the ID of the team of your Apple Developer Account (Something like S1235Q75WSA)
#  - APPLE_APPLE_ID: This is the ID of your Apple Developer Account (usually your email)
#  - APPLE_APP_SPECIFIC_PASSWORD: The Application Specific Password created in your Developer Account.
#
# Context and materials that inspired this script:
#  - https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-pyinstaller-macos-dmg/
#  - https://medium.com/flutter-community/build-sign-and-deliver-flutter-macos-desktop-applications-on-github-actions-5d9b69b0469c
#  - https://defn.io/2023/09/22/distributing-mac-apps-with-github-actions/
#  - https://gist.github.com/txoof/0636835d3cc65245c6288b2374799c43

# Build the project
[ -e build ] && rm -r build
[ -e dist ] && rm -r dist
python build.py

# Codesign the executable created by pyinstaller
echo "Codesigning the executable created by PyInstaller"
echo $CSC_LINK | base64 --decode > certificate.p12
security create-keychain -p thisisatemporarypass build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p thisisatemporarypass build.keychain
security import certificate.p12 -k build.keychain -P $CSC_KEY_PASSWORD -T /usr/bin/codesign
security set-key-partition-list -S apple-tool:,apple:,codedign: -s -k thisisatemporarypass build.keychain
/usr/bin/codesign --force --deep --options=runtime --entitlements ./packaging/macos/entitlements.mac.plist -s $APPLE_TEAM_ID --timestamp dist/opendataeditor/opendataeditor

# Create dmg folder and copy our signed executable
mkdir -p dist/dmg
cp "dist/opendataeditor/opendataeditor" "dist/dmg"

# Create the dmg file
VERSION=$(python -c "import ode; print(ode.__version__)")
FILENAME=opendataeditor-macos-$VERSION.dmg
[ -e $FILENAME ] && rm $FILENAME
echo "Creating the DMG file"
create-dmg \
  --volname "Open Data Editor" \
  --volicon "./packaging/macos/icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "opendataeditor" 200 190 \
  --hide-extension "opendataeditor" \
  --app-drop-link 600 185 \
  $FILENAME \
  "dist/dmg/"

# Notarize the DMG File
echo "Notarizing the DMG file"
xcrun notarytool submit --verbose --team-id $APPLE_TEAM_ID --apple-id $APPLE_ID --password $APPLE_APP_SPECIFIC_PASSWORD --wait $FILENAME

# Staple the file
echo "Stapling the file"
xcrun stapler staple $FILENAME
