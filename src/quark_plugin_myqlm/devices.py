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
import importlib

from quark.core import Core, Result, Data
from quark.interface_types import Other, SampleDistribution, Circuit

from qat.core import Circuit as QaptivaCircuit
from qat.core import Job
from qat.qpus import get_default_qpu

@dataclass
class MyQLMDigitalQPU(Core):
    """
    Provides access to myQLM QPUs. There are several concrete implementations available which can be selected 
    by specifiying the constructor argument 'qpu_class_name'. Currently supported values for 'qpu_class_name' are
       + PyLinalg
       + CLinalg
    If no qpu_class_name is provided the myQLM method get_default_qpu will be used to create the QPU instance.
    
    The constructor argument 'nbshots' allows the specification of the number of shots as positive integer. 
    If 'nbshots' is specified the probability distribution for the states will be estimated from the corresponding 
    relative counts. If 'nbshots' is not specified or set to 0 the probability distribution will be calculated exactly.

    See also the myQLM Documentation.
    """

    qpu_class_name: str = None
    nbshots: int = None

    def getQPU(self):
        if self.qpu_class_name is None:
            return get_default_qpu()
        module_name = "qat.qpus"
        module = importlib.__import__(module_name, fromlist=(self.qpu_class_name,))
        return getattr(module, self.qpu_class_name)()

    def preprocess(self, data: Circuit|Other[QaptivaCircuit]) -> Result:
        """
        Executes the given circuit on the selected myQLM QPU.
        return Data(Other(qat.core.Job))
        """
        if isinstance(data, Other):
            assert isinstance(data.data, QaptivaCircuit)
            circ: QaptivaCircuit = data.data
            job = circ.to_job(nbshots=self.nbshots) if self.nbshots is not None else circ.to_job()
        elif isinstance(data, Circuit):
            from qat.interop.openqasm import OqasmParser
            parser = OqasmParser()
            adapted_circ = data.as_qasm_string().replace(
                "qubit", "qreg").replace("bit", "creg")
            circ = parser.compile(adapted_circ)
            job = circ.to_job(
                nbshots=self.nbshots, job_type="SAMPLE") if self.nbshots is not None else circ.to_job()
        else:
            raise ValueError(f"unsupported type {type(data)}")
        self.nbqbits = circ.nbqbits
        self.job = job
        return Data(Other(job))

    def postprocess(self, input_data: any) -> Result:
        """
        return Data(SampleDistribution)
        """
        # framework will probably be changed to use the preprocess output as postprocess input for leaf modules.
        if input_data is None:
            job = self.job
        else:
            assert isinstance(job, Job )
        result = self.getQPU().submit(self.job)
        return Data(
            SampleDistribution.from_list([(sample.state.bitstring, sample.probability) for sample in result],
                                         nbshots = 0 if self.nbshots is None else self.nbshots)
        )