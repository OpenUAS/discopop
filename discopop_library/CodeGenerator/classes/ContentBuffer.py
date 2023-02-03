# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.

import copy
from typing import List

from discopop_library.CodeGenerator.classes.Enums import PragmaPosition
from discopop_library.CodeGenerator.classes.Line import Line
from discopop_library.CodeGenerator.classes.Pragma import Pragma


class ContentBuffer(object):
    lines: List[Line]
    max_line_num: int  # used to determine width of padding
    file_id: int
    next_free_region_id = 0

    def __init__(self, file_id: int, source_code_path: str, tab_width: int = 4):
        self.file_id = file_id
        self.lines = []
        self.max_line_num = 0
        # load source code
        with open(source_code_path, "r") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                idx = idx + 1  # start with line number 1
                self.max_line_num = idx
                line_obj = Line(idx, line_num=idx, content=line)
                self.lines.append(line_obj)

    def print_lines(self):
        for line in self.lines:
            print(line)

    def __get_next_free_region_id(self) -> int:
        buffer = self.next_free_region_id
        self.next_free_region_id += 1
        return buffer

    def get_modified_source_code(self) -> str:
        result = ""
        for line in self.lines:
            if not line.content.endswith("\n"):
                line.content += "\n"
            result += line.content
        return result

    def append_line_before(self, parent_line_num: int, line: Line):
        """Appends line before the specified parent_line_num"""
        for idx, potential_parent_line in enumerate(self.lines):
            if potential_parent_line.line_num == parent_line_num:
                self.lines.insert(idx, line)
                return

    def append_line_after(self, parent_line_num: int, line: Line):
        """Appends line after the specified parent_line_num"""
        for idx, potential_parent_line in enumerate(self.lines):
            if potential_parent_line.line_num == parent_line_num:
                if idx + 1 < len(self.lines):
                    self.lines.insert(idx + 1, line)
                else:
                    self.lines.append(line)
                return

    def add_pragma(self, pragma: Pragma, parent_regions: List[int]):
        """insert pragma into the maintained list of source code lines"""
        if pragma.start_line is None or pragma.end_line is None:
            raise ValueError(
                "Unsupported start or end line: ", pragma.start_line, "-", pragma.end_line
            )
        if pragma.file_id is None:
            raise ValueError("Unsupported file_id: ", pragma.file_id)
        if pragma.file_id != self.file_id:
            return  # incorrect target file, ignore the pragma

        # construct line
        pragma_line = Line(pragma.start_line)
        pragma_line.content = pragma.pragma_str
        pragma_line.belongs_to_regions = copy.deepcopy(parent_regions)
        # create new region if necessary
        if len(pragma.children) > 0:
            region_id = self.__get_next_free_region_id()
            pragma_line.owns_region = region_id
            pragma_line.belongs_to_regions.append(region_id)

        if pragma.pragma_position == PragmaPosition.BEFORE_START:
            self.append_line_before(pragma.start_line, pragma_line)
        elif pragma.pragma_position == PragmaPosition.AFTER_START:
            self.append_line_after(pragma.start_line, pragma_line)
        elif pragma.pragma_position == PragmaPosition.BEFORE_END:
            self.append_line_before(pragma.end_line, pragma_line)
        elif pragma.pragma_position == PragmaPosition.AFTER_END:
            self.append_line_after(pragma.end_line, pragma_line)
        else:
            raise ValueError("Unsupported pragma position: ", pragma.pragma_position)

        # update belonging information of contained lines
        tmp_start_line = (
            pragma.start_line
            if pragma.pragma_position == PragmaPosition.BEFORE_START
            else pragma.start_line + 1
        )
        tmp_end_line = pragma.end_line + 1
        for line_num in range(tmp_start_line, tmp_end_line):
            for line in self.lines:
                if line.line_num == line_num:
                    line.belongs_to_regions += [
                        n
                        for n in pragma_line.belongs_to_regions
                        if n not in line.belongs_to_regions
                    ]

        # append children to lines (mark as contained in region)
        for child_pragma in pragma.children:
            self.add_pragma(child_pragma, pragma_line.belongs_to_regions)
