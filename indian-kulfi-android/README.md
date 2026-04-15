# Indian Kulfi Offline Android App

Separate native Android project for The Indian Kulfi inventory workflow.

## What it includes

- Kotlin + Jetpack Compose UI
- Room database for fully offline product, stock, sales, and expense management
- Dashboard with daily metrics and low-stock alerts
- Product catalog with stock movement entry
- Sales capture with stock deduction
- Operations expense logging
- Seven-day report summary
- Seeded Indian Kulfi flavor catalog using the existing brand's pricing patterns

## Open the project

1. Open `indian-kulfi-android` in Android Studio.
2. Let Android Studio sync Gradle.
3. Run the `app` configuration on an emulator or device with Android 8.0+.

## Notes

- This app is intentionally offline-only and does not request internet access.
- Gradle wrapper binaries are not generated here, so Android Studio or a local Gradle install will handle the first sync.
- The visual palette follows the existing Indian Kulfi brown, gold, and cream branding.
