import os
import sys
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
import numpy as np
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
try:
    plt.rcParams['date.epoch'] = '0000-12-31'
except:
    pass
debug = False


def nash_sutcliffe_efficiency(qsim, qobs):
    qsim = np.log(qsim)
    qobs = np.log(qobs)
    qsim[np.isinf(qsim)] = np.nan
    qobs[np.isinf(qobs)] = np.nan
    numerator = np.nansum((qsim - qobs) ** 2)
    denominator = np.nansum((qobs - np.nanmean(qobs)) ** 2)
    nse = 1 - (numerator / denominator)
    return nse


def calculate_paee(qsim, qobs):
    err = np.nansum(qsim - qobs)
    mz = np.nanmean(qobs)
    samples = np.where(~np.isnan(qobs))
    n = len(samples[0])
    result = (1./(mz * n)) * err
    return result * 100


def calculate_aaee(qsim, qobs):
    result = np.abs(calculate_paee(qsim, qobs))
    return result


def mean_max_min(q, conv=1):
    return np.nanmean(q), np.nanmax(q), np.nanmin(q)


def read_gage(f, start_date="1-1-1970"):
    dic = {'date': [], 'stage': [], 'flow': [], 'month': [], 'year': []}
    m, d, y = [int(i) for i in start_date.split("-")]
    start_date = dt.datetime(y, m, d) - dt.timedelta(seconds=1)
    with open(f) as foo:
        for ix, line in enumerate(foo):
            if ix < 2:
                continue
            else:
                t = line.strip().split()
                date = start_date + dt.timedelta(days=float(t[0]))
                stage = float(t[1])
                flow = float(t[2])
                dic['date'].append(date)
                dic['year'].append(date.year)
                dic['month'].append(date.month)
                dic['stage'].append(stage)
                dic['flow'].append(flow)

    return dic


def read_observation_data(f):
    return pd.read_csv(f)


