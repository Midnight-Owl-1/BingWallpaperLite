import os
import sqlite3
import requests
import ctypes
import sys
import time
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from pyvda import VirtualDesktop, get_virtual_desktops
except ImportError:
    get_virtual_desktops = None
    VirtualDesktop = None

# Fetches the latest Bing wallpaper in 4K, saves it locally, and sets it as the desktop
# background. If you use multiple virtual desktops, each one gets a different recent
# wallpaper (newest on desktop 1, next on desktop 2, etc.).
# Run with --browse to view your wallpaper history and apply any previous image.

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL   = 'https://bingwallpaper.anerg.com'
SAVE_DIR   = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'BingDaily')
DB_PATH    = os.path.join(SCRIPT_DIR, 'history.db')

os.makedirs(SAVE_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS wallpapers (id INTEGER PRIMARY KEY, date TEXT UNIQUE, local_path TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    conn.commit()
    return conn


def _get_desktop_count():
    """Return the number of virtual desktops, or 1 if pyvda is not available."""
    if get_virtual_desktops is None:
        return 1
    return len(get_virtual_desktops())


def _apply_to_desktops(paths):
    """Set wallpapers across all virtual desktops.
    paths[0] -> desktop 1, paths[1] -> desktop 2, etc.
    If there are more desktops than paths, the last path is reused.
    Falls back to setting only the current desktop if pyvda is not installed.
    """
    if not paths:
        return
    if get_virtual_desktops is None:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, paths[0], 3)
        return
    desktops = get_virtual_desktops()
    origin   = VirtualDesktop.current()
    for i, desktop in enumerate(desktops):
        path = paths[i] if i < len(paths) else paths[-1]
        desktop.go()
        time.sleep(0.25)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
    origin.go()


def get_latest_bing_info():
    resp = requests.get(BASE_URL, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    detail_link = soup.find('a', href=lambda x: x and '/detail/' in x)
    if not detail_link:
        return None, None
    detail_url  = BASE_URL + detail_link['href']
    detail_resp = requests.get(detail_url, timeout=10)
    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
    uhd_node    = detail_soup.find('a', href=lambda x: x and 'w:3840' in x)
    if not uhd_node:
        uhd_node = detail_soup.find('a', string=lambda x: x and 'UHD' in x.upper())
    if not uhd_node:
        return None
    href = uhd_node['href']
    return href if href.startswith('http') else BASE_URL + href


def run_daily_update():
    conn  = init_db()
    today = datetime.now().strftime('%Y-%m-%d')

    last_run = conn.execute('SELECT value FROM settings WHERE key="last_success"').fetchone()
    if last_run and last_run[0] == today:
        print(f'Already updated today ({today}).')
        return

    print("Fetching today's 4K wallpaper...")
    img_url = get_latest_bing_info()
    if not img_url:
        print('Failed to find 4K image.')
        return

    file_path = os.path.join(SAVE_DIR, f'{today}.jpg')
    if not os.path.exists(file_path):
        img_data = requests.get(img_url, timeout=30).content
        with open(file_path, 'wb') as f:
            f.write(img_data)

    conn.execute('INSERT OR IGNORE INTO wallpapers (date, local_path) VALUES (?, ?)', (today, file_path))
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES ("last_success", ?)', (today,))
    conn.commit()

    n     = _get_desktop_count()
    rows  = conn.execute('SELECT local_path FROM wallpapers ORDER BY date DESC LIMIT ?', (n,)).fetchall()
    _apply_to_desktops([r[0] for r in rows])


def browse_mode():
    conn = init_db()
    rows = conn.execute('SELECT date, local_path FROM wallpapers ORDER BY date DESC').fetchall()
    if not rows:
        print('No history found.')
        return

    print('--- Bing Wallpaper History ---')
    for idx, row in enumerate(rows):
        print(f'[{idx}] {row[0]}: {row[1]}')

    try:
        choice = input('Enter number to apply wallpaper (or Enter to exit): ').strip()
        if choice:
            idx   = int(choice)
            n     = _get_desktop_count()
            paths = [r[1] for r in rows[idx:idx + n]]
            _apply_to_desktops(paths)
            print('Wallpaper updated!')
    except (ValueError, IndexError):
        print('Invalid selection.')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--browse':
        browse_mode()
    else:
        run_daily_update()
