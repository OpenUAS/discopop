# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.
from typing import List

from .PETGraphX import DummyNode, LoopNode, PETGraphX, NodeType, EdgeType
from .pattern_detectors.do_all_detector import run_detection as detect_do_all, DoAllInfo
from .pattern_detectors.geometric_decomposition_detector import run_detection as detect_gd, GDInfo
from .pattern_detectors.pipeline_detector import run_detection as detect_pipeline, PipelineInfo
from .pattern_detectors.reduction_detector import run_detection as detect_reduction, ReductionInfo
from discopop_explorer.pattern_detectors.task_parallelism.task_parallelism_detector import (
    build_preprocessed_graph_and_run_detection as detect_tp,
)
from .pattern_detectors.PatternInfo import PatternInfo
from .variable import Variable


class DetectionResult(object):
    pet: PETGraphX
    reduction: List[ReductionInfo]
    do_all: List[DoAllInfo]
    pipeline: List[PipelineInfo]
    geometric_decomposition: List[GDInfo]
    task: List[PatternInfo]

    def __init__(self, pet: PETGraphX):
        self.pet = pet
        pass

    def __str__(self):
        result_str = ""
        for v in self.__dict__.values():
            if type(v) == PETGraphX:
                continue
            value_str = "\n\n\n"
            for entry in v:
                try:
                    value_str += str(entry) + "\n\n"
                except NotImplementedError:
                    value_str += entry.to_string(self.pet) + "\n\n"
            result_str += value_str
        return result_str


class PatternDetectorX(object):
    pet: PETGraphX

    def __init__(self, pet_graph: PETGraphX) -> None:
        """This class runs detection algorithms on CU graph

        :param pet_graph: CU graph
        """
        self.pet = pet_graph

    def __merge(self, loop_type: bool, remove_dummies: bool):
        """Removes dummy nodes

        :param loop_type: loops only
        :param remove_dummies: remove dummy nodes
        """
        dummies_to_remove = set()
        for node in self.pet.all_nodes():
            if not loop_type or isinstance(node, LoopNode):
                if remove_dummies and isinstance(node, DummyNode):
                    continue
                for s, t, e in self.pet.out_edges(node.id, [EdgeType.CHILD, EdgeType.CALLSNODE]):
                    if remove_dummies and isinstance(self.pet.node_at(t), DummyNode):
                        dummies_to_remove.add(t)

        for n in dummies_to_remove:
            self.pet.g.remove_node(n)

    def detect_patterns(
        self,
        cu_dict,
        dependencies,
        loop_data,
        reduction_vars,
        file_mapping,
        cu_inst_result_file,
        llvm_cxxfilt_path,
        discopop_build_path,
        enable_task_pattern,
    ):
        """Runs pattern discovery on the CU graph"""
        self.__merge(False, True)
        self.pet.calculateFunctionMetadata()
        res = DetectionResult(self.pet)

        # reduction before doall!
        res.reduction = detect_reduction(self.pet)
        print("REDUCTION DONE.")
        res.do_all = detect_do_all(self.pet)
        print("DOALL DONE.")
        res.pipeline = detect_pipeline(self.pet)
        print("PIPELINE DONE.")
        res.geometric_decomposition = detect_gd(self.pet)
        print("GEO. DEC. DONE.")

        # check if task pattern should be enabled
        if enable_task_pattern:
            res.task = detect_tp(
                cu_dict,
                dependencies,
                loop_data,
                reduction_vars,
                file_mapping,
                cu_inst_result_file,
                llvm_cxxfilt_path,
                discopop_build_path,
            )
        return res
