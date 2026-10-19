## infoscaner说明

本菜鸡在实际运用过程中曾遇到过一个问题，即单一工具很多时候收集到的信息不够全面，本菜鸡就想通过缝合加本菜鸡的一些对数据的处理输出,以扩大信息收集的范围和准确度  
infoscaner目前仅支持在linux上运行，将被动收集与主动收集集成于一体可自动化的工具，本工具源代码位于src目录下，各位大佬可在此基础上进行改进，infoscaner结构如下图所示  
![image.png](https://image.3001.net/images/20210128/1611831895_60129a5755475ec0381f2.png!small)主调用函数为infoscaner.py，目录下有缝合的crawlergo、rad等工具

## infoscaner环境要求

具有python3和python2两种环境  
python3安装requirements.txt中的库  
使用命令`pip3 install -r requirements.txt`  
进入Sublist3r-master目录下，运行`python2 setup.py install`命令安装sublist3r  
安装nmap  
安装whatweb  
安装wafw00f

## infoscaner使用

### 查看帮助

进入infoscaner目录下  
使用命令`python3 infoscaner.py -h`  
![image.png](https://image.3001.net/images/20210128/1611832429_60129c6d68aaea9dcdebe.png!small)

### 获取whois信息

使用命令`python3 infoscaner.py -u vulnweb.com -w`  
![image.png](https://image.3001.net/images/20210128/1611832553_60129ce92e0a3684f053b.png!small)  
若需要将whois信息输出至文件，可使用-o参数后面跟写入的路径  
`python3 infoscaner.py -u vulnweb.com -w -o ./whois.txt`

### 获取C段和旁站信息

`python3 infoscaner.py -u vulnweb.com -N`  
![image.png](https://image.3001.net/images/20210128/1611832701_60129d7d9df6c3cdc48fd.png!small)若需要将whois信息输出至文件，可使用-o参数后面跟写入的路径  
`python3 infoscaner.py -u vulnweb.com -N -o ./Csegment.txt`

### 获取CMS指纹信息

`python3 infoscaner.py -u vulnweb.com -C`  
![image.png](https://image.3001.net/images/20210128/1611832802_60129de2a323360f83344.png!small)

### ICP备案号查询

`python3 infoscaner.py -u testphp.vulnweb.com -i`

### nslookup查询

`python3 infoscaner.py -u testphp.vulnweb.com -n`  
![image.png](https://image.3001.net/images/20210128/1611832989_60129e9db264393c0f529.png!small)

### WAF检测

`python3 infoscaner.py -u testphp.vulnweb.com -W`  
![image.png](https://image.3001.net/images/20210128/1611833073_60129ef174d87c057b358.png!small)

### FTP匿名登陆

`python3 infoscaner.py -u testphp.vulnweb.com -y`  
![image.png](https://image.3001.net/images/20210128/1611833124_60129f2403ae179368048.png!small)

### 子域名扫描

target为指定目标文件  
`python3 infoscaner.py -u ./target/target.txt -s`  
![image.png](https://image.3001.net/images/20210128/1611833197_60129f6de33d32529dbb9.png!small)

### 全面扫描

`python3 infoscaner.py -u 192.168.2.1 -a`  
![image.png](https://image.3001.net/images/20210128/1611833330_60129ff299ddfbeb87825.png!small)

### 端口扫描

`python3 infoscaner.py -u 192.168.2.1 -p 80,443`  
![image.png](https://image.3001.net/images/20210128/1611833375_6012a01f8fbac6795f352.png!small)![image.png](https://image.3001.net/images/20210128/1611833414_6012a046383fed8707492.png!small)

### 目录爬取

`python3 infoscaner.py -u testphp.vulnweb.com -D`  
![image.png](https://image.3001.net/images/20210128/1611833549_6012a0cd519cc584d1f52.png!small)![image.png](https://image.3001.net/images/20210128/1611833567_6012a0df5af6d80b4788d.png!small)

## 总结

本工具是为了自动化和方便其他人在渗透测试或CTF过程中自动化操作。对目标信息收集后使用者可使用数据库等手段自动化且准确的利用本工具。

工具链接<https://github.com/CMACCKK/infoscaner>

