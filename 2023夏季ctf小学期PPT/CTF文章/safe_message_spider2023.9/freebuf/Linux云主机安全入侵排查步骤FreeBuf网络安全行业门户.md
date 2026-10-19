# 导语

经常有用户报障系统被植入恶意程序，如挖矿软件、ddos攻击病毒、syn映射攻击病毒等，可以按照以下流程为用户排查入侵病毒类型：

# 一、定位病毒进程

对于用户反馈云主机性能卡顿，CPU和内存占用较高的情况：

执行TOP命令，查看占用CPU较高的异常进程，一般多为80%以上，有个别病毒占用CPU可能不高，但是从command名称明显不是系统进程或用户进程，如TSM，Lixsyn，ynlyvtpxia等。

如图所示：

![1684821729_646c56e1f2d811319e761.png!small](https://image.3001.net/images/20230523/1684821729_646c56e1f2d811319e761.png!small)

注意运行异常进程的用户，大部分为root，也有可能为其他应用用户，一般为可以登录系统的用户，病毒破解用户登录密码后使用该用户登录系统，根据入侵的用户的权限等将病毒程序上传到不同目录，此类病毒一般具有防止被删除和进程自动启动的功能。

即无法从目录中删除，删除后还会自动恢复。使用Kill -9命令清理进程后片刻会再次自动启动该进程。

上图红框中的即为病毒程序，虽然占用CPU和出网带宽不高，但是仍然具有防止删除和自动启动的特征。

找到进程后记录PID进程号，后续定位病毒程序未知会用到。  
  
对于用户反馈连接云主机卡顿，但CPU和内存占用不高的情况，可能是云主机出网带宽跑满导致。此时ping云主机公网IP会出现大量丢包。

通过VNC连接云主机，使用iftop命令可以定位到占用带宽较高的进程 **（iftop命令使用教程可参考文档《Linux流量监控工具 - iftop
(最全面的iftop教程)》：** https://developer.jdcloud.com/article/1729 **）**
，一般多为同一端口有大量外部公网IP的数据进出，此种现象也多为病毒或恶意攻击导致。

使用iftop -P定位占用流量较高的端口，再使用lsof -i:端口号命令查看占用端口的进程号并记录。

# 二、定位病毒程序位置

按照第一步定位的病毒进程号定位运行的病毒程序路径，命令如下

ll /proc/进程号

linux系统对于每个运行的进程会在/proc目录下建立以进程号命名的临时目录，该目录记录了进程的相关信息，其中exe项目即为进程对应的程序路径，如图所示：

![1684821751_646c56f767b27f823b31a.png!small](https://image.3001.net/images/20230523/1684821751_646c56f767b27f823b31a.png!small)

病毒文件被上传到了/usr/bin目录下，显然病毒获取了root权限。有时也会放置在/tmp目录下，因病毒获得的不同用户权限而异。进入文件所在路径，大多数病毒文件删除后还会再次出现，无法彻底清除。

这也是我们一般建议用户中毒后重置系统的原因。将病毒文件或者病毒文件所在的由病毒创建的目录生成tar包，然后使用lrzsz工具下载至本地。

单个文件之所以打tar包是避免下载至本地后防止被杀毒软件删除，之后上传至病毒分析网站后如果不是tar包格式有时也会无法分析出结果。  
病毒分析网站有很多，常用的有：

  * https://x.threatbook.cn/
  * http://www.virustotal.com
  * http://r.virscan.org

以https://x.threatbook.cn/为例，打开网页后，点击下图红框的上传文件，选择病毒tar包上传。

![1684821766_646c57063d02e4e15da88.png!small](https://image.3001.net/images/20230523/1684821766_646c57063d02e4e15da88.png!small)

等待文件上传完成后，点击下面红框中的扫描文件，进入分析页面，网站会使用不同的安全软件分析病毒并给出分析结果。

有些能检测出是病毒，有些检测不是病毒，有一款以上的文件报毒即可确认是病毒。

如图所示，扫描出病毒是DDoS攻击病毒 。

![1684821778_646c57127b5dd20974aac.png!small](https://image.3001.net/images/20230523/1684821778_646c57127b5dd20974aac.png!small)

确认病毒类型后，可以尝试参考文档《Linux系统对DDoS木马病毒排查及清除》（附产品）进行清除。

如果无法彻底清除，建议备份好系统中的个人数据后使用私有镜像或官方镜像重置系统。  
通常绝大多数安全入侵都是通过完全开放的端口策略以及应用漏洞实现，因此使用默认安全组开放所有端口的安全风险极高。

 **特别提示：**

针对linux云主机，建议您绑定linux开放22端口安全组，移除默认安全组，单独开放需要的端口，操作方法请参考下列文档：

安全组概述（https://docs.jdcloud.com/cn/virtual-machines/security-group-overview）

安全组绑定云主机（https://docs.jdcloud.com/cn/virtual-machines/associate-security-group）

安全组解绑云主机（https://docs.jdcloud.com/cn/virtual-machines/disassociate-security-group）

配置安全组入站规则（https://docs.jdcloud.com/cn/virtual-machines/configurate-inbound-rules）

配置安全组出站规则（https://docs.jdcloud.com/cn/virtual-machines/configurate-outbound-rules）

修改ssh协议端口（https://docs.jdcloud.com/cn/virtual-machines/ssh-service-change-port）

使用复杂密码并定期更换

同时定期对您的云主机制作私有镜像（https://docs.jdcloud.com/cn/virtual-machines/create-private-image）和云硬盘快照（https://docs.jdcloud.com/cn/cloud-disk-service/create-clouddisk-snapshot），备份您的系统配置和数据，以便在出现意外时可以使用私有镜像重置您的系统。

