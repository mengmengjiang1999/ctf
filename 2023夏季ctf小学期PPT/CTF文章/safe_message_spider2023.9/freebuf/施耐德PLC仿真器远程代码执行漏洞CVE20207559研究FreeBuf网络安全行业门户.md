Schneider Electric EcoStruxure Control Expert（前称Unity Pro）是法国施耐德电气（Schneider
Electric）公司的一套用于Schneider
Electric逻辑控制器产品的编程软件。其中PLC仿真器是软件内置的一个有PLC仿真功能windows应用程序。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
## Part2 漏洞描述

该漏洞源于当通过Modbus协议收到一个手动构造的恶意请求时，会导致EcoStruxure Control
Expert软件中的PLC仿真器程序崩溃或远程代码执行。

漏洞名称| 施耐德 PLC 仿真器远程代码执行漏洞  
---|---  
CVE编号| CVE-2020-7559  
漏洞类型| 远程代码执行  
漏洞等级| 7.5 高危  
公开状态| 公开  
时间线| 2020-08-13 - 供应商披露2020-11-04 - 分配 CVE2020-11-09 - 供应商发布2020-12-08 - 公开发布  
  
## Part3 影响范围

Schneider Electric EcoStruxure Control Expert version <= v14.1

## Part4 复现环境

Windows 10

Schneider Electric EcoStruxure Control Expert v14.1

## Part5 漏洞复现

\- 安装Schneider Electric EcoStruxure Control Expert v14.1

\- 软件路径

C:\Program Files (x86)\Schneider Electric\ControlExpert 14.1\PLC_Simulator

![v2-e64415c1861dfbc7320a26f58fea9e75_720w.jpg](https://image.3001.net/images/20220505/1651726208_62735780ba5210e5218d4.jpg!small)

\- 启动sim仿真器程序

![v2-fb6a0a8e4f8d8cda1b290fac1c3d32eb_720w.jpg](https://image.3001.net/images/20220505/1651726209_62735781287044fbb7e7e.jpg!small)

\- 查看启动端口502开放,程序启动成功！

![v2-66346373a6c1ddd7d91cb8ab855d5332_720w.jpg](https://image.3001.net/images/20220505/1651726209_627357815c37cc1b34fc6.jpg!small)

\- 运行测试脚本

![v2-cf336af748b4e5371d6b0c60d1478fc8_720w.jpg](https://image.3001.net/images/20220505/1651726209_62735781c5b329583ee18.jpg!small)

强制关闭远程连接，进程退出，复现成功!

![v2-cf2afcac1f153436fb524c5c7da566e4_720w.jpg](https://image.3001.net/images/20220505/1651726210_6273578247cdfb86f593b.jpg!small)

## Part6 漏洞细节

· Xdbg加载sim.exe 在tcp/ip模块中下断点。

![v2-81809d377cf1fa8a4a1cb08fa4e8f4f2_720w.jpg](https://image.3001.net/images/20220505/1651726210_627357827e62a2bbbd191.jpg!small)

· 然后运行test.py测试脚本。

程序断下,单步运行，查看接收buffer位置数据。

![v2-f8e4ce8697ed105301b83779068ed720_720w.jpg](https://image.3001.net/images/20220505/1651726211_6273578388de22ab14fc0.jpg!small)

是我们发送的测试数据。

在接收数据位置下硬件访问断点。

![v2-68587f9c4e2db23f538fdcd249dfb9cf_720w.jpg](https://image.3001.net/images/20220505/1651726211_62735783d34deab4109a2.jpg!small)

· 运行程序。

![v2-66ce0eccf53cfdb0fb7b6709b621412e_720w.jpg](https://image.3001.net/images/20220505/1651726212_627357843130f156b5f23.jpg!small)

程序断到这里，返回一层。

![v2-138fac9a29ddb4dee1f3f70da6199727_720w.jpg](https://image.3001.net/images/20220505/1651726212_627357846825b7c757cbe.jpg!small)

可以看到是 exec.dll 模块中调用memcpy 时产生的栈溢出,

再返回一层。

![v2-53ee1861f12bff207c7618333206e2c5_720w.jpg](https://image.3001.net/images/20220505/1651726212_62735784b67e75904b87b.jpg!small)

发现接收网络发包的位置是ebp-0x8004，

可以推算网络发包数据超过0x8000就可以造成栈溢出，

然后构造恶意数据包，利用栈溢出造成远程代码执行。

如果要达到远程代码执行的目的，需要绕过栈Cookie校验，SafeSEH检测和DEP保护三道防护才可以。

## Part7 修复和缓解建议

· 升级软件到最新版本。

· 如果不能升级到最新版，可以使用流量检测设备监控Modbus协议MBAP中data_length字段，数值超过 0x8000
大小（10进制32768）即可报警。

· 安装主机卫生设置通讯白名单。

