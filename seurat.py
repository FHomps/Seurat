import os
import sys
import time
import re
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from graphviz import Source

REGEX_TRANSFORMATIONS = [
    #(r'(\d+)', r'NUMBER_\1'),  # Replace numbers with 'NUMBER_<number>'
    #(r'(\b\w{1,3}\b)', r'SHORT_\1')  # Replace short words with 'SHORT_<word>'
]

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, watched_file, render_format):
        super().__init__()
        self.watched_file = watched_file
        self.render_format = render_format

    def on_modified(self, event):
        if event is None or event.src_path == self.watched_file:
            transformed_contents = apply_regex_transformations(read_file_contents(self.watched_file))
            graph = Source(transformed_contents)
            path_without_ext = os.path.splitext(self.watched_file)[0]
            output_dot_path = path_without_ext + ".dot"
            write_to_file(output_dot_path, transformed_contents)
            if self.render_format:
                try:
                    graph.render(
                        output_dot_path,
                        format=self.render_format,
                        outfile=path_without_ext + '.' + self.render_format
                    )
                except Exception as e:
                    print(f"Error: {e}")

def read_file_contents(file_path):
    with open(file_path, 'r') as file:
        contents = file.read()
    return contents

def apply_regex_transformations(contents):
    for pattern, replacement in REGEX_TRANSFORMATIONS:
        contents = re.sub(pattern, replacement, contents)
    return contents

def write_to_file(file_path, contents):
    with open(file_path, 'w') as file:
        file.write(contents)

def main(watched_file, render_formatat):
    if not os.path.exists(watched_file):
        print(f"Error: '{watched_file}' does not exist.")
        sys.exit(1)

    if not watched_file.endswith(".sdot"):
        print("Error: Please provide a '.sdot' file.")
        sys.exit(1)

    watched_file = os.path.abspath(watched_file)

    event_handler = FileChangeHandler(watched_file, render_formatat)

    event_handler.on_modified(None)

    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(watched_file))
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("watched_file", help="File to watch (.sdot)")
    parser.add_argument("--format", choices=["png", "jpg", "pdf"], help="Render format (png, jpg, pdf)")
    args = parser.parse_args()
    main(args.watched_file, args.format)
