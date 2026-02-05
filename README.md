A terminal-based metadata and album-art viewer for **cmus** using
`mediainfo`, `chafa`, and `rich`.

## Features
- Displays track metadata from cmus
- Renders album art in the terminal

## Requirements
- cmus
- mediainfo
- chafa
- Python 3.10+

## Usage
`Bash`: python cmusmetadata.py

## Issues
- FLAC files that are split using cue sheets may not display metadata correctly or be played properly at all.
- Cover image flickers on track change.
- I would like to address these issues in the future but only if I can do so without adding more dependencies
