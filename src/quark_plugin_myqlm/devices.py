from dataclasses import dataclass
import importlib

from quark.core import Core, Result, Data
from quark.interface_types import Other, SampleDistribution

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
    relative counts otherwise the probability distribution will be calculated exactly.

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

    def preprocess(self, data: Other[QaptivaCircuit]) -> Result:
        """
        Executes the given circuit on the selected myQLM QPU.
        return Data(Other(qat.core.Job))
        """
        assert (isinstance(data, Other) and isinstance(data.data, QaptivaCircuit))
        if isinstance(data, Other):
            circ: QaptivaCircuit = data.data
            if self.nbshots is not None:
                job = circ.to_job(nbshots=self.nbshots)
            else:
                job = circ.to_job()
        else:
            raise NotImplementedError
        self.job = job
        return Data(Other(job))

    def postprocess(self, input_data: any) -> Result:
        """
        return Data(ProbabilityDistribution)
        """
        # framework will probably be changed to use the preprocess output as postprocess input for leaf modules.
        if input_data is None:
            job = self.job
        else:
            assert isinstance(job, Job )
        result = self.getQPU().submit(self.job)

        return Data(
            SampleDistribution.from_list([(sample.state.bitstring, sample.probability) for sample in result])
        )