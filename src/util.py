import numpy as np

def createDataMap(array):
    outlier = []
    dict = {}
    mean_x = (np.average(array[0]))
    mean_y = (np.average(array[1]))

    center_p = np.array((mean_x, mean_y))

    for i in range(len(array[0])):
        point = np.array((array[0][i], array[1][i]))
        point_tuple = (array[0][i], array[1][i])
        distance = np.linalg.norm(center_p - point)
        data = {point_tuple: distance}
        dict.update(data)

    if len(dict) > 2:
        val_list = list(dict.values())
        key_list = list(dict.keys())
        mean = np.mean(val_list)
        sd = np.std(val_list)
        for i in range(len(val_list)):
            z = (val_list[i] - mean) / sd
            if z > 0.5 or z < -0.5:
                key = key_list[i]
                outlier.append(key)
        return outlier