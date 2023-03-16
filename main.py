import os
import hydra
from omegaconf.dictconfig import DictConfig

from pathlib import Path
from loguru import logger

import pandas as pd

from batch_fit import BatchFit
from batch_fit.data_combiner import Point, read_single_group, write_ex


@hydra.main(config_path="configs", config_name="fit.yaml")
def main(cfg: DictConfig):
    # iterate through subjects' directories

    right_lung_groups = cfg.groups_right_lung
    scaffold_path = Path(cfg.scaffold_path)
    setting_files_path = Path(__file__).parent / 'fit_settings'

    if Path(cfg.root_directory).exists():

        for subject_path in Path(cfg.root_directory).iterdir():

            subject_rms = dict()

            logger.info(f'-------')
            logger.info(f'Subject {subject_path.stem}')

            output_ex = subject_path / f'{subject_path.stem}_combined_lung_data.ex'

            # first combine all .exdata files into one single .ex file
            if subject_path.is_dir():
                if not output_ex.exists():
                    single_data = dict()

                    logger.info(f'Generating EX file')

                    for ex_file in subject_path.glob("*.exdata"):
                        points = list()
                        file_name = ex_file.stem
                        if file_name in right_lung_groups.keys():
                            group_name = right_lung_groups[file_name]
                            data = read_single_group(str(ex_file))
                            for p in data:
                                points.append(_create_point(p))
                            single_data[group_name] = points

                    write_ex(output_ex, single_data)

            # now fit the subject
            # create an output directory using Hydra to store all the fitting files
            hydra_cfg = hydra.core.hydra_config.HydraConfig.get()
            current_hydra_output_dir = Path(hydra_cfg.runtime.output_dir)
            output_fit_dir = current_hydra_output_dir / 'fit_files' / f'{subject_path.stem}'
            output_fit_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f'Fitting')

            # define the fitter
            if scaffold_path.is_file() and output_ex.is_file():
                batch_fit = BatchFit(scaffold_path, output_ex, output_fit_dir / 'fit_')
                setting_id = cfg.fit_setting
                setting_file = setting_files_path / f'settings_{setting_id}.json'
                batch_fit.load_fit_settings(setting_file)
                batch_fit.run()

                subject_rms[subject_path.stem] = batch_fit.get_group_rms()
                subject_rms[subject_path.stem].update({'total': batch_fit.get_total_rms()[0]})

                output_csv_path = Path(__file__).parent / Path(
                    cfg.rms_output_directory) / f'{Path(cfg.rms_output_file_name)}.csv'

                df = pd.DataFrame(subject_rms)

                if os.path.isfile(output_csv_path):
                    existing_df = pd.read_csv(output_csv_path, index_col=0)
                    combined_df = pd.concat([existing_df, df[subject_path.name]], axis=1)

                else:
                    combined_df = df

                combined_df.to_csv(output_csv_path)


def _create_point(pts):
    return Point(float(pts[0]),
                 float(pts[1]),
                 float(pts[2]))


if __name__ == '__main__':
    main()
