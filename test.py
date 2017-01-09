# -*- coding:utf-8 -*-

from datetime import datetime
import  time
def log_decorator(fun):
    def wapper(*args,**keyargs):

        now = datetime.now()

        logfile = 'log.txt'
        f = open(logfile,'a')
        f.write("start is:"+now.strftime('%Y-%m-%d %H:%M:%S'))
        f.write('\n')
        start = time.clock()
        fun(*args,**keyargs)
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

    return wapper

@log_decorator
def myfun(a,b,c):
    n = 100000
    for i in xrange(n):
        pass

if __name__ == "__main__":
    myfun(1,2,4)