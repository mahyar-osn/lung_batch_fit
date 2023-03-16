from pathlib import Path

from scaffoldfitter.fitter import Fitter
from scaffoldfitter.fitterjson import decodeJSONFitterSteps


class BatchFit:
    """
    Module to use Scaffold Fitter library without using GUI. This module is specifically designed for running batch
    fitting jobs.
    """

    def __init__(self, model_file_path: Path, data_file_path: Path, output_dir: Path):
        self._fitter = Fitter(str(model_file_path), str(data_file_path))
        self._filename_stem = model_file_path.stem
        self._output_dir = str(output_dir)
        self._fitter.load()

    def get_group_rms(self):
        return self._fitter.getGroupRMS()

    def get_total_rms(self):
        return self._fitter.getDataRMSAndMaximumProjectionError()

    def load_fit_settings(self, settings_file: Path):
        if settings_file.is_file():
            with open(settings_file, "r") as f:
                self._fitter.decodeSettingsJSON(f.read(), decodeJSONFitterSteps)

    def run(self, step=None):
        self._fitter.run(endStep=step, modelFileNameStem=str(self._output_dir))
