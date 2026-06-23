# DashDone

**DashDone: Turn your 'to-do' into 'done'.**

A production-ready offline-first mobile productivity app (tasks + habits + stats) built with Expo SDK 54 and an optional FastAPI dev backend.

## Project structure

```
DashDone/
├── app/          # Expo React Native app (offline SQLite by default)
├── backend/      # FastAPI + SQLAlchemy API (optional, for dev/testing)
└── README.md
```

## Mobile app (default — fully offline)

The app stores all data locally with **expo-sqlite**. No account, no server, no internet required for normal use.

### Requirements

- Node.js 20+
- npm
- Android Studio (for native Android build / AAB)

### Run in development

```bash
cd app
npm install
npx expo start
```

Press `a` for Android emulator or scan the QR code with Expo Go.

### Storage modes

| Mode | Env var | Behavior |
|------|---------|----------|
| **local** (default) | `EXPO_PUBLIC_STORAGE_MODE=local` | All data on device |
| remote | `EXPO_PUBLIC_STORAGE_MODE=remote` + `EXPO_PUBLIC_API_URL=http://YOUR_LAN_IP:8000` | Uses FastAPI backend |

Create `app/.env` for optional overrides:

```env
EXPO_PUBLIC_STORAGE_MODE=local
# EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
```

## Backend (optional dev API)

### Requirements

- Python 3.11–3.13 recommended (3.14 may need prebuilt pydantic wheels)

### Run

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux
```

Windows:

```powershell
.\run.ps1
```

macOS/Linux:

```bash
chmod +x run.sh && ./run.sh
```

API docs: http://localhost:8000/docs

### Endpoints

All routes require `X-Device-Id` header (UUID v4). The mobile app generates this automatically.

- `POST /devices/register`
- Tasks: `GET/POST /tasks`, `GET/PATCH/DELETE /tasks/{id}`
- Categories: `GET/POST /categories`, `DELETE /categories/{id}`
- Habits: `GET/POST /habits`, `DELETE /habits/{id}`, `POST /habits/{id}/log`
- Stats: `GET /stats/weekly`, `/stats/categories`, `/stats/summary`, `/stats/habit-streaks`
- `DELETE /devices/{device_id}/data`

## Android release build (signed AAB)

### 1. Prebuild native project

```bash
cd app
npx expo prebuild --platform android
```

### 2. Generate release keystore (one-time)

```bash
keytool -genkeypair -v -storetype PKCS12 -keystore dashdone-release.keystore -alias dashdone -keyalg RSA -keysize 2048 -validity 10000
```

Move the keystore to `app/android/app/dashdone-release.keystore` (or your preferred path).

### 3. Configure signing

Add to `app/android/gradle.properties`:

```properties
MYAPP_UPLOAD_STORE_FILE=dashdone-release.keystore
MYAPP_UPLOAD_KEY_ALIAS=dashdone
MYAPP_UPLOAD_STORE_PASSWORD=your_store_password
MYAPP_UPLOAD_KEY_PASSWORD=your_key_password
```

Add to `app/android/app/build.gradle` inside `android { signingConfigs { release { ... } } buildTypes { release { signingConfig signingConfigs.release } } }`:

```gradle
signingConfigs {
    release {
        storeFile file(MYAPP_UPLOAD_STORE_FILE)
        storePassword MYAPP_UPLOAD_STORE_PASSWORD
        keyAlias MYAPP_UPLOAD_KEY_ALIAS
        keyPassword MYAPP_UPLOAD_KEY_PASSWORD
    }
}
buildTypes {
    release {
        signingConfig signingConfigs.release
    }
}
```

### 4. Build the AAB

```bash
cd app/android
./gradlew bundleRelease
```

Windows:

```powershell
cd app\android
.\gradlew.bat bundleRelease
```

Output: `app/android/app/build/outputs/bundle/release/app-release.aab`

Upload this file to Google Play Console.

## App configuration

- **Package:** `com.dashdone.app`
- **Version:** 1.0.0 (versionCode 1)
- **Permissions:** `INTERNET`, `POST_NOTIFICATIONS` (habit reminders)

## Features checklist

- [x] Home: week strip, progress card, task timeline, habits
- [x] Tasks: filters, pull-to-refresh, swipe complete/delete
- [x] Add modal: task + habit with notifications
- [x] Calendar: month navigation, task dots, status badges
- [x] Stats: weekly chart, habit streaks, category breakdown, points
- [x] Settings: dark/light theme, clear all data, about
- [x] Anonymous device ID (no login)
- [x] Offline-first local SQLite
- [x] Optional FastAPI backend for dev

## No stubs policy

Every screen loads real data from the repository layer. Buttons perform real actions. Empty and error states are implemented throughout.
