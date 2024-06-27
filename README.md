# Setup

Simply install the plugin in your environment. Until a version is published to PyPI, use:
```
pip install git+https://github.com/b12consulting/hydra_paired_sweeper.git
```

# Usage

Using this sweeper in Hydra multirun mode will sweep over multiple parameters in parallel,
such as a python `zip` would:

```
python your_app.py hydra/sweeper=paired --multirun paramA=10,50 paramB=2,3 paramC=true
```

Will create two runs, one with `paramA=10 paramB=2 paramC=true` and the other with `paramA=50 paramB=3 paramC=true`.