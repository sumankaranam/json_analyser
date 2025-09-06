import xml.etree.ElementTree as ET
import sqlite3
from typing import Dict, List, Any
import pandas as pd
from tqdm import tqdm
import logging
from pathlib import Path
import itertools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLFlattener:
    def __init__(self, db_path: str = 'xml_data.db'):
        self.db_path = db_path
        self.batch_size = 1000
        self.current_group_id = 0  # Add a counter for group IDs

    def create_tables(self, conn: sqlite3.Connection) -> None:
        """Create necessary database tables"""
        conn.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_files INTEGER,
            marked_y INTEGER,
            marked_n INTEGER
        )''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            name TEXT,
            marked TEXT,
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        )''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            first TEXT,
            second TEXT,
            percentage REAL,
            FOREIGN KEY (group_id) REFERENCES groups (group_id)
        )''')

    def process_large_xml(self, xml_path: str) -> None:
        """Process large XML file using iterative parsing"""
        logger.info(f"Processing XML file: {xml_path}")
        
        conn = sqlite3.connect(self.db_path)
        self.create_tables(conn)
        
        try:
            # Use iterparse to handle large XML files
            context = ET.iterparse(xml_path, events=('end',))
            
            current_group: Dict[str, Any] = {}
            files_buffer: List[Dict] = []
            matches_buffer: List[Dict] = []
            
            for event, elem in tqdm(context, desc="Processing XML"):
                if elem.tag == 'group':
                    # Process group
                    group_data = self._process_group(elem)
                    if group_data:
                        self._insert_group(conn, group_data)
                        
                        # Process files and matches within the group
                        files = self._process_files(elem, group_data['group_id'])
                        matches = self._process_matches(elem, group_data['group_id'])
                        
                        files_buffer.extend(files)
                        matches_buffer.extend(matches)
                        
                        # Batch insert when buffer is full
                        if len(files_buffer) >= self.batch_size:
                            self._batch_insert_files(conn, files_buffer)
                            files_buffer = []
                        
                        if len(matches_buffer) >= self.batch_size:
                            self._batch_insert_matches(conn, matches_buffer)
                            matches_buffer = []
                    
                    # Clear element to free memory
                    elem.clear()
            
            # Insert remaining buffers
            if files_buffer:
                self._batch_insert_files(conn, files_buffer)
            if matches_buffer:
                self._batch_insert_matches(conn, matches_buffer)
            
            conn.commit()
            logger.info("Processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing XML: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _process_group(self, group_elem: ET.Element) -> Dict:
        """Process a single group element"""
        files = group_elem.findall('file')
        marked_y = sum(1 for f in files if f.get('marked') == 'y')
        marked_n = sum(1 for f in files if f.get('marked') == 'n')
        
        # Increment group ID for each new group
        self.current_group_id += 1
        
        return {
            'group_id': self.current_group_id,  # Use sequential ID instead of hash
            'total_files': len(files),
            'marked_y': marked_y,
            'marked_n': marked_n
        }

    def _process_files(self, group_elem: ET.Element, group_id: int) -> List[Dict]:
        """Process files within a group"""
        return [{
            'group_id': group_id,
            'name': file.get('name', ''),
            'marked': file.get('marked', '')
        } for file in group_elem.findall('file')]

    def _process_matches(self, group_elem: ET.Element, group_id: int) -> List[Dict]:
        """Process matches within a group"""
        return [{
            'group_id': group_id,
            'first': match.get('first', ''),
            'second': match.get('second', ''),
            'percentage': float(match.get('percentage', 0))
        } for match in group_elem.findall('match')]

    def _insert_group(self, conn: sqlite3.Connection, group_data: Dict) -> None:
        """Insert group data into database"""
        conn.execute('''
        INSERT INTO groups (group_id, total_files, marked_y, marked_n)
        VALUES (?, ?, ?, ?)
        ''', (group_data['group_id'], group_data['total_files'],
              group_data['marked_y'], group_data['marked_n']))

    def _batch_insert_files(self, conn: sqlite3.Connection, files: List[Dict]) -> None:
        """Batch insert files into database"""
        conn.executemany('''
        INSERT INTO files (group_id, name, marked)
        VALUES (?, ?, ?)
        ''', [(f['group_id'], f['name'], f['marked']) for f in files])

    def _batch_insert_matches(self, conn: sqlite3.Connection, matches: List[Dict]) -> None:
        """Batch insert matches into database"""
        conn.executemany('''
        INSERT INTO matches (group_id, first, second, percentage)
        VALUES (?, ?, ?, ?)
        ''', [(m['group_id'], m['first'], m['second'], m['percentage']) for m in matches])

def main():
    xml_path = 'duplicates.xml'
    db_path = 'xml_data.db'
    
    flattener = XMLFlattener(db_path)
    try:
        flattener.process_large_xml(xml_path)
        logger.info(f"Data successfully stored in {db_path}")
    except Exception as e:
        logger.error(f"Failed to process XML: {str(e)}")

if __name__ == "__main__":
    main()