## ****概述****

一个真实的Linux恶意软件入侵环境，往往包含有病毒文件、病毒进程、恶意启动项、网络通信流量等病毒项，若我们只获得单一的病毒文件，很难还原出恶意软件的整个攻击环境，从而不便于对攻击链进行全面的研究分析，以及产品安全能力测试。下面，介绍一种基于Docker的方法，可以自动化地采集及还原恶意软件的整个攻击场景，以最大程度地模拟主机中毒的环境，方便后续对恶意软件进行研究与分析。

该方法的原理是，使用bash脚本自动化收集中毒主机上的病毒项，然后打包成容器环境，最后通过Docker在本地模拟运行，这时生成的Docker容器就包含了完整的恶意软件环境。

![](https://image.3001.net/images/20201126/1606375883_5fbf59cbb3125b25f1dd9.png!small)

##  ** **详细步骤****

如下，以StartMiner（8220挖矿家族）的中毒环境作为演示，通过命令可以看到主机中包含有恶意定时任务、病毒文件、病毒进程等信息。

![](https://image.3001.net/images/20201126/1606375902_5fbf59dee0368e52376f2.png!small)

采集脚本具体的代码如下，主要采集以下目录的文件：

  * /tmp/、/root/、/opt/ 病毒文件常见目录
  * 定时任务文件
  * ssh缓存文件
  * syslog和audit安全日志
  * 进程信息
  * 网络信息

![](https://image.3001.net/images/20201126/1606375922_5fbf59f2a1f809aacaf7a.png!small)

然后自动化生产docker-compose.yml文件，用于一键创建docker容器。

![](https://image.3001.net/images/20201126/1606375971_5fbf5a23816b20c3d246e.png!small)

malbox.sh脚本运行数秒后，即可打包好所有病毒项，生成文件malbox.tar.gz。

![](https://image.3001.net/images/20201126/1606375983_5fbf5a2f6b2efb07ba1c8.png!small)

将malbox.tar.gz在本地解压缩，malbox目录便包含Docker环境的所需的文件系统和配置文件，docker-compose.yml的功能为映射关键目录，及模拟执行恶意命令。在运行之前需要自定义下docker-compose.yml的信息，填上病毒家族名，以及启动时要运行的命令（可以参考ps.txt及netstat.txt填上需要模拟的病毒进程命令）。

![](https://image.3001.net/images/20201126/1606375994_5fbf5a3a6e2ac980111a6.png!small)

修改完后，使用命令docker-compose up -d即可一键部署容器，查看容器列表，若出现了startmienr_2010便说明容器运行成功了。

![](https://image.3001.net/images/20201126/1606376020_5fbf5a5445635c162ba7e.png!small)

恶意软件容器所使用的基础镜像为malbox，该镜像在ubuntu镜像基础上新增了恶意软件常用到的一些命令及服务（wget、curl、ssh、crontab等），以达到更好的模拟效果。

![](https://image.3001.net/images/20201126/1606376032_5fbf5a608810191c9f438.png!small)

使用docker exec -it startminer_2010
/bin/bash命令，就能进入到容器，此时的环境就跟中毒主机的环境几乎一样了，可以在该环境中进行排查分析。

![](https://image.3001.net/images/20201126/1606376042_5fbf5a6a858d65220f113.png!small)

查看进程，也能清晰地看到恶意的下载进程，以及CPU占用率极高的挖矿进程。

![](https://image.3001.net/images/20201126/1606376054_5fbf5a7629ee1626c6fb5.png!small)

容器中的syslog日志和audit.log日志，也有助于研究员对整个恶意软件的攻击链进行溯源。

![](https://image.3001.net/images/20201126/1606376066_5fbf5a820694149983669.png!small)

audit可以使用自定义规则进行监控，将可疑行为按照ATT&CK矩阵进行分类。

![](https://image.3001.net/images/20201126/1606376078_5fbf5a8e30006bc74d171.png!small)

##  ** **总结****

模拟出来的恶意软件容器，方便搭建及部署，若有蜜网或EDR环境，还可以将容器接入到其中以更好地检测收集恶意软件的恶意流量、恶意行为。

##  ** **参考链接****

https://github.com/vulhub/vulhub/

