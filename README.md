# Bing Wallpaper

A lightweight Python script that automatically downloads the daily [Bing homepage wallpaper](https://bingwallpaper.anerg.com) in 4K and sets it as your Windows desktop background. If you use multiple virtual desktops, each one gets a different recent image.

## Why?

Microsoft's official Bing Wallpaper app has some problems:
- Sometimes stops updating for days at a time
- Opens the Bing homepage in your browser uninvited
- Installs bloatware (desktop widgets, visual search buttons)
- Takes up ~900 MB of disk space

This script does the one thing the app was good at - beautiful daily wallpapers - with none of the baggage.

## How It Works

1. Scrapes the latest wallpaper from [bingwallpaper.anerg.com](https://bingwallpaper.anerg.com), a third-party Bing wallpaper archive that has been reliably cataloguing images since 2009
2. Downloads the 4K (3840×2160) version to `%USERPROFILE%\Pictures\BingDaily\`
3. Stores a record in a local SQLite database (`history.db`) to avoid redundant downloads
4. Sets the wallpaper on each virtual desktop (newest image on desktop 1, next newest on desktop 2, etc.)

## Setup

### Prerequisites
- Windows 10/11
- Python 3.8+

### Installation

1. Clone this repository (or download and extract it) to a permanent location:
   ```
   git clone https://github.com/Midnight-Owl-1/BingWallpaperLite.git
   cd BingWallpaperLite
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > **Note:** `pyvda` is only needed if you use multiple virtual desktops. The script works fine without it - it will just set the wallpaper on your current desktop.

3. Run it once to verify everything works:
   ```
   python bing_wallpaper.py
   ```

### Automate with Task Scheduler

To get a new wallpaper every day automatically:

1. Open **Task Scheduler** (`taskschd.msc`)
2. Click **Create Task** (not "Create Basic Task")
3. **General** tab:
   - Name: `Daily Bing Wallpaper`
   - Check **Run only when user is logged on**
4. **Triggers** tab - add two triggers:
   - **Daily** at **3:00 AM**
   - **At log on** (catches up if the PC was off at 3 AM)
5. **Actions** tab:
   - Action: **Start a program**
   - Program/script: Browse to `run_bing.bat` in this folder
   - Start in: The folder containing `run_bing.bat`
6. **Conditions** tab:
   - Uncheck *"Start the task only if the computer is on AC power"* (if on a laptop)
7. **Settings** tab:
   - Check *"Run task as soon as possible after a scheduled start is missed"*
8. Click **OK**

## Browse Mode

Want to revisit a previous wallpaper? Run:
```
browse_wallpapers.bat
```

This shows a numbered list of every wallpaper you've downloaded. Enter a number to apply that image (and the ones after it) across your virtual desktops.

## Notes

- **Image source:** This script relies on [bingwallpaper.anerg.com](https://bingwallpaper.anerg.com), a community archive of Bing's daily images. It has been online and actively maintained since 2009. If the site ever goes down, the script will simply fail gracefully without changing your current wallpaper.
- **Virtual desktops are optional.** If you don't use them (or don't install `pyvda`), the script just sets the wallpaper on your single desktop.
- Images are saved to `%USERPROFILE%\Pictures\BingDaily\` - you can delete old ones whenever you like.