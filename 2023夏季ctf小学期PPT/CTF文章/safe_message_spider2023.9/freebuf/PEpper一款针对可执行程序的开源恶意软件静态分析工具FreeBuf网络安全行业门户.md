**今天给大家介绍的是一款名叫PEpper的工具，这是一款开源的脚本工具，广大研究人员可以利用该工具来对可执行程序进行恶意软件静态分析。**

![](https://image.3001.net/images/20190914/1568450819_5d7ca90373e6a.jpg!small)

##  工具安装

> eva@paradise:~$ git clone <https://github.com/Th3Hurrican3/PEpper/>
>
> eva@paradise:~$ cd PEpper
>
> eva@paradise:~$ pip3 install -r requirements.txt
>
> eva@paradise:~$ python3 pepper.py ./malware_dir

##  工具运行截图

##
![](https://image.3001.net/images/20190914/1568450841_5d7ca9195530f.png!small)![](https://image.3001.net/images/20190914/1568450841_5d7ca9196d185.png!small)![](https://image.3001.net/images/20190914/1568450841_5d7ca9196e8ae.png!small)![](https://image.3001.net/images/20190914/1568450842_5d7ca91a10f4c.png!small)

###  CSV输出

![](https://image.3001.net/images/20190914/1568450849_5d7ca921c95b8.png!small)

##  特征提取

> 可疑的熵比；
>
> 可疑代码大小；
>
> 可疑的调试时间戳；
>
> 出口流量数量；
>
> 反调试调用数；
>
> 虚拟机检测调用数；
>
> 可疑的API调用数；
>
> 可疑的字符串数；
>
> YARA规则匹配数；
>
> URL数量；
>
> IP数量；
>
> GS支持；
>
> CFG支持；
>
> DEP支持；
>
> ASLR支持；
>
> SEH支持；
>
> TLS支持；
>
> 导入哈希；
>
> VirusTotal数据库检测；
>
> 封装器检测；
>
> 数字证书检测；

##  注意事项

> 1、可直接针对单个或多个PE进行分析；
>
> 2、可将分析结果输出保存为output.csv文件；
>
> 3、支持使用VirusTotal Scan，需在virustotal.py文件中添加VirusTotal私钥（要求联网）；

###  参考代码库

> 1、LIEF项目：【[传送门](https://github.com/lief-project/LIEF)】
>
> 2、PEstudio：【[传送门](https://www.winitor.com/)】
>
> 3、PEframe：【[传送门](https://github.com/guelfoweb/peframe)】
>
> 4、Yara-Rules:【[传送门](https://github.com/Yara-Rules/rules)】

##  项目地址

> PEpper：【[GitHub传送门](https://github.com/Th3Hurrican3/PEpper)】

 ***
参考来源：[Th3Hurrican3](https://github.com/Th3Hurrican3/PEpper)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

