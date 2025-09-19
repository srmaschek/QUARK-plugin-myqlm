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