if __name__ == "__main__":
    print("\n@@@@ CREATING GAGE OUTPUT FIGURE @@@@")
    ws = os.path.abspath(os.path.dirname(__file__))
    start_date = "10-1-1947"
    obs_name = os.path.join(ws, 'stream_gages_monthly_SACr.dat')
    obs_df = read_observation_data(obs_name)

    if debug:
        gage_name = os.path.join(ws, "..", "output", "SACr.gag1")
        gage_no = 1
        out_name = os.path.join(ws, "script_output", "test.png")
        out_csv = os.path.join(ws, "script_output", "test.csv")
        out_csv2 = os.path.join(ws, 'script_output', 'test2.csv')
    else:
        gage_name = os.path.join(ws, sys.argv[1])
        gage_no = sys.argv[2]
        if gage_no not in ('1', '2', '3', '4', '5'):
            raise AssertionError("Gage number must be 1, 2, 3, 4, or 5")
        out_name = os.path.join(ws, sys.argv[3])
        out_csv = os.path.join(ws, sys.argv[4])
        out_csv2 = os.path.join(ws, sys.argv[5])

    gage_no = 'gage_{}'.format(gage_no)

    data = read_gage(gage_name, start_date)
    df = pd.DataFrame.from_dict(data)
    df.date = pd.to_datetime(df.date).values.astype(np.int64)
    df = df.groupby(['year', 'month'], as_index=False)[['stage', 'flow', 'date']].mean()
    df.date = pd.to_datetime(df.date)
    date = df['date'].values

    obs_date = []
    for iloc, row in obs_df.iterrows():
        t = df[(df['year'] == row.year) & (df['month'] == row.month)]
        if len(t.date.values) > 0:
            obs_date.append(t.date.values[0])
        else:
            obs_date.append(np.nan)

    obs_df['date'] = obs_date

    xlim = [min(date), max(date)]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # lns1 = ax.plot(date, df['stage'].values, '--', color='peru',
    #                label="Simulated stage")
    # ax2 = ax.twinx()
    lns2 = ax.plot(date, df['flow'].values, 'b-', label=r"Simulated Flow")

    mask = np.isnan(obs_df['date'].values)
    obs_date = np.ma.array(obs_df['date'].values, mask=mask)
    obs_flow = np.ma.array(obs_df[gage_no].values, mask=mask)

    lns3 = ax.plot(obs_date, obs_flow, 'r-',
                   label=r"Observed Flow")

    ax.set_xlabel("Date")
    ax.set_xlim(xlim)
    # ax.set_ylabel(r"Monthly mean stage, in $m$", fontsize=12)
    # ax.yaxis.label.set_color("peru")
    ax.set_ylabel(r"Monthly mean flow, in $m^{3}\,d^{-1}$", fontsize=12)
    ax.yaxis.label.set_color("b")
    ax.set_yscale('log')

    lns = lns2 + lns3 # + lns1
    labels = [l.get_label() for l in lns]
    ax.legend(lns, labels, loc=0)
    plt.subplots_adjust(left=0.12, bottom=0.11, right=0.81, top=0.88)
    plt.savefig(out_name)
    plt.close()

    df = df.drop(columns=['date'])
    df.to_csv(out_csv, index=False)

    sim = df.flow.values
    obs = [np.nan, np.nan, np.nan] + list(obs_df[gage_no].values) + [np.nan, np.nan, np.nan]
    obs = np.array(obs)
    plt1980 = True
    if len(sim) != len(obs):
        obs = obs[0:len(sim)]
        plt1980 = False
    nse = nash_sutcliffe_efficiency(sim, obs)
    nnse = 1 / (2 - nse)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lmin = np.min(sim)
    lmax = np.max(sim)

    if lmin > np.min(obs):
        lmin = np.min(obs)

    if lmax < np.max(obs):
        lmax = np.max(obs)

    if lmin <= 0:
        lmin = 1

    ax.scatter(obs, sim)
    ax.plot([lmin, lmax], [lmin, lmax], "k--")

    ax.set_xlim([lmin, lmax])
    ax.set_ylim([lmin, lmax])
    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlabel(r"Observed mean monthly flow, in $m^{3}\,d^{-1}$",
                  fontsize=12)
    ax.set_ylabel(r"Simulated mean monthly flow, in $m^{3}\,d^{-1}$",
                  fontsize=12)
    ax.text(0.25, 0.93,
            'NSE: {:.2f}'.format(nse),
            transform=ax.transAxes)
    ax.text(0.25, 0.87,
            'NNSE: {:.2f}'.format(nnse),
            transform=ax.transAxes)
    out_name = out_name[:-4] + "_1to1.png"
    plt.savefig(out_name)
    print(nse, nnse)

    paee = calculate_paee(sim, obs)
    aaee = calculate_aaee(sim, obs)
    smean, smax, smin = mean_max_min(sim)
    omean, omax, omin = mean_max_min(obs)

    header = "PAEE,AAEE,sim mean m^3/mo,sim max m^3/mo,sim min m^3/mo,obs mean m^3/mo,obs max m^3/mo,obs min m^3/mo\n"
    metrics = "{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(paee, aaee, smean, smax, smin, omean, omax, omin)

    with open(out_csv2, 'w') as foo:
        foo.write(header)
        foo.write(metrics)

    if not plt1980:
        sys.exit(1)

    df = df[df.year >= 1980]
    obs_df = obs_df[obs_df.year >= 1980]
    if len(df) == 0 or len(obs_df) == 0:
        print('zzzxxx')
        sys.exit(0)
    sim = df.flow.values
    obs = list(obs_df[gage_no].values) + [np.nan, np.nan, np.nan]
    obs = np.array(obs)
    nse = nash_sutcliffe_efficiency(sim, obs)
    nnse = 1 / (2 - nse)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lmin = np.min(sim)
    lmax = np.max(sim)

    if lmin > np.min(obs):
        lmin = np.min(obs)

    if lmax < np.max(obs):
        lmax = np.max(obs)

    if lmin <= 0:
        lmin = 1

    ax.scatter(obs, sim)
    ax.plot([lmin, lmax], [lmin, lmax], "k--")

    ax.set_xlim([lmin, lmax])
    ax.set_ylim([lmin, lmax])
    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlabel(r"Observed mean monthly flow, in $m^{3}\,d^{-1}$", fontsize=12)
    ax.set_ylabel(r"Simulated mean monthly flow, in $m^{3}\,d^{-1}$", fontsize=12)
    ax.text(0.25, 0.93,
            'NSE: {:.2f}'.format(nse),
            transform=ax.transAxes)
    ax.text(0.25, 0.87,
            'NNSE: {:.2f}'.format(nnse),
            transform=ax.transAxes)
    out_name = out_name[:-4] + "_after_1980.png"
    plt.savefig(out_name)
    print(nse, nnse)


