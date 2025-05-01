import geocoder
import logging

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s | DateTime: %(asctime)s | File: %(name)s | Message: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logging.getLogger('geocoder').setLevel(logging.WARNING)


def get_current_location():
    """
    Get the current geolocation (latitude and longitude) based on IP address.
    
    Returns:
        dict: Dictionary containing 'lat', 'lng', 'x', and 'y' keys.
    """
    location_data = {
        "lat": '',
        "lng": '',
        "x": [''],
        "y": ['']
    }
    try:
        g = geocoder.ip('me')  # Get current location based on IP
        if g.latlng:
            lat, lng = g.latlng
            location_data = {
                "lat": str(lat),
                "lng": str(lng),
                "x": [''],
                "y": ['']
            }
            # logger.info(f"Location detected successfully: lat={lat}, lng={lng}")
        else:
            logger.warning("Location could not be detected. Returning empty values.")
        return location_data
    except Exception as e:
        logger.error(f"Error occurred while detecting location: {e}")
        return location_data