import re
from typing import List, Dict

# Regular expression for splitting lines
PATTERN_SPLIT_LINES = r'\n'


class DataCompressor:
    def __init__(self):
        self.lines = None
        self.result_dict: Dict[str, List[str]] = {}
        self.reserve_list: List[str] = []

    def start_compressing(self, text: str):
        self.lines: List[str] = self._create_lines(text)
        self._main_loop(self.lines)

    def _create_lines(self, text) -> List[str]:
        return [line for line in re.split(PATTERN_SPLIT_LINES, text) if line]

    def _create_patterns(self, line: str) -> List[str]:
        if not line:
            raise ValueError('text is empty in DataCompressor')
        return list(filter(None, re.split(r'(\s+|\W+)', line)))

    def _main_loop(self, lines: List[str]):
        while lines:
            current_line = lines.pop(0)
            base_pattern = self._create_patterns(current_line)
            self._recursive_extract(base_pattern, lines, 1, False)
            self._cleanup_empty_entries()
            self._process_result_dict()

    def _cleanup_empty_entries(self):
        # Remove key-value pairs with empty lists
        keys_to_remove = [key for key, value in self.result_dict.items() if not value]
        for key in keys_to_remove:
            del self.result_dict[key]

    def _process_result_dict(self):
        if not self.result_dict:
            return
        processed_dict = {}
        for base_pattern, values in self.result_dict.items():
            value_suffixes = [value.removeprefix(base_pattern) for value in values]
            processed_string = base_pattern + ', '.join(value_suffixes)
            self.reserve_list.append(processed_string)
        self.result_dict = {}

    def _recursive_extract(self, pattern_parts: List[str], lines: List[str], i: int, added_to_reserve: bool):
        if i > len(pattern_parts):
            return

        # Create the current pattern based on the first i parts
        current_pattern = ''.join(pattern_parts[:i])
        current_pattern_escaped = re.escape(current_pattern)

        # Split lines into matching and non-matching with the current pattern
        matched_lines = [line for line in lines if re.match(current_pattern_escaped, line)]

        if matched_lines:
            # Add matching lines to the result dictionary
            self.result_dict[current_pattern] = matched_lines

            # Remove matching lines from the overall list of lines
            for line in matched_lines:
                lines.remove(line)

            # Recursively call the function with an increased number of parts
            self._recursive_extract(pattern_parts, matched_lines, i + 1, added_to_reserve)
        else:
            # Add the entire pattern as a string to the reserve_list if this is the first miss
            if not added_to_reserve:
                self.reserve_list.append(''.join(pattern_parts))
                added_to_reserve = True
            # Continue recursively to explore further parts of the pattern
            self._recursive_extract(pattern_parts, lines, i + 1, added_to_reserve)

    def get_compressed_output(self):
        return ' ' + self.reserve_list[0] + '\n ' + '\n '.join(self.reserve_list[1:])
