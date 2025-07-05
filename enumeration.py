import os
import curses

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}

def is_image_file(filename):
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS

def file_browser(stdscr):
    curses.curs_set(0)
    current_path = os.getcwd()

    while True:
        try:
            raw_entries = os.listdir(current_path)
            raw_entries.sort()
        except PermissionError:
            raw_entries = []

        # Filter: Show all folders, only image files
        entries = ['..'] + [
            e for e in raw_entries
            if os.path.isdir(os.path.join(current_path, e)) or is_image_file(e)
        ]

        selected = 0

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"🖼️ {current_path} (s/w: move, Enter: open/select, q: quit)")
            height, width = stdscr.getmaxyx()

            for i, entry in enumerate(entries):
                prefix = "👉 " if i == selected else "   "
                full_path = os.path.join(current_path, entry)
                entry_type = "📂" if os.path.isdir(full_path) else "🖼️"
                if i + 1 < height:
                    stdscr.addstr(i + 1, 0, f"{prefix}{entry_type} {entry[:width - 6]}")

            stdscr.refresh()
            key = stdscr.getch()

            if key == ord('s') and selected < len(entries) - 1:
                selected += 1
            elif key == ord('w') and selected > 0:
                selected -= 1
            elif key == ord('q'):
                return None
            elif key in [10, 13]:  # Enter
                chosen = entries[selected]
                full_path = os.path.join(current_path, chosen)

                if chosen == '..':
                    current_path = os.path.dirname(current_path)
                    break
                elif os.path.isdir(full_path):
                    current_path = full_path
                    break
                elif is_image_file(chosen):
                    return os.path.abspath(full_path)

def run_browser():
    selected_file = curses.wrapper(file_browser)
    if selected_file:
        print(selected_file)

if __name__ == "__main__":
    run_browser()
