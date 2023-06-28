# AMASS-Annotation-Unifier
Unify text-motion datasets (like BABEL, HumanML3D, KIT-ML) into a common motion-text representation.

All these datasets have a lot of common source of motions, but the process are usually different:
- KIT-ML use [Master Motor Map](https://mmm.humanoids.kit.edu)
- HumanML3D extract and transform joints from SMPL
- BABEL use raw SMPL pose parameters

The goal of this repo is to create a common reprensentation of the annotations for these datasets. The output of each of these scripts is a json file, like this one (for HumanML3D):
```json
{
  "000000": {
    "path": "KIT/3/kick_high_left02_poses",
    "duration": 5.82,
    "annotations": [
      {
        "seg_id": "000000_0",
        "text": "a man kicks something or someone with his left leg.",
        "start": 0.0,
        "end": 5.82
      },
      ...
```
where we get the original path from AMASS (``SMPL+H G`` version), the duration of the motion, and the annotations (ID, text, start, end).


### Installation
Make sure to have these package in your python3 environment:

```bash
pip install pandas
pip install tqdm
pip install numpy
pip install orjson
```

For AMASS (see below), please download the ``SMPL+H G`` version.

## Dataset processes
### HumanMl3D

1. Download and put [AMASS](https://amass.is.tue.mpg.de/download.php) motions into ``datasets/AMASS/``.
2. Clone the [HumanML3D](https://github.com/EricGuo5513/HumanML3D) repo to ``datasets/HumanML3D/`` and unzip the ``texts.zip`` file.
3. Execute the cmd:

```bash
python humanml3d.py
```

### KITML

1. Download and put [AMASS](https://amass.is.tue.mpg.de/download.php) motions into ``datasets/AMASS/``.
2. Download [KIT-ML])(https://motion-annotation.humanoids.kit.edu/dataset/) motions, and unzip in the folder ``datasets/kit-mocap/``.
3. Execute the cmd:

```bash
python kitml.py
```

The script ``kitml_text_preprocess.py`` is made to produce the files ``kitml_process/amass-path2kitml.json`` and ``kitml_process/kitml_not_found_amass.json``. It is already executed so you don't need to.


### BABEL

1. Download and put [AMASS](https://amass.is.tue.mpg.de/download.php) motions into ``datasets/AMASS/``.
2. Download the [BABEL](https://teach.is.tue.mpg.de/download.php) annotations from TEACH into ``datasets/babel-teach/``.
3. Execute the cmd:

```bash
python babel.py
```

## Merging the datasets

To use all datasets at the same time, we can use the cmd:

```bash
python merge.py
```

It will create a json file (in ``outputs/babel_humanml3d_kitml.json``) structured in this way:
```json
{
 "CMU/75/75_18_poses": {
    "duration": 5.05,
    "annotations": [
      {
        "seg_id": "babel_04565_seq_0",
        "babel_id": "67ed4f2f-ab40-4e64-98e5-d6185a9e8df4",
        "text": "sit",
        "start": 0.0,
        "end": 5.05
      },
      {
        "seg_id": "babel_04565_seg_4",
        "babel_id": "bb06e44a-641f-4dc3-a7fb-f2a2259ec095",
        "text": "sit",
        "start": 1.69,
        "end": 3.252
      },
      {
        "seg_id": "humanml3d_007848_2",
        "text": "a person sits down on an object, then stands back up.",
        "start": 0.0,
        "end": 5.05
      },
      {
        "seg_id": "kitml_02926_0",
        "text": "A person sits down on a chair behind him and stands up again.",
        "start": 0.0,
        "end": 5.05
      },
      ...
```


## Credits
For all the datasets, be sure to read and follow their license agreements, and cite them accordingly.
If you find this code useful in your research, you may cite this paper:

```bibtex
@article{petrovich23tmr,
    title     = {{TMR}: Text-to-Motion Retrieval Using Contrastive {3D} Human Motion Synthesis},
    author    = {Petrovich, Mathis and Black, Michael J. and Varol, G{\"u}l},
    journal   = {arXiv preprint},
    year      = {2023}
}
```