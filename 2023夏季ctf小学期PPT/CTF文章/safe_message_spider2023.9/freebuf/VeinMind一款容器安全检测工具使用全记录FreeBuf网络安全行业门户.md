最近在调研国内外开源的容器安全相关工具，发现了很多优秀的项目，国外的项目有trivy、anchor等，在漏洞检测这块做的很出色了；而国内的项目不多，关注非漏洞检测的工具更少，所以对一款名为问脉的开源容器安全工具集比较感兴趣，遂记录初次使用的过程。

首先，了解一下官方描述的具体功能：

  1. 支持镜像中五种威胁的检测：恶意样本、后门、弱口令、敏感文件、异常历史命令

  2. 支持镜像资产清点

  3. 支持扫描本地镜像、仓库镜像，支持集成dockhub/harbor等主流仓库

  4. 支持在 github action / jenkins / gitlab 中进行集成

  5. 支持以平行容器的方式运行，也可下载源码本地编译使用

  6. 实现了一套插件系统，使用宿主程序可以一次调用多个插件进行扫描，可以自己针对具体业务编写插件

好像给官方提 Issue 或 PR 还能有礼品，打算依次体验一下如何使用

##  **一：用宿主程序进行本地镜像中五种威胁检测**

  * `./parallel-container-run.sh scan-host -h`，查看扫描本地镜像命令参数

![image](https://image.3001.net/images/20220715/1657875716_62d12d044e83721d2f8be.png!small)

  * `./parallel-container-run.sh scan-host`，使用所有已识别插件扫描本地所有镜像

![image](https://image.3001.net/images/20220715/1657875736_62d12d187ed449860e574.png!small)

发现其中一个高危的敏感信息，输出检测详情

![image](https://image.3001.net/images/20220715/1657875747_62d12d2384a06a96a1078.png!small)

  * 查看当前插件列表 `./parallel-container-run.sh list plugin`

![image](https://image.3001.net/images/20220715/1657875757_62d12d2d6267b34d41084.png!small)

  * `./parallel-container-run.sh scan-host -g "**/veinmind-weakpass"`，指定只使用弱口令插件扫描

![image](https://image.3001.net/images/20220715/1657875767_62d12d3786c48d1c9b19a.png!small)

发现高危的弱口令风险，输出检测详情

![image](https://image.3001.net/images/20220715/1657875776_62d12d4051a958ef7ee4b.png!small)

##  **二、使用宿主程序进行仓库镜像的检测**

  * ./parallel-container-run.sh scan-registry -h ，查看扫描远程仓库命令参数

![image](https://image.3001.net/images/20220715/1657875791_62d12d4f3341242f6ba00.png!small)

  * ./parallel-container-run.sh scan-registry oodo ，试试扫描 docker hub 公开仓库中的 oodo 镜像

![image](https://image.3001.net/images/20220715/1657875822_62d12d6ed13ead9e41fce.png!small)  
![image](https://image.3001.net/images/20220715/1657875831_62d12d7742f9d28ccaef8.png!small)  
![image](https://image.3001.net/images/20220715/1657875842_62d12d823e094261aca6c.png!small)

##  **三、在 CI/CD 中集成使用**

![image](https://image.3001.net/images/20220715/1657876042_62d12e4a6990012840da3.png!small)

##  **四、K8s快速安装部署**

![image](https://image.3001.net/images/20220715/1657876084_62d12e74bc462f84d2a6a.png!small)

##  **五、总结**

简单使用下来，问脉是很容易上手的，几乎没有理解成本。扫描本地镜像时检测出了好几个敏感信息和弱口令，看介绍官方还做了一个宿主，可以一个工具调用其他检测插件，还可以自己根据插件规范开发特定需求的插件进行调用，还是比较靠谱的，希望官方持续增加工具的检测规则，调研时提的
issue 集成 Jenkins 很快就实现了，看来是专人维护，项目活跃度蛮高的。

项目地址：https://github.com/chaitin/veinmind-tools

其他文章：[一种在构建阶段保护镜像安全的方法](https://www.freebuf.com/articles/container/340556.html)

