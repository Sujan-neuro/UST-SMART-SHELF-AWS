import os
# ── Disable Streamlit’s file‐watcher to avoid torch.classes introspection errors
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import cv2
import logging
import traceback
import streamlit as st

from configs.utils import LoopAd
from configs.config import TOPICS
from log_utils.logs import LogHandler
from faceprocessor import FaceProcessor
from kafka_functions.kafka_producer import send_to_kafka
from streamlit_files.streamlit_utils import set_page_style, display_header, sidebar_config

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

log_handler = LogHandler()
loopad = LoopAd()


def initialize_session_state() -> None:
    """Initialize Streamlit session state variables."""
    try:
        if "run_loop" not in st.session_state:
            st.session_state.run_loop = False
        if "detection_log" not in st.session_state:
            st.session_state.detection_log = []
    except Exception as e:
        logger.error(f"Error initializing session state: {e}", exc_info=True)


def initialize_face_processor(config: dict) -> FaceProcessor:
    """Initialize and return the FaceProcessor object."""
    try:
        return FaceProcessor(
            process_interval_sec=config["process_interval_sec"],
            tracking_duration_sec=config["tracking_duration_sec"],
            confidence_threshold=config["confidence_threshold"],
            min_face_ratio=config["min_face_ratio"],
            default_camera_index=config["default_camera_index"],
            identify_age=config["identify_age"],
            identify_gender=config["identify_gender"]
        )
    except Exception as e:
        logger.error(f"Error initializing FaceProcessor: {e}", exc_info=True)
        raise


def draw_bbox_with_label(frame, bbox, age, gender) -> None:
    """Draw bounding box and label on the frame."""
    try:
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)
        label = f"Age: {age} | Gender: {gender}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 3)
    except Exception as e:
        logger.error(f"Error drawing bounding box: {e}", exc_info=True)


def format_age(age: int) -> str:
    """Format the age into defined age ranges."""
    try:
        if age == 0:
            return 'Neutral'
        elif age < 20:
            return "below 20"
        elif age > 60:
            return "above 60"
        else:
            return f"{age-5}-{age+5}"
    except Exception as e:
        logger.warning(f"Error formatting age: {e}")
        return 0


def update_detection_log(message: str, log_placeholder) -> None:
    """Append a single message to the sidebar log without interrupting the app."""
    try:
        st.session_state.detection_log.append(message)
        # show most recent at the top
        log_text = "\n".join(reversed(st.session_state.detection_log))
        log_placeholder.text_area("Detection Log", value=log_text, height=300, disabled=True)
        log_handler.store_log(message)
    except Exception as e:
        logger.warning(f"Error updating detection log: {e}", exc_info=True)


def process_stream(face_processor: FaceProcessor, config: dict, frame_placeholder, log_placeholder) -> None:
    """Main loop to process camera stream."""
    try:
        st.success("Smart Shelf is running. Press 'STOP' to end.")
        # DEBUG: show config
        # st.sidebar.markdown("**DEBUG CONFIG**")
        # st.sidebar.write(config)

        while st.session_state.run_loop:
            ret, frame = face_processor.cap.read()
            if not ret:
                st.error("Failed to retrieve frame. Exiting...")
                logger.info("Failed to retrieve frame. Exiting...")
                st.session_state.run_loop = False
                break

            bbox, result = face_processor.processor.process_frame(frame)
            if result:
                age = format_age(result.get("age", 0))
                gender = result.get("gender", "Neutral")
                draw_bbox_with_label(frame, bbox, age, gender)
                result = loopad.assign_age(result)

                person_id = result.get("visitorId")
                if face_processor.tracker.check_for_api(person_id):
                    log_entry = f"Person identified: {person_id}"
                    update_detection_log(log_entry, log_placeholder)
                    
                    logger.info(f"New detection: {result}")
                    log_entry = (
                                f"Date: {result.get('visitDate', 'None')} | "
                                f"Time: {result.get('visitTime', 'None')} | "
                                f"Age: {age} | Gender: {gender}"
                            )
                    update_detection_log(log_entry, log_placeholder)
                    logger.info(log_entry)
                    try:
                        send_to_kafka(result, TOPICS)
                        log_entry = f"Payload sent to Kafka successfully. If you do not see the ad, it may either be currently playing or there could be an issue with the display."
                        update_detection_log(log_entry, log_placeholder)
                        log_handler.store_log(f"Payload: {result}")
                        logger.info(log_entry)
                        log_entry = f"_____________________Transaction Successful__________________"
                        update_detection_log(log_entry, log_placeholder)
                    except Exception as e:
                        logger.warning(f"Unable to send payload to Kafka: {e}", exc_info = True)
                        log_entry = f"Issue with kafka, unable to send the payload to kafka."
                        update_detection_log(log_entry, log_placeholder)
                        logger.warning(log_entry)
                        log_entry = f"________________________Transaction Failed____________________"
                        update_detection_log(log_entry, log_placeholder)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB")

            # safe stop check
            if config.get("stop"):
                st.session_state.run_loop = False
                logger.info(f"App stopped.")
                break

        face_processor.cap.release()
        st.info("Smart Shelf stopped. Press RUN from the sidebar to restart.")
    except Exception:
        logger.error("Error in processing stream", exc_info=True)
        st.error("An error occurred during stop:\n" + traceback.format_exc())


def main() -> None:
    """Entry point for running the Smart Shelf Streamlit app."""
    try:
        set_page_style()
        display_header()

        initialize_session_state()
        config = sidebar_config()

        if config.get("run"):
            logger.info("App started...")
            st.session_state.run_loop = True

        frame_placeholder = st.empty()
        log_placeholder = st.empty()

        face_processor = initialize_face_processor(config)

        if st.session_state.run_loop:
            process_stream(face_processor, config, frame_placeholder, log_placeholder)
        else:
            st.info("Press RUN from the sidebar to start Smart Shelf.")
    except Exception as e:
        logger.error(f"Unexpected error in main app: {e}", exc_info=True)
        st.error("Unexpected error in main:\n" + traceback.format_exc())


if __name__ == "__main__":
    main()