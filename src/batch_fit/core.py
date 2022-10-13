from pathlib import Path

from scaffoldfitter.fitter import Fitter
from scaffoldfitter.fitterstepalign import FitterStepAlign
from scaffoldfitter.fitterstepconfig import FitterStepConfig
from scaffoldfitter.fitterstepfit import FitterStepFit


class BatchFit:
    """
    Module to use Scaffold Fitter library without using GUI. This module is specifically designed for running batch
    fitting jobs.
    """

    def __init__(self, model_file_path: Path, data_file_path: Path, output_dir: Path):
        self._fitter = Fitter(str(model_file_path), str(data_file_path))
        self._output_dir = str(output_dir)
        self._filename_stem = model_file_path.stem

        self.__initialize()

    def __initialize(self):
        self._fitter.load()
        self.add_config(central=True)
        self.add_align(groups=True)  # init alignment
        self.add_config(groups=None, central=False)

    def add_config(self, groups=None, central: bool = False):
        config_step = FitterStepConfig()
        config_step.setGroupCentralProjection(groupName=groups, centralProjection=central)
        self._fitter.addFitterStep(config_step)
        self.run(step=config_step)

    def add_align(self, groups=True):
        align_step = FitterStepAlign()
        align_step.setAlignGroups(groups)
        self._fitter.addFitterStep(align_step)
        self.run(step=align_step)

    # TODO!!:
    def add_fit(self, groups=None, weight: float = 0., strain: float = 0., curvature: float = 0., n_it: int = 1):
        fitter_step = FitterStepFit()
        fitter_step.setGroupDataWeight(groupName=groups, weight=weight)
        fitter_step.setGroupStrainPenalty(groupName=groups, strainPenalty=[strain])
        fitter_step.setGroupCurvaturePenalty(groupName=groups, curvaturePenalty=[curvature])
        fitter_step.setNumberOfIterations(numberOfIterations=n_it)
        self._fitter.addFitterStep(fitter_step)
        self.run(step=fitter_step)

    def run(self, step=None):
        self._fitter.run(endStep=step, modelFileNameStem=str(self._output_dir))
