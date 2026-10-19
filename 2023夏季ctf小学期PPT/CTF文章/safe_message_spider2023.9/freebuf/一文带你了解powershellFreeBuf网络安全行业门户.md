**前言** ：powershell在后渗透阶段是一个渗透利器，使用它会提高我们的渗透速度。

###

## 一、初始powershell

 **windows powershell** 是一种命令行外壳程序和脚本环境，它内置在每个受支持的windows版本中（windows7,win
2008R2以及更高版本），为windows命令行使用者和脚本编写者利用.NET
Framework的强大功能提供了便利。只要可以在一台计算机上运行代码，就可以将powershell脚本文件（.ps1）下载到磁盘中执行（甚至无须将脚本文件写到磁盘中）。也可以把powershell看做命令提示符cmd.exe的拓展
Powershell需要.NET环境的支持，同时支持.NET对象，其可读性，易用性局所有Shell之首。powershell这些特点，使它逐渐成为一个非常流行得力的安全测试工具。  
POWERSHELL具有：

  1. 在WIN7版本上的操作系统是默认安装的
  2. 脚本可以在内存中允许，不需要写入磁盘
  3. 几乎不会触发杀毒软件
  4. 可以远程执行
  5. 目前很多工具都是基于powershell开发的
  6. 使windows的脚本的执行变得更加容易
  7. cmd.exe的运行通常会被阻止，但是powersehll的运行通常不会被阻止
  8. 可用于管理活动目录  
