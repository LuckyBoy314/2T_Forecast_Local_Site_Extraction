# -*- coding:utf-8 -*-
from math import sqrt
from datetime import datetime, timedelta
import os,time
from bokeh.plotting import figure, output_file, save, ColumnDataSource #,show
from bokeh.models import Range1d, Span, BoxAnnotation, HoverTool
from datetime import datetime, timedelta
from win32api import GetSystemMetrics
from bokeh.models.widgets import Panel, Tabs

cwd = os.getcwd()
def log_decorator(fun):
    def wapper(*args,**keyargs):
        now = datetime.now()

        logfile = 'log.txt'
        f = open(logfile,'a')
        f.write("start is:"+now.strftime('%Y-%m-%d %H:%M:%S'))
        f.write('\n')
        start = time.clock()
        fun_result = fun(*args,**keyargs)
        end = time.clock()
        elapsed = end - start
        for each in args:
            f.write(str(each))
            f.write('\n')

        for key, each in keyargs.items():
            f.write(str(key)+":"+str(each))
            f.write('\n')

        f.write("Time used: %.6fs, %.6fms" % (elapsed, elapsed * 1000))
        f.write('\n')
        f.write("*****************")
        f.write('\n')
        f.close
        return fun_result
    return wapper

def readDataFromFile(file_path):
    with open(file_path, 'r') as f:
        d = [line for line in f.readlines() if line[:-1].strip()]  # 去除空行读入
        data_text = [line.split() for line in d[3:]]  # 跳过头信息从第四行开始读数据，存入二维数据，注意数据类型是字符串

    data = [[float(i) for i in row] for row in data_text]
    return data


def loadParameters(paras_file):
    paras = []
    with open(paras_file, 'r') as f:
        for line in f:
            s = line.split(' ')
            for i in xrange(2, 8):
                if i <= 3:
                    s[i] = int(s[i])
                else:
                    s[i] = float(s[i])

            paras.append(s[2:])
    # paras = [[int(i) for i in row] for row in paras]
    # paras = [[float(i) for i in row[2:]] for row in paras]
    return paras

@log_decorator
def extractValues(params,root,date,out_path):
    file_names =[f_name for f_name in os.listdir(root) if date in f_name]
    outfile = os.path.join(out_path,'20'+date+'.txt')
    with open(outfile, 'w') as out:
        for f in file_names:
            # 处理时间字符串
            datetime_str = '20' + f
            dt = datetime_str[:-4]
            delta = datetime_str[-3:]
            dt_obj = datetime.strptime(dt, '%Y%m%d%H') + timedelta(hours=int(delta))
            dt_str = datetime.strftime(dt_obj, "%Y/%m/%d %H:%M")
            out.write(dt_str + '\t')

            data = readDataFromFile(os.path.join(root,f))

            for p in params:  # 注意di和wi的位置要匹配  #分别处理每个县
                d1 = data[p[0]][p[1]]
                d2 = data[p[0] + 1][p[1]]
                d3 = data[p[0]][p[1] + 1]
                d4 = data[p[0] + 1][p[1] + 1]
                w1 = p[2]
                w2 = p[3]
                w3 = p[4]
                w4 = p[5]
                z = (d1 * w1 + d2 * w2 + d3 * w3 + d4 * w4) / (w1 + w2 + w3 + w4)
                z_str = '%.2f' % z
                out.write(z_str + '\t')
            out.write('\n')

