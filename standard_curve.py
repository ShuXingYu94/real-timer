import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
from io import BytesIO
from st_aggrid import AgGrid


@st.cache
def default_standard_curve_df():
    df = pd.DataFrame(data={'DNA copies/unit': [100000, 10000, 1000, 100, 10], 'log/unit': [5, 4, 3, 2, 1],
                            'Ct': [12.05, 14.15, 17.91, 21.68, 24.87]})
    return df


def standard_curve():
    df = default_standard_curve_df()
    st.sidebar.markdown('## Fetch default format file')
    st.sidebar.download_button('Download Sample file', df.to_csv(index=False).encode('utf-8'),
                               'standard_curve_sample.csv')
    st.sidebar.markdown('## Input formatted file')
    file = st.sidebar.file_uploader(label='Only csv file is available:', type='csv', accept_multiple_files=False)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('### Input Data: \n > Press the "Draw" button to get result.')
        if not file:
            data = df
        else:
            data = pd.read_csv(file)
        grid_return = AgGrid(data, editable=True, fit_columns_on_grid_load=True, height=data.shape[0]*28+40,
                             GridUpdateMode='VALUE_CHANGED', theme='streamlit')
        grid = grid_return["data"]

    with col2:
        st.subheader('Calculation and Download Settings')
        st.markdown('##### Need In-Figure Result:')
        show_calculation_state = st.checkbox('Show Calculation Result in Figure')
        st.markdown('##### Available Format:')
        output_format = st.radio('SVG Format Recommended', ('svg', 'jpg', 'png', 'pdf'))

    data = grid
    x = data['log/unit']
    y = data['Ct']

    linreg = LinearRegression()
    x = x.values.reshape(-1, 1)

    fig = plt.figure(figsize=(8, 5))

    linreg.fit(x, y)
    y_predict = linreg.predict(x)

    plt.scatter(x, y, color='black')
    plt.plot(x, y_predict, color='black')

    slope = linreg.coef_
    intercept = linreg.intercept_
    rsqr = linreg.score(x, y)
    plt.title('qPCR Standard Curve')
    plt.xlabel('Log DNA copies/unit')
    plt.ylabel('Cycle Threshold')
    if show_calculation_state:
        plt.text(x.max() * 3 / 4, y.min() + (y.max() - y.min()) * 2.5 / 4,
                 s='Slope = {} \n\nIntercept = {} \n\nR$^2$ = {}'.format(round(slope[0], 4), round(intercept, 4),
                                                                         round(rsqr, 4)))

    col3, col4 = st.columns([1, 1])
    col3.subheader("Figure to Output")
    col3.pyplot(fig)
    col4.subheader('Calculation Result:')
    col4.markdown(' > **Slope = {}** \n\n > **Intercept = {}** \n\n > **R$^2$ = {}**'.format(round(slope[0], 4),
                                                                                             round(intercept, 4),
                                                                                             round(rsqr, 4)),
                  unsafe_allow_html=True)

    fn = 'standard_curve.{}'.format(output_format)
    img = BytesIO()
    plt.savefig(img, format=output_format)

    btn = col4.download_button(
        label="Download image",
        data=img,
        file_name=fn
    )
