![](https://image.3001.net/images/20230802/1690957532_64c9f6dc720cac0e64216.jpeg!small)  

## 关于Graphcat

Graphcat是一个针对密码破解结果的可视化图表生成脚本，该工具基于Python开发，可以帮助广大研究人员根据密码破解结果来生成可视化图表数据，其中涵盖了hashcat、John
the Ripper和NTDS。

## 工具安装

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Orange-Cyberdefense/graphcat

然后切换到项目目录中，并执行安装命令即可：

    
    
    cd graphcat
    
    pip install .

## 工具帮助信息

    
    
    $ graphcat.py -h
    
    usage: graphcat.py [-h] -potfile hashcat.potfile -hashfile hashfile.txt [-john] [-format FORMAT] [-export-charts] [-output-dir OUTPUT_DIR] [-debug]
    
     
    
    Password Cracking Graph Reporting
    
     
    
    options:
    
      -h, --help            显示工具帮助信息和退出
    
      -potfile hashcat.potfile
    
                            Hashcat Potfile
    
      -hashfile hashfile.txt
    
                            包含哈希的文件路径（按行分隔）
    
      -john                 John potfile
    
      -format FORMAT        哈希文件格式，1为哈希；2为用户名；3为username:uid:lm:ntlm；
    
      -export-charts         生成png图表报告
    
      -output-dir OUTPUT_DIR
    
                            输出目录
    
      -debug                开启调试模式

## 工具使用

我们需要使用-potfile参数给Graphcat提供一个potfile，默认为hashcat，我们也可以使用-john来提供一个john
potfile，或使用-hashifle来提供一个哈希文件：

    
    
    $ graphcat.py -hashfile entreprise.local.ntds -potfile hashcat.pot
    
    [-] Parsing potfile
    
    [-] 164 entries in potfile
    
    [-] Parsing hashfile
    
    [-] 1600 entries in hashfile
    
    [-] Generating graphs...
    
    [-] Generating report...
    
    [-] Report available at graphcat_1672941324.pdf

## 数据格式

### 仅哈希

    
    
    aad3b435b51404eeaad3b435b51404ee
    
    aad3b435b51404eeaad3b435b51404ee
    
    aad3b435b51404eeaad3b435b51404ee

### 用户名+哈希

    
    
    test1:aad3b435b51404eeaad3b435b51404ee
    
    test2:aad3b435b51404eeaad3b435b51404ee
    
    test3:aad3b435b51404eeaad3b435b51404ee

### Secretsdump

    
    
    waza.local\test1:4268:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::
    
    waza.local\test2:4269:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::
    
    waza.local\test3:4270:aad3b435b51404eeaad3b435b51404ee:aad3b435b51404eeaad3b435b51404ee:::

如果哈希文件中某个哈希出现了不止一次，工具同样会对其进行多次计算。

除此之外，如果你提供的secretsdump包含了密码历史，工具还会对密码历史的相似性进行分析。

## 工具输出样例

![](https://image.3001.net/images/20230802/1690957608_64c9f7284d87ec14fc8cc.png!small)![](https://image.3001.net/images/20230802/1690957616_64c9f730e76416d2fc386.png!small)

![](https://image.3001.net/images/20230802/1690957625_64c9f739d948be26c2136.png!small)

![](https://image.3001.net/images/20230802/1690957633_64c9f741ef0feb5b2e2b5.png!small)

![](https://image.3001.net/images/20230802/1690957646_64c9f74e300b97080fa46.png!small)

![](https://image.3001.net/images/20230802/1690957655_64c9f7575e1173c5a58a5.png!small)

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/Orange-Cyberdefense/graphcat/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Graphcat** ：【[ _GitHub传送门_](https://github.com/Orange-Cyberdefense/graphcat)】

