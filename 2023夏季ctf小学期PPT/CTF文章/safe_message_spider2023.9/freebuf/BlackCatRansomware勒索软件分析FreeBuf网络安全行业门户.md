## 一、概述

此次分析的样本是一种勒索软件，属于BlackCat Ransomware家族。兰眼下一代威胁检测系统对该文件的告警信息如下：

![图片.png](https://image.3001.net/images/20220819/1660879969_62ff0461b06d4ea6449ab.png!small)

BlackCat(又名ALPHV)是一个勒索软件家族，于2021年11月中旬浮出水面，并因其复杂性和创新性而迅速臭名昭著。BlackCat采用勒索软件即服务(RaaS)商业模式，在已知的网络犯罪论坛中招揽附属公司，允许附属公司利用勒索软件并保留80%-90%的赎金，其余部分将支付给BlackCat作者。

## 二、分析

### 2.1 基本信息

  
|  
  
---|---  
文件名| 7d113c2d5968d2ca2fe57d8a8170a68f  
文件类型| PE32 executable (GUI) Intel 80386 (stripped to external PDB), for MS
Windows  
文件大小| 827918 bytes  
MD5| 7d113c2d5968d2ca2fe57d8a8170a68f  
SHA1| 002b2329018e16938525a9abddd6e424b5df4a29  
编译器| GNU linker ld (GNU Binutils)(2.37)[GUI32]  
编译时间| 1970-01-01 08:00:00 (被修改过)  
所属家族| BlackCat Ransomware  
  
### 2.2 关键行为分析

#### 2.2.1 反沙箱

该样本通过检查DirectX是否正常来判断当前环境是否为真实环境。当IDirect3D9::GetDeviceCaps()
方法返回D3DERR_NOTAVAILABLE(0x8876086A)时，则说明当前环境缺少图形驱动程序和DirectX组件，进而判断当前环境为沙箱。样本相关代码如下：

  1. 创建IDirect3D9对象  
![image](https://image.3001.net/images/20220819/1660878338_62fefe0281017b9ca1cdd.png!small)

  2. 调用IDirect3D9::GetDeviceCaps() 方法判断设备信息。这里样本通过偏移的方式调用了该方法。  
![image](https://image.3001.net/images/20220819/1660878346_62fefe0a371f053889b4d.png!small)

#### 2.2.2 释放文件

该样本在 C:\Users\xxx\ 下释放公钥信息。

![image](https://image.3001.net/images/20220819/1660878419_62fefe53ade5f6643c59c.png!small)

文件内容如下：

![image](https://image.3001.net/images/20220819/1660878426_62fefe5ad8ca4834c2e04.png!small)

#### 2.2.3 删除卷影

该样本通过com组件VssModuleKeeper删除卷影'\?\Volume{cd35a174-87d4-11e7-afcc-806e6f6e6963}。

![图片.png](https://image.3001.net/images/20220819/1660880183_62ff0537a92c25c363da9.png!small)

#### 2.2.4 遍历文件并加密

遍历卷行为:

![image](https://image.3001.net/images/20220819/1660878562_62fefee28db8fe2461d47.png!small)

![image](https://image.3001.net/images/20220819/1660878568_62fefee8c17ebb3a54bdf.png!small)

遍历文件行为：该样本首先获取所有待加密文件的句柄，再执行加密。

![image](https://image.3001.net/images/20220819/1660878592_62feff0090a05546cca83.png!small)

![image](https://image.3001.net/images/20220819/1660878604_62feff0c99022f6696496.png!small)

加密文件以_encrypted结尾：

![image](https://image.3001.net/images/20220819/1660878615_62feff1761867d904c706.png!small)  
该样本将所有待加密文件的内容全部读取到内存，而后在内存中一次性加密，内存占用非常大。

## 三、总结

本次分析的样本通过调用com组件删除卷影，进而加密文件防止恢复。且其反沙箱手段对qemu沙箱效果显著。近期勒索软件事件频发，各企业机构应当重视网络安全。

