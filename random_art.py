#!/usr/bin/env python3
import os
import random
import sys
import platform
import re
import shutil
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ART_DIR = os.path.join(BASE_DIR, "ascii")


def read_ascii_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    # 🔥 Qui convertiamo le “␛” nel vero codice ESC
    data = data.replace("␛", "\x1b")
    data = data.replace("\\e", "\x1b")     # se per caso contiene "\e"
    data = data.replace("\\ESC", "\x1b")   # se contiene "\\ESC"
    # rimuovi eventuali resti di sequenze ANSI senza l'ESC (es. '0m')
    # Ma non rimuovere '0m' che fa parte di numeri/CSI (es. '246m'): usiamo lookaround
    data = re.sub(r'(?<![0-9;])0m(?![0-9;])', '', data)
    return data


def read_os_release():
    try:
        with open('/etc/os-release', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('PRETTY_NAME='):
                    return line.split('=', 1)[1].strip().strip('"')
    except Exception:
        pass
    # fallback
    return platform.system()


def uptime_str():
    try:
        with open('/proc/uptime', 'r') as f:
            up_seconds = float(f.readline().split()[0])
            return str(timedelta(seconds=int(up_seconds)))
    except Exception:
        return 'unknown'


def get_memory():
    # Returns total and used in MiB
    try:
        mem = {}
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                parts = line.split(':')
                key = parts[0]
                val = parts[1].strip().split()[0]
                mem[key] = int(val)
        total_kb = mem.get('MemTotal', 0)
        avail_kb = mem.get('MemAvailable', mem.get('MemFree', 0))
        used_kb = total_kb - avail_kb
        return total_kb // 1024, used_kb // 1024
    except Exception:
        return None, None


def get_cpu():
    try:
        model = None
        cores = 0
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                if line.startswith('model name') and model is None:
                    model = line.split(':', 1)[1].strip()
                if line.startswith('processor'):
                    cores += 1
        return model or platform.processor() or 'unknown', cores
    except Exception:
        return platform.processor() or 'unknown', 0


def disk_usage(path='/'):
    try:
        d = shutil.disk_usage(path)
        total_gb = d.total // (1024 ** 3)
        used_gb = (d.total - d.free) // (1024 ** 3)
        return total_gb, used_gb
    except Exception:
        return None, None


def gather_stats():
    stats = []
    stats.append(("OS", read_os_release()))
    stats.append(("Host", platform.node()))
    stats.append(("Kernel", platform.release()))
    stats.append(("Uptime", uptime_str()))
    stats.append(("Shell", os.environ.get('SHELL', 'unknown')))
    stats.append(("Terminal", os.environ.get('TERM', 'unknown')))
    cpu_model, cores = get_cpu()
    stats.append(("CPU", f"{cpu_model} ({cores} cores)"))
    total_mem, used_mem = get_memory()
    if total_mem:
        stats.append(("Memory", f"{used_mem}MiB / {total_mem}MiB"))
    total_d, used_d = disk_usage('/')
    if total_d:
        stats.append(("Disk /", f"{used_d}G / {total_d}G"))
    return [f"{k}: {v}" for k, v in stats]


def format_stats_stylish(stats_tuples, max_width=None):
    """Return a list of styled string lines for the stats panel.

    - Uses ANSI colors and bold for labels/values.
    - If `pyfiglet` is available, renders the Host name in a small figlet font.
    """
    bold = "\x1b[1m"
    reset = "\x1b[0m"
    cyan = "\x1b[36m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"

    # Prepare plain (unstyled) lines first, so wrapping won't cut ANSI sequences
    plain_lines = []

    host = None
    for k, v in stats_tuples:
        if k.lower() == 'host':
            host = v
            continue
        plain_lines.append(f"{k}: {v}")

    banner_lines = []
    try:
        import pyfiglet
        if host:
            fig = pyfiglet.Figlet(font='small')
            banner = fig.renderText(host).rstrip('\n')
            banner_lines = banner.splitlines()
    except Exception:
        banner_lines = []

    # No wrapping: keep each stat on a single line. If too long, truncate the value
    wrap_width = max_width or 80
    styled_lines = []

    # Add banner (if any), truncating each banner line to wrap_width
    for b in banner_lines:
        if len(b) <= wrap_width:
            styled_lines.append(yellow + b + reset)
        else:
            styled_lines.append(yellow + b[:wrap_width] + reset)

    # For each plain stat 'K: V', keep it together; if needed, truncate V
    for pl in plain_lines:
        if ': ' in pl:
            k, v = pl.split(': ', 1)
            label_len = len(k) + 2  # 'K: '
            avail = wrap_width - label_len
            if avail < 0:
                # label itself longer than wrap_width, truncate label
                k_trunc = k[:max(0, wrap_width-1)] + '…' if wrap_width > 1 else k[:wrap_width]
                label = f"{bold}{cyan}{k_trunc}:{reset}"
                styled_lines.append(f"{label} {green}{v}{reset}")
                continue
            if len(v) > avail:
                if avail > 1:
                    v = v[:avail-1] + '…'
                else:
                    v = '…'
            label = f"{bold}{cyan}{k}:{reset}"
            value = f"{green}{v}{reset}"
            styled_lines.append(f"{label} {value}")
        else:
            styled_lines.append(f"{green}{pl}{reset}")

    return styled_lines


def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*[mKHFJmsu]', '', s)


def visible_len(s):
    return len(strip_ansi(s))


def truncate_ansi_line(line, max_visible):
    """Truncate a line containing ANSI escapes preserving full escape sequences.

    - Copies whole escape sequences (starting with \x1b[ and ending with a letter).
    - Counts only visible characters toward max_visible.
    - Appends an ellipsis character '…' (visible) if truncated and ensures we close styling with \x1b[0m.
    """
    if max_visible is None or max_visible <= 0:
        return ''

    out = ''
    visible = 0
    i = 0
    L = len(line)
    while i < L and visible < max_visible:
        ch = line[i]
        if ch == '\x1b':
            # copy full CSI/escape sequence
            m = re.match(r'\x1b\[[0-9;]*[A-Za-z]', line[i:])
            if m:
                seq = m.group(0)
                out += seq
                i += len(seq)
                continue
            else:
                # unknown escape: copy single char
                out += ch
                i += 1
                continue
        else:
            out += ch
            i += 1
            # count visible char (note: tabs are counted as 1)
            visible += 1

    # if there's remaining visible content, we truncated
    if i < L:
        # add ellipsis (visible) if room, else replace last char
        if visible < max_visible:
            out += '…'
        else:
            # replace last visible char with ellipsis
            # find last char position in out (skip trailing ANSI sequences)
            j = len(out) - 1
            # remove trailing ANSI sequences
            while j >= 0 and out[j] == 'm' or (j>0 and out[j-1]=='\x1b'):
                j -= 1
            if j >= 0:
                out = out[:j] + '…' + out[j+1:]
        # ensure we reset styles to avoid color bleed
        out += '\x1b[0m'

    return out


def print_side_by_side(ascii_text, stats_lines):
    ascii_lines = ascii_text.splitlines()
    if not ascii_lines:
        ascii_lines = ['']

    # compute visible width of ascii (without ANSI)
    visible_width = max((visible_len(line) for line in ascii_lines), default=0)

    term_w = shutil.get_terminal_size((80, 20)).columns

    # compute stats panel width
    stats_width = max((visible_len(line) for line in stats_lines), default=0)
    stats_width = min(stats_width, term_w // 2)

    # available width for ascii when side-by-side
    left_available = term_w - stats_width - 3

    # If not enough space to show ascii + stats side-by-side, print stats below
    if left_available < 20:
        # print ascii (truncate to terminal width)
        for line in ascii_lines:
            out = truncate_ansi_line(line, term_w)
            print(out)
        print()
        for line in stats_lines:
            print(line)
        return

    # Otherwise, prepare side-by-side: truncate ascii lines to left_available
    left_width = left_available

    # pad ascii lines to same height as stats
    lines = max(len(ascii_lines), len(stats_lines))
    for i in range(lines):
        a = ascii_lines[i] if i < len(ascii_lines) else ''
        s = stats_lines[i] if i < len(stats_lines) else ''

        a_trunc = truncate_ansi_line(a, left_width)
        pad = left_width - visible_len(a_trunc)
        if pad < 1:
            pad = 1
        sys.stdout.write(a_trunc + ' ' * pad + s + '\n')


def main():
    files = [f for f in os.listdir(ART_DIR) if os.path.isfile(os.path.join(ART_DIR, f))]
    if not files:
        print("Nessun file trovato.")
        sys.exit(1)

    chosen = random.choice(files)
    art = read_ascii_file(os.path.join(ART_DIR, chosen))
    stats_tuples = []
    # reconstruct tuples from gather_stats to keep keys separate
    # (gather_stats previously returned list of 'K: V' strings)
    raw = []
    for item in gather_stats():
        if ': ' in item:
            k, v = item.split(': ', 1)
            stats_tuples.append((k, v))
        else:
            raw.append(item)

    # prepare styled stats lines; pass terminal width for figlet truncation
    term_w = shutil.get_terminal_size((80, 20)).columns
    styled = format_stats_stylish(stats_tuples, max_width=max(10, term_w // 2))
    print_side_by_side(art, styled)


if __name__ == '__main__':
    main()
