from PIL import Image
import streamlit as st
from plot_expression import *
from standard_curve import *
from cq_calculate import *

APP_TITLE = "Realtime PCR Calculator"

# Set the configs
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=Image.open(r'./cache/logo/R.ico'),
    layout="wide",
    initial_sidebar_state="auto",
)
icon = Image.open(r'./cache/logo/Logo.png')


def general_main(icon):
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)
    st.title('qPCR Result Calculation')
    st.sidebar.image(icon, use_column_width=True)
    st.sidebar.markdown('''[![ShuXingYu94 - real-timer](https://img.shields.io/static/v1?label=ShuXingYu94&message=real-timer&color=green&logo=github)](https://github.com/ShuXingYu94/real-timer)
        [![GitHub tag](https://img.shields.io/github/tag/ShuXingYu94/real-timer?include_prereleases=&sort=semver&color=green)](https://github.com/ShuXingYu94/real-timer/releases/)''')
    st.info('Please input file on the left.')


# Main function
def qPCR_generator_main():
    # Make general page information.
    general_main(icon)
    st.sidebar.markdown('## Available Function')
    func = st.sidebar.selectbox('Choose one to begin with:',
                                ['Standard Curve Figure', 'Figure From Expression', 'Figure From Cq'])

    if func == 'Standard Curve Figure':
        standard_curve()
    elif func == 'Figure From Expression':
        expression_plot()
    elif func == 'Figure From Cq':
        cq_calculate()


# Run
if __name__ == '__main__':
    try:
        qPCR_generator_main()
    except (ValueError, IndexError) as val_ind_error:
        st.error(f"There is a problem with values/parameters or dataset due to {val_ind_error}.")
    except TypeError as e:
        st.warning("TypeError exists in {}".format(e))
        pass
