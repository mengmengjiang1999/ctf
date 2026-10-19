# **Dirmap安装：**

由于dirmap是由python开发的，需要依赖

gevent

requests

progressbar2

lxml

这四个库，所以：拉取镜像完成后需要直接读取他给的一个txt文件，就会自动安装上

python3 -m pip install -r requirement.txt

###  **1.从github上面拉取工具**

> git clone https://github.com/H4ckForJob/dirmap.git && cd dirmap && python3
> -m pip install -r requirement.txt

![1620628335_6098d36fed4d6dd2d4ab0.png!small?1620628336047](https://image.3001.net/images/20210510/1620628335_6098d36fed4d6dd2d4ab0.png!small?1620628336047)

拉取成功我们就可以去使用了![1620628344_6098d378e66781b080430.png!small?1620628344860](https://image.3001.net/images/20210510/1620628344_6098d378e66781b080430.png!small?1620628344860)

###  **2.参数详解**

> -h 帮助
>
> -t 线程
>
> -i 指定url或者ip
>
> -lcf 通过配置文件加载配置
>
> -iF 文件读取
>
> \--debug

###  **3.配置文件**

所有的扫描都要基于这个配置文件，所以说这个配置文件是这款工具的核心

参考

[
_https://blog.csdn.net/sc_Pease/article/details/108702325_](https://blog.csdn.net/sc_Pease/article/details/108702325)

![1620628372_6098d39454cf67ca1faf6.png!small](https://image.3001.net/images/20210510/1620628372_6098d39454cf67ca1faf6.png!small)

###  **4.演示：**

> python3 dirmap.py -i http://www.xxx.com.hk/ -lcf

![1620628533_6098d43544e22cd92723a.png!small?1620628533271](https://image.3001.net/images/20210510/1620628533_6098d43544e22cd92723a.png!small?1620628533271)

  

####  **基础使用**

> python3 dirmap.py -i https://www.xxx.com -lcf
>
> python3 dirmap.py -i 192.168.1.1 -lcf

####  **单目标，默认为http**

> python3 dirmap.py -i https://www.xxx.com -lcf
>
> python3 dirmap.py -i 192.168.1.1 -lcf

####  **子网（CIDR格式）**

> python3 dirmap.py -i 192.168.1.0/24 -lcf

####  **网络范围**

> python3 dirmap.py -i 192.168.1.1-192.168.1.254 -lcf

####  **文件读取**

> python3 dirmap.py -iF chaosec.txt -lcf

这样我们这款工具就部署好了

#  **Dirsearch**

### 1\. **从github上面进行拉取该工具：**

> git clone
> [_https://github.com/maurosoria/dirsearch_](https://github.com/maurosoria/dirsearch)&&
> cd dirsearch && python3 -m pip install -r requirements.txt

![1620628560_6098d4504548935349489.png!small?1620628560165](https://image.3001.net/images/20210510/1620628560_6098d4504548935349489.png!small?1620628560165)

也可分开执行，像我

> python3 -m pip install -r requirements.txt //读取该文件，就是更新或者安装相对应的pip库文件

![1620628613_6098d48508a97aa19d49c.png!small?1620628613082](https://image.3001.net/images/20210510/1620628613_6098d48508a97aa19d49c.png!small?1620628613082)

安装完成，运行如下：

![1620628687_6098d4cfd0ee53effc7c8.png!small?1620628687815](https://image.3001.net/images/20210510/1620628687_6098d4cfd0ee53effc7c8.png!small?1620628687815)

### 1\. **参数详解**

> -h, --help 查看帮助
>
> -u URL, --url=URL 设置url
>
> -L URLLIST, --url-list=URLLIST 设置url列表
>
> -e EXTENSIONS, --extensions=EXTENSIONS 网站脚本类型
>
> -w WORDLIST, --wordlist=WORDLIST 设置字典
>
> -l, --lowercase 小写
>
> -f, --force-extensions 强制扩展字典里的每个词条
>
> -s DELAY, --delay=DELAY 设置请求之间的延时
>
> -r, --recursive Bruteforce recursively 递归地扫描
>
> –scan-subdir=SCANSUBDIRS, --scan-subdirs=SCANSUBDIRS 扫描给定的url的子目录(用逗号隔开
>
> -t THREADSCOUNT, )
>
> –exclude-subdir=EXCLUDESUBDIRS, --exclude-subdirs=EXCLUDESUBDIRS
> 在递归过程中排除指定的子目录扫描(用逗号隔开)
>
> \--threads=THREADSCOUNT 设置扫描线程
>
> -x EXCLUDESTATUSCODES, --exclude-status=EXCLUDESTATUSCODES 排除指定的网站状态码(用逗号隔开)
>
> -c COOKIE, --cookie=COOKIE 设置cookie
>
> –ua=USERAGENT, --user-agent=USERAGENT 设置用户代理
>
> -F, --follow-redirects 跟随地址重定向扫描
>
> -H HEADERS, --header=HEADERS 设置请求头
>
> –random-agents, --random-user-agents 设置随机代理
>
> –timeout=TIMEOUT 设置超时时间
>
> –ip=IP 设置代理IP地址
>
> –proxy=HTTPPROXY, --http-proxy=HTTPPROXY 设置http代理。例如127.0.0.1:8080
>
> –max-retries=MAXRETRIES 设置最大的重试次数
>
> -b, --request-by-hostname 通过主机名请求速度，默认通过IP
>
> –simple-report=SIMPLEOUTPUTFILE 保存结果，发现的路径
>
> –plain-text-report=PLAINTEXTOUTPUTFILE 保存结果，发现的路径和状态码
>
> –json-report=JSONOUTPUTFILE 以json格式保存结果

![1620628717_6098d4ed65c17d447fe0f.png!small?1620628717416](https://image.3001.net/images/20210510/1620628717_6098d4ed65c17d447fe0f.png!small?1620628717416)

参考链接：https://blog.csdn.net/qq_44841017/article/details/105733100

### 2\. **演示**

> ./dirsearch.py -u http://www.xxx.com.hk/ –plain-text-report=/root/1.txt

扫描该网站，并且将路径和状态保存到/root/1.txt里面

发现这个不能指定路径，他只给出来他默认保存的路径，刚才那个参数应该就是区别是否输出状态码到这个扫描文件中![1620628728_6098d4f84bbf48be87dd5.png!small?1620628728503](https://image.3001.net/images/20210510/1620628728_6098d4f84bbf48be87dd5.png!small?1620628728503)

