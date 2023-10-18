# %% Configuration

file_name = "Example_Cations"  # Beginning of the input csv file name. Assumes it is followed by '_in.csv'

std_file = "Example_Standards.csv"

cal_mode = "all"  # 'all': Calibrate based on a linear regression of all standards
# 'interpolated': Creates a new regression for each time the standards are measured, then inerpolates between these to account for measurement drift (usually insignificant, but check the graphs)

dilution = 1 # Number of times the solution has been diluted.

# Example lists of ions to choose from
all_cations = ["Ca", "Mg", "Na", "K", "NH4"]
all_anions = ["Cl", "F", "SO4", "NO3"]
SW_cations = ["Ca", "Mg", "Na", "K"]
SW_anions = ["Cl", "SO4"]

species = SW_cations  # List of measured species to calibrate for.

# %%
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit

from plotly_default import go
from plotly.subplots import make_subplots
import plotly.express as px

pd.options.mode.chained_assignment = None

# %% Read in data

df = pd.read_csv(f"{file_name}_in.csv")
standards = pd.read_csv(std_file)

# Keep only necessary columns
area_cols = [f"{s} Area" for s in species]
df = df[["Name", "Type"] + area_cols]

# Remove rows that are all NaN
df.dropna(how="all", inplace=True)

# Replace 'n.a.' with 0
df[area_cols] = df[area_cols].replace("n.a.", 0).astype(float)

# Split df into groups based on when the Type column changes
# (cumulative sum of instances when Type is different to preceding item)
df["Group"] = (df["Type"] != df["Type"].shift()).cumsum()

# Add column to keep track of measurement number
df["Measurement"] = df.index

df
# %% Split up dataframe
sample_df = df.query("Type == 'Unknown'")
standard_df = df.query("Type == 'Standard'")

# Add true concentrations to standard_df
std_df = standard_df.merge(standards, how="left", on="Name")

std_groups = std_df.groupby("Group")

# %% perform calibration
reg_dict = {}


def y_mx(x, m):
    return m * x


def y_mx_c(x, m, c):
    return m * x + c


for s in species:
    if cal_mode == "all":
        # Fits standards to conc = m * area and saves m in the regression dictionary
        reg_dict[s] = curve_fit(
            y_mx, xdata=list(std_df[f"{s} Area"]), ydata=list(std_df[s])
        )[0][0]

        # Corrects samples based on the same regression
        sample_df.loc[:, s] = sample_df.loc[:, f"{s} Area"] * reg_dict[s]

    elif cal_mode == "interpolated":
        reg_dict[s] = []
        av_runs = []

        for _, std_group in std_groups:
            # Calculate regression for each standard
            reg_dict[s].append(
                curve_fit(
                    y_mx, xdata=list(std_group[f"{s} Area"]), ydata=list(std_group[s])
                )[0][0]
            )
            # Calculate average run number
            av_runs.append(std_group["Measurement"].mean())

        # Fit linear regression to drift in calibration line
        m, c = curve_fit(y_mx_c, xdata=av_runs, ydata=reg_dict[s])[0]

        sample_df.loc[:, f"{s}_slope"] = m * sample_df.loc[:, "Measurement"] + c
        sample_df.loc[:, s] = sample_df.loc[:, f"{s} Area"] * sample_df.loc[:, f"{s}_slope"]

    else:
        raise ValueError(
            "Please specify 'all' or 'interpolated' for the calibration mode"
        )


# %% Plot calibration curve
col_seq = px.colors.qualitative.D3

n_rows = len(species)
fig = make_subplots(rows=n_rows, cols=1, subplot_titles=species, vertical_spacing=0.05)

for r, s in enumerate(species):
    fig.update_yaxes(title=f"[{s}] (mol/kg)", rangemode="tozero", row=r + 1, col=1)

    if cal_mode == "all":
        # Plot trend line for all standards
        xx = np.array([0, df[f"{s} Area"].max() * 1.02])
        yy = reg_dict[s] * xx
        fig.add_trace(
            go.Scatter(
                x=xx,
                y=yy,
                mode="lines",
                marker_color=col_seq[0],
                opacity=0.3,
                name="Trendline",
            ),
            row=r + 1,
            col=1,
        )

    # Plot standards
    for n, (_, std_group) in enumerate(std_groups):
        # Plot trend line for each group of standards
        if cal_mode == "interpolated":
            xx = np.array([0, df[f"{s} Area"].max() * 1.02])
            yy = reg_dict[s][n] * xx
            fig.add_trace(
                go.Scatter(
                    x=xx,
                    y=yy,
                    mode="lines",
                    marker_color=col_seq[n + 1],
                    opacity=0.3,
                    name=f"Trendline {n+1}",
                ),
                row=r + 1,
                col=1,
            )

        fig.add_trace(
            go.Scatter(
                x=std_group[f"{s} Area"],
                y=std_group[s],
                text=std_group["Name"],
                marker_color=col_seq[n + 1],
                marker_line_color=col_seq[n + 1],
                marker_line_width=2,
                name=f"Standards {n+1}",
                mode="markers",
                marker_symbol="cross-thin",
                marker_size=8,
            ),
            row=r + 1,
            col=1,
        )

    # Plot calibated samples
    fig.add_trace(
        go.Scatter(
            x=sample_df[f"{s} Area"],
            y=sample_df[s],
            text=sample_df["Name"],
            mode="markers",
            marker_color=col_seq[0],
            marker_size=4,
            name="Samples",
        ),
        row=r + 1,
        col=1,
    )

fig.update_layout(width=500, height=400 * n_rows, showlegend=False)

fig.update_xaxes(rangemode="tozero")
fig.update_xaxes(title="Measured Area (μS⋅min)", row=n_rows, col=1)

fig.show()
# %% Export calibrated concentrations
output_df = sample_df.loc[:, ["Name"] + species]

# Correct for dilution
for s in species:
    output_df[s] = output_df[s] * dilution

output_df.to_csv(f"{file_name}_out.csv", index=False)
# %% Save calibration plots

fig.write_image("calibration_plots.pdf")

print("Calibration complete!")

# %%
