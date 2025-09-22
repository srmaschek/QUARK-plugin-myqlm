# Copyright (c) 2025 Science + Computing AG / Eviden SE (Atos Group)
#
# This file is part of the QUARK benchmarking framework.
# It provides a wrapper for myQLM (https://myqlm.github.io/).
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#
# Contact: stefan-raimund.maschek@eviden.com


from dataclasses import dataclass

from quark.core import Core, Result, Data
from quark.interface_types import Other, SampleDistribution

from qat.lang.AQASM import Program, H, CNOT

@dataclass
class GHZtoQaptivaCircuit(Core):

    def preprocess(self, data):
        problem:dict = data.data
        my_program = Program()
        qbits_reg = my_program.qalloc(problem.get("size"))
        H(qbits_reg[0])
        for i in range(problem.get("size")-1):
            CNOT(qbits_reg[i], qbits_reg[i+1])
        circ = my_program.to_circ()
        return Data(Other(circ))
    
    def postprocess(self, data: SampleDistribution):
        assert isinstance(data, SampleDistribution)
        return Data(data)