# 读入文本数据
# data是二维数据，每列表示某个站点的在一时间序列上的值
@log_decorator
def plot_2T(date, files):

    tabs = []
    output_file(os.path.join(cwd,'2T_Forecast.html'), title=u'2米温度预报')
    for target_file in files:
        fs = target_file.split('/')
        title = fs[-1][4:10]+" " + fs[-2]+u" 2米温度预报"
        if fs[-3] == "2TMax3h":
            title = fs[-1][4:10]+" " + fs[-2]+u" 过去3小时2米最高温度预报"
        if fs[-3] == "2TMin3h":
            title = fs[-1][4:10]+" " + fs[-2]+u" 过去3小时2米最低温度预报"

        data = []
        with open(target_file, 'r') as f:
            for line in f:
                data.append(line.split('\t'))

        # 数据的时间序列的节点数目
        n_series = len(data)

        #如果没有数据，则返回，防止出错
        if n_series ==0:
            continue

        # 获取每个站点的名字
        names = []
        with open('stations.ini', 'r') as f:
            for line in f:
                s = line.split(',')
                names.append(s[1])
        
        # 站点数目
        n_locations = len(names)

        # X轴，时间坐标轴，dateX是用时间对象表示的，dateX_str是字符串形式的为了便于在tooltip中显示
        # 注意bokeh在将时间对象作为X轴时会将本地时间转换为世界时，为了避免这种转换，需要再本地时间上再加上8h（北京时比世界时快8h）
        dateX = [datetime.strptime(data[i][0], "%Y/%m/%d %H:%M") + timedelta(hours=8) for i in xrange(n_series)]
        dateX_str = [datetime.strftime(x - timedelta(hours=8), "%m/%d %Hh") for x in dateX]

        # 将文本数据data转换为浮点型values
        # 注意values也是二维数据，但与data不同的是，values中每行表示某个站点的在一时间序列上的值，而不是每列
        values = []
        for j in xrange(1, n_locations + 1):  # 第一列是时间，从第二列开始
            values.append([float(data[i][j]) for i in xrange(n_series)])

        # todo 宽度根据显示器控制
        # todo 暂时采用同一样式，以后再更换
        # todo 除了直线，考虑柱状图、平滑曲线等其他形式


        tools_to_show = 'hover,box_zoom,pan,save,resize,reset,wheel_zoom'

        p = figure(plot_width=GetSystemMetrics(0)-150,plot_height=GetSystemMetrics(1)-250,
            x_axis_type="datetime", tools=tools_to_show, active_scroll="wheel_zoom")
	
        colors = ['red', 'blue', 'green', 'orange', 'yellow', 'purple', 'pink']

        # 分别为每个站点绘制时间序列变化曲线
        for i, name, color in zip(range(n_locations), names, colors):
            source = ColumnDataSource(data={
                'dateX': dateX,
                'v': values[i],
                'dateX_str': dateX_str,
                'name': [name for n in xrange(n_series)]
            })

            p.line('dateX', 'v', color=color, legend=name, source=source)
            circle = p.circle('dateX', 'v', fill_color="white", size=8, color=color, legend=name, source=source)
            p.tools[0].renderers.append(circle)
        #显示标签
        hover = p.select(dict(type=HoverTool))
        hover.tooltips = [(u"温度", "@v"), (u"站点", "@name"), (u"时间", "@dateX_str")]
        hover.mode = 'mouse'

        # 标题设置
        p.title.text = title
        p.title.align = "center"
        p.title.text_font_size = "25px"
        # p.title.background_fill_color = "#aaaaee"
        # p.title.text_color = "orange"
        p.xaxis.axis_label = u'日期/时间'
        p.yaxis.axis_label = u'温度(℃)'

        # 显示三天
        # p.x_range = Range1d(time.mktime((datetime(2016, 11, 8, 17, 0, 0)+ timedelta(hours=8)).timetuple())*1000,
        #                     time.mktime((datetime(2016, 11, 12, 20, 0, 0)+ timedelta(hours=8)).timetuple())*1000)

        # 加入预报时效界限
        # todo.根据上午还是下午确定不同的日界线
        # location使用实数表示，所以必须把时间转换成时间戳，但不清楚为什么要乘以1000
        n_days = (dateX[-1] - dateX[0]).days + 1
        forecast_span = [Span(location=time.mktime((dateX[0]+timedelta(days=i)+timedelta(hours=12)).timetuple()) * 1000,
                        dimension='height', line_color='red', line_dash='dashed', line_width=2)
                         for i in xrange(n_days)]
        for span in forecast_span:
            p.add_layout(span)
        # #显示风力等级
        # low_box = BoxAnnotation(top=5, fill_alpha=0.1, fill_color='red')
        # mid_box = BoxAnnotation(bottom=5, top=20, fill_alpha=0.1, fill_color='green')
        # high_box = BoxAnnotation(bottom=20, fill_alpha=0.1, fill_color='red')
        # p.add_layout(low_box)
        # p.add_layout(mid_box)
        # p.add_layout(high_box)

        tab = Panel(child=p, title=fs[-2]+" "+fs[-3])
        tabs.append(tab)
    tabs = Tabs(tabs = tabs)
    save(tabs)
	

if __name__ == '__main__':
    param_EC_HR_2T = loadParameters(os.path.join(cwd,'EC_HR_2T.txt'))
    param_T639_HR_2T = loadParameters(os.path.join(cwd,'T639_HR_2T.txt'))
    param_GERMAN_HR_2T = loadParameters(os.path.join(cwd,'GERMAN_HR_2T.txt'))
    params = [param_EC_HR_2T,
                param_T639_HR_2T,
                param_GERMAN_HR_2T,
                param_EC_HR_2T,
                param_EC_HR_2T
              ]

    roots = []
    with open(os.path.join(cwd,'settings.ini'),'r') as f_settings:
        for line in f_settings:
            roots.append(line.strip())
    roots = roots[1:]


    out_paths = [''.join([cwd,'/ElementsForecast/2T/EC_HR']),
                 ''.join([cwd,'/ElementsForecast/2T/T639_HR']),
                 ''.join([cwd,'/ElementsForecast/2T/GERMAN_HR']),
                 ''.join([cwd,'/ElementsForecast/2TMax3h/EC_HR']),
                 ''.join([cwd,'/ElementsForecast/2TMin3h/EC_HR'])
                 ]

    for each_path in out_paths:
        if not os.path.exists(each_path):
            os.makedirs(each_path)

    now = datetime.now()
    today = now.strftime('%Y%m%d')
    nowtime = now.strftime('%Y%m%d%H')
    if nowtime < today+"12":
        yesterday = now -timedelta(days = 1)
        start_predict = (yesterday.strftime('%Y%m%d')+"20")[2:]
    else:
        start_predict = (today+"08")[2:]
    date = start_predict


    files = [''.join([cwd,'/ElementsForecast/2T/EC_HR/20' ,date , '.txt']),
    ''.join([cwd,'/ElementsForecast/2T/T639_HR/20' , date , '.txt']),
    ''.join([cwd,'/ElementsForecast/2T/GERMAN_HR/20' , date , '.txt']),
    ''.join([cwd,'/ElementsForecast/2TMax3h/EC_HR/20' , date , '.txt']),
    ''.join([cwd,'/ElementsForecast/2TMin3h/EC_HR/20' , date , '.txt'])]

    #温度提取
    for i in xrange(5):
        extractValues(params[i], roots[i], date, out_paths[i])

    #绘图
    plot_2T(date,files)




	



