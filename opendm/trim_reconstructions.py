import numpy as np
import math
import shutil
import copy
from opensfm import io, types
from typing import Iterable

def trim_reconstructions_json(filename: str, max_angle_deg: float) -> None:
    shutil.copyfile(filename, filename + ".bak")
    with open(filename, "rt") as fin:
        reconstructions = io.reconstructions_from_json(io.json_load(fin))

    reconstructions = trim_reconstructions(reconstructions, max_angle_deg: float)
    
    with open(filename, "wt") as fout:
        io.json_dump(io.reconstructions_to_json(reconstructions), fout, minify=False)

def trim_reconstructions(reconstructions: Iterable[types.Reconstruction], max_angle_deg: float) -> Iterable[types.Reconstruction]:
    s = math.sin(math.radians(max_angle_deg))
    c = math.cos(math.radians(max_angle_deg))
    normal_vecs = [np.array([c, 0, s]), np.array([0, c, s]), np.array([-c, 0, s]),  np.array([0, -c, s])]
    lens = [-1.0e9, -1.0e9, -1.0e9, -1.0e9]
    for k, reconstruction in enumerate(reconstructions):
        for shot_id in reconstruction.shots:
            p = reconstruction.get_shot(shot_id).pose.get_origin()

            for i in range(4):
                pN = p.dot(normal_vecs[i])
                if pN > lens[i]:
                    lens[i] = pN

        trimmed_reconstruction = copy.deepcopy(reconstruction)
        for point_id in reconstruction.points:
            p = reconstruction.get_point(point_id).coordinates
            for i in range(4):
                pN = p.dot(normal_vecs[i])
                if pN > lens[i]:
                    trimmed_reconstruction.remove_point(point_id)
                    break
        reconstructions[k] = trimmed_reconstruction
    return reconstructions