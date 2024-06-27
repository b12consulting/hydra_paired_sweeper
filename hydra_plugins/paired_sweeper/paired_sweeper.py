from dataclasses import dataclass

import logging
from pathlib import Path
from typing import Any

from hydra.plugins.launcher import Launcher
from hydra.plugins.sweeper import Sweeper
from hydra.core.config_store import ConfigStore
from hydra.core.plugins import Plugins
from hydra.core.override_parser.overrides_parser import OverridesParser
from hydra.types import HydraContext
from hydra.types import TaskFunction
from omegaconf import DictConfig, OmegaConf

log = logging.getLogger(__name__)


@dataclass
class LauncherConfig:
    _target_: str = "hydra_plugins.paired_sweeper.paired_sweeper.PairedSweeper"
    params: dict[str, str] | None = None


ConfigStore.instance().store(group="hydra/sweeper", name="paired", node=LauncherConfig)


class PairedSweeper(Sweeper):
    def __init__(self, params: dict[str, str] | None = None):
        self.params = params or {}
        self.config: DictConfig | None = None
        self.launcher: Launcher | None = None
        self.hydra_context: HydraContext | None = None

    def setup(
        self,
        *,
        hydra_context: HydraContext,
        task_function: TaskFunction,
        config: DictConfig,
    ) -> None:
        self.config = config
        self.launcher = Plugins.instance().instantiate_launcher(
            hydra_context=hydra_context, task_function=task_function, config=config
        )
        self.hydra_context = hydra_context

    def _parse_config(self) -> list[str]:
        params_conf = []
        for k, v in self.params.items():
            params_conf.append(f"{k}={v}")
        return params_conf

    def sweep(self, arguments: list[str]) -> Any:
        assert self.config is not None
        assert self.launcher is not None

        log.info(f"Sweep output dir : {self.config.hydra.sweep.dir}")

        sweep_dir = Path(self.config.hydra.sweep.dir)
        sweep_dir.mkdir(parents=True, exist_ok=True)
        OmegaConf.save(self.config, sweep_dir / "multirun.yaml")

        arguments = self._parse_config() + arguments

        parser = OverridesParser.create()
        parsed = parser.parse_overrides(arguments)

        # this holds the parameters that are being swept synchronously
        sweeper_overrides = []
        # this holds the overrides that are not being swept
        single_overrides = []

        for override in parsed:
            if override.is_sweep_override():
                sweep_choices = override.sweep_string_iterator()
                key = override.get_key_element()
                sweep = [f"{key}={val}" for val in sweep_choices]
                if sweeper_overrides and len(sweeper_overrides[0]) != len(sweep):
                    raise ValueError(
                        "All swept parameters must sweep the same number of values"
                    )
                sweeper_overrides.append(sweep)
            else:
                key = override.get_key_element()
                value = override.get_value_element_as_str()
                single_overrides.append(f"{key}={value}")

        overrides = [list(z) + single_overrides for z in zip(*sweeper_overrides)]

        initial_job_idx = 0
        self.validate_batch_is_legal(overrides)
        results = self.launcher.launch(overrides, initial_job_idx=initial_job_idx)

        return results
