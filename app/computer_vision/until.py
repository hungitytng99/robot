import numpy as np

def angleBetweenPoints(a, b, c):
    """ compute the angle in degress betwen 3 points as a float """
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.arccos(cosine_angle)
