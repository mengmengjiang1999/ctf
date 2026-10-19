# 前言

这是一个用来检测 Docker 容器逃逸方法的小脚本，在拿到 Docker 容器权限后，可以很方便的使用这个工具去进行逃逸方法的检测。

写这个工具的起因还是因为没找到自己中意的逃逸检测工具，目前虽然已有了一些利用工具，但对逃逸的利用方法数量比较有限，而我只想要一个用来检测的工具，就像是检测
Linux 提权的那种脚本一样，让工具告诉我有哪些逃逸方法，我自己再灵活的进行容器逃逸。

目前该工具支持以下逃逸方法的检测：

  * 容器处于特权模式
  * 挂载了 Docker Socket
  * 挂载了宿主机 Procfs
  * 挂载了宿主机根或者宿主机 etc 目录
  * 开启了 Docker 远程 API 访问接口
  * CVE-2016-5195 DirtyCow 脏牛漏洞
  * CVE-2020-14386
  * CVE-2022-0847 DirtyPipe
  * CVE-2017-1000112
  * CVE-2021-22555
  * pod 挂载了宿主机 /var/log 目录
  * 当前容器有 CAP_DAC_READ_SEARCH 权限
  * 当前容器有 CAP_SYS_ADMIN 权限
  * 当前容器有 CAP_SYS_PTRACE 权限

后面还会不断更新支持新的逃逸方法，同时也欢迎您提 pr
以共同完善这个工具，工具项目地址：<https://github.com/teamssix/container-escape-check>

# 使用

这个工具使用起来非常简单，可以在 Docker 容器中一键运行：

    
    
    wget https://raw.githubusercontent.com/teamssix/container-escape-check/main/container-escape-check.sh | bash
    

如果 Docker 不通外网，也可以克隆项目到本地，再放到容器中运行：

    
    
    git clone https://github.com/teamssix/container-escape-check.git
    cd container-escape-check
    chmod +x container-escape-check.sh
    ./container-escape-check.sh
    

![image](https://image.3001.net/images/20220402/1648894043_6248205bb998dab353dee.png!small)

如果感觉还不错，记得给项目点个小星星(star) ✨

# 一些注意事项

  * 这个脚本需要在 Docker 容器中运行
  * 这里的检测方法大多是基于我自己的经验，可能会存在检测误检或者漏检的情况，如果您发现了这种情况，欢迎提 Issue

