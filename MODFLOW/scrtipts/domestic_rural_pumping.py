import pandas as pd


def qtot(ser):
    '''
    Calculate rural residential water use based on the following demand types:
    1: indoor + outdoor
    2: indoor only
    3: outdoor only

    Values in acre-feet per year
    Qindoor = 0.24
    perc_Irrigated = 0.028 #percen
    Id = 2.9

    example:
    df.loc[:,['Demand Type','area_ac']].apply(qtot,axis=1)

    Args:
        ser: needs to have "Demand Type" =1,2,3, and have area_ac (area in acres) calculated

    Returns:

    '''
    Qindoor = 0.24
    perc_Irrigated = 0.028
    Id = 2.9
#     Id = 5.0
    acres = ser['area_ac']
    if ser['Demand Type'] == 1:
        irrigated_area = acres*perc_Irrigated
        if irrigated_area>0.375:
            irrigated_area = 0.375

        outdoor = Id * irrigated_area
        Qparcel = Qindoor +   outdoor

        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])
    elif ser['Demand Type'] == 2: # indoor only
        outdoor = 0
        Qparcel = Qindoor
        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])
    else : # outdoor only
        Qindoor = 0
        irrigated_area = acres*perc_Irrigated
        if irrigated_area>0.375:
            irrigated_area = 0.375
        outdoor = Id * irrigated_area
        Qparcel = outdoor
        return pd.Series([Qindoor,outdoor,Qparcel],index = ['Yearly_pumping_indoor_AF',
                                                            'Yearly_pumping_outdoor_AF',
                                                            'Yearly_pumping_Total_AF'])