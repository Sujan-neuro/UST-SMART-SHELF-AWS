import logging
import streamlit as st
from configs.config import (
    PROCESS_INTERVAL_SEC,
    TRACKING_DURATION_SEC,
    CONFIDENCE_THRESHOLD,
    MIN_FACE_RATIO
)
from configs.camera import list_available_cameras

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

CAMERA_LIST = list_available_cameras(max_tested=10)

def set_page_style() -> None:
    """
    Sets the style for the Streamlit page including background color, button styles, etc.

    Returns:
        None
    """
    try:
        logging.info('Setting page style for Streamlit')
        st.set_page_config(page_title="Smart Shelf", page_icon="🧠", layout="wide")
        st.markdown("""
            <style>
                .main { background-color: #0D3B66; }
                h1, h2, h3, .stButton>button {
                    color: #0a4d8c;
                }
                .stButton>button {
                    background-color: #0a4d8c;
                    color: white;
                    border-radius: 10px;
                    padding: 0.5em 1em;
                    margin-top: 10px;
                }
                .stButton>button:hover {
                    background-color: #09396b;
                }
                .css-1d391kg { background-color: #0D3B66 !important; }
            </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        logging.error(f"Error in setting page style: {e}")
        raise

def display_header() -> None:
    """
    Displays the header for the Smart Shelf app with title and logo.

    Returns:
        None
    """
    try:
        logging.info('Displaying header')
        col1, col2 = st.columns([4, 1])
        with col1:
            st.title("Smart Shelf")
        with col2:
            st.image("./src/configs/ust_logo.png", width=70)
    except Exception as e:
        logging.error(f"Error in displaying header: {e}")
        raise

def sidebar_config() -> dict:
    """
    Configures the sidebar with options to customize the app settings.

    Returns:
        dict: A dictionary containing all selected configuration options.
    """
    try:
        logging.info('Configuring sidebar')
        # Normal Configurable
        st.sidebar.subheader("Normal Configurable Items")
        identify_age = st.sidebar.selectbox("Identify Age", [True, False], index=1)
        identify_gender = st.sidebar.selectbox("Identify Gender", [True, False], index=1)
        default_cam = st.sidebar.selectbox("Select Camera", CAMERA_LIST)

        # Detailed Configurable
        st.sidebar.subheader("Detailed Configurable Items")
        process_interval = int(st.sidebar.selectbox("Process Interval (sec)", [PROCESS_INTERVAL_SEC, 1, 3, 4]))
        tracking_duration = int(st.sidebar.selectbox("Send API Response (sec)", [TRACKING_DURATION_SEC, 2, 4, 5]))

        confidence = st.sidebar.text_input("Face Identification Confidence (0 to 1)", str(CONFIDENCE_THRESHOLD))
        try:
            confidence = float(confidence)
            if not 0 <= confidence <= 1:
                st.sidebar.warning("Confidence must be between 0 and 1. Using default.")
                confidence = CONFIDENCE_THRESHOLD
        except Exception as e:
            logging.warning(f"Invalid confidence input: {e}. Using default.")
            confidence = CONFIDENCE_THRESHOLD

        face_ratio = st.sidebar.text_input("Minimum Face Ratio (0 to 1)", str(MIN_FACE_RATIO))
        try:
            face_ratio = float(face_ratio)
            if not 0 <= face_ratio <= 1:
                st.sidebar.warning("Minimum face ratio must be between 0 and 1. Using default.")
                face_ratio = MIN_FACE_RATIO
        except Exception as e:
            logging.warning(f"Invalid face ratio input: {e}. Using default.")
            face_ratio = MIN_FACE_RATIO

        run = st.sidebar.button("RUN")
        stop = st.sidebar.button("STOP")

        return {
            "identify_age": identify_age,
            "identify_gender": identify_gender,
            "default_camera_index": default_cam,
            "process_interval_sec": process_interval,
            "tracking_duration_sec": tracking_duration,
            "confidence_threshold": confidence,
            "min_face_ratio": face_ratio,
            "run": run,
            "stop": stop
        }
    except Exception as e:
        logging.error(f"Error in sidebar configuration: {e}")
        raise