[![1631407647_613d4e1fdd310fa1187f6.png!small?1631407648313](https://image.3001.net/images/20210912/1631407647_613d4e1fdd310fa1187f6.png!small?1631407648313)](https://shs3.b.qianxin.com/attack_forum/2021/09/attach-471252d86ad56aa438e21ed84a84feab3a7683ca.png)

### 1.查看版本”Get-Host”或者$psversiontable

###
![1631407675_613d4e3beacf8f94ca8ad.png!small?1631407676283](https://image.3001.net/images/20210912/1631407675_613d4e3beacf8f94ca8ad.png!small?1631407676283)

### 2.计算1gb,数学运算

![1631407709_613d4e5dae77c67bb2675.png!small?1631407710030](https://image.3001.net/images/20210912/1631407709_613d4e5dae77c67bb2675.png!small?1631407710030)

### 3.Get-Serivce获取服务

![1631407736_613d4e78bc88271a66125.png!small?1631407737148](https://image.3001.net/images/20210912/1631407736_613d4e78bc88271a66125.png!small?1631407737148)

## 二、 powershell的快捷键

  1. `ALT+F7 清除命令的历史记录`
  2. `PgUp PgDn 翻页的效果`
  3. `Esc 清除当前命令行`
  4. `管道的作用是将一个命令的输出作为另一个命令的输入，两个命令之间用“|”连接`
  5. `Tab 自动补齐命令或者文件名`

###

#

### 1.powershell管道和重定向

![1631407763_613d4e93da37853e5cdfa.png!small?1631407764191](https://image.3001.net/images/20210912/1631407763_613d4e93da37853e5cdfa.png!small?1631407764191)  
重定向>,如果存在文件会覆盖，>>才是追加 将列出的信息重定向到文件  
**![1631407775_613d4e9f8214c4ced151b.png!small?1631407775821](https://image.3001.net/images/20210912/1631407775_613d4e9f8214c4ced151b.png!small?1631407775821)type是显示文件内容**

### 2.powershell执行外部命令

![1631407799_613d4eb7b38f14400d8c2.png!small?1631407800090](https://image.3001.net/images/20210912/1631407799_613d4eb7b38f14400d8c2.png!small?1631407800090)  
查看系统变量  
$env:path  
![1631407815_613d4ec74d2798c84a4ce.png!small?1631407815614](https://image.3001.net/images/20210912/1631407815_613d4ec74d2798c84a4ce.png!small?1631407815614)

### 3.powershell命令集合

Get-comannd获取所有命令  
![1631407841_613d4ee1622b36782a667.png!small?1631407841759](https://image.3001.net/images/20210912/1631407841_613d4ee1622b36782a667.png!small?1631407841759)get-help
xxx命令![1631407853_613d4eed5501c1d3fec5c.png!small?1631407853694](https://image.3001.net/images/20210912/1631407853_613d4eed5501c1d3fec5c.png!small?1631407853694)

> 还可以看到别名gcm  
> get-process获取进程信息  
> get-alias 获取当前会话的别名  
> get-history
> 获取历史命令![1631407884_613d4f0c20206e87111b9.png!small?1631407884576](https://image.3001.net/images/20210912/1631407884_613d4f0c20206e87111b9.png!small?1631407884576)

### 4.powershell别名使用

get-alias -name 别名  
![1631407916_613d4f2c3462f964bec1d.png!small?1631407916484](https://image.3001.net/images/20210912/1631407916_613d4f2c3462f964bec1d.png!small?1631407916484)

查找Remove开头的所有别名  
get-alias | where
{$_.definition.startswith(“Remove”)}![1631407926_613d4f366e9a98a41a20f.png!small?1631407926756](https://image.3001.net/images/20210912/1631407926_613d4f366e9a98a41a20f.png!small?1631407926756)

查找所有的别名  
get-alias | group-object definition | sort -descending
Count![1631407954_613d4f52f41a588cb08c1.png!small?1631407955382](https://image.3001.net/images/20210912/1631407954_613d4f52f41a588cb08c1.png!small?1631407955382)

### 5.powershell变量基础

PS D:> $name=”x”  
PS D:>
$name![1631407983_613d4f6feff414458894d.png!small?1631407984287](https://image.3001.net/images/20210912/1631407983_613d4f6feff414458894d.png!small?1631407984287)

### 6 Powershell变量操作

可以像python一样交换变量  
![1631408010_613d4f8a0a5c544ba0952.png!small?1631408010436](https://image.3001.net/images/20210912/1631408010_613d4f8a0a5c544ba0952.png!small?1631408010436)  
ls variable:  
查看变量![1631408022_613d4f96d43e4b64e50c2.png!small?1631408023256](https://image.3001.net/images/20210912/1631408022_613d4f96d43e4b64e50c2.png!small?1631408023256)

## 三、进阶用法

### 1.powershell自动化变量

就是powershell打开后自动加载的变量  
![1631408070_613d4fc60dd06857c5cd0.png!small?1631408070310](https://image.3001.net/images/20210912/1631408070_613d4fc60dd06857c5cd0.png!small?1631408070310)  
powershell环境变量  
ls env:  
一定要有:  
![1631408085_613d4fd55717014a4bb8d.png!small?1631408085684](https://image.3001.net/images/20210912/1631408085_613d4fd55717014a4bb8d.png!small?1631408085684)  
打印某个环境变量的值![1631408129_613d500119ac2cab05aaa.png!small?1631408129385](https://image.3001.net/images/20210912/1631408129_613d500119ac2cab05aaa.png!small?1631408129385)

创建环境变量  
$env:name=”x”  
[![1631408153_613d5019d57f91c7513b6.png!small?1631408154156](https://image.3001.net/images/20210912/1631408153_613d5019d57f91c7513b6.png!small?1631408154156)](https://shs3.b.qianxin.com/attack_forum/2021/08/attach-332720767cb09d7e9d8c5bd91d9a46ac7cb71823.png)  
删除环境变量:  
del env:name  
![1631408164_613d5024379a2e2bbc430.png!small?1631408164517](https://image.3001.net/images/20210912/1631408164_613d5024379a2e2bbc430.png!small?1631408164517)

### 2.Powershell脚本执行策略

为了阻止使用者运行恶意脚本，powershell提供了一个执行策略。在默认情况下，这个执行策略设置为“不能运行”
如果powershell脚本无法执行，可以使用Get-ExecutionPolicy查看当前的执行策略  
![1631408188_613d503c74c38517a1635.png!small?1631408188781](https://image.3001.net/images/20210912/1631408188_613d503c74c38517a1635.png!small?1631408188781)

Restricted:脚本不能运行（默认设置） RemoteSigned:在本地创建的脚本可以运行，但从网上下载的脚本不能运行（拥有数字证书的签名除外）
AllSigned:仅当脚本由受信任的发布者签名时才能运行 Unrestricted:允许所有脚本运行 可以使用下面的命令设置powershell的执行策略
Set-ExecutionPolicy 运行脚本:  
![1631408217_613d5059ecc3b05a9c00b.png!small?1631408218271](https://image.3001.net/images/20210912/1631408217_613d5059ecc3b05a9c00b.png!small?1631408218271)

### 3.powershell与其他脚本程序的互相调用

[![1631408260_613d50841d5d63c939efd.png!small?1631408260374](https://image.3001.net/images/20210912/1631408260_613d50841d5d63c939efd.png!small?1631408260374)](https://shs3.b.qianxin.com/attack_forum/2021/08/attach-2ddc2c897ac74ea9232e7c7adea621224f0227f4.png)  
![1631408276_613d50947a1d58b8fd912.png!small?1631408276778](https://image.3001.net/images/20210912/1631408276_613d50947a1d58b8fd912.png!small?1631408276778)

### 4.powershell实现用户交互

$input=read-host
“请输入您的姓名”![1631408313_613d50b9e0b88ff32d674.png!small?1631408314251](https://image.3001.net/images/20210912/1631408313_613d50b9e0b88ff32d674.png!small?1631408314251)

### 5.powershell格式化字符串

 **Powershell条件操作符**

  1. nq 不等于
  2. -gt 大于
  3. -lt 小于
  4. -contains包括 (1,2,3) contains 1
  5. -not 取反

  6. -eq 等于

###
![1631408624_613d51f04572a1c5abf73.png!small?1631408624628](https://image.3001.net/images/20210912/1631408624_613d51f04572a1c5abf73.png!small?1631408624628)

### 6.powershell操作注册表

Powershell可以使用文件操作API来操作注册表，注册表项就类似于Windows的文件夹。![1631408653_613d520d654af41c2a911.png!small?1631408653751](https://image.3001.net/images/20210912/1631408653_613d520d654af41c2a911.png!small?1631408653751)

上述例子就演示了利用cd指令（Set-Location）设置当前的注册表路径， 然后通过dir指令（Get-ChildItem）获取所有的子项。  
注册表项API  
在Powershell中，注册表项基本上和文件夹是对等的，可以使用文件夹操作相关API来操作注册表项。通常的操作有：  
新建项： New-Item （mkdir、ni）  
重命名项：Rename-Item （ren、rni）  
删除项： Remove-Item （rm）  
获取子项：Get-ChildItem （dir）

