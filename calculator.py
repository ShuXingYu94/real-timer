import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.express as px
from itertools import cycle
from plotly.graph_objs import Bar
import streamlit as st
import plotly.io as pio
from io import BytesIO


@st.cache(allow_output_mutation=True)
def default_expression_data():
    sample = pd.read_csv(r'./cache/sample_data.csv')
    return sample


def reduce(ls):
    new_ls = list(dict.fromkeys(ls))
    return new_ls


def expression_calculate():
    df = default_expression_data().copy()
    st.sidebar.markdown('## Fetch default format file')
    st.sidebar.download_button('Download Sample file', df.to_csv(index=False).encode('utf-8'), 'expression_sample.csv')
    st.sidebar.markdown('## Input formatted file')
    file = st.sidebar.file_uploader(label='Only csv file is available:', type='csv', accept_multiple_files=False)

    if not file:
        st.markdown('### Sample Data: \n > Press the "Draw" button to get sample result.')
        data = df
    else:
        st.markdown('### Input Data: \n > Press the "Draw" button to get result.')
        data = pd.read_csv(file)
    st.sidebar.markdown('## Draw Figure by:')
    divide = st.sidebar.radio('Default is Target Gene', ['Target', 'Cultivar', 'Treatment'])
    st.dataframe(data, width=1000)
    st.sidebar.markdown('## Available Format:')
    output_format = st.sidebar.radio('SVG Format Recommended', ('svg', 'jpg', 'png', 'pdf'))

    if st.button('Draw'):
        looplist = reduce(list(data[divide].values))
        ls = ['Target', 'Cultivar', 'Treatment']
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
