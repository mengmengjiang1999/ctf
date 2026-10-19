## 引子：

通常我们会使用wirshark来对流量包进行分析，有时借助于其他工具能更方便快捷的进行流量分析，最近在做CTF时，顺便找了些工具使用，分享下开箱试用：

## 工具一:Pcap-Analyzer

### 项目地址

> <https://github.com/HatBoy/Pcap-Analyzer>

### 建议环境

运行环境：Python 3.5.X  
操作系统：Linux (以Ubuntu 15.10为例)

由于数据分析占用内存较大，建议配置2G内存以上

### 安装部署

1、使用debian9，默认自带python3.5.3

![1635403142_617a458620a9ff69039f0.png!small](https://image.3001.net/images/20211028/1635403142_617a458620a9ff69039f0.png!small)

![1635403146_617a458ac00014eb9241b.png!small](https://image.3001.net/images/20211028/1635403146_617a458ac00014eb9241b.png!small)

2、Python包管理器安装及依赖安装：

> sudo apt-get install python-setuptools python-pip  
> sudo apt-get install tcpdump graphviz imagemagick python-gnuplot python-> crypto python-pyx  
> sudo pip3 install Flask  
> sudo pip3 install Flask-WTF  
> sudo pip3 install geoip2  
> sudo pip3 install pyx  
> sudo pip3 install requests

该处容易踩坑，出现以下错误:

（1）

    
    
    File "/usr/local/lib/python3.5/dist-packages/gunicorn/util.py", line 358, in import_app
    mod = importlib.import_module(module)
    File "/usr/lib/python3.5/importlib/init.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
    File "", line 986, in _gcd_import
    File "", line 969, in _find_and_load
    File "", line 958, in _find_and_load_unlocked
    File "", line 673, in _load_unlocked
    File "", line 665, in exec_module
    File "", line 222, in _call_with_frames_removed
    File "/root/Code/Pcap-Analyzer/run.py", line 4, in
    from app import app
    File "/root/Code/Pcap-Analyzer/app/init.py", line 11, in
    from app import views
    File "/root/Code/Pcap-Analyzer/app/views.py", line 12, in
    from .utils.ipmap_tools import getmyip, get_ipmap, get_geo
    File "/root/Code/Pcap-Analyzer/app/utils/ipmap_tools.py", line 7, in
    import geoip2.database
    File "/usr/local/lib/python3.5/dist-packages/geoip2/database.py", line 9, in
    import maxminddb
    File "/usr/local/lib/python3.5/dist-packages/maxminddb/init.py", line 5, in
    import maxminddb.reader
    File "/usr/local/lib/python3.5/dist-packages/maxminddb/reader.py", line 36
    _buffer: Union[bytes, FileBuffer, "mmap.mmap"]
    ^
    SyntaxError: invalid syntax
    [2020-11-24 21:25:42 +0800] [23934] [INFO] Worker exiting (pid: 23934)
    [2020-11-24 21:25:42 +0800] [23931] [INFO] Shutting down: Master
    [2020-11-24 21:25:42 +0800] [23931] [INFO] Reason: Worker failed to boot.
    

（2）

    
    
    File "/usr/local/lib/python3.5/dist-packages/gunicorn/app/wsgiapp.py", line 48, in load_wsgiapp
        return util.import_app(self.app_uri)
      File "/usr/local/lib/python3.5/dist-packages/gunicorn/util.py", line 359, in import_app
        mod = importlib.import_module(module)
      File "/usr/lib/python3.5/importlib/__init__.py", line 126, in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
      File "<frozen importlib._bootstrap>", line 986, in _gcd_import
      File "<frozen importlib._bootstrap>", line 969, in _find_and_load
      File "<frozen importlib._bootstrap>", line 958, in _find_and_load_unlocked
      File "<frozen importlib._bootstrap>", line 673, in _load_unlocked
      File "<frozen importlib._bootstrap_external>", line 673, in exec_module
      File "<frozen importlib._bootstrap>", line 222, in _call_with_frames_removed
      File "/home/tools/Pcap-Analyzer/run.py", line 4, in <module>
        from app import app
      File "/home/tools/Pcap-Analyzer/app/__init__.py", line 11, in <module>
        from app import views
      File "/home/tools/Pcap-Analyzer/app/views.py", line 6, in <module>
        from .forms import Upload, ProtoFilter
      File "/home/tools/Pcap-Analyzer/app/forms.py", line 4, in <module>
        from flask_wtf import FlaskForm
      File "/usr/local/lib/python3.5/dist-packages/flask_wtf/__init__.py", line 1, in <module>
        from .csrf import CSRFProtect, CsrfProtect
      File "/usr/local/lib/python3.5/dist-packages/flask_wtf/csrf.py", line 220
        dest = f'{view.__module__}.{view.__name__}'
    

故建议通过安装如下版本的模块：

> Flask==1.1.4
>
> Flask_WTF==0.14.3
>
> geoip2==2.9.0
>
> requests==2.12.4
>
> scapy==2.4.0
>
> WTForms==2.3.3

3、修改配置文件

> 注意修改config.py配置文件中的目录位置
>
> UPLOAD_FOLDER = '/home/dj/PCAP/' 上传的PCAP文件保存的位置
>
> FILE_FOLDER = '/home/dj/Files/'
> 提取文件时保存的位置，下面必须要有All、FTP、Mail、Web子目录，用于存放提取不同协议的文件
>
> PDF_FOLDER = '/home/dj/Files/PDF/' PCAP保存为PDF时保存的位置

注意：该处目录需要手动创建（如mkdir dj），否则在后期上传流量包的时候，会提示目录不存在；

4、服务器安装

> Gunicorn服务器：pip3 install gunicorn
>
> Nginx服务器：sudo apt-get install nginx
>
> Nginx配置：修改/etc/nginx/nginx.conf文件，在http{}中添加下面代码：
>  
>  
>     server {
>     listen 80;
>     server_name yourdomain.com;
>     access_log /var/log/nginx/access.log;
>     error_log /var/log/nginx/error.log;
>  
>          location / {
>             #root   html;
>             #index  index.html index.htm;
>              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
>              proxy_set_header Host $http_host;
>              proxy_pass http://127.0.0.1:8000;
>         }
>  
>         error_page   500 502 503 504  /50x.html;
>         location = /50x.html {
>             root   html;
>         }}

注：

（1）需要注意，作者github上的配置文件最后少了一个"}"，按照以上配置即可；server_name处填写你的域名,通过nginx转发即可；

（2）当上传文件过大 nginx 会报错：

    
    
    “413 Request Entity Too Large”修改nginx.conf文件，在http{}中添加：
    
    
    client_max_body_size 10m;

![1635403671_617a47970315c159fa53f.png!small](https://image.3001.net/images/20211028/1635403671_617a47970315c159fa53f.png!small)重启nginx即可：

（3）程序中设定了上传后缀，但在实操中 还有pcapng等后缀，需要修改文件/app/utils/upload_tools.py，来增加新后缀：

![1635403799_617a48177aeb9dccda3fa.png!small](https://image.3001.net/images/20211028/1635403799_617a48177aeb9dccda3fa.png!small)

    
    
    #上传后缀名校验
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['pcap', 'cap' , 'pcapng'])
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    

### 运行界面

![1635404260_617a49e4768aa948e9c7f.png!small?1635404259126](https://image.3001.net/images/20211028/1635404260_617a49e4768aa948e9c7f.png!small?1635404259126)

### 功能介绍

（1）数据分析

![1635404477_617a4abdaf372f46b7c1a.png!small?1635404476448](https://image.3001.net/images/20211028/1635404477_617a4abdaf372f46b7c1a.png!small?1635404476448)

点击任意一条数据可以查看详细数据包：

![1635404527_617a4aef0bdea7ae4802c.png!small?1635404525783](https://image.3001.net/images/20211028/1635404527_617a4aef0bdea7ae4802c.png!small?1635404525783)

协议过滤：

![1635404572_617a4b1c37062b46dbb17.png!small?1635404570948](https://image.3001.net/images/20211028/1635404572_617a4b1c37062b46dbb17.png!small?1635404570948)

协议分析：

![1635404559_617a4b0f057b32820a015.png!small?1635404557512](https://image.3001.net/images/20211028/1635404559_617a4b0f057b32820a015.png!small?1635404557512)

流量分析：

![1635404589_617a4b2da7b8a4f1a6844.png!small?1635404588389](https://image.3001.net/images/20211028/1635404589_617a4b2da7b8a4f1a6844.png!small?1635404588389)

访问IP流量(可视化地图炮)：

![1635404604_617a4b3cb46297132d40d.png!small?1635404603620](https://image.3001.net/images/20211028/1635404604_617a4b3cb46297132d40d.png!small?1635404603620)

（2）数据提取

包括了web数据、mail数据、ftp数据、telnet数据、敏感数据、客户端信息等：

![1635404756_617a4bd4d98db21096976.png!small?1635404755484](https://image.3001.net/images/20211028/1635404756_617a4bd4d98db21096976.png!small?1635404755484)

同样的，我们选中其中一条数据的时候，会弹出对应详细数据包：

![1635404793_617a4bf9938f8b0485e7d.png!small?1635404792302](https://image.3001.net/images/20211028/1635404793_617a4bf9938f8b0485e7d.png!small?1635404792302)

（3）异常信息：

该处可分析出部分异常数据警告，如sql注入，上传等：  
![1635404859_617a4c3bb8b2a434ee740.png!small?1635404858291](https://image.3001.net/images/20211028/1635404859_617a4c3bb8b2a434ee740.png!small?1635404858291)

（4）文件提取：

![1635404961_617a4ca14dc0f06297d52.png!small?1635404959855](https://image.3001.net/images/20211028/1635404961_617a4ca14dc0f06297d52.png!small?1635404959855)

提取数据包中的文件，包括web、mail、ftp等其他文件：

![1635408210_617a5952326933dae8f29.png!small?1635408208590](https://image.3001.net/images/20211028/1635408210_617a5952326933dae8f29.png!small?1635408208590)

## 工具二:Pcap Analyzer Online

### 项目地址：

https://github.com/le4f/pcap-analyzer

### 建议环境

python2+debian、建议内存2G+

### 安装部署

（1）

> $ git clone https://github.com/le4f/pcap-analyzer.git  
> $ cd pcap-analyzer  
> $ pip install -r requirements.txt  
> $ chmod +x run.sh  
> $ ./run.sh  
> View http://127.0.0.1:8080/

（同样可以配置nginx进行转发）

（2）需要安装scapy模块，建议2.4.0版本：

> pip install scapy==2.4.0

（3）安装tshark：

> apt-get install tshark

否则，会在运行分析数据包时报错。

（4）修改/server/static/js/upload.js 文件：

> f (!(/\\.(pcap)$/i).test(uploadFile.name)) {  
> alert('Pcap file only!');  
> goUpload = false;  
> }

此处

### 运行界面

![1635407229_617a557dc7d1e812e1f8c.png!small?1635407228191](https://image.3001.net/images/20211028/1635407229_617a557dc7d1e812e1f8c.png!small?1635407228191)

### 功能介绍

上传流量包后，进行分析：

![1635407260_617a559c2af20e7362c30.png!small?1635407258521](https://image.3001.net/images/20211028/1635407260_617a559c2af20e7362c30.png!small?1635407258521)

分析报告中也包含了协议统计：

![1635407292_617a55bcd30227a79c4d5.png!small?1635407292698](https://image.3001.net/images/20211028/1635407292_617a55bcd30227a79c4d5.png!small?1635407292698)

详细流量包数据：

![1635407341_617a55edc69e19110b957.png!small?1635407340293](https://image.3001.net/images/20211028/1635407341_617a55edc69e19110b957.png!small?1635407340293)

点击选中的某条记录，弹出相关信息：

![1635407451_617a565be6164516b58c9.png!small?1635407450307](https://image.3001.net/images/20211028/1635407451_617a565be6164516b58c9.png!small?1635407450307)

![1635409066_617a5caaef6febc60d2fb.png!small?1635409065313](https://image.3001.net/images/20211028/1635409066_617a5caaef6febc60d2fb.png!small?1635409065313)

## 工具三：cloud-pcap

### 项目地址：

> <https://github.com/thepacketgeek/cloud-pcap>

### 部署与界面：

![1635419423_617a851fc81073cc78c83.png!small?1635419421753](https://image.3001.net/images/20211028/1635419423_617a851fc81073cc78c83.png!small?1635419421753)

![1635413240_617a6cf84bbe567fe116f.png!small?1635413238457](https://image.3001.net/images/20211028/1635413240_617a6cf84bbe567fe116f.png!small?1635413238457)

## 结束

个人认为，借助此类可视化强的辅助系统，在写报告汇总的时候，可以更好展现流量数据，更清晰的反应事件信息。

## 其他在线流量分析网址：

> <https://apackets.com/upload>

![1635425739_617a9dcb478709008c00d.png!small?1635425739319](https://image.3001.net/images/20211028/1635425739_617a9dcb478709008c00d.png!small?1635425739319)

> <https://www.cloudshark.org/captures#>
>
> <https://www.cloudshark.org/captures/d9353f10683c>

![1635425864_617a9e480b3f2f024c5be.png!small?1635425864485](https://image.3001.net/images/20211028/1635425864_617a9e480b3f2f024c5be.png!small?1635425864485)

> <https://pcap.honeynet.org.my/v1/>

![1635425763_617a9de394fad95d637d1.png!small?1635425763589](https://image.3001.net/images/20211028/1635425763_617a9de394fad95d637d1.png!small?1635425763589)

