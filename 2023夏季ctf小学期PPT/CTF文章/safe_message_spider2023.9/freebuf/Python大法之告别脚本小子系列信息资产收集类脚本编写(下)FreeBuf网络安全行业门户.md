作者：阿甫哥哥

原文来自：[https://bbs.ichunqiu.com/article-1618-1.html](https://bbs.ichunqiu.com/article-1618-1.html?from=beef)

  

系列文章专辑：  
[Python大法之告别脚本小子系列](https://bbs.ichunqiu.com/forum.php?mod=collection&action=view&ctid=137?from=beef)  
目录:

> 0x05 高精度字典生成脚本编写  
>  
> 0x06 Queue模块的讲解  
>  
> 0x07 目录扫描脚本编写  
>  
> 0x08 C段扫描脚本编写

0x05 高精度字典生成脚本编写

  
![image.png](https://image.3001.net/images/20180717/15317961376643.png!small)思路来自i春秋讲师ADO的课程，传送门：  

[Python安全工具开发应用 > 高精度字典生成（一）](https://www.ichunqiu.com/course/53477?from=beef)

有人可能会问生成字典有什么卵用？？

如果你在爆破中用一个G大小的字典，可能也不会获得到什么信息，但是，如果你通过已知的部分信息生成字典进行爆破，这样你的成功率会大大的提高，本文用到的模块也是exrex，思路也五五开。。。

官方介绍：<https://github.com/asciimoo/exrex>

安装方法：pip install exrex

建立一个密码字典（无非就是已知的信息）

  
![image.png](https://image.3001.net/images/20180717/15317962525539.png!small)  

我只是简单的举了个栗子，也用了一个简单的匹配方式

    
    
    #-*- coding: UTF-8 -*-  
    
    import exrex  
      
    
    def dic_create(hosts):  
    
            web_dics = hosts.split('.')  
    
            for web_dic in web_dics:  
    
                    f_pass = open('pass.txt',"r")  
    
                    for dic_pass in f_pass:  
    
                            dics = list(exrex.generate(web_dic+'[!@#]'+dic_pass))  
    
                            for dic in dics:  
    
                                    print dic.strip('\n')  
      
    
    if __name__ == '__main__':  
    
            dic_create('www.ichunqiu.com')

  
这样就简单的造了一个字典生成器

问题又来了，他把我域名中的http://,www，com都生成了，其实并没有什么卵用。。。所以，就要去掉他

    
    
    #-*- coding: UTF-8 -*-  
    
    import exrex  
      
    
    def dic_create(hosts):  
    
            web_dics = hosts.split('.')  
    
            for web_dic in web_dics:  
    
                    if web_dic not in web_white:  
    
                            f_pass = open('pass.txt',"r")  
    
                            for dic_pass in f_pass:  
    
                                    dics = list(exrex.generate(web_dic+'[!@#]'+dic_pass))  
    
                                    for dic in dics:  
    
                                                    print dic.strip('\n')  
      
    
    if __name__ == '__main__':  
    
            web_white = ['com','cn','org','edu','gov','www']  
    
            host = 'www.ichunqiu.com'  
    
            if '://' in host:  
    
                    host = host.split('://')[1]  
    
            if '/' in host:  
    
                    host = host.replace('/','')  
    
            dic_create(host)

然后就差不多了，顶多加个判断，排除简单的密码组合

    
    
    #-*- coding: UTF-8 -*-  
    
    import exrex  
      
    
    def dic_create(hosts):  
    
            web_dics = hosts.split('.')  
    
            for web_dic in web_dics:  
    
                    if web_dic not in web_white:  
    
                            f_pass = open('pass.txt',"r")  
    
                            for dic_pass in f_pass:  
    
                                    dics = list(exrex.generate(web_dic+'[!@#]'+dic_pass))  
    
                                    for dic in dics:  
    
                                            if len(dic) > 5:  
    
                                                    print dic.strip('\n')  
      
    
    if __name__ == '__main__':  
    
            web_white = ['com','cn','org','edu','gov','www']  
    
            host = raw_input('PLEASE INPUT YOUR TARGET:')  
    
            if '://' in host:  
    
                    host = host.split('://')[1]  
    
            if '/' in host:  
    
                    host = host.replace('/','')  
    
            dic_create(host)

  
![1.gif](https://image.3001.net/images/20180717/15317991193187.gif!small)  

0x06 Queue模块的讲解

自带的模块，不用安装，你们可以去看官方文档学习，我也只是简单的说一下

创建一个队列

    
    
    D:\ichunqiu\items>python  
    
    Python 2.7 (r27:82525, Jul  4 2010, 09:01:59) [MSC v.1500 32 bit (Intel)] on win32  
    
    Type "help", "copyright", "credits" or "license" for more information.  
    
    >>> import Queue  
    
    >>> queue = Queue.Queue()

将值放入队列中

    
    
    >>> for i in range(8):  
    
    ...     queue.put(i)  
    
    ...

返回队列大小

    
    
    >>> queue.qsize()  
    
    8

取出队列中的值

    
    
    >>> queue.get()  
    
    0  
    
    >>> queue.get()  
    
    1  
    
    >>> queue.get()  
    
    2

Threading与Queue的结合

    
    
    #-*- coding: UTF-8 -*-  
    
    import threading  
    
    import Queue  
      
    
    class DemoRUN(threading.Thread):  
    
        def __init__(self,queue):  
    
            threading.Thread.__init__(self)  
    
            self._queue = queue  
    
        def run(self):  
    
            while not self._queue.empty():  
    
                key = self._queue.get()  
    
                print key  
    
    def main():  
    
        threads = []  
    
        threadnum = 20        #线程数  
    
        queue = Queue.Queue()  
    
        for i in range(1,9):  
    
            queue.put(i)  
    
        for i in xrange(threadnum):  
    
            threads.append(DemoRUN(queue))  
    
        for t in threads:  
    
            t.start()  
    
        for t in threads:  
    
            t.join()  
    
    if __name__ == '__main__':  
    
        main()

这就是一个大概的模块

0x07 目录扫描脚本编写

![image.png](https://image.3001.net/images/20180717/15317963475289.png!small)

目录扫描，顾名思义，就是目录扫描，在信息收集中也算重要的一环了  
所以我先简单放出一个单线程版，大概思路就是引入字典，URl+字典内容，访问，状态码是200就保留

    
    
    #-*- coding: UTF-8 -*-  
    
    import requests  
      
    
    def scan_target_url_exists(target_url):  
    
        headers={  
    
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
    
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',  
    
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',  
    
            'Accept-Encoding': 'gzip, deflate',  
    
            'Referer': 'http://www.google.com'  
    
            }  
    
        status_codes = [200]  
    
        all_lines=open(dir_file,'r').readlines()  
    
        for i in all_lines:  
    
                url = target_url+'/'+str(i)  
    
            req=requests.head(url.strip(),timeout=8,headers=headers)  
    
            if req.status_code in status_codes:  
    
                print 'CODE:%s,URL:%s'%(str(req.status_code),url.strip('\n').strip('\r'))  
    
                open('exists_target_url.txt','a').write(url)  
      
    
    if __name__ == '__main__':  
    
        dir_file='demo.txt'  
    
        target_url='localhost'  
    
        if target_url.startswith('http://') or target_url.startswith('https://'):  
    
            pass  
    
        else:  
    
            target_url = 'http://' + target_url  
    
        scan_target_url_exists(target_url)  
    

  
没有什么知识点，直接看吧，接下来，是多线程的

用到了queue，优化了一下code

    
    
    #-*- coding: UTF-8 -*-  
    
    import requests  
    
    from threading import Thread, activeCount  
    
    import Queue  
      
    
    queue = Queue.Queue()  
    
    dir_file='demo.txt'  
      
    
    def scan_target_url_exists(target_url):  
    
        headers={  
    
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
    
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',  
    
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',  
    
            'Accept-Encoding': 'gzip, deflate',  
    
            'Referer': 'http://www.google.com'}  
    
        status_codes = [200]  
    
        try:  
    
            req=requests.head(target_url.strip(),timeout=8,headers=headers)  
    
            if req.status_code in status_codes:  
    
                print 'CODE:%s,URL:%s'%(str(req.status_code),target_url.strip('\n').strip('\r'))  
    
                open('exists_target_url.txt','a').write(target_url)  
    
        except:  
    
            pass  
    
    def open_pathfile(file):  
    
        all_lines=open(file,'r').readlines()  
    
        for line in all_lines:  
    
            if target_url.endswith('/'):  
    
                if line.startswith('/'):  
    
                    queue.put(target_url+line[1:])  
    
                else:  
    
                    queue.put(target_url + line)  
    
            else:  
    
                if line.startswith('/'):  
    
                    queue.put(target_url + line)  
    
                else:  
    
                    queue.put(target_url + '/' + line)  
      
    
    if __name__ == '__main__':  
    
        print '''  
    
     ____  _      ____                    
    
    |  _ \(_)_ __/ ___|  ___ __ _ _ __    
    
    | | | | | '__\___ \ / __/ _` | '_ \   
    
    | |_| | | |   ___) | (_| (_| | | | |  
    
    |____/|_|_|  |____/ \___\__,_|_| |_|  
      
    
        '''  
    
        target_url=raw_input('Please input your target:')  
    
        threadnum = raw_input('Please input your threadnum:')  
    
        if target_url.startswith('http://') or target_url.startswith('https://'):  
    
            pass  
    
        else:  
    
            target_url = 'http://' + target_url  
    
        print 'The number of threads is %s' % threadnum  
    
        print 'Matching.......'  
    
        open_pathfile(dir_file)  
    
        while queue.qsize() > 0:  
    
            if activeCount() <= int(threadnum):  
    
                Thread(target=scan_target_url_exists,args=(queue.get(),)).start()

  
  

当然了，阅读原文查看你们想要的目录扫描的字典>>>>[https://bbs.ichunqiu.com/article-1618-1.html](https://bbs.ichunqiu.com/article-1618-1.html?from=beef)

