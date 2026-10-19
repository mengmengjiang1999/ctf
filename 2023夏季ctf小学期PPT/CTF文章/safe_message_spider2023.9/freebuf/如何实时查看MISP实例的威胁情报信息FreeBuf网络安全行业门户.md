![](https://image.3001.net/images/20200207/1581088082_5e3d7d52025a6.jpg!small)

**在这篇文章中，将会给大家介绍如何利用Misp-Dashboard实时查看来自MISP实例的威胁情报信息。Misp-Dashboard可以帮助研究人员实时查看MISP实例（ZMQ Feeds）传递的数据和统计结果。Misp-Dashboard是一款仪表盘工具，它可以作为一款威胁情报实时感知工具来使用，该工具继承了Gamification工具来显示每一个组织的贡献度以及实时排名，仪表盘内容还可以给安全操作中心（SOC）、安全研究团队或网络安全测试人员提供威胁追踪服务。**

##  功能介绍

###  实时信息仪表盘

> 1、可订阅来自不同MISP实例的多个ZMQ feeds；
>
> 2、可查看不同组织的实时贡献度；
>
> 3、显示实时可解析的威胁情报发布地理位置；

![](https://image.3001.net/images/20200207/1581088094_5e3d7d5e0e7b4.png!small)

###  地理定位仪表盘

> 1、提供历史地理位置信息，以支持安全团队、CSIRT或SOC在其选区内发现威胁；
>
> 2、从特定区域获取地理位置信息；

![](https://image.3001.net/images/20200207/1581088105_5e3d7d69d1fae.png!small)

###  贡献度仪表盘（集成Gamification）

> 1、所有组织的月贡献度；
>
> 2、最新贡献的组织（动态更新）；
>
> 3、所有组织的贡献等级；
>
> 4、每一个组织的贡献类别；
>
> 5、选中组织的当前排名（动态更新）；

![](https://image.3001.net/images/20200207/1581088122_5e3d7d7aa312a.png!small)![](https://image.3001.net/images/20200207/1581088122_5e3d7d7ab7024.png!small)

###  用户仪表盘

> 1、显示平台使用时间和使用方式；
>
> 2、登录和贡献时间；

![](https://image.3001.net/images/20200207/1581088137_5e3d7d89c9437.png!small)

###  趋势仪表盘

> 1、提供实时信息以支持安全团队、CSIRT或SOC发现威胁和恶意活动；
>
> 2、显示更多的活动事件、分类和标签；
>
> 3、显示讨论信息；

![](https://image.3001.net/images/20200207/1581088162_5e3d7da22044a.png!small)

##  工具安装

注意：该工具目前只支持在类Unix操作系统平台上运行，比如说Linux等等。

首先，使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/MISP/misp-dashboard.git

然后切换到本地项目目录中，运行下列命令：

    
    
    ./install_dependencies.sh

更新配置文件config.cfg，并匹配用户本地系统，此时需要修改的参数如下：

    
    
    edisGlobal -> host
    
        RedisGlobal -> port
    
        RedisGlobal -> zmq_url
    
        RedisGlobal -> misp_web_url
    
        RedisMap -> pathMaxMindDB

##  工具更新

重新运行install_dependencies.sh脚本来获取新的依赖组件：

    
    
    ./install_dependencies.sh

对比config.cfg.default文件中的修改项，然后重新更新你的配置文件config.cfg。

请确保当前没有zmq Python3脚本正在运行，因为该脚本会阻止项目更新：

    
    
    + virtualenv -p python3 DASHENV
    
        Already using interpreter /usr/bin/python3
    
        Using base prefix '/usr'
    
        New python executable in /home/steve/code/misp-dashboard/DASHENV/bin/python3
    
        Traceback (most recent call last):
    
          File "/usr/bin/virtualenv", line 9, in <module>
    
            load_entry_point('virtualenv==15.0.1', 'console_scripts', 'virtualenv')()
    
          File "/usr/lib/python3/dist-packages/virtualenv.py", line 719, in main
    
            symlink=options.symlink)
    
          File "/usr/lib/python3/dist-packages/virtualenv.py", line 942, in create_environment
    
            site_packages=site_packages, clear=clear, symlink=symlink))
    
          File "/usr/lib/python3/dist-packages/virtualenv.py", line 1261, in install_python
    
            shutil.copyfile(executable, py_executable)
    
          File "/usr/lib/python3.5/shutil.py", line 115, in copyfile
    
            with open(dst, 'wb') as fdst:
    
        OSError: [Errno 26] Text file busy: '/home/steve/code/misp-dashboard/DASHENV/bin/python3'

接下来，运行下列命令重启系统：

    
    
    ./start_all.sh

或

    
    
    ./start_zmq.sh
    
        ./server.py &

##  启动系统

注意：Misp-Dashboard仅需常规权限即可运行，无需使用root权限。

确保本地已运行了Redis服务器：

    
    
    redis-server --port 6250

激活你的Virtualenv环境：

    
    
    . ./DASHENV/bin/activate

启用zmq_subscriber来监听MISP feed：

    
    
    ./zmq_subscriber.py &

开启调度程序来处理接收到的信息：

    
    
    ./zmq_dispatcher.py &

开启Flask服务器：

    
    
    ./server.py &

访问接口：

    
    
    http://localhost:8001/

或者，你也可以直接运行start_all.sh脚本来自动运行上述所有命令。

###  身份认证

我们可以在config/config.cfg文件中设置“auth_enabled = True”来启用身份认证功能。

###  zmq_subscriber选项

    
    
    A zmq subscriber. It subscribe to a ZMQ then redispatch it to the MISP-dashboard
    
        optional arguments:
    
          -h, --help            show this help message and exit
    
          -n ZMQNAME, --name ZMQNAME
    
                                The ZMQ feed name
    
          -u ZMQURL, --url ZMQURL
    
                                The URL to connect to

##  使用mod_wsgi在产品中完成部署

安装Apache mod-wsgi（Python 3）：

    
    
    sudo apt-get install libapache2-mod-wsgi-py3

如果你安装了Python2版本的mod_wsgi，那么旧版本的将会被替换：

    
    
    The following packages will be REMOVED:
    
          libapache2-mod-wsgi
    
        The following NEW packages will be installed:
    
          libapache2-mod-wsgi-py3

接下来，配置项目文件夹权限和文件（“/etc/apache2/sites-available/misp-dashboard.conf”）：

    
    
    <VirtualHost *:8001>
    
            ServerAdmin admin@misp.local
    
            ServerName misp.local
    
            DocumentRoot /var/www/misp-dashboard
    
            WSGIDaemonProcess misp-dashboard \
    
               user=misp group=misp \
    
               python-home=/var/www/misp-dashboard/DASHENV \
    
               processes=1 \
    
               threads=15 \
    
               maximum-requests=5000 \
    
               listen-backlog=100 \
    
               queue-timeout=45 \
    
               socket-timeout=60 \
    
               connect-timeout=15 \
    
               request-timeout=60 \
    
               inactivity-timeout=0 \
    
               deadlock-timeout=60 \
    
               graceful-timeout=15 \
    
               eviction-timeout=0 \
    
               shutdown-timeout=5 \
    
               send-buffer-size=0 \
    
               receive-buffer-size=0 \
    
               header-buffer-size=0 \
    
               response-buffer-size=0 \
    
               server-metrics=Off
    
            WSGIScriptAlias / /var/www/misp-dashboard/misp-dashboard.wsgi
    
            <Directory /var/www/misp-dashboard>
    
                WSGIProcessGroup misp-dashboard
    
                WSGIApplicationGroup %{GLOBAL}
    
                Require all granted
    
            </Directory>
    
            LogLevel info
    
            ErrorLog /var/log/apache2/misp-dashboard.local_error.log
    
            CustomLog /var/log/apache2/misp-dashboard.local_access.log combined
    
            ServerSignature Off
    
        </VirtualHost>

##  项目地址

> Misp-Dashboard：【[GitHub传送门](https://github.com/MISP/misp-dashboard)】

 *** 参考来源：[MISP](https://github.com/MISP/misp-dashboard)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

