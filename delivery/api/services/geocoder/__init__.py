from .geocoder import Geocoder2GIS
from .geocoder import GeocoderOSM
from .geocoder import GeocoderRemoteServiceRequestError
from .geocoder import GeocoderRemoteServiceResponseError


service = Geocoder2GIS()
geocoder_osm = GeocoderOSM()
