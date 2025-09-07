
# XML Data Analyzer

A Python GUI application for analyzing XML files containing duplicate file information and storing the data in SQLite database with memory-efficient processing.

## Features

- Memory-efficient XML parsing using iterative approach
- Batch processing for database operations
- Progress tracking with visual feedback
- Comprehensive logging
- SQLite database storage
- Modern GUI with:
  - Thumbnail preview of images
  - Group-wise duplicate viewing
  - Navigation controls
  - File path tooltips
  - Context menu for copying paths
  - Image preview on click
  - Original/Duplicate status indication

## Requirements

- Python 3.7 or higher
- Operating System: Windows/Linux/MacOS

### Dependencies

- pandas: Data manipulation
- lxml: XML processing
- tqdm: Progress bars
- ttkthemes: Modern GUI themes
- Pillow: Image processing
- python-tk: GUI framework
- sqlalchemy: Database operations

## Installation

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
```bash
# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install package and dependencies:
```bash
# For users
pip install -e .

# For developers (includes testing tools)
pip install -e ".[dev]"
```

## Usage

1. Start the application:
```bash
python xml_analyzer.py
```

2. XML Analysis Mode:
   - Click "Browse XML" to select input XML file
   - Set database name
   - Click "Process XML"
   - Monitor progress in real-time

3. View Duplicates Mode:
   - Click "Browse DB" to select database
   - Click "Load Duplicates"
   - Navigate through groups using:
     - Previous/Next buttons
     - Page navigation
     - Direct group access

4. Image Interaction:
   - Hover: Shows full file path
   - Left-click: Opens image in default viewer
   - Right-click: Copy file path menu

## Database Schema

### all_groups Table
- `id` (INTEGER PRIMARY KEY)
- `group_id` (INTEGER)
- `file_id` (INTEGER)
- `filepath` (TEXT)
- `filename` (TEXT)
- `duplicate_flag` (BOOLEAN)

### matches Table
- `id` (INTEGER PRIMARY KEY)
- `group_id` (INTEGER)
- `first` (INTEGER)
- `second` (INTEGER)
- `percentage` (REAL)

## Configuration

- Batch size: Adjustable in XMLFlattener class (default: 1000)
- Groups per page: Adjustable in UI (default: 5)
- Thumbnail size: 150x150 pixels (adjustable in code)
- Database path: User-configurable
- Logging level: INFO by default

## Development

### Setup Development Environment
```bash
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Install development dependencies
4. Make your changes
5. Run tests and linting
6. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details