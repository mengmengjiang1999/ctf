**介绍：**

该篇章主要介绍如何编写自己的信息收集工具，主要流程如下：

1、向bing搜索引擎发起request请求，获取url数据

2、使用正则表达式对获取的数据进行处理

3、用多线程，对处理的数据进行二次请求，返回标题等数据

4、使用openyxl模块，将数据保存为.xlsx格式

 **请注意：**

该篇章目的是熟悉Python编程，学习Python的一些常见模块，在编写程序的过程中会有很多操作和方式方法，望大家能共同加油学到东西。本文仅用于技术讨论与研究，这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

 **本文涉及到模块有：**

    
    
    #coding:utf-8
    import requests     #发起request请求
    import urllib3      #处理请求https异常报错问题
    import re       #使用正则表达式对请求到的数据进行处理
    from optparse import OptionParser   #自定义输入参数
    import threading        #多线程模块
    import queue            #多线程辅助模块，使用队列的方式对多线程进行控制
    from bs4 import BeautifulSoup   #与re类似 使用正则表达式对请求到的数据进行处理
    import time,datetime    #获取当前的时间
    from openpyxl import  * #数据处理，将获取到的数据保存在excel文件中
    

**属性：**

    
    
    heads = {                       #全局变量  请求头
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)                          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',   #模拟浏览器请求
    'Connection':'close',
    'Accept-Encoding':'gzip, deflate'
    }
    count=1                         #全局变量  用于序号字段
    queueLock = threading.Lock()    #全局变量  使用线程锁处理 线程异常问题
    class DoRun(threading.Thread):  #自定义 多线程运行时使用的类
    

**方法：**

    
    
    def get_Input():    #获取search语句 和 page
    def getUrls(search,page):       #构造搜索语句，在bing搜索引擎搜索数据并返回urls
    def req(url):   #对url进行验证，返回numb,url,title,status
    def init_excel(filename):  #创建.xlsx表格，并初始化内容
    def Save_Date(date,filename):   #将数据存储到表格当中
    def run():     #核心代码
    

