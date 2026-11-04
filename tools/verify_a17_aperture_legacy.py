#!/usr/bin/env python3
"""Source-only invariant check for the *unported* 2024 PE Aperture snapshot.

This intentionally does NOT advertise Android 17 build/runtime compatibility.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID = "{http://schemas.android.com/apk/res/android}"


def check(ok: bool, description: str) -> None:
    if not ok:
        raise AssertionError(description)
    print(f"PASS: {description}")


def text(path: str) -> str:
    p = ROOT / path
    check(p.is_file(), f"tracked file present: {path}")
    return p.read_text(encoding="utf-8")


def main() -> None:
    app_bp = text("app/Android.bp")
    lib_bp = text("app/libs/Android.bp")
    gradle = text("app/build.gradle.kts")
    settings = text("settings.gradle.kts")

    check(bool(re.search(r'android_app\s*\{\s*name:\s*"Aperture"', app_bp)),
          "Aperture Soong module exists")
    check('sdk_version: "34"' in app_bp, "historical Soong SDK 34 confirmed")
    check('defaults: ["aapt_version_code_defaults"]' in app_bp,
          "historical PE version-code build dependency documented")
    check('overrides: ["Camera2"]' not in app_bp,
          "historical fork does not replace the baseline Camera2 module")
    check('compileSdk = 34' in gradle and 'targetSdk = 34' in gradle,
          "historical Gradle compileSdk/targetSdk 34 confirmed")
    check("include(\":app\")" in settings and "include(\":lens_launcher\")" in settings,
          "Gradle includes both modules")

    # Each generated prebuilt artifact must exist in the checkout.
    patterns = re.findall(r'\b(?:aars|jars):\s*\[([^\]]*)\]', lib_bp, re.S)
    artifacts = []
    for group in patterns:
        artifacts.extend(re.findall(r'"([^"]+\.(?:aar|jar))"', group))
    check(len(artifacts) >= 20, "historical vendored AAR/JAR references enumerated")
    missing = [p for p in artifacts if not (ROOT / "app/libs" / p).is_file()]
    check(not missing, f"all {len(artifacts)} vendored AAR/JAR paths exist; missing={missing}")

    for required in ("ApertureFrameworksBaseOverlay", "ApertureLensLauncher"):
        check(f'"{required}"' in app_bp, f"Soong requires {required}")
    check((ROOT / "rro_overlays/ApertureFrameworksBaseOverlay/Android.bp").is_file(),
          "overlay module definition exists")
    check((ROOT / "lens_launcher/Android.bp").is_file(),
          "lens launcher module definition exists")

    manifest = ET.parse(ROOT / "app/src/main/AndroidManifest.xml").getroot()
    perms = {x.get(ANDROID + "name") for x in manifest.findall("uses-permission")}
    check({"android.permission.CAMERA", "android.permission.RECORD_AUDIO"}.issubset(perms),
          "camera and microphone permissions exist in legacy manifest")
    libraries = manifest.findall("./application/uses-library")
    check(any(x.get(ANDROID + "name") == "androidx.camera.extensions.impl"
              and x.get(ANDROID + "required") == "false" for x in libraries),
          "camera extensions implementation remains optional")
    check(any(x.get(ANDROID + "name") == ".SecureCameraActivity"
              and x.get(ANDROID + "exported") == "true"
              for x in manifest.findall("./application/activity")),
          "secure camera intent activity is exported in legacy manifest")

    print("PASS: legacy-source invariants only. AOSP17 build and mondrian runtime NOT TESTED.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ET.ParseError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
