**2022年5月23日，fastjson官方发布安全通报，fastjson <=
v1.2.80存在反序列化任意代码执行漏洞，在特定条件下可绕过默认autoType关闭限制，可能会导致远程服务器被攻击，风险影响较大。**

 **fastjson是开源JSON解析库，它可以解析JSON格式的字符串，支持将Java
Bean序列化为JSON字符串，也可以从JSON字符串反序列化到Java Bean。由于具有执行效率高的特点，应用范围广泛。**

 **Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 无| 无  
  
 **Part2 漏洞描述**

fastjson已使用黑白名单用于防御反序列化漏洞，经研究在特定条件下可绕过默认autoType关闭限制，攻击远程服务器，风险影响较大。

漏洞名称| Fastjson 反序列化漏洞  
---|---  
CVE编号| 无  
漏洞类型| 远程代码执行  
公开状态| 未公开  
时间线| 2022-05-23 - 供应商发布更新与通告  
影响范围| Fastjson version <= v1.2.80  
  
 **Part3 漏洞复现**

\- 复现环境：

Windows 10

Fastjson v1.2.78

Eclipse

\- 新建win10 x64 虚拟机

\- 安装jdk 1.9 x64

![v2-0b60c76127b06a9d44e2e8fdabde630b_720w.jpg](https://image.3001.net/images/20220825/1661399749_6306f2c57af976d864488.jpg!small)

\- 配置java环境，可以正确执行java -version

![v2-6dd311996a3561c0594b957bbd3a581e_720w.jpg](https://image.3001.net/images/20220825/1661399750_6306f2c629fe0c54eb416.jpg!small)

\- 安装并启动eclipse x64

![v2-4c3e0fb3cd7d816ae49a13a4e028a9f2_720w.jpg](https://image.3001.net/images/20220825/1661399750_6306f2c6e033019f1f531.jpg!small)

\- 新建java工程

\- 导入 fastjson 1.2.78 jar包

\- Main函数执行fastjson反序列化

String json = "{\"@type\":\"******\"}";

JSON.parse(json);

\- 提示 autoType 不支持,默认关闭autoType

![v2-f80660a0bce36e5ba2bc9cd84b436614_720w.jpg](https://image.3001.net/images/20220825/1661399751_6306f2c76ed2426b70db6.jpg!small)

\- 新建测试绕过类

![v2-cf16bd072efa5bac6f526bfdb0778117_720w.jpg](https://image.3001.net/images/20220825/1661399751_6306f2c7f2cf0d2ebc484.jpg!small)

\- 运行测试代码

String json =
"{\"@type\":\"******\",\"@type\":\"*******\",\"value\":\"calc\"}";

JSON.parse(json);

\- 成功弹出计算器

![v2-37ba834b4bd5864fb0d407a9d609803c_720w.jpg](https://image.3001.net/images/20220825/1661399752_6306f2c8b1c282d8fad58.jpg!small)

 **\- 复现成功！**

 **Part4 漏洞细节**

不能代码执行的流程是抛出“autoType is not support”异常信息，从而防止被恶意利用来执行任意代码。

![v2-e08f449e6ec2e5699466a18385096407_720w.jpg](https://image.3001.net/images/20220825/1661399753_6306f2c94fecdc0ea38a4.jpg!small)

此漏洞借助构造特殊类，走到下图代码分支，达到绕过反序列化检测的目的。

绕过之后直接运行到加载类的代码分支，不抛出异常。

![v2-384816402455d0a2a31c154339d81904_720w.jpg](https://image.3001.net/images/20220825/1661399753_6306f2c9e8c7e79e3dbc8.jpg!small)

其中需要注意，所有代码流程中都有“safeMode”检测，所以开启“safeMode”可以缓解漏洞。

autoType里面有“safeMode”检查

![v2-40bb10fa66db7c7616e98b8c76af5503_720w.jpg](https://image.3001.net/images/20220825/1661399754_6306f2ca858cbfd9c1d87.jpg!small)

 **Part5 修复缓解建议**

1\. 升级到最新版本1.2.83

2\. safeMode加固

3\. 升级到fastjson v2

4\. 使用noneautotype版本

* * *

目前，安帝科技工业互联网安全虚拟化靶场平台已集成该漏洞分析研究的环境和组件，可测试、验证、演示该漏洞及其利用过程。

![v2-c6c918b0eb972876211205894d045e11_720w.jpg](https://image.3001.net/images/20220825/1661399755_6306f2cb1d49dd6aed03d.jpg!small)

(靶机启动界面)

![v2-69bc601f831b892e4280bf4e9629c463_720w.jpg](https://image.3001.net/images/20220825/1661399755_6306f2cba863fc4370ebf.jpg!small)

