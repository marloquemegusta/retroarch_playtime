import os
import re
import sys
from datetime import datetime, timedelta
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

def load_emulator_to_console(file_path):
    """
    Load the emulator to console mapping from a file.
    
    Args:
        file_path (str): Path to the file containing emulator to console mappings.
    
    Returns:
        dict: A dictionary mapping emulators to consoles.
    """
    emulator_to_console = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                emulator, console = line.strip().split(',')
                emulator_to_console[emulator] = console
    return emulator_to_console

# Load the dictionary from the file
emulator_to_console = load_emulator_to_console('consoles_emulators.txt')

def parse_log_file(file_path):
    """
    Parse a RetroArch log file to extract game title, play time, console, start date, and end date.
    
    Args:
        file_path (str): Path to the log file.
    
    Returns:
        tuple: A tuple containing game title, play time, console, start date, and end date.
    """
    game_title = None
    play_time = timedelta()
    console = None
    start_date = None
    end_date = None
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            if 'Redirecting save file to' in line:
                match = re.search(r'/([^/]+)\.srm', line)
                if match:
                    game_title = match.group(1)
            if 'Content ran for a total of' in line:
                match = re.search(r'(\d+) hours, (\d+) minutes, (\d+) seconds', line)
                if match:
                    hours, minutes, seconds = map(int, match.groups())
                    play_time += timedelta(hours=hours, minutes=minutes, seconds=seconds)
            if 'Loading dynamic libretro core from' in line:
                match = re.search(r'Loading dynamic libretro core from: "([^"]+)"', line)
                if match:
                    emulator = match.group(1).split('/')[-1].split('_')[0]
                    console = emulator_to_console.get(emulator, emulator)
            if 'Built:' in line:
                match = re.search(r'Built: (.+)', line)
                if match:
                    start_date = datetime.strptime(match.group(1), '%b %d %Y').strftime('%Y-%m-%d')
            if 'Threaded video stats' in line:
                match = re.search(r'Threaded video stats: Frames pushed: \d+, Frames dropped: \d+', line)
                if match:
                    end_date = datetime.strptime(os.path.basename(file_path).split('__')[1].replace('.log', ''), '%Y_%m_%d').strftime('%Y-%m-%d')
    
    return game_title, play_time, console, start_date, end_date

def aggregate_play_times(log_folder):
    """
    Aggregate play times from all log files in a folder.
    
    Args:
        log_folder (str): Path to the folder containing log files.
    
    Returns:
        dict: A dictionary containing aggregated play times for each game.
    """
    play_times = {}
    
    for log_file in os.listdir(log_folder):
        if log_file.endswith('.log'):
            file_path = os.path.join(log_folder, log_file)
            game_title, play_time, console, start_date, end_date = parse_log_file(file_path)
            if game_title:
                if game_title not in play_times:
                    play_times[game_title] = {
                        'play_time': timedelta(),
                        'console': console,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                play_times[game_title]['play_time'] += play_time
    
    return play_times

def print_play_times(play_times):
    """
    Print the aggregated play times in a formatted table.
    
    Args:
        play_times (dict): A dictionary containing aggregated play times for each game.
    """
    table_data = []
    for game_title, data in play_times.items():
        play_time = data['play_time']
        if play_time >= timedelta(minutes=5):
            total_seconds = int(play_time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            table_data.append([
                game_title,
                data['console'] if data['console'] else "N/A",
                data['start_date'] if data['start_date'] else "N/A",
                data['end_date'] if data['end_date'] else "N/A",
                play_time,
                f"{hours}h {minutes}m {seconds}s"
            ])
    
    # Sort by play time in descending order
    table_data.sort(key=lambda x: x[4], reverse=True)
    
    # Remove the timedelta column before printing
    table_data = [[row[0], row[1], row[2], row[3], row[5]] for row in table_data]
    
    headers = [
        Fore.CYAN + "Game Title" + Style.RESET_ALL,
        Fore.CYAN + "Console" + Style.RESET_ALL,
        Fore.CYAN + "Start Date" + Style.RESET_ALL,
        Fore.CYAN + "End Date" + Style.RESET_ALL,
        Fore.CYAN + "Total Play Time" + Style.RESET_ALL
    ]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python retroarch_playtime.py <log_folder_path>")
        sys.exit(1)
    
    log_folder = sys.argv[1]
    play_times = aggregate_play_times(log_folder)
    print_play_times(play_times)