# 搭建 CentOS7 + vscode + suricata 6.0.12 源码修改调试环境

## 一、简介

### 1\. 需求

最近有个使用suricata进行日志分析的需求，通过分析协议发现 suricata 对于http
的解析输出日志中，仅包含请求头和URL字段，不包含请求体和响应体的数据。

虽然第二篇文章-[流量分析工具（二）：centos7 + suricata + redis +
ELK](https://www.freebuf.com/sectool/364203.html)  
-中提到可以通过编写规则和 lua 脚本的方式获取到 http 的请求体和响应体，但是那个方式无疑不是最终的解决方案，此时修改源码是最理想的方式。  
通过调研，可以通过修改源码的方式增加suricata http 协议对于请求体和响应体输出。此外，对于给suricata 增加 kafka
日志输出模块的功能也是需要开发调试环境的。

### 2\. 依赖环境

    
    
    系统环境：centos7
    需要依赖：
    	VSCodeUserSetup-x64-1.78.2.exe
    	htp-0.5.17.tar.gz
    	LuaJIT-2.0.5.tar.gz
    	suricata-6.0.12.tar.gz
    下载方式: 
        https://www.openinfosecfoundation.org/download/suricata-6.0.12.tar.gz
        https://github.com/OISF/libhtp/releases/download/0.5.17/htp-0.5.17.tar.gz
        http://luajit.org/download/LuaJIT-2.0.5.tar.gz
    

### 3\. 调试步骤

  1. 先 运行 `./configure`生成 `MakeFile`文件

  2. 然后 运行 `make`命令，然后运行 `make install`，安装生成可执行文件 `/usr/bin/suricata`，CentOS 是安装在 `/usr/bin/suricata`，ubuntu 是安装在 `/bin/suricata`

  3. 修改源码之后，重新执行 `make && make install`

  4. 运行 F5 执行加载 `lunch.json`文件中的配置的命令和参数， 即可以开始下断点调试

  5. 如果还有修改代码，则重新再次 `make && make install`，然后 F5 运行调试

## 二、CentOS 7 安装 suricata 6.0.12

### 1\. 安装调试环境

    
    
    yum install gcc make cmake gdb -y
    

### 2\. suricata安装依赖

编译的时候打开 debug 功能，可以看到 debug 日志，打开参数`--enable-debug`

    
    
    # 更新yum源
    /bin/mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak
    curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo
    yum install -y http://rpms.famillecollet.com/enterprise/remi-release-7.rpm
    
    # 安装依赖
    yum install -y python3-pip gcc tcl htop net-tools gcc libpcap-devel pcre-devel libyaml-devel file-devel zlib-devel jansson-devel nss-devel libcap-ng-devel libnet-devel tar make libnetfilter_queue-devel lua-devel PyYAML cargo libevent-devel libffi-devel libmaxminddb-devel lz4-devel openssl-devel python3-devel rustc unzip hiredis-devel kernel-devel gperftools-libs -y
    
    
    
    # 安装LuaJIT
    cd /tmp
    wget http://luajit.org/download/LuaJIT-2.0.5.tar.gz
    tar -zxf LuaJIT-2.0.5.tar.gz
    cd LuaJIT-2.0.5/
    ./configure
    make && make install
    cd ..
    
    # 安装HTP库
    cd /tmp
    wget https://github.com/OISF/libhtp/releases/download/0.5.17/htp-0.5.17.tar.gz
    tar -xzvf htp-0.5.17.tar.gz
    cd htp-0.5.17/
    ./configure
    make && make install
    cd ..
    
    echo "/usr/local/lib" >> /etc/ld.so.conf
    ldconfig
    
    # 安装 redis，可选
    yum --enablerepo=remi install redis -y
    sed -i "s?client-output-buffer-limit pubsub 32mb 8mb 60?client-output-buffer-limit pubsub 2gb 1gb 60?" /etc/redis/redis.conf
    systemctl daemon-reload
    # systemctl status redis.service
    systemctl start redis.service
    systemctl enable redis.service
    
    
    
    # 安装 suricata
    cd /tmp
    wget https://www.openinfosecfoundation.org/download/suricata-6.0.12.tar.gz
    tar zxvf suricata-6.0.12.tar.gz
    cd suricata-6.0.12/
    ./configure \
        --prefix=/usr \
        --sysconfdir=/etc \
        --localstatedir=/var \
        --enable-nfqueue \
        --enable-luajit \
        --with-libluajit-includes=/usr/local/include/luajit-2.0/ \
        --with-libluajit-libraries=/usr/local/lib/ \
        --enable-redis \
        --enable-hiredis \
        --enable-profiling \
        --enable-geoip \
        --enable-rust \
        --enable-debug \
        --enable-profiling #启用性能分析
    
    make
    make install
    make install-conf
    /bin/cp -d libhtp/htp/.libs/libhtp.so* /lib64/
    ldconfig
    
    suricata -V
    
    # 打开 suricata 的单线程调试模式
    suricata -i ens33 -c /etc/suricata/suricata_redis.yaml -v --runmode single
    
    # 安装参考
    https://www.osgeo.cn/suricata/install.html
    

### 2\. vscode 远程打开项目目录

在 windows 上使用 VS Code 打开 CentOS 上的项目目录  
![图片.png](https://image.3001.net/images/20230604/1685886650_647c96baa19d0c38c20d2.png!small)

打开项目目录  
![图片.png](https://image.3001.net/images/20230604/1685886799_647c974f07bad7c13a926.png!small)

安装插件 C/C++、GDB Debug

![image](https://image.3001.net/images/20230604/1685886412_647c95cc38c4a0f27684a.png!small)

![image](https://image.3001.net/images/20230604/1685886426_647c95dabdf5bde29d630.png!small)

添加调试配置

![image](https://image.3001.net/images/20230604/1685886439_647c95e74f4d80403e1e8.png!small)

选择 GDB Debug，必须要先安装了 `GDB Debug`插件才会出现这个功能

![image](https://image.3001.net/images/20230604/1685886453_647c95f5a5f220c049582.png!small)

修改
`lunch.json`配置，参考链接：<https://blog.csdn.net/NotANumber123/article/details/125925974>

    
    
    # lunch.json
    {
        "version": "0.2.0",
        "configurations": [
            {
                "type": "cppdbg",
                "request": "launch",
                "name": "(gdb) 启动",
                # 放入 suricata 的路径，可以用 which 参数查看
                "program": "/usr/bin/suricata",
                //要启动的程序命令参数
                "args": [
                    "-i", "ens33", "-c", "/etc/suricata/suricata.yaml", "-v", "--runmode", "single"
                ],
                //在程序进入main函数的时候停止
                "stopAtEntry": true,
                "MIMode": "gdb",
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    
    
    #查看 suricata 存放的目录
    [root@sensor nta-suricata]# which suricata
    /usr/bin/suricata
    

如果提示 gdb 找不到，则新建或 ~~ ~~修改~~~~`.vscode/c_cpp_properties.json`文件

    
    
    {
        "configurations": [
            {
                "name": "Linux",
                # 这一步是消除引用的波浪线的，但是没生效，就先留着吧~~~~
                "includePath": [
                    "${workspaceFolder}/src/**",
                    "${workspaceFolder}/**"
                ],
                "defines": [],
                "compilerPath": "/usr/bin/gcc",
                "cStandard": "c11",
                "cppStandard": "c++98",
                "intelliSenseMode": "linux-gcc-x64"
            }
        ],
        "version": 4
    }
    

### 3\. F5调试进入-主程序入口

找到main函数的入库，因为在 `lunch.json`中设置了在主函数下断点，所以按下 F5 的时候能看到在主函数的位置停止。

    
    
    cat ${workspaceFolder}/src/main.c
    

![图片.png](https://image.3001.net/images/20230604/1685887120_647c989061add0e427762.png!small)

修改`${workspaceFolder}/src/suricata.c`文件，新建一行输出日志的代码，在这行下断点（在 1121
行的行号前面鼠标左键单击），看看效果

    
    
    SCLogNotice("test - 123456");
    

![图片.png](https://image.3001.net/images/20230604/1685887755_647c9b0b99988d61f9a81.png!small)

重新编译运行

    
    
    make
    make install
    

![图片.png](https://image.3001.net/images/20230604/1685888030_647c9c1e24721cc610d3a.png!small)

按 F5 运行调试，然后下一步  
![图片.png](https://image.3001.net/images/20230604/1685887792_647c9b300a3112284c6db.png!small)

![图片.png](https://image.3001.net/images/20230604/1685888075_647c9c4be3f2b8e0780f8.png!small)

到此，就算是配置好了，可以调试了。

