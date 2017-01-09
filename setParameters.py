# -*- coding: utf-8 -*-
from math import sqrt, fabs

def setParameters(out_paras_file ,start_lon, start_lat, res_lon, res_lat, power=2,stations = 'Stations.ini'):
    '设置每个站点的插值参数，依次为：站点ID，站名，起始行索引，起始列索引，w1,w2,w3,w4(四个反距离权重）'
    with open(out_paras_file, 'w') as w:
        with open(stations,'r') as f:
            for line in f:
                s = line.split(',')
                lon = float(s[2])
                lat = float(s[3])
                col_beginIndex = int(fabs((lon - start_lon) / res_lon))
                row_beginIndex = int(fabs((lat - start_lat) / res_lat))
                row_endIndex = row_beginIndex + 1
                col_endIndex = col_beginIndex + 1
                x1 = start_lon + res_lon * col_beginIndex
                x2 = start_lon + res_lon * col_endIndex
                y1 = start_lat + res_lat * row_beginIndex
                y2 = start_lat + res_lat * row_endIndex
                w1 = 1.0 / (sqrt((x1 - lon) ** 2 + (y1 - lat) ** 2)) ** power
                w2 = 1.0 / (sqrt((x1 - lon) ** 2 + (y2 - lat) ** 2)) ** power
                w3 = 1.0 / (sqrt((x2 - lon) ** 2 + (y1 - lat) ** 2)) ** power
                w4 = 1.0 / (sqrt((x2 - lon) ** 2 + (y2 - lat) ** 2)) ** power
                out_line = '%s %s %d %d %.6f %.6f %.6f %.6f\n' % (
                    s[0], s[1], row_beginIndex, col_beginIndex, w1, w2, w3, w4)
                w.writelines(out_line)


if __name__ == '__main__':
    #设置EC_HR插值参数
    #todo 为避免参数出错，应改为自动根据头文件进行判断
    setParameters('EC_HR_2T.txt',start_lon=60.0, start_lat=70.0, res_lon=0.125, res_lat=-0.125)
    #设置T639_HR插值参数
    setParameters('T639_HR_2T.txt', start_lon=0.0, start_lat=90.0, res_lon=0.281250, res_lat=-0.281250)
    # 设置GERMAN_HR插值参数
    setParameters('GERMAN_HR_2T.txt', start_lon=0.0, start_lat=-10.0, res_lon=0.25, res_lat=0.25)
