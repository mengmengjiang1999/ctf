# 一、漏洞利用说明

该实验在虚拟机环境下完成，使用渗透工具库metaspolit中的

exploit/windows/fileformat/office_word_hta 组件。

针对操作系统:

Windows 7 32bit

Windows 10 64bit

# 二、 环境说明

## 2.1 攻击机操作系统

建议使用:

Debian

Ubuntu

macOS

Kali linux(自带工具)

Windows 10

软件/工具环境:

Metaspolit

## 2.2 被攻击机环境

属于内部局域网

# 三、 攻击过程

## 3.1 打开metaspolit

![1619576415_6088c65fe73f4ea55f500.png!small?1619576416375](https://image.3001.net/images/20210428/1619576415_6088c65fe73f4ea55f500.png!small?1619576416375)

## 3.2 使用exploit/windows/fileformat/office_word_hta 组件

![1619576424_6088c668240003faaef57.png!small?1619576424396](https://image.3001.net/images/20210428/1619576424_6088c668240003faaef57.png!small?1619576424396)

## 3.3 运行

![1619576430_6088c66ea1c9a0bc8765f.png!small?1619576430933](https://image.3001.net/images/20210428/1619576430_6088c66ea1c9a0bc8765f.png!small?1619576430933)

## 3.4 在受攻击机输入Local IP后面的链接

![1619576441_6088c67972d66679bc347.png!small?1619576441753](https://image.3001.net/images/20210428/1619576441_6088c67972d66679bc347.png!small?1619576441753)

点击运行.

## 3.5 利用产生的文件在metaspolit产生会话

![1619576448_6088c680930f4e9d2fb1c.png!small?1619576448889](https://image.3001.net/images/20210428/1619576448_6088c680930f4e9d2fb1c.png!small?1619576448889)

## 3.6 查看会话

在运行的会话当中执行sessions命令 ,可以发现目标攻击机已经在session中

![1619576454_6088c686b5674929bcdf9.png!small?1619576455057](https://image.3001.net/images/20210428/1619576454_6088c686b5674929bcdf9.png!small?1619576455057)

## 3.7 对攻击机进行提权

根据以上会话产生的ID号, 使用sessions -i ID号来与第一个会话进行连接.

![1619576467_6088c69394a3c0bdb3b16.png!small?1619576467894](https://image.3001.net/images/20210428/1619576467_6088c69394a3c0bdb3b16.png!small?1619576467894)

使用shell进行提权

可以看到已经拿到超级管理员的权限.

![1619576481_6088c6a1e13c714061325.png!small?1619576482280](https://image.3001.net/images/20210428/1619576481_6088c6a1e13c714061325.png!small?1619576482280)

Windows 10实测也同样可以拿到超级管理员权限.

  
  

# 四. 防护措施

针对个人用户:

安装不带广告的杀毒软件(例如火绒等), 并且看到不明文件不要点击下载或者运行, 如是自动下载的不要点击运行, 直接删除就不会建立会话。

# 五. 结论

此漏洞对Windows个人用户安全性不强的用户进行攻击便显得很容易成功.

