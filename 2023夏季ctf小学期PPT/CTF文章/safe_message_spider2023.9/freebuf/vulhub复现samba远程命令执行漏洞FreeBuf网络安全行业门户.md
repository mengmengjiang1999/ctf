****Samba远程命令执行漏洞****

 ** **目的**** ：检测是否存在Samba漏洞，利用Samba漏洞远程控制目标系统

 ** **目标系统（vulhub靶机）：****

  1. 启动环境，进入路径为cd /home/vulhub/vulhub-master/samba/CVE-2017-7494
  2. 运行测试环境docker-compose up -d

 ** **Kali渗透：****

  1. 信息收集：

扫描目标主机，查看开放端口及操作系统等信息，发现其开放445端口，可能存在漏洞

![](https://image.3001.net/images/20201201/1606819451_5fc61e7b45f1db1755564.png!small)

  2. 漏洞探测：

使用metasploit中Samba漏洞扫描模块检测出存在漏洞：

![](https://image.3001.net/images/20201201/1606819466_5fc61e8a5c7cc3d844c0e.png!small)

  3. 漏洞验证及利用：

利用漏洞获取目标系统远程控制权限：

![](https://image.3001.net/images/20201201/1606819481_5fc61e998e2b2d455a99f.png!small)

获取shell：

![](https://image.3001.net/images/20201201/1606819500_5fc61eac1663413d7212d.png!small)

