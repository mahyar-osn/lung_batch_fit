import hydra
from omegaconf.dictconfig import DictConfig

from pathlib import Path

from batch_fit import BatchFit


@hydra.main(config_path="configs", config_name="fit.yaml")
def main(cfg: DictConfig):
    for input_zinc_model_file, input_zinc_data_file in zip(cfg.inputs.model_file_name,
                                                           cfg.inputs.data_file_name):
        input_zinc_model_file = Path(input_zinc_model_file)
        input_zinc_data_file = Path(input_zinc_data_file)
        if cfg.output_path is None:
            hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
            current_hydra_output_dir = Path(hydra_cfg.runtime.output_dir)
            output_fit_dir = current_hydra_output_dir / 'fit_files' / f'{input_zinc_data_file.stem}'
            output_fit_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_fit_dir = Path(cfg.output_path)

        batch_fit = BatchFit(input_zinc_model_file, input_zinc_data_file, output_fit_dir / 'fit_')

        for strain, curvature in zip(cfg.params.strain, cfg.params.curvature):
            batch_fit.add_fit(strain=strain,
                              curvature=curvature)


if __name__ == '__main__':
    main()
