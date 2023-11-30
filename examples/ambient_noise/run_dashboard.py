import numpy as np

from shakeflow import ambient_noise_dashboard

paras = {
    "ppsd": False,
    "beamforming": False,
    "cross_correlation": True,
    "dvv": True,
}


def __main__():
    ambient_noise_dashboard(paras)
