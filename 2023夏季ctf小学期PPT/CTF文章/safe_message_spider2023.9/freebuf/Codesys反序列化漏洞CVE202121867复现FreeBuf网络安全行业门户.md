CODESYS Development System是德国3S-Smart Software
Solutions公司的一套用于工业控制器和自动化技术领域的编程工具。它支持IEC61131-3标准IL 、ST、 FBD 、LD、 CFC、 SFC
六种PLC编程语言，用户可以在同一项目中选择不同的语言编辑子程序、功能模块等。

 **Part1 漏洞状态**

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 未知  
  
 **Part2 漏洞描述**

CODESYS Development System 3.5.16和3.5.17的ObjectManager.plugin
ObjectStream.ProfileByteArray功能中存在不安全反序列化漏洞，攻击者可借助特制的文件利用该漏洞执行任意命令。

‍漏洞名称| CODESYS Development System ObjectManager.plugin
ObjectStream.ProfileByteArray不安全的反序列化漏洞  
---|---  
CVE编号| CVE-2021-21867  
漏洞类型| 反序列化漏洞  
漏洞等级| 高危（8.8）  
受影响的产品| CODESYS Development System 3.5.16CODESYS Development System 3.5.17  
公开状态| 公开  
时间线| 2021.05.18 – 发现漏洞2021.07.26 – 公开发布  
  
Part3漏洞复现 **1\. 实验环境** 实验主机：win10 64软件版本：CODESYS Development System
3.5.16.0（64位）
**2.涉及工具**[http://ysoserial.net](https://link.zhihu.com/?target=http%3A//ysoserial.net)
**3.漏洞复现**

1）构造恶意项目文件，首先使用反序列化工具[http://ysoserial.net](https://link.zhihu.com/?target=http%3A//ysoserial.net)在命令行执行如下命令生成恶意项目文件：ysoserial.exe
-f BinaryFormatter -g TypeConfuseDelegate -o base64 -c "calc"

其次，将有效负载插入到项目文件的“Profile”数组字段中，如果导入成功会弹出计算器。构造的恶意文件如下：

![v2-c47c90681c4f609081fd6937a789f2cb_720w.jpg](https://image.3001.net/images/20220825/1661400163_6306f4635a5029346be0d.jpg!small)

2）将第一步生成的恶意项目文件导入到CODESYS Development System中，结果弹出计算器，如下图所示：

![v2-49e9230f08510c2b217e2c72c4465782_720w.jpg](https://image.3001.net/images/20220825/1661400164_6306f46412b913b3a76c5.jpg!small)

### Part4漏洞分析

借助dnspy反汇编工具对CODESYS.exe进行调试，导入文件时设置断点，该处会进行文件打开并读取操作，如下：

![v2-a4ee62f56adaa374b9dba6fbf263f1bd_720w.jpg](https://image.3001.net/images/20220825/1661400164_6306f464e392daf0ef1a9.jpg!small)

随后执行至ObjectStream.ProfileByteArray处，当执行至165行处，会将存储文件内容的变量“value”传递给“ChunkedMemoryStream”，如下图所示：

![v2-ca46a9d533cc2ed8a62cdafb0f1893f4_720w.jpg](https://image.3001.net/images/20220825/1661400165_6306f465b529952defc6a.jpg!small)

BinaryFormatter.Deserialize将执行反序列化操作，问题就出在此处，下面对反序列化过程进行详细描述。操作过程中会将“ChunkedMemoryStream”值传递给“serializationStream”，如下图所示：

![v2-8c58b5cd5e04cda6d18b2e316cf07f2a_720w.jpg](https://image.3001.net/images/20220825/1661400166_6306f466590d019933e14.jpg!small)

在ObjectReader.Deserialize处首先调用__BinaryParser. __BinaryParser，如下图所示：

![v2-bd908c98906a7485c2fa492cdf235a21_720w.jpg](https://image.3001.net/images/20220825/1661400167_6306f46701340d6507d61.jpg!small)

在__BinaryParser.
__BinaryParser将“serializationStream”实例化一个steam对象，并赋值给“this”，如下图所示：

![v2-d7b10486c38d74ecde98bb2b931affae_720w.jpg](https://image.3001.net/images/20220825/1661400167_6306f467a101813991f14.jpg!small)

调用ObjectReader.Deserialize中对this进行反序列化操作。在反序列化过程中，因为攻击向量为TypeConfuseDelegate，反序列化工程中会执行SortedSet<T>的反序列化，其中IDeserializationCallback
接口定义的 OnDeserialization() 方法用于在反序列化后自动调用。

![v2-130c022146f31ff191beb86477562c4e_720w.jpg](https://image.3001.net/images/20220825/1661400168_6306f468582ec4b9fc46d.jpg!small)

观看SortedSet<T> 的OnDeserialization() 函数，可以看到其先取出 Comparer赋给当前新的
SortedSet<T>对象，即this，然后调用Add方法来添加元素。如下图所示：

![v2-b9fc62b698920411c84892eb80970f79_720w.jpg](https://image.3001.net/images/20220825/1661400168_6306f468e2019f6cada4b.jpg!small)

在SortedSet<T>使用Add方法添加第二个元素时就会开始调用比较函数。也就是说，在反序列化SortedSet<T>
时，会触发SortedSet<T>排序，进而调用设置的比较器中的比较函数，如下图所示：

![v2-20f22ebeb2ed5cac5fb6cee8961ba5dd_720w.jpg](https://image.3001.net/images/20220825/1661400169_6306f469891bc06291e69.jpg!small)

由于可以设置比较函数，而且传给比较函数的两个参数就是Add的前两个string 元素(可控)，那么如果将比较函数设置为Process.Start()
函数，我们就可以实现代码执行了。

![v2-7e6b5cfb2f2badd67ff4f6f22de387e1_720w.jpg](https://image.3001.net/images/20220825/1661400170_6306f46a3ecb734f9e58c.jpg!small)

###  **Part5修复建议**

将软件升级至3.5.17以后的版本。

* * *

目前，安帝科技工业互联网安全虚拟化靶场平台已集成该漏洞分析研究的环境和组件，可测试、验证、演示该漏洞及其利用过程。

![v2-1b743ed410bce4e671238a92ffec9341_720w.jpg](https://image.3001.net/images/20220825/1661400171_6306f46b09159d487b3ba.jpg!small)

靶机启动界面

![v2-f5b9a2eb52a50274bcc20d30b12c8e38_720w.jpg](https://image.3001.net/images/20220825/1661400171_6306f46bb4a95da20beb4.jpg!small)

漏洞复现过程文章

安帝科技工业网络靶场定位于一个能够映射真实的IT/OT运营环境的可配置和可扩展的成本效益比高的混合平台，可批量整合（虚拟、实体）OT环境特定的硬件资源(不同供应商的PLCs、HMIs、RTUs、历史数据库、SCADA等)，同时模拟出IT/OT的各种工业流程场景和攻击场景，将虚拟化IT/OT网络与工业流程仿真模型相结合，提供安全可靠的科研、教育、培训、演练、对抗、比赛、演示等功能和服务。

![v2-481c073f1f401c89a799474571ec7363_720w.jpg](https://image.3001.net/images/20220825/1661400172_6306f46c54847424bf7e9.jpg!small)

工业互联网安全虚拟化靶场平台首页

 **SAFE获取更多情报**

联系我们，获取更多漏洞情报详情及处置建议，让企业远离漏洞威胁。  
电话：18511745601

邮箱：shiliangang@andisec.com

