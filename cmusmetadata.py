import subprocess
import os
import re
import time
import sys
from rich.console import Console
from rich.traceback import install

# Enable rich traceback globally
install(show_locals=True)
console = Console()


def get_current_file():
    try:
        result = subprocess.run(['cmus-remote', '-Q'], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return None, "[bold red]cmus is not currently running[/]"

    for line in result.stdout.splitlines():
        if line.startswith('file '):
            path = line[5:] # Leaves only the pure path
            return os.path.expanduser(path), None

    return None, "[yellow]No track currently playing[/]"


def get_metadata(file_path):
    if not os.path.isfile(file_path):
        return None, "[bold red]File does not exist[/]"
    try:
        result = subprocess.run(["mediainfo", file_path], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return None, f"[bold red]mediainfo failed: {e}[/]"

    output = result.stdout

    metadata = {
        'Title': 'Unknown',
        'Artist': 'Unknown',
        'Album': 'Unknown',
        'Codec': 'Unknown',
        'File size': 'Unknown',
        'Date': 'Unknown',
        'Bit depth': 'Unknown',
        'Bit rate': 'Unknown',
        'Sampling rate': 'Unknown',
        'Duration': 'Unknown',
        'URL': 'Unknown',
        'Track position': 'Unknown',
        'Track total': 'Unknown',
    }

    patterns = {
        'Title': r'^Title\s*:\s*(.+)$',
        'Artist': r'^Performer\s*:\s*(.+)$',
        'Album': r'^Album\s*:\s*(.+)$',
        'Codec': r'^Format\s*:\s*(.+)$',
        'File size': r'^File size\s*:\s*(.+)$',
        'Date': r'^Recorded date\s*:\s*(.+)$',
        'Bit depth': r'^Bit depth\s*:\s*(.+)$',
        'Bit rate': r'^Bit rate\s*:\s*(.+)$',
        'Sampling rate': r'^Sampling rate\s*:\s*(.+)$',
        'Duration': r'^Duration\s*:\s*(.+)$',
        'URL': r'^URL\s*:\s*(.+)$',
        'Track position': r'^Track name/Position\s*:\s*(.+)$',
        'Track total': r'^Track name/Total\s*:\s*(.+)$',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output, re.MULTILINE)
        if match:
            metadata[key] = match.group(1)

    return metadata, None


def get_album_cover(file_path):
    album_path = os.path.dirname(file_path)
    if not os.path.isdir(album_path):
        return None

    try:
        for item in os.listdir(album_path):
            if item.lower().endswith(('.png','.jpg','.jpeg')):
                return os.path.join(album_path, item)
    except FileNotFoundError:
        return None

    return None


def main(file_path):
    if not os.path.isfile(file_path):
        console.print("[bold red]No valid file found...[/]")
        return

    meta, error = get_metadata(file_path)
    if error:
        console.print(error)
        return

    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    console.rule('[bold red] METADATA', characters='=', style="white")
    print()
    print(f'{"Title":15}: {meta.get("Title")}')
    print(f'{"Album":15}: {meta.get("Album")}')
    print(f'{"Artist":15}: {meta.get("Artist")}')
    print(f'{"Date":15}: {meta.get("Date")}')
    print(f'{"Duration":15}: {meta.get("Duration")}')
    print(
        f'{"Track position":15}: '
        f'{meta.get("Track position")}/{meta.get("Track total")}'
    )
    print()
    console.rule(characters='=', style="white")
    print()
    print(f'{"Codec":15}: {meta.get("Codec")}')
    print(f'{"File size":15}: {meta.get("File size")}')
    print(f'{"Bit rate":15}: {meta.get("Bit rate")}')
    print(f'{"Bit depth":15}: {meta.get("Bit depth")}')
    print(f'{"Sampling rate":15}: {meta.get("Sampling rate")}')
    print()
    console.rule(characters='=', style="white")
    print()

    album_cover_path = get_album_cover(file_path)
    if album_cover_path:
        try:
            subprocess.run([
                'chafa',
                '--align=center',
                '--size=40x40',
                album_cover_path
            ])
        except Exception:
            console.print_exception(show_locals=True)
    else:
        console.print("[yellow]Could not find album cover...[/]")


last_file = None

# Adjust font size depending on window size
subprocess.run(['kitty', '@', 'set-font-size', '12'], stderr=subprocess.DEVNULL)

while True:
    try:
        file_path, error = get_current_file()

        if error:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            console.print(error)

        elif file_path and os.path.isfile(file_path):
            if file_path != last_file:
                last_file = file_path
                main(file_path)

        else:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            console.print("[cyan]Waiting for song to play...[/]")

    except Exception:
        console.print_exception(show_locals=True)

    time.sleep(1)
