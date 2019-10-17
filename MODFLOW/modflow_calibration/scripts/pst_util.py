import os, sys
import pandas as pd
import pyemu

def generate_template_from_input(input_fname, tpl_file):
    """
    """
    df_par = pd.read_csv(input_fname,  index_col=False)
    with open(tpl_file, 'w') as ofp:
        ofp.write('ptf ~\n')
        header = ''
        for col in df_par.columns:
            header = header + col + ','
        header = header[:-1] + "\n" # remove last comma and new line
        ofp.write(header)
        for i, row in df_par.iterrows():
            line = ''
            for col in df_par.columns:
                if col in ['parval1']:
                    line = line +  '~{0:^12}~'.format(row['parnme']) + ','

                else:
                    line = line + '{}'.format(row[col]) + ','
            line = line[:-1]
            line = line + "\n"
            ofp.write(line)


def reorder_df(df1, df2, col1, col2):
    df1 = df1.set_index(col1)
    df1 = df1.reindex(index=df2[col2])
    df1 = df1.reset_index()
    return df1

def generate_inst_from_output(output_fname, insfilename):
    #def simple_ins_from_obs2(obsnames=['obs1'], marker='!', obs_width=100, insfilename='model.output.ins'):

    df_obs = pd.read_csv(output_fname,  index_col=False)
    marker = '*'
    obs_width = 100

    fid = open(insfilename, 'w')
    fid.write("pif %s\n" % (marker))
    header = ''
    for col in df_obs.columns:
        header = header + col + ','
    header = header[:-1]   # remove last comma and new line
    header = marker + header + marker + "\n"
    fid.write(header)

    for i, row in df_obs.iterrows():
        line = "l1 "
        line = line + marker
        for col in df_obs.columns:

            if col in ['obsval']:
                line = line + marker
                line = line + ' !{}! '.format(row['obsnme']) +  marker + ','
            else:
                line = line + '{}'.format(row[col]) + ','
        line = line[:-1]
        line = line + marker
        line = line + "\n"
        fid.write(line)

    fid.close()

    pass
