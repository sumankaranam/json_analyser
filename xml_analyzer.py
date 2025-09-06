import xml.etree.ElementTree as ET
import sqlite3
from typing import Dict, List, Any, Set
from tqdm import tqdm
import logging
from pathlib import Path
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLFlattener:
    def __init__(self, db_path: str = 'xml_data.db'):
        self.db_path = db_path
        self.batch_size = 1000
        self.current_group_id = 0

    def create_tables(self, conn: sqlite3.Connection) -> None:
        """Create required database tables"""
        # Create all_groups table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS all_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            file_id INTEGER,
            filepath TEXT,
            filename TEXT,
            duplicate_flag BOOLEAN DEFAULT 1
        )''')

        # Create matches table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            first INTEGER,
            second INTEGER,
            percentage REAL
        )''')

    def process_group(self, group_elem: ET.Element) -> tuple[List[Dict], List[Dict]]:
        """Process a single group element"""
        self.current_group_id += 1
        group_id = self.current_group_id
        
        # Process files
        files = group_elem.findall('file')
        group_records = []
        for file_id, file_elem in enumerate(files):
            filepath = file_elem.get('path', '')
            filename = Path(filepath).name if filepath else ''
            
            group_records.append({
                'group_id': group_id,
                'file_id': file_id,
                'filepath': filepath,
                'filename': filename,
                'duplicate_flag': True
            })

        # Process matches
        matches = group_elem.findall('match')
        match_records = []
        all_100_percent = True
        
        for match_elem in matches:
            percentage = float(match_elem.get('percentage', 0))
            match_records.append({
                'group_id': group_id,
                'first': int(match_elem.get('first', 0)),
                'second': int(match_elem.get('second', 0)),
                'percentage': percentage
            })
            if percentage < 100:
                all_100_percent = False

        # Update duplicate_flag if all matches are 100%
        if all_100_percent and group_records:
            # Randomly select one file to mark as non-duplicate
            non_dup_idx = random.randint(0, len(group_records) - 1)
            group_records[non_dup_idx]['duplicate_flag'] = False

        return group_records, match_records

    def process_large_xml(self, xml_path: str) -> None:
        """Process large XML file using iterative parsing"""
        logger.info(f"Processing XML file: {xml_path}")
        
        conn = sqlite3.connect(self.db_path)
        self.create_tables(conn)
        
        try:
            context = ET.iterparse(xml_path, events=('end',))
            group_buffer = []
            match_buffer = []
            
            for event, elem in tqdm(context, desc="Processing XML"):
                if elem.tag == 'group':
                    group_records, match_records = self.process_group(elem)
                    
                    group_buffer.extend(group_records)
                    match_buffer.extend(match_records)
                    
                    # Batch insert when buffer is full
                    if len(group_buffer) >= self.batch_size:
                        self._batch_insert_groups(conn, group_buffer)
                        group_buffer = []
                    
                    if len(match_buffer) >= self.batch_size:
                        self._batch_insert_matches(conn, match_buffer)
                        match_buffer = []
                    
                    elem.clear()
            
            # Insert remaining buffers
            if group_buffer:
                self._batch_insert_groups(conn, group_buffer)
            if match_buffer:
                self._batch_insert_matches(conn, match_buffer)
            
            conn.commit()
            logger.info("Processing completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing XML: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def _batch_insert_groups(self, conn: sqlite3.Connection, data: List[Dict]) -> None:
        """Batch insert group records"""
        conn.executemany('''
        INSERT INTO all_groups (group_id, file_id, filepath, filename, duplicate_flag)
        VALUES (:group_id, :file_id, :filepath, :filename, :duplicate_flag)
        ''', data)

    def _batch_insert_matches(self, conn: sqlite3.Connection, data: List[Dict]) -> None:
        """Batch insert match records"""
        conn.executemany('''
        INSERT INTO matches (group_id, first, second, percentage)
        VALUES (:group_id, :first, :second, :percentage)
        ''', data)

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