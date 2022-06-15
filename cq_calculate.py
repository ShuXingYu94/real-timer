import math
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
from itertools import cycle
from plotly.graph_objs import Bar
import streamlit as st
import plotly.io as pio
from io import BytesIO
from st_aggrid import AgGrid


def reduce(ls):
    new_ls = list(dict.fromkeys(ls))
    return new_ls


@st.cache
def get_gene_list(df):
    ls = reduce(df['Target'].tolist())
    return ls


@st.cache(allow_output_mutation=True)
def default_expression_data():
    sample = pd.read_csv(r'./cache/sample_cq.csv')
    return sample


def cq_to_expression(df, control_gene='Actin'):
    target_genes = list(dict.fromkeys(df['Target'].tolist()))
    target_genes.remove(control_gene)
    st.text(target_genes)
    df = df[df['Content'].str.contains('Unkn')]
    df = df[['Target', 'Sample', 'Biological Set Name', 'Cq']]
    df.groupby(['Target', 'Sample', 'Biological Set Name']).agg('mean')
    repeat = df.groupby(['Target', 'Sample', 'Biological Set Name']).size()
    mean = df.groupby(['Target', 'Sample', 'Biological Set Name']).agg('mean')
    std = df.groupby(['Target', 'Sample', 'Biological Set Name']).agg('std')
    mean.columns = ['Cq Mean']
    std.columns = ['Cq Std']
    cal_df = pd.concat([mean, std], axis=1)
    cal_df.loc[:, 'Repeat Num'] = repeat
    tmp = cal_df.loc[target_genes, 'Cq Mean'] - cal_df.loc[control_gene, 'Cq Mean']

    cal_df.loc[target_genes, 'dCq'] = tmp.to_list()

    cal_df.loc[:, 'Cq SE'] = cal_df['Cq Std'] / (2 * cal_df['Repeat Num'])
    s_target = cal_df.loc[target_genes, 'Cq SE'].to_list()
    s_control = cal_df.loc[control_gene, 'Cq SE'].to_list()
    st.dataframe(cal_df)
    st.text(s_target)
    st.text(s_control)
    tmp = []
    for a in range(0, len(s_target)):
        tmp.append(math.sqrt(s_target[a] ** 2 + s_control[a] ** 2))
    cal_df.loc[target_genes, 'Cq SD'] = tmp
    tmp = cal_df.reset_index()

    result = tmp[tmp['Target'] != control_gene].copy()

    # result=result[result['dCq'].notnull()].copy()

    ls = result['dCq'].to_list()
    m = result['dCq'].agg('max')
    ls = [a - m for a in ls]
    result.loc[:, 'ddCq'] = ls
    ls_cq = result['ddCq'].to_list()
    ls_sd = result['Cq SD'].to_list()
    ls_exp = []
    ls_esd = []
    for a in range(len(ls_cq)):
        cq = ls_cq[a]
        sd = ls_sd[a]
        ls_exp.append(math.pow(2, -cq))
        ls_esd.append(math.pow(2, -cq) - math.pow(2, -cq - sd))
    result.loc[:, 'Expression'] = ls_exp
    result.loc[:, 'Expression SD'] = ls_esd
    result = result[['Target', 'Sample', 'Biological Set Name', 'Cq Mean',
                     'Repeat Num', 'dCq', 'Cq SD', 'ddCq', 'Expression',
                     'Expression SD']]
    return result

def plot_expression(data,divide,output_format):
    looplist = reduce(list(data[divide].values))
    ls = ['Target', 'Sample', 'Biological Set Name']
    ls.remove(divide)
    st.subheader("Relative Gene Expression")
    columns = ['Expression']
    error_column = 'Expression SD'
    count = 0

    if len(looplist) == 1:
        row = 1
        col = 1
        wid=400
        hei=400
    else:
        row = int(np.ceil(len(looplist) / 2))
        col = 2
        wid = 400*col
        hei = 400*row
    fig = make_subplots(rows=row, cols=col)

    pio.templates.default = "simple_white"

    for target in looplist:
        count += 1
        row_count = int(np.ceil(count / 2))
        col_count = 2 - int(count % 2)

        tmp = data[data[divide] == target]

        palette = cycle(px.colors.qualitative.Alphabet)
        colors = {c: next(palette) for c in looplist}

        for cols in columns:
            fig.add_trace(Bar(x=[tmp[ls[0]], tmp[ls[1]]], y=tmp[cols], name=target, legendgroup=cols,
                              marker_color=colors[target], showlegend=True,
                              error_y={'array': tmp[error_column].to_list(), 'type': 'data', 'visible': True}),
                          row=row_count, col=col_count)

    fig.update_layout(barmode='group', width=wid, height=hei)

    st.plotly_chart(fig, False)

    st.subheader('Download Figure Above')
    fn = 'expression.{}'.format(output_format)
    img = BytesIO()
    fig.write_image(img, format=output_format)

    btn = st.download_button(
        label="Download image",
        data=img,
        file_name=fn
    )


def cq_calculate():
    df = default_expression_data().copy()
    st.sidebar.markdown('## Fetch default format file')
    st.sidebar.download_button('Download Sample file', df.to_csv(index=False).encode('utf-8'), 'cq_sample.csv')
    st.sidebar.markdown('## Input formatted file')
    file = st.sidebar.file_uploader(label='csv or xlsx files are acceptable:', type=['csv', 'xlsx'],
                                    accept_multiple_files=False)

    st.markdown('### Input Data: \n > Press the "Calculate" button to get result.')
    if not file:
        data = df
    else:
        if 'csv' in file.name:
            data = pd.read_csv(file)
        else:
            data = pd.read_excel(file)
    grid_return = AgGrid(data, editable=True, fit_columns_on_grid_load=True, height=250,
                         GridUpdateMode='VALUE_CHANGED', theme='streamlit')
    grid = grid_return["data"]
    ls = get_gene_list(grid)

    st.sidebar.markdown('## Draw Figure by:')
    divide = st.sidebar.radio('Default is Target Gene', ['Target', 'Sample', 'Biological Set Name'])
    st.sidebar.markdown('## Available Format:')
    output_format = st.sidebar.radio('SVG Format Recommended', ('svg', 'jpg', 'png', 'pdf'))

    control_gene = st.selectbox('Select control gene', ls, index=len(ls) - 1)
    if st.button('Calculate'):
        data = grid
        result_df = cq_to_expression(data, control_gene)
        grid_return = AgGrid(result_df, editable=False, fit_columns_on_grid_load=False, height=250, theme='streamlit')
        output = grid_return["data"]
        plot_expression(output,divide,output_format)