# constants.py

"""This module defines project-level constants."""

class ConstantsNamespace():
    __slots__ = ()
    # overall
    WARNING = "⚠️"
    ERROR = "🚨"
    INFO = "ℹ️"
    SUCCESS = "✅"
    
    # orbit compare
    COMP_SAMPLE_TIME = 60*5 # segundos
    COMP_NUMBER_SAMPLES = 80
    GAMA_BRN_AZ = 207.77878
    GAMA_BRN_EL = 0.1
    GAMA_BRN_D = 19049.6
    GAMA_ECEF_X = 5179474.6
    GAMA_ECEF_Y = -3661013.7
    GAMA_ECEF_Z = -670180.8
    GAMA_LAT = -6.071928859515179
    GAMA_LON = -35.25385792507863
    GAMA_H = 118.94240806899084