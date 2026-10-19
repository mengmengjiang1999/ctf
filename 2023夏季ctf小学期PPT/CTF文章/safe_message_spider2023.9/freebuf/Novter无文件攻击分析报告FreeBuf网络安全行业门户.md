# 1 病毒信息

 **病毒名称:** Trojan.Script.akg

 **病毒类型:** 后门

 **MD** **5** **:** 08ac667c65d36d6542917655571e61c8

 **SHA1:** 5b24a3b32d9dba95b296a7a16cbcf50a7df2d196

 **文件类型:** EXE 32位

 **文件大小:** 84,992 字节

 **传播途径:** 无主动传播方式, 由上一级下载

 **影响系统:** winxp及以上系统

# 2 病毒概况

近期,江民赤豹安全实验室捕获到名为“Novter”的后门木马,通过分析发现“Novter”是采用了无文件攻击技术,通过hta文件释放脚本代码主要隐藏在注册表里,并通过后门构成僵尸网络,隐蔽性较强,主要通过广告流量欺诈获利｡

“Novter”并不是一款新的病毒,早在今年3月,赤豹安全实验室就通过江民全球病毒样本监测分析平台截获到Novter的样本,其主要受害者分布在美国和欧洲地区,
且仍在向更多地区传播扩散,Novter利用CMSTPLUA COM接口来绕过UAC保护, 通过更改注册表禁止Windows
Defender防护软件以及windows自动更新, 创建BITS任务或更改注册表以实现持久化｡

# 3 病毒行为摘要

## 3.1 文件行为

以下为正则语法, 除了<>, 表示变量, 另外病毒文件名符合[a-zA-Z0-9]{10}, 且随机, 例如h1Jinr79hv, fHPqbx7WKY等.

创建C:\Documents and Settings\\(<username>|All Users)\Application
Data\\[a-zA-Z0-9]{10}.hta

将%SystemRoot%\notepad.exe拷贝并重命名为C:\Documents and
Settings\<username>\Application Data\246765678

## 3.2 进程行为

创建名为”Global\CreatorsPatch”的互斥体

创建名为”76547890876578”的BITS任务

## 3.3 注册表行为

创建注册表项(HKLM|HKCU)\Software(\Wow6432Node)?\\[a-zA-Z0-9]{10}

在上述项下创建3个值, 名字均符合[a-zA-Z0-9]{10}形式, 且名字看起来随机.

在上述项下创建2个值, 名字分别为: 194956, 2177774

创建注册表值(HKLM|HKCU)\ SOFTWARE\Microsoft\Windows\CurrentVersion\Run
值名[a-zA-Z0-9]{10}, 内容为一个病毒hta文件全路径.

## 3.4 网络行为

向C&C地址发送HTTP请求并读取返回数据, 具

体C&C列表见附录(IOCs)

# 4 详细分析报告

1) 检查自身权限, 根据不同权限选择并设置当前目录为:

C:\Documents and Settings\<username>\Application Data 或

CSIDL_COMMON_APPDATA C:\Documents and Settings\All Users\Application Data

![1572233855_5db6627f65a53.png!small](https://image.3001.net/images/20191028/1572233855_5db6627f65a53.png!small)

后续步骤中提到的当前目录即为此目录

2) 遍历系统进程名, 检测是否有指定进程存在:

