# DionexCal

This script will take in the measured peak areas for the desired cations or anions in the input csv file, and use the known concentrations of standards in the standards file to perform a linear calibration to calculate the concentrations of the desired ions in the unknown samples. The resulting concentrations are output to a csv file. Plots are also produced to visualise the linearity of the calibration line.

### Required packages

- `numpy`
- `scipy`
- `pandas`
- `plotly`
- `kaleido`

These can all be installed in your Python environment by running the terminal command `pip install numpy scipy pandas plotly kaleido`.

### Input file

This should be in csv format and end in `_in.csv`. Examples for cations and anions are provided. Ensure that the names of the ions and standards you provide are consistent with those in the standards file and in the `species` configuration option.

Required columns:

| Column name  | Contents                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| `Name`       | Name of standard or sample                                                                                   |
| `Type`       | `Standard` or `Unknown`                                                                                      |
| `<ion> Area` | Measured peak areas. Replace `<ion>` with the desired ion name. Add more columns for as many ions as needed. |

### Standards file

This should also be in csv format and have consistent names of ions and standards with the input file.

Required columns:
| Column name | Contents |
| ------------ | ---------- |
| `Name` | Name of standard |
| `<ion>` | Concentration of ion in mol/dm³. Replace `<ion>` with the desired ion name. Add more columns for as many ions as needed. |

### Output files

These will have the same name as the input file, except ending in `_out.csv`.

Output columns:
| Column name | Contents |
| ------------ | ---------- |
| `Name` | Name of sample |
| `<ion>` | Concentration of ion, corrected for the given dilution factor, in mol/dm³ (or whatever unit the standards were specified in).|

Plots will also be exported in vector format to `calibration_plots.pdf`.

### Configuration

This is done by editing the first section of the script.

| Variable    | Value                                                                                                                                                                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `file_name` | Path to input file (not including the `_in.csv` ending)                                                                                                                                                                                                                               |
| `std_file`  | Path to standards file (this time include the `.csv`)                                                                                                                                                                                                                                 |
| `cal_mode`  | `'all'`: Calibrate based on a linear regression of all standards together. `'interpolated'`: Creates a new regression for each time the standards are measured, then interpolates between these to account for measurement drift (usually insignificant, but check the graphs first!) |
| `dilution`  | Number of times the sample has been diluted. For example, if I added 0.1 ml of sample to 0.9 ml of water, the dilution factor would be 10.                                                                                                                                            |
| `species`   | List of the ion names to be calibrated. Make sure they are consistent with those in the input file! There are ready-made lists to choose from with common varieties of ions.                                                                                                          |

### Running the script

Make sure the output file is not open while running the script.

The script can be run inside (a) Jupyter notebook cell(s), or by calling the following terminal command whilst your Python environment is activated and you are navigated to the folder containing the script:

`python dionex_calibration.py`

If you are running from the terminal, the script will try to open a browser tab to display an interactive version of the calibration plots. Once the script has finished, it will print `Calibration complete!`
