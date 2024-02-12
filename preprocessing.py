import numpy as np

def pad_or_crop_3d_array(array, target_shape):
    # Get the current shape of the array
    current_shape = array.shape
    
    # Initialize padding or cropping parameters
    pad_width = []
    crop_slices = []
    
    # Calculate padding or cropping for each dimension
    for i in range(3):
        diff = target_shape[i] - current_shape[i]
        if diff > 0:
            # Pad the array
            pad_before = diff // 2
            pad_after = diff - pad_before
            pad_width.append((pad_before, pad_after))
            crop_slices.append(slice(None))
        elif diff < 0:
            # Crop the array
            crop_start = abs(diff) // 2
            crop_end = current_shape[i] - (abs(diff) - crop_start)
            crop_slices.append(slice(crop_start, crop_end))
            pad_width.append((0, 0))
        else:
            # No padding or cropping needed
            pad_width.append((0, 0))
            crop_slices.append(slice(None))
    
    # Pad or crop the array
    if np.any(np.array(pad_width) != (0, 0)):
        padded_array = np.pad(array, pad_width, mode='constant', constant_values=0)
    else:
        padded_array = array[crop_slices[0], crop_slices[1], crop_slices[2]]
    
    return padded_array



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
    return np.array(new_3d_arr)

