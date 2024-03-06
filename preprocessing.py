import numpy as np
import math

class Seismic:
    @staticmethod
    def __get_FFID(trace):
        header = trace.stats.segy.trace_header
        return int.from_bytes(header.unpacked_header[8:12], byteorder="little" if header.endian=="<" else "big")

    @staticmethod
    def __get_xy(trace):
        header = trace.stats.segy.trace_header
        return int.from_bytes(header.unpacked_header[72:76], byteorder="little" if header.endian=="<" else "big"), int.from_bytes(header.unpacked_header[76:80], byteorder="little" if header.endian=="<" else "big")

    def __init__(self, stream):
        self.stream = stream

        self.min_FFID = float("inf")
        self.max_FFID = -float("inf")

        self.min_x = float("inf")
        self.max_x = -float("inf")

        self.min_y = float("inf")
        self.max_y = -float("inf")

        for trace in self.stream:
            ffid = Seismic.__get_FFID(trace)
            if ffid>self.max_FFID:
                self.max_FFID = ffid
            elif ffid<self.min_FFID:
                self.min_FFID = ffid
            x, y = Seismic.__get_xy(trace)
            if x > self.max_x:
                self.max_x = x
            if x < self.min_x:
                self.min_x = x

            if y > self.max_y:
                self.max_y = y
            if y < self.min_y:
                self.min_y = y
        
        self.num_inlines = [0]
        self.last_ffid = Seismic.__get_FFID(stream[0])

        traces = []
        for trace in self.stream:
            traces.append(trace)
            ffid = Seismic.__get_FFID(trace)
            if ffid!=self.last_ffid:
                self.num_inlines.append(0)
            self.num_inlines[-1] += 1
            self.last_ffid = ffid

        
        self.num_inlines = np.bincount(self.num_inlines).argmax()
        self.num_crosslines = len(self.stream)//self.num_inlines
        self.sample_depth = len(self.stream[0])

        self.trace_array = []
        for ct, trace in enumerate(traces):
            if ct%self.num_inlines==0:
                self.trace_array.append([])
            self.trace_array[-1].append(trace)


        if(len(self.trace_array[-1])!=self.num_inlines):
            self.trace_array.pop()


        self.seismic_array = []
        for x in range(len(self.trace_array)):
            self.seismic_array.append([])
            for y in range(len(self.trace_array[0])):
                self.seismic_array[-1].append(self.trace_array[x][y].data)


        self.seismic_array = np.array(self.seismic_array)


    def get_index_from_coordinate(self, x, y, sample):
        closestIdx = (0, 0, 0)
        closestDist = float("inf")
        target_coordinate = (x, y, sample)
        
        for x in range(len(self.trace_array)):
            for y in range(len(self.trace_array[0])):
                traceX, traceY = Seismic.__get_xy(self.trace_array[x][y])

                dist = math.sqrt((traceX-target_coordinate[0])**2+(traceY-target_coordinate[1])**2)

                if dist < closestDist:
                    closestDist = dist
                    closestIdx = (x, y, round(target_coordinate[2]))
        return closestIdx
    
    def get_fault_indexes(self, fault:str):
        lines = fault.split("\n")
        coordinates = []
        for i in lines:
            coord = []
            for n in i.split(" "):
                if n!='':
                    coord.append(float(n))
                if len(coord)>=3:
                    coordinates.append(self.get_index_from_coordinate(coord[0], coord[1], coord[2]))
                    break
        return coordinates



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

