## Hashcat介绍

Hashcat号称宇宙最强密码破解工具，其是一款开源软件，有针对Windows、Mac和Linux的版本，支持CPU、GPU、APU、DSP和FPGA等多种计算核心，支持多种hash散列算法，支持对rar、office、pdf、windows账户、wifi等多种密码的破解，本文以Windows
10系统下的Hashcat安装配置、具体密码破解方法和密码保护技巧等展开介绍。

## 安装配置

首先前往[Hashcat官网](https://hashcat.net/hashcat/)下载软件包，我下载的版本为
v6.1.1，此处需注意下载hashcat binaries名称后面的软件包，其已经编译生成了直接可以运行的exe可执行文件，而hashcat
sources需要利用类似MinGW的编译工具对Hashcat源码进行编译来生成可执行文件，下载好Hashcat软件包之后可以直接在主目录下通过命令行运行Hashcat（Hashcat为命令行模式工作），注意一定要进入Hashcat软件包的主目录来运行hashcat，此处推荐一个方法可以在软件包主目录的地址栏直接输入cmd使得命令行窗口直接将地址跳转到Hashcat主目录，最后我用的测试电脑配置如下，马上我们就可以开始Hashcat的探索之旅。  
![image](https://image.3001.net/images/20210311/1615440260_6049a9846407f44238773.png!small)  
同时，在使用Hashcat进行密码破解的时候需要辅助工具来获取加密文件的Hash，此处选用John the
Ripper来获取加密文件的Hash（具体版本john-1.9.0），其也是通过命令行来运行，在密码破解和保护小结将具体介绍其使用方法，运行John the
Ripper需要安装python和perl来运行其对应脚本文件，同时需要配置相应的环境变量。

## Hashcat使用

首先我们可以通过hashcat --help指令来查看Hashcat常用的命令行，这也是学习任何一种语言或者方法时最实用的技术。

    
    
    -a  指定要使用的破解模式，其值参考后面对参数。“-a 0”字典攻击，“-a 1” 组合攻击；“-a 3”掩码攻击。
    -m  指定要破解的hash类型，如果不指定类型，则默认是MD5
    -o  指定破解成功后的hash及所对应的明文密码的存放位置,可以用它把破解成功的hash写到指定的文件中
    --force 忽略破解过程中的警告信息,跑单条hash可能需要加上此选项
    --show  显示已经破解的hash及该hash所对应的明文
    --increment  启用增量破解模式,你可以利用此模式让hashcat在指定的密码长度范围内执行破解过程
    --increment-min  密码最小长度,后面直接等于一个整数即可,配置increment模式一起使用
    --increment-max  密码最大长度,同上
    --outfile-format 指定破解结果的输出格式id,默认是3
    --username   忽略hash文件中的指定的用户名,在破解linux系统用户密码hash可能会用到
    --remove     删除已被破解成功的hash
    -r       使用自定义破解规则
    

同时也可以查看[Hashcat](https://hashcat.net/wiki/)的wiki，上面包括Hashcat常用的攻击类型、常见Hash类型对照表、掩码设置方式、支持的平台类型等都有详细说明，这里就不再详细说明，有任何疑问可以直接后台联系。

## 密码破解和保护

首先测试了下所用配置笔记本的算力，通过指令hashcat -b即可看到其针对各种Hash类型独立显卡GeForce 940MX、核显Graphics
630以及CPU Intel Core(TM) i7-7700HQ（对应图中设备1、2以及3）各自的算力。  
![image](https://image.3001.net/images/20210311/1615440293_6049a9a55caa9d505041f.png!small)下面针对rar、office、pdf加密文件选用掩码攻击的方式以及zip加密文件选用字典攻击的方式来对比密码破解效率。  
新建测试用rar加密文件“test.rar”，在john-1.9.0的run目录下运行命令行，输入指令

    
    
    rar2john.exe test.rar
    

得到结果

    
    
    test.rar:$rar5$16$17ef7a950b46655b9885e6cdade46948$15$d132b6edad975688f01a00df22ef20c1$8$6b4b7c0213e56414
    

在Hashcat的wiki中点击进入Example
hashes搜索“rar5”查出其对应ID为13000，之后进入Hashcat命令行，输入命令如下，其中-m后面对应的是所查Hash的ID，-a后面的3对应为掩码攻击，?d对应一个数字。

    
    
    hashcat.exe -m 13000 -a 3 $rar5$16$17ef7a950b46655b9885e6cdade46948$15$d132b6edad975688f01a00df22ef20c1$8$6b4b7c0213e56414 ?d?d?d?d -o out.txt
    

最后运行结果如图，将破解所得密码导入out.txt文件，运行过程中可以通过按S键来查看实时破解状态。  
![image](https://image.3001.net/images/20210311/1615440357_6049a9e58b7c274221fde.png!small)后续破解word加密文件的指令及输出如下：

    
    
    python office2john.py test.docx                 获取word加密文件的Hash指令(此处需要安装python并配置环境变量)
    test.docx:$office$*2013*100000*256*16*561f4dcaaac333e7c06d150f9ea5aea2*ef4e7b026217124561ecb865b324eac4*e9ef4a859f2c81581db0e27d9ce48e6451b82cd1641941e8adc10dc5600969cb                                所得Hash返回结果
    hashcat.exe -m 9600 -a 3 $office$*2013*100000*256*16*561f4dcaaac333e7c06d150f9ea5aea2*ef4e7b026217124561ecb865b324eac4*e9ef4a859f2c81581db0e27d9ce48e6451b82cd1641941e8adc10dc5600969cb ?d?d?d?d -o out.txt                 Hashcat破解对应hash
    

破解pdf加密文件的指令及输出如下：

    
    
    perl pdf2john.pl test.pdf                       获取pdf加密文件的Hash指令(此处需要安装perl并配置环境变量)
    test.pdf:$pdf$4*4*128*-3904*0*16*55f913d20e34724fd70d3004f5e43166*32*7a29310ea5dc0276d34c1bef24595d61984a08eb759eaba56bd4887a260bbcce*32*de0c200bbe6887a980dc429edbdabc40f39a368841d804afefa726b2bd7c7b24   所得Hash返回结果
    hashcat.exe -m 10500 -a 3 $pdf$4*4*128*-3904*0*16*55f913d20e34724fd70d3004f5e43166*32*7a29310ea5dc0276d34c1bef24595d61984a08eb759eaba56bd4887a260bbcce*32*de0c200bbe6887a980dc429edbdabc40f39a368841d804afefa726b2bd7c7b24 ?l?l?l?l?l?l -o out.txt  Hashcat破解对应hash，此处?l对应一个小写字母
    

使用字典破解zip加密文件的指令及输出如下：

    
    
    zip2john.exe test.zip                            获取zip加密文件的Hash指令
    test.zip/test.txt:$pkzip2$1*1*2*0*15*9*4aac42f3*0*26*0*15*4aac*470b*6fa72c2bc69e5738181cb7f406187f8084ce07cf5f*$/pkzip2$:test.txt:test.zip::test.zip                                              所得Hash返回结果
    hashcat -a 0 -m 17210 $pkzip2$1*1*2*0*15*9*4aac42f3*0*26*0*15*4aac*470b*6fa72c2bc69e5738181cb7f406187f8084ce07cf5f*$/pkzip2$ password.txt --force
        password.txt中存放密码字典
    

以上利用Hashcat对rar、zip、pdf、word加密文件进行了破解，选用的方法主要是字典破解和掩码破解，此处所选用的例子为了演示方便都是比较简单的密码，实际情况可能遇到各种类型的密码，在密码长度、类型都未知的情况下，最好首先选用字典破解的方式，后续也会分享一些收集的字典以及字典下载的链接，如果拿现有字典没能跑出密码，则只能使用暴力破解或者掩码组合暴力破解的方式，此时对电脑性能的要求就特别高，而且密码越复杂（比如密码中同时包括字母、数字、特殊字符、汉字等等）破解难度呈指数级增加，后续将深度挖掘hashcat这款密码破解神器，同时分享一些破解技巧以及密码设置的技巧。  
转载声明：如果希望转载请于公众号（安全fun）后台联系，或者邮件至anquanfun@163.com，转载时请保留原作者（安全fun）及出处信息，转载文章禁止声明原创，更多合作也可邮件至anquanfun@163.com。  
免责声明：本公众号所涉及内容仅供安全研究与教学使用，如出现其他风险，后果自负。

