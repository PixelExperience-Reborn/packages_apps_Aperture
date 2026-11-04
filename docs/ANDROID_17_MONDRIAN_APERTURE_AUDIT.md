# P1 — Aperture Android 17 / mondrian source audit

Date: 2026-11-04. Status: **AUDIT ONLY; NOT PORTED; NOT SELECTED IN ANDROID 17 MANIFEST**.

## Scope and provenance

- Historical PixelExperience-Reborn source: `seventeen` at commit `1a68ce0ff88b083daf8c7ddc7bd3c1cd2a4dce69`, Git tree `12c2b5afdf7bfdb37abb9d9c3ad5e94d6a132241` (latest observed source commit dated 2024-03-01).
- Comparison source: official `LineageOS/android_packages_apps_Aperture`, `lineage-24.0` at commit `0a140ed30b5c9f46b055c76f3fec03f1026cff25`, Git tree `5f2f28d8c12107493c71eceda3c3236eabd84523`, observed 2026-11-04.
- Target: PixelExperience-Reborn **AOSP 17** (API 37), **mondrian only**. The upstream branch name and API 36 configuration do not by themselves establish AOSP 17 compatibility.
- Source of truth for active selection is the staged manifest branch `port/a17-aosp17-manifest-20261102`. The official AOSP17 source graph already includes `platform/packages/apps/Camera2` at `packages/apps/Camera2`. Aperture is **not** selected in its P0/P1 profiles.

## Verified legacy vs current upstream design

| Area | Historical PE fork | Official LineageOS comparison |
| --- | --- | --- |
| Gradle compile/target API | 34 / 34 | 36 / 36 (not API 37) |
| Soong `app/Android.bp` SDK | `sdk_version: "34"` | `sdk_version: "36"` |
| Java/Kotlin | Java 8-era configuration | Java 17; Kotlin 2.2 version catalog |
| CameraX artifacts | 1.4.0-alpha04 | 1.7.0-alpha03; additional Camera2 Pipe/Viewfinder dependencies |
| Media3 artifacts | 1.1.1 | 1.10.0 |
| Coil | 2.4.0 | 3.0.4 |
| ZXing | core 3.5.2 | core 3.5.3 and zxing-cpp Android 3.1.1 |
| Soong integration | PE-specific `aapt_version_code_defaults`; no `overrides` | `overrides: ["Camera2"]`, `use_embedded_native_libs`, additional sysconfig modules |
| Packaging | APK + overlay + lens launcher | APK + overlay + lens launcher + package stopped/preinstalled sysconfig |
| Native/prebuilt libs | Existing vendored AAR/JAR collection | Different collection incl. JNI-bearing libraries |

Both trees provide `app/Android.bp`, `app/libs/Android.bp`, Gradle build files, a camera app manifest, `ApertureFrameworksBaseOverlay` and `ApertureLensLauncher`. The library list in `app/libs/Android.bp` references vendored AAR/JAR files; these references must remain consistent with the checked-out tree.

These comparisons are *source/configuration observations*, not proof that one version works on AOSP17. Historical commits must be reviewed and compared before treating a change as PixelExperience-specific; a 2024 snapshot is not itself a patch queue.

## Integration decision — deliberately gated

1. **Do not** reference the 2024 `seventeen` app as an Android17-ready `packages/apps/Aperture` manifest replacement.
2. **Do not** copy the 2026 upstream `Android.bp` into the older tree or just change `sdk_version`; the Kotlin API, dependency graph, CameraX/Media3 AAR/JAR set, JNI extraction, resource overlays and install sysconfig must be consistent.
3. **Do not** set `PRODUCT_PACKAGES += Aperture` or enable `overrides: ["Camera2"]` for mondrian before Soong and device validation. Preserve working AOSP Camera2 until a functional replacement is demonstrated.
4. Review all `Android.bp` static module names against the **actual AOSP17** tree and prebuilts (including `androidx.*`, `kotlin-stdlib`, `kotlinx-coroutines`, Material, Guava, ZXing and zxing-cpp). No one-off dependency stubs.
5. Resolve the provenance and license of vendored AAR/JAR/JNI artifacts, artifact checksums, target API behavior, Android 17 scoped media access, camera/microphone/location permissions, secure camera/lockscreen intents, and camera extensions provider.
6. Verify `android.hardware.camera.*` characteristics, logical/physical lenses, camera2 camera IDs, video encoder/quality selection, preview, zoom, flash/torch, QR scan, geotagging and external-capture intents on **POCO F5 Pro / Redmi K60 (mondrian)**.

## Acceptance gates

- [x] Trace both source commits/trees and compare build/integration metadata.
- [x] Confirm that staged AOSP17 manifest still selects AOSP Camera2 and excludes Aperture.
- [x] Maintain a source-only regression gate for the untouched historical fork (see `tools/verify_a17_aperture_legacy.py`).
- [ ] Produce a reviewed, reproducible AOSP17 candidate source branch with complete dependencies and licenses (upstream changes plus PE-specific review).
- [ ] Pass clean AOSP17 Soong `m Aperture`, dependency resolution, RRO/required modules, native library packaging and install path verification.
- [ ] Pass Gradle build where applicable, lint/tests and APK manifest/API checks.
- [ ] Check RRO ownership, single camera default/overrides behavior, sysconfig package state and SELinux (if services require additional policy).
- [ ] Validate runtime camera/photo/video/QR/secure capture on mondrian.
- [ ] Only then create a separate opt-in manifest profile pinned to an immutable candidate commit, with targeted sync + joint profile CI.

## What the audit CI does and does not prove

The host check verifies historical file/Soong/manifest invariants and existence of checked-in AAR/JAR dependencies. It is **not** an Android build, a dependency-resolution proof against AOSP17, a camera runtime test, or a claim that the app has been ported. This branch changes no app runtime sources. It must not be merged into a release source graph as if it were a working A17 camera.

Next scheduled P1 row in the 135-repository matrix: `packages/apps/Camera2` (official AOSP17 baseline, audited separately).
