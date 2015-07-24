import panes as pns
import matplotlib.pyplot as plt
import code

def plot_daily_average(series, fname, title, ylabel):
    plt.clf()
    series.plot(kind='line')
    plt.ylabel(ylabel)
    plt.title(title)

    # Relabel x-axis
    plt.xticks(rotation=90)
    oldticks = plt.gca().get_xticklabels()
    newticks = []
    for tick in oldticks:
        text = tick.get_text()
        hr = int(text[:2])
        if hr != 18:
            last_hr = str(hr-1) + ":00"
            text = last_hr + " - " + text
        else:
            last_hr = str(hr-1) + ":00"
            text = last_hr + " - " + "end"
        newticks.append(text)

    #code.interact(local=locals())

    plt.gca().set_xticklabels(newticks)

    # Save
    plt.savefig(fname+'.eps', format='eps', dpi=1200)

def mean_prod_by_hour(df, series):
    return df.groupby(by=lambda x: '{0:02d}:00'.format(x.hour))[series].mean()

if __name__ == '__main__':
    home = '/Users/micahsmith/Development/workspace/panes/'
    spath = home+'Results/Plots/'

    panes_file = home+'Data/Raw/panesmdc.txt'
    panes = pns.load_data_panes(panes_file)
    panes = pns.add_variables(panes)

    # Average productivity by hour
    mean_prod_hrly = mean_prod_by_hour(panes, 'd1panes')
    plot_daily_average(mean_prod_hrly, 
            fname=spath+'mean_prod_hrly',
            title='Productivity',
            ylabel='Mean change in panes')

    mean_prod_hrly = mean_prod_by_hour(panes, 'absd1panes')
    plot_daily_average(mean_prod_hrly, 
            fname=spath+'mean_abs_prod_hrly_hrly',
            title='Productivity',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour, excluding non-workdays.
    panes_only_workdays = panes[panes['is_workday']]
    mean_prod_hrly_only_workdays = mean_prod_by_hour(
            panes_only_workdays, 'd1panes')
    plot_daily_average(mean_prod_hrly_only_workdays, 
            fname=spath+'mean_prod_hrly_only_workdays',
            title='Productivity, excluding non-workdays',
            ylabel='Mean change in panes')

    mean_prod_hrly_only_workdays = mean_prod_by_hour(
            panes_only_workdays, 'absd1panes')
    plot_daily_average(mean_prod_hrly_only_workdays, 
            fname=spath+'mean_abs_prod_hrly_only_workdays',
            title='Productivity, excluding non-workdays',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour of the week, excluding days in which the RAN
    # was reset.
    panes_excl_reset = panes[~panes['is_ran_reset_today']]
    mean_prod_hrly_excl_reset = mean_prod_by_hour(panes_excl_reset, 'd1panes')
    plot_daily_average(mean_prod_hrly_excl_reset, 
            fname=spath+'mean_prod_hrly_excl_reset',
            title='Productivity, excluding RAN resets',
            ylabel='Mean change in panes')

    mean_prod_hrly_excl_reset = mean_prod_by_hour(panes_excl_reset, 'absd1panes')
    plot_daily_average(mean_prod_hrly_excl_reset, 
            fname=spath+'mean_abs_prod_hrly_excl_reset',
            title='Productivity, excluding RAN resets',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour of the week, excluding days in which the RAN
    # was reset, excluding non-workdays.
    panes_excl_reset_only_workdays = panes_excl_reset[panes_excl_reset['is_workday']]
    mean_prod_hrly_excl_reset_only_workdays = mean_prod_by_hour(
            panes_excl_reset_only_workdays, 'd1panes')
    plot_daily_average(mean_prod_hrly_excl_reset_only_workdays, 
            fname=spath+'mean_prod_hrly_excl_reset_only_workdays',
            title='Productivity, excluding RAN resets and non-workdays',
            ylabel='Mean change in panes')

    mean_prod_hrly_excl_reset_only_workdays = mean_prod_by_hour(
            panes_excl_reset_only_workdays, 'absd1panes')
    plot_daily_average(mean_prod_hrly_excl_reset_only_workdays, 
            fname=spath+'mean_abs_prod_hrly_excl_reset_only_workdays',
            title='Productivity, excluding RAN resets and non-workdays',
            ylabel='Mean absolute change in panes')