**完整代码如下：**

    
    
    #coding:utf-8
    import requests     #发起request请求
    import urllib3      #处理请求https异常报错问题
    import re       #使用正则表达式对请求到的数据进行处理
    from optparse import OptionParser   #自定义输入参数
    import threading        #多线程模块
    import queue            #多线程辅助模块，使用队列的方式对多线程进行控制
    from bs4 import BeautifulSoup   #与re类似 使用正则表达式对请求到的数据进行处理
    import time,datetime    #获取当前的时间
    from openpyxl import  * #数据处理，将获取到的数据保存在excel文件中
    
    heads = {                       #全局变量  请求头
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',   #模拟浏览器请求
                'Connection':'close',
                'Accept-Encoding':'gzip, deflate'
            }
    count=1                         #全局变量  用于序号字段
    queueLock = threading.Lock()    #全局变量  使用线程锁处理 线程异常问题
    class DoRun(threading.Thread):  #自定义 多线程运行时使用的类
        def __init__(self,queue,filename):
            threading.Thread.__init__(self)
            self._queue=queue
            self._filename=filename
        def run(self):
            while not self._queue.empty():
                js=req(self._queue.get())
                #print(js)
                queueLock.acquire()
                if(js):
                    Save_Date(js,self._filename)
                queueLock.release()
    def init_excel(filename):  #创建.xlsx表格，并初始化内容
        wb=Workbook()
        filename=filename+".xlsx"
        ws=wb.create_sheet(index=0,title="域名")
        head=['序号','域名','标题','状态']
        for i in range(0,4):
            ws.cell(1,i+1).value=head[i]
        wb.save(filename)
    def Save_Date(date,filename):   #将数据存储到表格当中
        filename=filename+".xlsx"
        wb_save=load_workbook(filename)
        ws_save=wb_save.worksheets[0]
        current_row=ws_save.max_row+1
        current_col=1
        for key in date:
            ws_save.cell(date['numb']+1,current_col).value=str(date[key])
            current_col+=1
        wb_save.save(filename) 
    def req(url):   #对域名进行验证，返回状态码，title
        global count
        dir={'numb':0,'url':'url','title':'None','status':0}
        stat=0
        title="None"
    
        try:
            urllib3.disable_warnings()
            response = requests.get(url=url,headers=heads,verify=False,timeout=10)   #请求漏洞的url
            if response.status_code == 200:
                bs=BeautifulSoup(response.content,"html.parser")
                title=bs.find("title").text
                stat=response.status_code
                dir['numb']=count
                dir['url']=url
                dir['title']=title
                dir['status']=stat
                count+=1
                print("[+]"+url+"\ttitle:"+title)
                return dir
            else:
                print('[-]请求失败：\t{}\t{}'.format(url,response.status_code))
        except Exception as e:
            print('[-]请求失败: {}\t'.format(e,url))
    def getUrls(search,page):       #构造搜索语句，在bing搜索引擎 搜索数据并返回urls
        count=1
        urls=[]
        url="https://cn.bing.com/search?q={}&first={}"
        for i in range(1,page):
            if(i!=1):
                count=(i-2)*10+9
            url=url.format(search,i)
            try:
                resp=requests.get(url=url,headers=heads)
                html=resp.text
                if(resp.status_code==200):
                    res=re.findall(r'<a target="_blank" href="(.*?)"',html)
                    for u in res:
                        if(u not in urls):
                            urls.append(u)
                else:
                     print('[-]请求失败：\t{}\t{}'.format(url,resp.status_code))
            except Exception as e:
                print('[-]请求失败: {}\t'.format(e,url))
    
        return urls
    def get_Input():    #获取search语句 和 page
        optParser = OptionParser()
        optParser.add_option('-s','--search',action = 'store',type = "string" ,dest = 'search',help='漏扫文件的目录',default="search_def")
        optParser.add_option("-p","--page", action="store", type="int",dest="page",help='要搜索的页数',default=10)
        optParser.add_option("-t","--threads", action="store", type="int",dest="threads",help='线程数量，默认为10',default=10)
        (options , args) = optParser.parse_args()
        return options.search,options.page,options.threads
    def run():
        que=queue.Queue()
        print(datetime.datetime.now())              #打印开始时间
        search,page,thread_count=get_Input()        #获取输入的参数 如searce 、线程数、页面数
        if(search=="search_def"):
            print(r"[-]错误，未输入指定参数：python3 temp.py -s site:qq.com [-p 10] [-t 20] ")
            return
        print(search)
        threads=[]
        urls=getUrls(search,page)     #获取urls
        filename=''.join(re.findall("([a-z,0-9])",search))      #将输入的内容进行处理 ，作为文件的名称
        init_excel(filename)        #创建并初始化excel
        for url in urls:
            que.put(url)            #将获取的urls添加到queue中
        for i in range(thread_count):
            threads.append(DoRun(que,filename))     #使用多线程 默认调用 run()函数
        for i in threads:
            i.start()               #启动多线程
        for i in threads:
            i.join()                #等待线程结束
    
        print(datetime.datetime.now())      #打印结束时间
    run()
    

**使用说明：*** ***

    
    
    python3 .\bingying.py -s "site:.com" -p 10 -t 30
    Options:
    -h, --help  show this help message and exit
    -s SEARCH, --search=SEARCH    搜索的语法(默认 site:.com)
    -p PAGE, --page=PAGE          要搜索的页数（一页10条数据，默认10页）
    -t THREADS, --threads=THREADS 线程数量，(默认为10)
    

**结果呈现**

![1632291957_614acc75cf719787794df.png!small](https://image.3001.net/images/20210922/1632291957_614acc75cf719787794df.png!small)

