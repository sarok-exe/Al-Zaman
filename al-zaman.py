#!/usr/env/bin python3
# -*- coding: utf-8 -*-

"""
Al-Zaman - Digital Clock with Hijri Date
A minimal clock displaying Gregorian & Hijri dates, and big time.
Select a country from the menu, then press X to return to menu.
"""

import datetime
import time
import sys
import os
import select      # تم إضافة import select
import tty
import termios
import pytz
from hijri_converter import Gregorian
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.live import Live
from rich.align import Align
from rich.prompt import Prompt
from rich.table import Table

console = Console()

# ==================== ALL ARAB COUNTRIES ====================
COUNTRIES = {
    "1": {"name": "Morocco", "tz": "Africa/Casablanca"},
    "2": {"name": "Algeria", "tz": "Africa/Algiers"},
    "3": {"name": "Tunisia", "tz": "Africa/Tunis"},
    "4": {"name": "Libya",   "tz": "Africa/Tripoli"},
    "5": {"name": "Egypt",   "tz": "Africa/Cairo"},
    "6": {"name": "Sudan",   "tz": "Africa/Khartoum"},
    "7": {"name": "Palestine", "tz": "Asia/Gaza"},
    "8": {"name": "Lebanon", "tz": "Asia/Beirut"},
    "9": {"name": "Syria",   "tz": "Asia/Damascus"},
    "10": {"name": "Jordan",  "tz": "Asia/Amman"},
    "11": {"name": "Iraq",    "tz": "Asia/Baghdad"},
    "12": {"name": "Saudi Arabia", "tz": "Asia/Riyadh"},
    "13": {"name": "Yemen",   "tz": "Asia/Aden"},
    "14": {"name": "Oman",    "tz": "Asia/Muscat"},
    "15": {"name": "UAE",     "tz": "Asia/Dubai"},
    "16": {"name": "Qatar",   "tz": "Asia/Qatar"},
    "17": {"name": "Bahrain", "tz": "Asia/Bahrain"},
    "18": {"name": "Kuwait",  "tz": "Asia/Kuwait"},
    "19": {"name": "Mauritania", "tz": "Africa/Nouakchott"},
    "20": {"name": "Somalia", "tz": "Africa/Mogadishu"},
    "21": {"name": "Djibouti", "tz": "Africa/Djibouti"},
    "22": {"name": "Comoros", "tz": "Indian/Comoro"},
}

# ==================== ENGLISH NAMES ====================
WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS_GREGORIAN_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
MONTHS_HIJRI_EN = [
    "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani", "Jumada al-Awwal", "Jumada al-Thani",
    "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
]

def get_current_time(tz_name):
    tz = pytz.timezone(tz_name)
    return datetime.datetime.now(tz)

def get_hijri(dt):
    hijri = Gregorian(dt.year, dt.month, dt.day).to_hijri()
    return {
        "day": hijri.day,
        "month": hijri.month,
        "year": hijri.year,
        "month_name": MONTHS_HIJRI_EN[hijri.month - 1]
    }

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80

def show_country_selector():
    """Displays the country selection menu and returns the chosen country code."""
    console.clear()
    
    # شعار بسيط بدون خطوط مزدوجة
    logo = """
    ╭──────────────────────────────╮
    │         AL-ZAMAN v2.0         │
    │   Arab World Clock & Hijri    │
    ╰──────────────────────────────╯
    """
    console.print(logo, style="bold cyan", justify="center")
    
    # جدول الدول بخطوط عادية (simple)
    table = Table(title="[bold yellow]Select a Country[/bold yellow]", box=box.SIMPLE, border_style="blue")
    table.add_column("Code", style="cyan", justify="center")
    table.add_column("Country", style="green", justify="right")
    table.add_column("Timezone", style="white", justify="left")
    
    for code, info in COUNTRIES.items():
        table.add_row(code, info["name"], info["tz"])
    
    console.print(table)
    
    # إدخال المستخدم
    choice = Prompt.ask("[bold magenta]Enter country code[/bold magenta]", choices=list(COUNTRIES.keys()), default="1")
    return choice

def create_display(country_code):
    """Creates the clock display for the given country."""
    country = COUNTRIES[country_code]
    dt = get_current_time(country["tz"])
    hijri = get_hijri(dt)

    # Gregorian line
    greg_line = f"{WEEKDAYS_EN[dt.weekday()]}, {dt.day} {MONTHS_GREGORIAN_EN[dt.month-1]} {dt.year}"
    # Hijri line (weekday approximated by Gregorian weekday for simplicity)
    hijri_line = f"{WEEKDAYS_EN[dt.weekday()]}, {hijri['day']} {hijri['month_name']} {hijri['year']} AH"

    # Big time
    time_str = dt.strftime("%H:%M:%S")
    width = get_terminal_width()
    if width >= 70:
        big_time = " ".join(time_str)
    else:
        big_time = time_str

    country_line = country["name"]

    content = Text()
    content.append(greg_line + "\n", style="green on black")
    content.append(hijri_line + "\n\n", style="yellow on black")
    content.append(big_time + "\n\n", style="bold cyan on black")
    content.append(country_line, style="blue on black")

    return content

def run_clock(initial_country):
    """Runs the live clock with the given country, returns when user presses X."""
    selected = initial_country
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    def generate_layout():
        layout = Layout()
        layout.split_column(Layout(name="main", ratio=1))
        content = create_display(selected)
        layout["main"].update(
            Panel(
                Align.center(content, vertical="middle"),
                box=box.SIMPLE,
                border_style="white",
                title=None
            )
        )
        return layout

    try:
        with Live(generate_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                # التحقق من الضغط على مفتاح
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == 'x':
                        break
                live.update(generate_layout())
                time.sleep(0.5)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def main():
    while True:
        country_code = show_country_selector()
        run_clock(country_code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.clear()
        console.print("[green]Al-Zaman closed.[/green]")
