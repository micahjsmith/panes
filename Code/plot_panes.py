import panes as pns
import matplotlib.pyplot as plt

def plot_weekly_average(series, fname, title, ylabel):
    plt.clf()
    series.plot(kind='bar')
    plt.ylabel(ylabel)
    plt.title(title)

    # Mark every 9th tick, label in a nice way.
    ax = plt.gca()
    strday = {0:'Mon.',1:'Tue.',2:'Wed.',3:'Thu.',4:'Fri.',5:'Sat.',6:'Sun.'}
    oldticks = ax.get_xticklabels()[0::9]
    newticks = []
    for text in oldticks:
        text = text.get_text()
        text = strday[int(text[:2])]
        #text = strday[int(text[:2])] + text[2:]
        newticks.append(text)
    ax.set_xticks([x for x in range(0,len(series),9)])
    ax.set_xticklabels(newticks)

    # Save
    plt.savefig(fname+'.eps', format='eps', dpi=1200)

if __name__ == '__main__':
    home = '/Users/micahsmith/Development/workspace/panes/'
    spath = home+'Results/Plots/'

    panes_file = home+'Data/Raw/panesmdc.txt'
    panes = pns.load_data_panes(panes_file)
    panes = pns.add_variables(panes)

    # Function to average over hours of the week with nice format.
    my_format= lambda x: '{0:02d}, {1:02d}:00'.format(x.weekday(), x.hour)
    def mean_prod_by_hour_of_week(df, series):
        return df.groupby(by=my_format)[series].mean()

    # Average productivity by hour of the week
    mean_prod = mean_prod_by_hour_of_week(panes, 'd1panes')
    plot_weekly_average(mean_prod,
            fname=spath+'mean_prod', 
            title='Productivity',
            ylabel='Mean change in panes')

    mean_prod = mean_prod_by_hour_of_week(panes, 'absd1panes')
    plot_weekly_average(mean_prod,
            fname=spath+'mean_abs_prod', 
            title='Productivity',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour of the week, excluding non-workdays.
    panes_only_workdays = panes[panes['is_workday']]
    mean_prod_only_workdays = mean_prod_by_hour_of_week(
            panes_only_workdays, 'd1panes')
    plot_weekly_average(mean_prod_only_workdays, 
            fname=spath+'mean_prod_only_workdays',
            title='Productivity, excluding non-workdays',
            ylabel='Mean change in panes')

    mean_prod_only_workdays = mean_prod_by_hour_of_week(
            panes_only_workdays, 'absd1panes')
    plot_weekly_average(mean_prod_only_workdays, 
            fname=spath+'mean_abs_prod_only_workdays',
            title='Productivity, excluding non-workdays',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour of the week, excluding days in which the RAN
    # was reset.
    panes_excl_reset = panes[~panes['is_ran_reset_today']]
    mean_prod_excl_reset = mean_prod_by_hour_of_week(panes_excl_reset, 'd1panes')
    plot_weekly_average(mean_prod_excl_reset, 
            fname=spath+'mean_prod_excl_reset',
            title='Productivity, excluding RAN resets',
            ylabel='Mean change in panes')

    mean_prod_excl_reset = mean_prod_by_hour_of_week(panes_excl_reset, 'absd1panes')
    plot_weekly_average(mean_prod_excl_reset, 
            fname=spath+'mean_abs_prod_excl_reset',
            title='Productivity, excluding RAN resets',
            ylabel='Mean absolute change in panes')

    # Average productivity by hour of the week, excluding days in which the RAN
    # was reset, excluding non-workdays.
    panes_excl_reset_only_workdays = panes_excl_reset[panes_excl_reset['is_workday']]
    mean_prod_excl_reset_only_workdays = mean_prod_by_hour_of_week(
            panes_excl_reset_only_workdays, 'd1panes')
    plot_weekly_average(mean_prod_excl_reset_only_workdays, 
            fname=spath+'mean_prod_excl_reset_only_workdays',
            title='Productivity, excluding RAN resets and non-workdays',
            ylabel='Mean change in panes')

    mean_prod_excl_reset_only_workdays = mean_prod_by_hour_of_week(
            panes_excl_reset_only_workdays, 'absd1panes')
    plot_weekly_average(mean_prod_excl_reset_only_workdays, 
            fname=spath+'mean_abs_prod_excl_reset_only_workdays',
            title='Productivity, excluding RAN resets and non-workdays',
            ylabel='Mean absolute change in panes')
