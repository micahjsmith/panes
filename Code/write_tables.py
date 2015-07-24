import panes as pns
import matplotlib.pyplot as plt
import code

def describe_to_latex(df, fname, colnames, compile):
    df = df[~df['is_ran_reset_today']]
    df = df[df['is_workday']]
    df = df[colnames]

    format = lambda x: '{0:.2f}'.format(x)

    with open(fname,'w') as f:
        if compile:
            f.write('\\documentclass{article}\n')
            f.write('\\usepackage{booktabs}\n')
            f.write('\\begin{document}\n')
            f.write('\\begin{table}\n')
        f.write(df.describe().to_latex(float_format=format))
        if compile:
            f.write('\\end{table}\n')
            f.write('\\end{document}\n')

if __name__ == '__main__':
    home = '/Users/micahsmith/Development/workspace/panes/'
    spath = home+'Results/Plots/'

    panes_file = home+'Data/Raw/panesmdc.txt'
    panes = pns.load_data_panes(panes_file)
    panes = pns.add_variables(panes)
    serial_file = home+'Data/Raw/serial_episodes.csv'
    serial = pns.load_data_serial(serial_file)
    panes_hourly = pns.merge_panes_serial(panes, serial)

    # Compile tables?
    # compile = True
    compile = False

    # Hourly data table
    tex_file_hourly = home+'Results/Tables/describe_hourly.tex'
    describe_to_latex(panes_hourly,tex_file_hourly,['panes','absd1panes','sqd1panes'], compile)

    # Daily data table
    panes_daily = pns.collapse_to_daily(panes)
    panes_daily = pns.merge_panes_serial(panes_daily,serial)
    tex_file_daily= home+'Results/Tables/describe_daily.tex'
    describe_to_latex(panes_daily,tex_file_daily,['has_episode_today','absd1panes','sqd1panes'], compile)
