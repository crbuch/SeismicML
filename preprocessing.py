import torch
from torchvision.transforms.functional import pad, crop
import numpy as np


def cropAndOrPad(a:np.array, targetSize:tuple) -> torch.tensor:

    pad_top = max(0, (targetSize[1] - a.shape[0]) // 2)
    pad_bottom = max(0, targetSize[1] - a.shape[0] - pad_top)
    pad_left = max(0, (targetSize[0] - a.shape[1]) // 2)
    pad_right = max(0, targetSize[0] - a.shape[1] - pad_left)

    image = pad(torch.from_numpy(a), (pad_left, pad_top, pad_right, pad_bottom), fill=0 )

    top =  round((image.size(0)/2)-(image.size(0)/2))
    left =  round((image.size(1)/2)-(image.size(1)/2))
    height = targetSize[1]
    width = targetSize[0]

    image = crop(image, top, left, width, height)


    return image


def to3dArray(stream):
    inline_length = max(trace.stats.segy.trace_header.trace_sequence_number_within_line for trace in stream)
    crossline_length = len(stream) // (inline_length + 1)
    sample_depth_length = len(stream[0].data)

    seismic_3d_array = np.zeros(
    (inline_length + 1, crossline_length + 1, sample_depth_length)
    )

    # Populate the 3D array
    for i, trace in enumerate(stream):
        inline = trace.stats.segy.trace_header.trace_sequence_number_within_line
        crossline = i % (
            crossline_length + 1
        )  # Calculate crossline dynamically based on iteration
        seismic_3d_array[inline, crossline, :] = trace.data


    new_3d_arr = []

    for i in range(crossline_length):
        new_3d_arr.append(np.flipud(np.rot90(seismic_3d_array[:, i, :])))
    new_3d_arr = np.array(new_3d_arr)
    return new_3d_arr

