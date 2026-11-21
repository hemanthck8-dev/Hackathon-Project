# MediCare – Medicine Reminder Application

A modern, professional medicine reminder application built with **Python** and **Kivy**.  
Manage your medications, set reminders, track adherence, and never miss a dose.

---

## 📋 Features

| Feature | Description |
|---|---|
| **Dashboard** | Today's schedule, upcoming reminders, adherence stats |
| **Add Medicine** | Full form with name, dosage, time, dates, frequency, notes |
| **Medicine List** | View, edit, delete medicines organized by time of day |
| **Reminders** | Automatic popup alerts with **Taken** / **Skip** buttons |
| **History** | Complete log of taken and skipped medicines with stats |
| **Settings** | Notification preferences, data management, app info |
| **Persistent Data** | SQLite database survives app restarts |
| **Android Ready** | Designed for mobile screens, buildozer.spec included |

---

## 🗂️ Project Structure

```
medicinealert/
├── main.py                        # App entry point
├── database.py                    # SQLite database operations
├── reminder.py                    # Reminder checking & popup system
├── screens/
│   ├── __init__.py
│   ├── home_screen.py             # Dashboard screen
│   ├── add_medicine_screen.py     # Add/Edit medicine form
│   ├── medicines_screen.py        # Medicine list with edit/delete
│   ├── history_screen.py          # History & adherence stats
│   └── settings_screen.py         # Settings & app info
├── buildozer.spec                 # Android APK build configuration
└── README.md                      # This file
```

---

## 🚀 Installation & Setup (Windows / VS Code)

### Step 1: Install Python

Download and install **Python 3.9+** from [python.org](https://www.python.org/downloads/).  
During installation, check **"Add Python to PATH"**.

Verify:
```bash
python --version
```

### Step 2: Create a Virtual Environment (Recommended)

Open a terminal in VS Code (`Ctrl + ~`) and navigate to the project folder:

```bash
cd "C:\Users\Hemanth ck\OneDrive\Documents\medicinealert"
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install kivy[base] kivy[media]
```

> **Note:** If you encounter issues, try:
> ```bash
> pip install kivy
> ```

### Step 4: Run the Application

```bash
python main.py
```

The MediCare window will open with a 360×640 mobile-sized window.

---

## 📱 How to Use

### Adding a Medicine
1. Tap **Medicines** in the bottom bar
2. Tap the **+** button
3. Fill in the form:
   - **Medicine Name** – e.g., "Paracetamol"
   - **Dosage** – e.g., "1 tablet", "5 ml"
   - **Time** – Select hour and minute
   - **Start Date** – YYYY-MM-DD format (auto-filled with today)
   - **End Date** – Optional, leave empty for ongoing
   - **Frequency** – Daily or select specific days
   - **Notes** – Optional additional info
4. Tap **Save Medicine**

### Getting Reminders
- The app checks every 30 seconds for medicines that are due
- When a medicine is due, a popup appears with:
  - Medicine name and dosage
  - **Taken** button – marks medicine as taken
  - **Skip** button – marks medicine as skipped
- Each reminder only appears once per day per medicine

### Viewing History
- Tap **History** in the bottom bar
- See adherence rate, taken/skipped counts
- Filter by: All, Today, This Week
- Records are grouped by date

### Editing / Deleting
- Go to **Medicines** tab
- Tap **Edit** to modify a medicine
- Tap **Delete** to remove it (with confirmation)

---

## 🤖 Building the Android APK

### Prerequisites (Linux / WSL Required)

Buildozer requires a **Linux environment**. On Windows, use **WSL** (Windows Subsystem for Linux):

```bash
# In Windows PowerShell (as Admin):
wsl --install

# After restart, open WSL and run:
sudo apt update && sudo apt upgrade -y
```

### Step 1: Install Buildozer Dependencies

```bash
sudo apt install -y \
    python3-pip \
    build-essential \
    git \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-17-jdk \
    unzip \
    zip \
    autoconf \
    libtool \
    pkg-config \
    cmake
```

### Step 2: Install Buildozer and Cython

```bash
pip3 install --user buildozer cython virtualenv
```

### Step 3: Copy Project to WSL

```bash
# From WSL, copy the project:
cp -r /mnt/c/Users/"Hemanth ck"/OneDrive/Documents/medicinealert ~/medicinealert
cd ~/medicinealert
```

### Step 4: Build the APK

```bash
# Debug APK (for testing):
buildozer android debug

# Release APK (for distribution):
buildozer android release
```

The first build takes **15-30 minutes** as it downloads the Android SDK, NDK, and dependencies.

### Step 5: Find Your APK

The built APK will be in:
```
~/medicinealert/bin/medicare-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

### Step 6: Install on Android Device

```bash
# Via USB (with ADB):
buildozer android deploy

# Or copy the APK to your phone and install manually
```

> **Tip:** Enable "Install from Unknown Sources" on your Android device.

---

## 🧪 Testing Tips

### Quick Test: Add a medicine with the current time
1. Add a medicine with the reminder time set to the current time (or 1-2 minutes ahead)
2. Wait for the reminder popup to appear
3. Test both **Taken** and **Skip** buttons
4. Check the **History** tab to verify the record was saved

### Verify Database Persistence
1. Add several medicines
2. Close the app completely
3. Restart with `python main.py`
4. All medicines should still be there

---

## ⚙️ Database Schema

### `medicines` table
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Medicine name |
| dosage | TEXT | Dosage info |
| reminder_time | TEXT | Time in HH:MM format |
| start_date | TEXT | Start date YYYY-MM-DD |
| end_date | TEXT | End date (optional) |
| frequency | TEXT | "daily" or comma-separated days |
| notes | TEXT | Optional notes |
| active | INTEGER | 1 = active, 0 = inactive |
| created_at | TEXT | Creation timestamp |

### `history` table
| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| medicine_id | INTEGER | Foreign key → medicines.id |
| medicine_name | TEXT | Medicine name (denormalized) |
| dosage | TEXT | Dosage at time of action |
| scheduled_time | TEXT | Scheduled reminder time |
| action | TEXT | "taken" or "skipped" |
| action_time | TEXT | When the action was recorded |
| scheduled_date | TEXT | Date the medicine was scheduled |

### `settings` table
| Column | Type | Description |
|---|---|---|
| key | TEXT | Setting name |
| value | TEXT | Setting value |

---

## 🛠️ Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'kivy'` | Run `pip install kivy` |
| Window too small / too large | Edit `Config.set("graphics", "width/height")` in `main.py` |
| Reminders not showing | Make sure the medicine time matches the current time (HH:MM) |
| Buildozer fails | Ensure all apt dependencies are installed; check Java version |
| Database errors | Delete `medicare.db` to reset; the app recreates it on start |

---

## 📄 License

This project is provided as-is for educational and personal use.
