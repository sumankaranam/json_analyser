# XML Data Analyzer

A Python tool for analyzing large XML files and storing the data in SQLite database with memory-efficient processing.

## Features

- Memory-efficient XML parsing using iterative approach
- Batch processing for database operations
- Progress tracking with tqdm
- Comprehensive logging
- SQLite database storage with proper table relationships
- Support for large XML files

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

3. Install dependencies:
```bash
pip install -e .
```

## Usage

1. Place your XML file in the project directory
2. Run the analyzer:
```bash
python xml_analyzer.py
```

## Database Schema

### Groups Table
- `group_id` (INTEGER PRIMARY KEY)
- `total_files` (INTEGER)
- `marked_y` (INTEGER)
- `marked_n` (INTEGER)

### Files Table
- `file_id` (INTEGER PRIMARY KEY)
- `group_id` (INTEGER, FOREIGN KEY)
- `name` (TEXT)
- `marked` (TEXT)

### Matches Table
- `match_id` (INTEGER PRIMARY KEY)
- `group_id` (INTEGER, FOREIGN KEY)
- `first` (TEXT)
- `second` (TEXT)
- `percentage` (REAL)

## Example Queries

```sql
-- Get total number of groups
SELECT COUNT(*) FROM groups;

-- Get files marked as duplicates
SELECT * FROM files WHERE marked = 'y';

-- Get match statistics by group
SELECT g.group_id, COUNT(m.match_id) as match_count 
FROM groups g 
LEFT JOIN matches m ON g.group_id = m.group_id 
GROUP BY g.group_id;
```

## Configuration

- Batch size can be adjusted in `XMLFlattener` class (default: 1000)
- Database path can be specified when initializing `XMLFlattener`
- Logging level can be modified in the script

## Requirements

- Python 3.7+
- pandas
- lxml
- tqdm

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details