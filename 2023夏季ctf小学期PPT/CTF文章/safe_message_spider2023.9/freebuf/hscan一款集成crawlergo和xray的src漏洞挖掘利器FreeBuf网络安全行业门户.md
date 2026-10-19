##  
0x01 hscan介绍

###  
1 hscan是什么

  
hscan是一款旨在使用一条命令替代渗透前的多条扫描命令，通过集成crawlergo扫描和xray扫描、dirsearch、nmap、jsfinder、nikto等工具，并使用-u
\ -f \ -d 等参数进行扫描目标方式的管理，最后利用docker安装完相关依赖进行封装，形成一款docker参数化扫描的工具。

使用-d参数时，输入主域名，可自动使用oneforall遍历并扫描子域名；挖掘src蛮方便；

  

### 2 hscan做了哪些

\- 使用docker封装，使用参数运行  
\- 使用crawlergo爬取网接，传给xray扫描  
\- 使用dirsearch遍历目录及文件，传给xray扫描  
\- 集成jsfinder、nmap、nikto等工具，可拓展  
\- 增加xray扫描结束判断，避免实测中流量多大引起xray漏洞报告数量严重缺失  
\- 增加-u url扫描/ -f 文件/ -d 域名的扫描入口方式  
\- 集成crawlergo所需的浏览器 / chrome  
\- 集成所有脚本所需的依赖包  
\- 根据域名及扫描时间命名xray扫描报告  
\- ...  
  
本来意欲所有工具多线程并发走，但是后来发现多线程流量大了xray扫描出的漏洞结果严重缺失，所以又控制了扫描频度

###  
  
3 hscan流程图

![](https://image.3001.net/images/20210110/1610274529_5ffad6e1803b6702cb784.png!small)

  

## 0x02 hscan使用

  

### 1 拉取代码并创建docker

    
    
    https://github.com/zongdeiqianxing/hscan

###  
2 在目录下执行命令，或直接执行docker_run.sh

    
    
    Usage:  
    python3 recon.py -u url   
    python3 recon.py -f filename        #-f 文件扫描  
    python3 recon.py -d domain         #输入主域名，自动使用OneForAll遍历并扫描子域名  
      
    example：  
    docker run -ti -v `pwd`/:/root/ zongdeiqianxing/hscan:v1 -u testphp.vulnweb.com
    

  

### 3 扫描完毕后需要手动多按几次`ctrl
c`退出，之后即可在目录下看到html文件和url文件，其中html文件为xray扫描输出，url文件为其他工具的扫描输出

![](https://image.3001.net/images/20210110/1610274789_5ffad7e598aa144ff1dd8.png!small)![](https://image.3001.net/images/20210110/1610274801_5ffad7f1a8c211ad03978.png!small)![](https://image.3001.net/images/20210110/1610274822_5ffad80678acd68447d53.png!small)![](https://image.3001.net/images/20210110/1610274830_5ffad80ebda74c3cd98ae.png!small)

  

