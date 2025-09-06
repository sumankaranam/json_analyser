import json
from collections import Counter
from typing import Any, Dict, List
import pandas as pd

class JsonAnalyzer:
    def __init__(self, json_data: Any):
        self.data = json_data
        self.structure = {}
        self.stats = {}
    
    def analyze_structure(self, data: Any, path: str = "") -> None:
        """Recursively analyze JSON structure"""
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                self.structure[new_path] = type(value).__name__
                self.analyze_structure(value, new_path)
        elif isinstance(data, list):
            if data:  # Check if list is not empty
                self.structure[path] = f"list[{type(data[0]).__name__}]"
                for item in data:
                    self.analyze_structure(item, path)
    
    def calculate_stats(self, data: Any, path: str = "") -> None:
        """Calculate statistics for each field"""
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                self.calculate_stats(value, new_path)
        elif isinstance(data, list):
            if data:
                if path not in self.stats:
                    self.stats[path] = {
                        "count": len(data),
                        "distinct_count": len(set(str(x) for x in data))
                    }
                for item in data:
                    self.calculate_stats(item, path)
        else:
            if path not in self.stats:
                self.stats[path] = {
                    "distinct_count": 1,
                    "value": str(data)
                }
    
    def analyze(self) -> Dict:
        """Run complete analysis"""
        self.analyze_structure(self.data)
        self.calculate_stats(self.data)
        return {
            "structure": self.structure,
            "stats": self.stats
        }

def analyze_json_file(file_path: str) -> None:
    """Analyze JSON file and print results"""
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            
        analyzer = JsonAnalyzer(json_data)
        results = analyzer.analyze()
        
        print("\n=== JSON Structure ===")
        for path, type_info in results["structure"].items():
            print(f"{path}: {type_info}")
        
        print("\n=== Field Statistics ===")
        for path, stats in results["stats"].items():
            print(f"\nPath: {path}")
            for stat_name, stat_value in stats.items():
                print(f"{stat_name}: {stat_value}")

    except Exception as e:
        print(f"Error analyzing JSON file: {str(e)}")

if __name__ == "__main__":
    # Example usage
    file_path = "sample.json"
    analyze_json_file(file_path)