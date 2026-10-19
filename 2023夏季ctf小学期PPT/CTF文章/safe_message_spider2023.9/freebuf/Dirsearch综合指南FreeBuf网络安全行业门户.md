***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

在本文中，我们将学习如何使用 Dirsearch。

说起国内的御剑套装，相信各位都已经非常熟悉了。但御剑已经好多年不更新了，而且需要windows，有时候线程设置大了点，扫了半天中途还可能卡住不动了，也没有实时的数据保存，前功尽弃。总之各种不爽。

现在好用的web scanner也层出不穷，我根据自己的需求和实际使用体验，最终选择了dirsearch这款工具。

## 基本情况

它是一个命令行工具，旨在暴力破解网站中的目录和文件。

这是一个基于 Python 的命令行网站目录扫描器，旨在暴力破解站点结构，包括目录和文件。

## 安装

要求：python 3.7 或更高版本

选择以下安装选项之一：

    
    
    使用 git 安装： 
    git clone https://github.com/maurosoria/dirsearch.git
    使用 ZIP 文件安装： 
    https://github.com/maurosoria/dirsearch/archive/master.zip
    使用 Docker 安装： 
    docker build -t "dirsearch:v0.4.1"（ 更多信息 ）
    使用 Kali Linux 安装： 
    sudo apt-get install dirsearch
    使用 PyPi 安装： 
    pip3 install dirsearch
    

安装此工具后，我们需要浏览其目录并搜索 dirsearch.py​​。  
现在，我们只需要使用 [-h] 参数运行这个 python 编写的工具，通过这个我们可以看到它的所有参数及其功能。  
![图片.png](https://image.3001.net/images/20210616/1623832087_60c9b617e617c45dc0a1d.png!small)

## 简单使用

    
    
    python3 dirsearch.py -u https://target
    python3 dirsearch.py -e php,html,js -u https://target
    python3 dirsearch.py -e php,html,js -u https://target -w /path/to/wordlist

![图片.png](https://image.3001.net/images/20210616/1623832323_60c9b703775a208d98dbf.png!small)

## 以不同格式保存输出

 **以简单格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --simple-report=report  
      
    我们可以清楚地看到，我们的简单格式结果已成功创建。 现在，我们可以轻松地分析我们的结果。

 **以 JSON 格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --json-report=report  
    同样，如上所述，我们使用 nano 命令开始分析我们的结果。

 **以 XML 格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --xml-report=report

 **以 Markdown 格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --markdown-report=report

 **以 CSV 格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --csv-report=report

 **以普通格式保存输出**

    
    
    ./dirsearch.py​​ -u http://testphp.vulnweb.com/ --plain-text-report=report

## 递归扫描

通过使用 -r | --recursive 参数，dirsearch 将递归地强制所有目录。

    
    
    python3 dirsearch.py -e php,html,js -u https://target -r  
    现在，在完成通常的扫描一段时间后，它将遍历每个子文件夹以进行递归扫描。 正如我们在此屏幕截图中清楚地看到的那样，它针对子文件夹并告诉我们我们的攻击未完成的工作。

还有更多技巧欢迎各位表哥们继续发掘

 **获取更多学习资料、想加入社群、深入学习，请扫我的二维码或加Memory20000427。**

![image](https://image.3001.net/images/20210419/1618845155_607d9de3a20531de59a08.jpg!small)

  

