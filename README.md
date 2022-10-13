Batch fitting of lung subjects
-----------------------

This repo contains necessary codes to run a batch fitting process for annotated lung data using ScaffoldMaker
and OpenCMISS-Zinc 

### Requirements
* Python >= 3.6

### Installation

Inside the top level directory (i.e., `lung_batch_fit`) do:

(NOTE: since this installation uses the newly added `pyproject.toml` BETA, you need to first update your `pip` to 
its latest version).

```console
pip install -e .
```
The output of this command should be something like:

```console
Obtaining file:///D:/12-labours/codes/python-packages/batch_fit
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Installing backend dependencies ... done
  Preparing editable metadata (pyproject.toml) ... done
Collecting scaffoldmaker
  Downloading scaffoldmaker-0.7.1.tar.gz (555 kB)
     ---------------------------------------- 555.2/555.2 KB 11.6 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
Collecting hydra-core==1.2.0
  Using cached hydra_core-1.2.0-py3-none-any.whl (151 kB)
Collecting opencmiss.zinc>=3.8.0
  Using cached opencmiss.zinc-3.9.0-cp39-cp39-win_amd64.whl (5.9 MB)
Collecting antlr4-python3-runtime==4.9.*
  Using cached antlr4_python3_runtime-4.9.3-py3-none-any.whl
Collecting omegaconf~=2.2
  Downloading omegaconf-2.2.3-py3-none-any.whl (79 kB)
     ---------------------------------------- 79.3/79.3 KB 4.3 MB/s eta 0:00:00
Collecting packaging
  Using cached packaging-21.3-py3-none-any.whl (40 kB)
Collecting opencmiss.maths
  Downloading opencmiss.maths-0.1.1.tar.gz (13 kB)
  Preparing metadata (setup.py) ... done
Collecting opencmiss.utils>=0.3
  Downloading opencmiss.utils-0.4.1.tar.gz (24 kB)
  Preparing metadata (setup.py) ... done
Collecting scipy
  Downloading scipy-1.9.2-cp39-cp39-win_amd64.whl (40.1 MB)
     ---------------------------------------- 40.1/40.1 MB 11.7 MB/s eta 0:00:00
Collecting numpy
  Downloading numpy-1.23.4-cp39-cp39-win_amd64.whl (14.7 MB)
     ---------------------------------------- 14.7/14.7 MB 12.8 MB/s eta 0:00:00
Collecting PyYAML>=5.1.0
  Using cached PyYAML-6.0-cp39-cp39-win_amd64.whl (151 kB)
Collecting pyparsing!=3.0.5,>=2.0.2
  Using cached pyparsing-3.0.9-py3-none-any.whl (98 kB)
Building wheels for collected packages: batch-fit, scaffoldmaker, opencmiss.utils, opencmiss.maths
  Building editable for batch-fit (pyproject.toml) ... done
  Created wheel for batch-fit: filename=batch_fit-0.0.1-0.editable-py3-none-any.whl size=1293 sha256=79afac9497fd0c62cfbcdc2860c51e8879e748047a9e17de191633d452179742
  Stored in directory: C:\Users\mosa004\AppData\Local\Temp\pip-ephem-wheel-cache-1a15zp5_\wheels\a7\ec\c7\eeb50699aaaefa483e920cfabd23e82a02d63d3259e80d2dab
  Building wheel for scaffoldmaker (setup.py) ... done
  Created wheel for scaffoldmaker: filename=scaffoldmaker-0.7.1-py3-none-any.whl size=607740 sha256=073925f7a2f06c3520d5c9f8bde4e2f45a4cf838185770e64ec5f1db09af7138
  Stored in directory: c:\users\mosa004\appdata\local\pip\cache\wheels\d7\bf\de\ec4df3a7c9fa76447ca61b8595c027ff761c90230dc74dee9b
  Building wheel for opencmiss.utils (setup.py) ... done
  Created wheel for opencmiss.utils: filename=opencmiss.utils-0.4.1-py3-none-any.whl size=25029 sha256=c767eb7154ccc3c00ae9361c66b6d73a5a40320b3168fa945b18d11b51272e45
  Stored in directory: c:\users\mosa004\appdata\local\pip\cache\wheels\f7\29\53\1c4b134640aa694c43ae64375510e0f9bb7e5dd4068afd10e1
  Building wheel for opencmiss.maths (setup.py) ... done
  Created wheel for opencmiss.maths: filename=opencmiss.maths-0.1.1-py3-none-any.whl size=12691 sha256=15c6f90f6e4e9792ec1bf2cdd7c84e277a0319a8e4fdba932d561bf17daa3f07
  Stored in directory: c:\users\mosa004\appdata\local\pip\cache\wheels\be\1d\cb\6c57e36deb6de2d62c9799f8c0dbc7a66a6b5d6a12d01135ff
Successfully built batch-fit scaffoldmaker opencmiss.utils opencmiss.maths
Installing collected packages: opencmiss.zinc, opencmiss.maths, antlr4-python3-runtime, PyYAML, pyparsing, opencmiss.utils, numpy, scipy, packaging, omegaconf, scaffoldmaker, hydra-core, batch-fit
Successfully installed PyYAML-6.0 antlr4-python3-runtime-4.9.3 batch-fit-0.0.1 hydra-core-1.2.0 numpy-1.23.4 omegaconf-2.2.3 opencmiss.maths-0.1.1 opencmiss.utils-0.4.1 opencmiss.zinc-3.9.0 packaging-21.3 pyparsing-3.0.9 scaffoldmaker-0.7.1 scipy-1.9.2
```

### Usage

You can easily run the `python main.py` inside the top level directory. This script uses the `fit.yaml` file inside the
`configs` directory. Ensure that you set model and data input files in the correct fields. The `output_path` in the
config is optional. By default, the code saves all logs and fit related files inside the `output` directory which is
automatically created and timestamped each time you run the script.

In the config file, the fit parameters are set for the strain and curvature penalties. These values can be changed