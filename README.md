## Installation

Create and activate the Conda environment:

```bash
conda create -n gen python=3.8 -y
conda activate gen
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

## Training

To start training, run:

```bash
python main.py
```

By default, the training logs and model checkpoints are saved in the `output/` directory.

To specify a custom output directory:

```bash
python main.py --output_dir outputs
```
