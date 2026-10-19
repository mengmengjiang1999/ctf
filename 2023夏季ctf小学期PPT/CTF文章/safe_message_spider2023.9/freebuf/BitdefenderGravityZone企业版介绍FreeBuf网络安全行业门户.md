Bitdefender GravityZone 企业版提供了两种部署方式：

1\. **本地私有化部署** ，控制台部署到公司内部

2\. **SaaS云控制台版本** ，

此版本非常适合 远程办公，中小型企业，跨地区，跨区域的企业，控制台在云端，开帐号即可用，无需准备服务器部署控制台，可以在一个控制台全立全球的设备。

  

 **本文将介绍SaaS云控制台版本:**  

  

 **一. 获取登陆帐号**

填写试用表单，备注云版本，Bitdefender解决方案顾问会为你创建试用环境： <http://www.bitdefender-cn.com/trial.html>

系统会自动发送登陆凭据到邮箱

![1.png](https://image.3001.net/images/20200618/1592466335_5eeb1b9f4faad.png!small)

  

 **二. 登陆云控制台**
[https://gravityzone.bitdefender.com](https://gravityzone.bitdefender.com/)

此处可以选择简体中文，或者其它语言，总共11种语言，管理员可根据自己的喜好，选择语言登陆。

输入邮箱地址，进入安全验证，验证此帐号后，可进入下一步输入登陆密码：  

![2.png](https://image.3001.net/images/20200618/1592481728_5eeb57c0daae3.png!small)  

再次进入安全验证，2FA双重认证，需要输入Google身份验证器的6位验证码。

创建帐号时默认勾选开启了2FA，确保安全，也可以去掉此步骤，国内能正常使用Google身份验证器

![3.png](https://image.3001.net/images/20200618/1592466725_5eeb1d252a83e.png!small)  
进入控制台， **仪表盘** ，显示相应的报表事件，让你可以清晰查看状态，可点击相应的区域/元素，查看相应的事件  

![4.png](https://image.3001.net/images/20200618/1592466843_5eeb1d9ba6a4c.png!small)  

 **事件区域**

EDR模块的核心作用区域，EDR的事件是通过EPP传感器获取的，客户端集成了EPP+EDR

EPP拦截绝大部分事件， 降低警报和后面EDR事件数量，让你只需要花费少量的时间，关注高级复杂攻击

  

 **调查** 区域：展现Bitdefender未识别的新威胁，你需要密切关注此处的事件，根据标签卡调查事件和响应  

 **查看** 区域：查看Bitdefender已经识别的新威胁，你可以打开标签卡，调查并响应

你可以通过过滤器进行过滤，按危险评分过滤，或其它条件过滤  

![image.png](https://image.3001.net/images/20200618/1592467264_5eeb1f402d334.png!small)  

点击每个事件，进入事件分析视图，清晰展现每一步的动作，并提供响应的分析和缓解建议

![image.png](https://image.3001.net/images/20200618/1592467309_5eeb1f6dc7063.png!small)  

每个事件都提供了完整的分析树

![image.png](https://image.3001.net/images/20200618/1592467356_5eeb1f9cba243.png!small)  

管理员也可以远程对 **主机采取操作** ： **隔离主机，安装补丁，远程连接**

![image.png](https://image.3001.net/images/20200618/1592467444_5eeb1ff415a58.png!small)  

Bitdefender对事件的每一个步骤和维度都有详细的输出，例如查看网络连接：

![image.png](https://image.3001.net/images/20200618/1592467549_5eeb205dde638.png!small)  

可以进行丰富的搜索操作

![image.png](https://image.3001.net/images/20200618/1592467645_5eeb20bd527a1.png!small)  

 **黑名单区域，安全管理员可以添加MD5，哈希等，阻止文件执行，这是一个很好的应急响应工具**  
  
 **案例：**
黑客通常发送鱼叉式钓鱼附件，例如office文件，PDF，压缩文件等，如果端点安装的反病毒软件万一无法识别，用户打开文件，则用户计算机与黑客建立CC会话，电脑中招  
  
如果管理员可以添加附件MD5或哈希，则可不用喊话，广播  

![image.png](https://image.3001.net/images/20200618/1592467694_5eeb20ee8d986.png!small)![image.png](https://image.3001.net/images/20200618/1592467705_5eeb20f974ceb.png!small)  
  

 **事件搜索** ，提供高级查询，可依据自己的需求查询事件信息  

![image.png](https://image.3001.net/images/20200618/1592467732_5eeb211419f54.png!small)
**  
**

 **网络区域** ，列出所有托管设备&实时状态，提供了丰富的过滤器，管理员可以在此处查看端点的详细信息，添加/删除分组，运行远程任务，分配策略等等。  

![image.png](https://image.3001.net/images/20200618/1592467777_5eeb214191895.png!small)  
可以对整个组，或者单个，多个设备，分发任务， **管理员也可以在此处，对目标端点分发安全任务：**
**扫描，风险扫描，漏洞扫描，安装补丁，更新，卸载，重配置功能模块等。**

![image.png](https://image.3001.net/images/20200618/1592467844_5eeb218446750.png!small)

  

 **点击某个设备** ，弹出信息窗口，管理员可以查看客户端的防护状态，策略，扫描日志，并可以远程故障排除

如果某个指标异常，则会红色标签提示，例如：病毒库没更新，发现病毒，模块异常等。

![image.png](https://image.3001.net/images/20200618/1592467993_5eeb2219de805.png!small)  

 **补丁清单** ：运行漏洞扫描任务后，控制台集中显示所有设备的漏洞情况，包括操作系统和第三方应用程序，都可以修复补丁。厂商建议:
保持系统和软件更新，避免安全漏洞

你可以通过丰富的过滤器，进行搜索，排序，勾选相应的补丁完成补丁安装动作

![image.png](https://image.3001.net/images/20200618/1592467882_5eeb21aa11c09.png!small)

  

管理员可以对整组织，所选设备，一键分发补丁安装任务，当然也可以在策略中设置自动扫描漏洞，自动安装补丁，并且不强制重启。  
![image.png](https://image.3001.net/images/20200618/1592468061_5eeb225d523eb.png!small)  

 **安装包  
**

在安装包区域，创建安装包  

![image.png](https://image.3001.net/images/20200618/1592468144_5eeb22b035f99.png!small)  
编辑安装包功能模块：

![image.png](https://image.3001.net/images/20200618/1592468507_5eeb241b3b300.png!small)![image.png](https://image.3001.net/images/20200618/1592468536_5eeb24389c3cf.png!small)  
 **下载安装包部署：**

可通过发送email邀请同事安装

![image.png](https://image.3001.net/images/20200618/1592469249_5eeb27017607b.png!small)

  
  

 **任务区域** ：管理员分发的任务，都在这里有记录，可以查看详细信息，状态，报表等  

![image.png](https://image.3001.net/images/20200618/1592469462_5eeb27d6175ea.png!small)  
  

 **风险管理：** 主动发现资产的配置错误，是否遵循Windows安全基线配置，程序漏洞，提供自动、手动修复功能  

![image.png](https://image.3001.net/images/20200618/1592469995_5eeb29eb86cc5.png!small)

  

提供丰富的视图，Bitdefender自动扫描已知和最新的漏洞，例如SMB V3，并且持续更新  
![image.png](https://image.3001.net/images/20200618/1592470044_5eeb2a1c86eb5.png!small)

 **查看安全风险指标**

![image.png](https://image.3001.net/images/20200618/1592470219_5eeb2acb8f2b3.png!small)
**查看程序漏洞**

![image.png](https://image.3001.net/images/20200618/1592470207_5eeb2abf9465a.png!small)  

点击风险指标，自动弹出修复建议和操作

![image.png](https://image.3001.net/images/20200618/1592470173_5eeb2a9db3651.png!small)![image.png](https://image.3001.net/images/20200618/1592470245_5eeb2ae5d4a08.png!small)  

 **策略区域，** 管理所有的配置，一个策略模板支持Windows，Linux，mac OS， 虚拟化环境等  

![image.png](https://image.3001.net/images/20200618/1592470450_5eeb2bb2f1556.png!small)  

点击打开配置策略，策略配置保持后，自动下发，1分钟内应用到目标  

 **反恶意软件设置：**

![image.png](https://image.3001.net/images/20200618/1592470517_5eeb2bf5a1bee.png!small)  

 **关键技术策略配置：** 高级威胁防护，无文件攻击防护 对Powershell攻击，挖矿等100%阻断  
![image.png](https://image.3001.net/images/20200618/1592482139_5eeb595b22ece.png!small)

 **HyperDetect可调节机器学习** ，通过5亿用户的海量样本持续训练和机器学习，提前阻断未知威胁。

![image.png](https://image.3001.net/images/20200618/1592482174_5eeb597eef3d4.png!small)  

 **高级反漏洞，** 阻断提权和未经授权访问LSASS.EXE，  

![image.png](https://image.3001.net/images/20200618/1592482273_5eeb59e180ecd.png!small)  
利用机器学习拦截一系列漏洞利用技术, **不依赖特征码**  

![image.png](https://image.3001.net/images/20200618/1592482376_5eeb5a48bfd54.png!small)  

 **安全服务器：** 针对虚拟化环境，超融合，容器等提供特殊优化的安全保护

![image.png](https://image.3001.net/images/20200618/1592482503_5eeb5ac79ac4f.png!small)  

 **沙盒分析器：额外的安全防护层，实现可疑文件安全分析自动化，并提供手动分析功能，提供深度分析报告**

可运行在监控模式：可先使用，分析结果出来了决定动作

或拦截模式：先分析出结果了才能运行

内容预过滤技术提升检测速度

![image.png](https://image.3001.net/images/20200618/1592482523_5eeb5adbca255.png!small)  

防火墙：配置规则，阻止未经授权的访问

![image.png](https://image.3001.net/images/20200618/1592482568_5eeb5b0812642.png!small)
**  
**

 **网络攻击防护：根据ATT & CK 矩阵拦截5大分类**

防止攻击者利用网络漏洞来访问系统，进行横向移动。全面拦截暴力破解攻击，端口扫描，Samba攻击，服务漏洞攻击，窃取密码，网络漏洞利用，SQL注入攻击，目录遍历，僵尸网络攻击，恶意网址，远程IoT攻击，TOR/Onion连接等等。  
![image.png](https://image.3001.net/images/20200618/1592482646_5eeb5b56401ef.png!small)  

 **补丁管理** ：可设置本地补丁缓存服务器，下载补丁分发到内网电脑，配置自动补丁和漏洞扫描任务

![image.png](https://image.3001.net/images/20200618/1592482686_5eeb5b7ecfdc3.png!small)  

 **设备控制** ，控制移动硬盘等

![image.png](https://image.3001.net/images/20200618/1592482756_5eeb5bc4885a6.png!small)  

 **风险管理** ，自动风险分析

![image.png](https://image.3001.net/images/20200618/1592482785_5eeb5be1e0d66.png!small)  

 **策略分配规则：** 管理员可以建立多个策略模板，并根据用户的所在位置，自动切换策略  

![image.png](https://image.3001.net/images/20200618/1592482838_5eeb5c16afe1f.png!small)
**  
**

 **报表** 区域，提供丰富的报表模板，可添加立即报表，计划报表，自动发送到邮箱  
![image.png](https://image.3001.net/images/20200618/1592482865_5eeb5c31d0484.png!small)  

例如：网络事件报表，可查询当前网络中所有的攻击者IP

![image.png](https://image.3001.net/images/20200618/1592482923_5eeb5c6b29538.png!small)  

 **隔离区，** 集中显示所有设备被隔离的文件，此处可一键恢复被隔离的文件,并自动加入到排除规则  

![image.png](https://image.3001.net/images/20200618/1592482937_5eeb5c791c3c9.png!small)  

 **帐号区域：** 可添加一个或多个管理员账户，管理安全  

![image.png](https://image.3001.net/images/20200618/1592482998_5eeb5cb64f023.png!small)  

 **沙盒分析器:**
客户端自动将可疑文件发送到云沙盒分析，沙盒门户将结果反馈控制台和客户端，客户端根据判决采取操作。默认4分种返回结果，非常快，可以不用手动抓可疑文件给厂商入库了，一切安全自动化解决。

![image.png](https://image.3001.net/images/20200618/1592483071_5eeb5cffb16c2.png!small)  

 **点击事件卡** ，可查看详细分析结果，非常丰富信息

![image.png](https://image.3001.net/images/20200618/1592483202_5eeb5d828ae07.png!small)  
![image.png](https://image.3001.net/images/20200618/1592483269_5eeb5dc591e5e.png!small)  
![image.png](https://image.3001.net/images/20200618/1592483280_5eeb5dd0eb823.png!small)![image.png](https://image.3001.net/images/20200618/1592483289_5eeb5dd9dcea5.png!small)![image.png](https://image.3001.net/images/20200618/1592483299_5eeb5de32abb7.png!small)![image.png](https://image.3001.net/images/20200618/1592483331_5eeb5e03768c6.png!small)![image.png](https://image.3001.net/images/20200618/1592483351_5eeb5e17534b4.png!small)  

 **管理员也可手动提交文件，URL到Bitdefender云沙盒分析，提供了非常方便的安全分析工具**  

**![image.png](https://image.3001.net/images/20200618/1592483381_5eeb5e359a39c.png!small)  
**

 **配置：强制2FA，使用SSO单点登录**

**![image.png](https://image.3001.net/images/20200618/1592483409_5eeb5e51ac913.png!small)  
**

 **三. 客户端截图**

Bitdefender的客户端非常简洁，几乎是安装后可以忘记它。主面板即事件显示面板，以时间轴形式显示

**![image.png](https://image.3001.net/images/20200618/1592483544_5eeb5ed8ef527.png!small)  
**

**![image.png](https://image.3001.net/images/20200618/1592483602_5eeb5f12adbd4.png!small)  
**

 **
**![image.png](https://image.3001.net/images/20200618/1592483575_5eeb5ef7e6547.png!small)**
**  
**右下角图标，可一键切换语言**

**![image.png](https://image.3001.net/images/20200618/1592483690_5eeb5f6a391af.png!small)  
**

**![image.png](https://image.3001.net/images/20200618/1592483662_5eeb5f4e16a4f.png!small)![image.png](https://image.3001.net/images/20200618/1592483772_5eeb5fbccbac8.png!small)  
**

到此介绍完成，欢迎免费试用:<http://www.bitdefender-cn.com/trial.html>

如有需求，欢迎致电：4000-132-568

扫一扫，立即关注Bitdefender！

![cli_258px.png](https://image.3001.net/images/20200618/1592483821_5eeb5fed0df97.png!small)  