![1572233882_5db6629a36e6a.png!small](https://image.3001.net/images/20191028/1572233882_5db6629a36e6a.png!small)

比对时采用哈希值比较, 哈希算法如下:

![1572233904_5db662b098072.png!small](https://image.3001.net/images/20191028/1572233904_5db662b098072.png!small)

要寻找的哈希值:

![1572233923_5db662c30c6f1.png!small](https://image.3001.net/images/20191028/1572233923_5db662c30c6f1.png!small)

若发现存在, 以”p=p”为HTTP请求中可选字段向185.243.114.111发送信息:

![1572233969_5db662f160414.png!small](https://image.3001.net/images/20191028/1572233969_5db662f160414.png!small)

之后线程永久休眠。

3) 在本进程中查找指定模块名, 检测是否有指定模块, 若发现则报告”p=m”, 线程永久休眠.

![1572233991_5db663075f617.png!small](https://image.3001.net/images/20191028/1572233991_5db663075f617.png!small)

![1572234012_5db6631c424fa.png!small](https://image.3001.net/images/20191028/1572234012_5db6631c424fa.png!small)

模块名哈希:

![1572234035_5db66333c13e7.png!small](https://image.3001.net/images/20191028/1572234035_5db66333c13e7.png!small)

方式均与步骤2中类似

4) 检测本机是否只有一个处理器, 若是, 则报告”p=c”, 线程永久休眠:

![1572234087_5db66367ca0b3.png!small](https://image.3001.net/images/20191028/1572234087_5db66367ca0b3.png!small)

![1572234105_5db66379471f2.png!small](https://image.3001.net/images/20191028/1572234105_5db66379471f2.png!small)

5) 检测本进程是否被调试, 若是, 则报告”p=d”, 线程永久休眠:

![1572234126_5db6638e2cc3a.png!small](https://image.3001.net/images/20191028/1572234126_5db6638e2cc3a.png!small)

6) 检测本进程的线程睡眠是否有效, 若无效, 则报告”p=s”, 线程永久休眠。

![1572234146_5db663a296357.png!small](https://image.3001.net/images/20191028/1572234146_5db663a296357.png!small)

![1572234166_5db663b640c27.png!small](https://image.3001.net/images/20191028/1572234166_5db663b640c27.png!small)

7) 启用"SeTakeOwnershipPrivilege"权限:

![1572234212_5db663e4350e3.png!small](https://image.3001.net/images/20191028/1572234212_5db663e4350e3.png!small)

8) 检测当前权限, 若权限足够, 则禁止windefender以及windows 更新:

![1572234234_5db663fa772ad.png!small](https://image.3001.net/images/20191028/1572234234_5db663fa772ad.png!small)

![1572234256_5db664102587d.png!small](https://image.3001.net/images/20191028/1572234256_5db664102587d.png!small)

9) 创建线程, 向一个CC列表中的所有地址循环发送心跳包, 总数为1800次, 每次操作完成睡眠一秒:

![1572234276_5db6642442849.png!small](https://image.3001.net/images/20191028/1572234276_5db6642442849.png!small)

![1572234292_5db664349f1f2.png!small](https://image.3001.net/images/20191028/1572234292_5db664349f1f2.png!small)

CC列表, 其中的accl部分:

![1572234359_5db664776929d.png!small](https://image.3001.net/images/20191028/1572234359_5db664776929d.png!small)

10) 创建hta文件, 保存到当前目录, 将本程序exe数据和一段内嵌ps脚本, 一段内嵌js命令保存到注册表中, 建立持续机制:

![1572234378_5db6648a50c81.png!small](https://image.3001.net/images/20191028/1572234378_5db6648a50c81.png!small)

![1572234392_5db66498dfa03.png!small](https://image.3001.net/images/20191028/1572234392_5db66498dfa03.png!small)

这个键的会被创建在, 此键后续称为键1:

对于64位系统: (HKLM|HKCU)\Software\Wow6432Node

对于32位系统: (HKLM|HKCU)\Software\

此处的名称为随机名称, 均为10个字符长度, 每个字符可能为数字以及大小写字母. hta,js,ps的内容由于变量名随机故每次生成均不一样,
不过不一样的点也仅限于变量名.

持续机制有两种情况, 在第一种情况失败后会采用第二种情况:

1\. 创建名为”76547890876578”的BITS任务, 设定回调命令行执行:

C:\Windows\System32\cmd.exe /c "C:\ProgramData\h1Jinr79hv.hta" & exit 1

![1572234418_5db664b20f7de.png!small](https://image.3001.net/images/20191028/1572234418_5db664b20f7de.png!small)

2\.
根据权限在HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run或HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run下创建:

![1572234435_5db664c3db758.png!small](https://image.3001.net/images/20191028/1572234435_5db664c3db758.png!small)

重启后, 由持续机制命令, 执行hta文件:

![1572234541_5db6652d4aa18.png!small](https://image.3001.net/images/20191028/1572234541_5db6652d4aa18.png!small)

如上图所示, hta文件最终读取并执行(js Eval)保存在注册表中的js代码:

![1572234559_5db6653f1b80c.png!small](https://image.3001.net/images/20191028/1572234559_5db6653f1b80c.png!small)

保存在注册表中的js代码会执行一段ps代码:

![1572234610_5db6657251581.png!small](https://image.3001.net/images/20191028/1572234610_5db6657251581.png!small)

此ps代码的功能为, 读取并执行保存在注册表中的ps代码:

![1572234635_5db6658bc02be.png!small](https://image.3001.net/images/20191028/1572234635_5db6658bc02be.png!small)

![1572234651_5db6659b2a5fc.png!small](https://image.3001.net/images/20191028/1572234651_5db6659b2a5fc.png!small)

而保存在注册表中的ps代码的功能为, 将保存在注册表中的PE文件装载到本进程空间并执行, 至此持续化机制达成.

这个过程, 将混淆后的代码分散保存, 而运行时又能结合在一起, 单独地去看或调试某段代码, 就会有变量缺失的提示.

11) 判断当前进程权限, 若非管理员, 则使用CMSTPLUA COM接口过UAC得到管理员权限:

![1572234673_5db665b1e807f.png!small](https://image.3001.net/images/20191028/1572234673_5db665b1e807f.png!small)

12) 创建线程, 每6小时更新cc地址列表:

![1572234691_5db665c341cd2.png!small](https://image.3001.net/images/20191028/1572234691_5db665c341cd2.png!small)

从步骤9中, “acll”部分的cc地址, 获取数据:

![1572234736_5db665f031752.png!small](https://image.3001.net/images/20191028/1572234736_5db665f031752.png!small)

解析数据, 将配置数据保存到键一, 名为194956:

![1572234752_5db6660002228.png!small](https://image.3001.net/images/20191028/1572234752_5db6660002228.png!small)

故accl主要用于cc控制, acll主要用于下发配置.

13) 收集本机信息, 并发送信息到”accl”类服务器:

![1572234775_5db66617ebd13.png!small](https://image.3001.net/images/20191028/1572234775_5db66617ebd13.png!small)

收集的信息包括,系统信息, cpu,gpu信息, 反病毒产品信息, 内存信息, 本进程权限信息等等:

![1572234797_5db6662dc2170.png!small](https://image.3001.net/images/20191028/1572234797_5db6662dc2170.png!small)

![1572234815_5db6663fd572f.png!small](https://image.3001.net/images/20191028/1572234815_5db6663fd572f.png!small)

![1572234836_5db666545ec01.png!small](https://image.3001.net/images/20191028/1572234836_5db666545ec01.png!small)

14) 在步骤13发送信息后,可能会收到后门指令,如

![1572234865_5db666718b292.png!small](https://image.3001.net/images/20191028/1572234865_5db666718b292.png!small)

包含自身清理, 功能暂停/恢复, 下载额外模块并执行, 设定步骤13~14的循环间隔等.睡眠一段时间,默认为90分钟,之后跳转到13步骤进入下一轮活动.

此后门没有在本机打开任何端口,主要靠自身发送HTTP请求,而连接的目标端口全是80或443端口,故隐蔽性较高｡

# 5 总结

该样本的持久机制使用BITS后台任务, 比较有特点且隐蔽, 另外后门的网络通讯均通过感染端主动发起HTTP请求方式, 也比较隐蔽, 能穿透内网｡

值得注意的是, 若普通地启动此程序, 会导致本程序崩溃以及部分功能不表达,原因有两点:

i. 在sub_4014c6中, 作者为了消除内存中的hta,js,ps等文件数据, 使用memset, 对照常来说处于全局不可写数据段的数据进行清零:

![1572234887_5db666871b854.png!small](https://image.3001.net/images/20191028/1572234887_5db666871b854.png!small)

从这里可以看出, 此程序作者应该是确定此程序的数据段均可写, 这个程序有自己的加载方式｡

ii. 在调用COM接口之前, 本程序中并没有任何一处位置调用CoInitialize或CoInitializeEx等函数,
也就会造成BITS接口调用失败. 显然, 根据本程序的水平, 作者不会犯这种错误, 那么此程序被装载进入的进程必定已经初始化｡

# 6 附录(IOCs)

## 6.1 HASH

a82dd93585094aeba4363c5aeedd1a85ef72c60a03738b25d452a5d895313875

## 6.2 C&C

185.243.114.111

  
  
  
  
  
  
  
  
  
  
  

  

