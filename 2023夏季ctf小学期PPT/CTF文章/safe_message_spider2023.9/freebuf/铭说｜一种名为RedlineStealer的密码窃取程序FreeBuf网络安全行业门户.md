## **0 1 ****序言**

 **Redline Stealer是一个运行于MaaS（恶意软件即服务）模式的信息窃取程序。**
该恶意软件由C#编写而成，且在地下论坛根据功能的不同以不同的价格出售。

研究人员在windows系统上通过Regsvcs.exe部署Redline Stealer。Redline Stealer通过process
hollowing技术安装，Redline Stealer的装载器会在进程挂起状态时替换Regsvcs.exe进程的内容。然后RedLine的
PE（可移植可执行文件）会被映射到Regsvcs进程中，并且线程上下文会被指向Stealer的入口点，通过以上操作，stealer被伪装成合法进程在系统中运行。
**本文主要是通过代码分析Redline Stealer所运用的技术。**

###  **02** **Stealer的特征**

■窃取用户信息，如信用卡信息、登录数据和浏览器中自动填充表单；

■以目标电脑桌面和文档目录中的用户文件作为目标。文件抓取器专门查找加密数据，如钱包和种子相关文件；

■能够标记并窃取存储在电子账户中的信息，最多能标记10个加密电子钱包和40个电子账户浏览器扩展信息；

■对目标电脑桌面截图；

■窃取目标系统上安装的FileZilla FTP应用程序和V（虚拟）P（专用）N（网络）应用程序存储的用户数据信息；

■窃取Steam应用程序中的存储的特定用户数据和Discord令牌；

■能够在目标系统上执行命令和附加Payload。

##  **03** **内置配置**

RedLine stealer内置配置中存在一个叫Arguments的类，Arguments **包含以下字段** ：

![](https://image.3001.net/images/20221129/1669720869_6385eb25434ac859e9bbf.png!small)

![](https://image.3001.net/images/20221129/1669720891_6385eb3ba7effb5f8ae72.png!small)

RedLine stealer使用的加密方式包含 **base64加密和异或运算：**

■先将base64解密的数据做异或运算；

■再用base64解密上一步异或运算得出来的数据；

■最后得出的数据才是被RedLine stealer用于Command & Control通信的数据。

![](https://image.3001.net/images/20221129/1669720922_6385eb5acea6bab88ab1a.png!small)

通过base64解密出的数据的每个字符与运算结果进行异或运算（each_key_char % key.Length）

![](https://image.3001.net/images/20221129/1669720949_6385eb75a20d730711c21.png!small)

##  **04** **区域检查**

Redline运行前会先 **检测目标服务器所在地区** ，如下图所示：

![图片](https://image.3001.net/images/20221129/1669721208_6385ec7879ec789d16785.png!small)

RedLine
stealer保存了一份独联体国家的列表，如果目标服务器属于列表中的任何国家，则程序终止运行。这对于独联体国家的对手国家恶意软件程序开发者来说是很常见的行为。

![图片](https://image.3001.net/images/20221129/1669721218_6385ec826a84cc78e6e57.png!small)

##  **05** **Command & Control IP配置**

在区域检查之后，RedLine stealer从数据包中获取C2配置。

RedLine Stealer行为由参数控制，在获取到配置信息后，RedLine
Stealer会加载配置信息并将配置信息存储在一个叫settings的类中。

文件抓取器的配置中包含一个 **检查数据目录路径** 的方法，还包含一个用于 **检索目录中数据** 的方法。通过这两个方法， **RedLine
stealer会窃取所有文本文件和文档，还有** **包含密钥、电子账户和种子信息的文件** 。

![图片](https://image.3001.net/images/20221129/1669721245_6385ec9d4175488a6930a.png!small)

Redline会窃取各种应用程序的用户数据，包括浏览器、游戏启动器和虚拟专用网络。

![图片](https://image.3001.net/images/20221129/1669721263_6385ecaf6a5453c0d7428.png!small)

Redline同样会窃取电子钱包数据，配置信息中包含电子钱包的名字和从相应应用程序的用户数据目录中检索到的环境变量。

![图片](https://image.3001.net/images/20221129/1669721277_6385ecbdee00d0f71cbd4.png!small)

##  **06** **Redline stealer的实现**

 **Redline stealer的核心能力通过两种模式实现：** **FullInfoSender** 和 **PartsSender**
，两者相互独立。Redline
stealer通过软件版本来确定软件所运行的模式，版本号为1的运行FullInfoSender。FullInfoSender和PartsSender之间没有功能上的区别，它们遵循完全相同的逻辑。

![图片](https://image.3001.net/images/20221129/1669721295_6385eccf4f72796db4f2b.png!small)

Redline stealer能够执行各种操作。除了FullInfoSender和PartsSender之外，
TaskResolver类还提供了命令和payload执行能力。

![图片](https://image.3001.net/images/20221129/1669721313_6385ece1e1f0b8cda10da.png!small)

##  **07** **动态链接**

Redline stealer拥有 **在程序运行时动态加载DDLs** （动态链接库）去 **执行各种数据窃取活动**
的能力。Win32的API接口LoadLibraryA和GetProcAddress通过平台调用服务（P/invoke）定义。平台调用服务（P/Invoke）是公共语言基础结构（CLI）实现的一项功能，它能够通过管理代码调用本机代码。通过该服务，Redline
stealer能够在内存中加载特定的DLL模块，然后使用加载的DLL中的特殊方法去解析地址。

![图片](https://image.3001.net/images/20221129/1669721335_6385ecf7199222c7752bd.png!small)

动态加载DDLs主要运用在两个地方，一个是Redline stealer调取特定于浏览器的存储数据，另一个是抓取受害桌面截图。如：Redline
stealer在执行数据窃取过程中，加载bcrypt.dll执行各种密码运算操作。

Redline stealer能够加载gdi32.dll来执行图像相关进程，这个动态链接库被恶意软件广泛运用于屏幕捕获。Redline
stealer主要运用的是GetDeviceCaps函数。

![图片](https://image.3001.net/images/20221129/1669721349_6385ed05242a6826a290a.png!small)

##  **08** **系统信息**

 **信息窃取软件一般通过Windows 管理规范（WMI）来获得受害者的系统信息。** 以下为Redline stealer需要的信息：

■用户名称；

■屏幕分辨率；

■语言和windows版本；

■CPU、GPU和内存信息；

■已安装的浏览器；

■已安装的程序；

■已安装的防病毒程序；

■运行中的进程；

■可用的语言。

 **Redline stealer基于收集到的信息绘制用户模型并发送给C2服务器。**

![图片](https://image.3001.net/images/20221129/1669721377_6385ed215e28dad722b08.png!small)

##  **09** **浏览器数据**

 **Redline stealer主要从浏览器存储数据中获取以下信息：**

■Cookie；

■自动填充表单；

■存储的密码；

■存储的信用卡信息。

像其他信息窃取软件一样，Redline stealer **通过以下操作来窃取信息** ：

■获得浏览器中存储的SQL数据库文件；

![图片](https://image.3001.net/images/20221129/1669721404_6385ed3c129eafdd077c5.png!small)

■窃取存储在浏览器的“Local State”文件中的解密密钥，这些密钥是用来保护用户数据目录中的数据；

■接着Redline stealer利用解密密钥将数据库里面的数据解密；

■解密后的数据再发回C2服务器。

![图片](https://image.3001.net/images/20221129/1669721418_6385ed4a057fc238ff7dd.png!small)

Redline stealer通过构建SQL查询语句从数据库中获取数据：

![图片](https://image.3001.net/images/20221129/1669721432_6385ed58f1be45268e51d.png!small)

##  **10** **文件窃取**

通过解析C2服务器配置，发现在Id10文件存储了用户桌面目录和文件目录的匹配模型。Redline
stealer根据这些信息搜索并窃取所有包含了key、wallet、seed字段的文件和所有的文本和文件。

![图片](https://image.3001.net/images/20221129/1669721457_6385ed719e313a23397fa.png!small)

以下函数获取Id10的值通过FileSearcher.Search方法来完成搜索。

![图片](https://image.3001.net/images/20221129/1669721470_6385ed7eb174bc601fae6.png!small)

##  **11** **电子钱包和扩展**

 **C2服务器配置信息中包含供Redline stealer检索的电子钱包应用名** ，以下为目录详细内容（%AppData%）：

![图片](https://image.3001.net/images/20221129/1669721489_6385ed9116d2c094c1db0.png!small)

Redline stealer对照C2服务器配置信息中的电子钱包应用目录进行筛查，如果找到了相应的应用，Redline
stealer会将取得的“wallet.dat”文件发送给C2服务器。

![图片](https://image.3001.net/images/20221129/1669721506_6385eda2119effba0e0da.png!small)

 **Redline stealer还会收集安装在浏览器上的电子钱包扩展程序。** Redline
stealer有一个base64加密的数组将电子钱包扩展程序用“<extension_folder_id> | <extension_name>
”格式存储起来。扩展程序存储的重要数据会发送给C2服务器。

![图片](https://image.3001.net/images/20221129/1669721516_6385edac9a7f63956ae95.png!small)

##  **12** **游戏启动器**

Redline stealer会检索Steam程序路径：

![图片](https://image.3001.net/images/20221129/1669721534_6385edbeabd02a6b2985d.png!small)

Redline
stealer主要着重查找包含ssfn字段的，config文件和vdf文件。文件路径是通过实例化GameLauncher类生成的。然后利用FIleScanning.Search方法搜索这些文件，生成的数据最终会发送给C2服务器。

![图片](https://image.3001.net/images/20221129/1669721544_6385edc845684de905b72.png!small)

##  **13 V（虚拟）P（专用）N（网络）**

Redline stealer主要关注以下这几个虚拟专用网络：

■NordV（虚拟）P（专用）N（网络）

■OpenV（虚拟）P（专用）N（网络）

■ProtonV（虚拟）P（专用）N（网络）

 **对于处理NordV（虚拟）P（专用）N（网络）程序：**

■Redline stealer会检索路径C:\Users\user\AppData\Local\NordV（虚拟）P（专用）N（网络）；

■将NordV（虚拟）P（专用）N（网络）.exe目录中的“user.config”（xml）文件筛选出来；

■打开用户配置查找包含“//setting/value”的代码；

再将获取到的数据加密后发送给C2服务器。

![图片](https://image.3001.net/images/20221129/1669721568_6385ede01046eff9da359.png!small)

 **对于OpenV（虚拟）P（专用）N（网络）和ProtonV（虚拟）P（专用）N（网络）** ，Redline
stealer分别从相应的目录中搜索config文件和ov（虚拟）p（专用）n（网络）文件。

##  **14** **FTP程序**

 **Redline stealer主要关注FileZilla这个FTP程序** ，在目标系统的APP数据目录中检索以下两个文件：

■sitemanager.xml

■recentservers.xml

获取上述XML文件的路径后，Redline stealer将解析并窃取密码和用户信息。

![图片](https://image.3001.net/images/20221129/1669721589_6385edf5bfae669af4a95.png!small)

##  **15** **屏幕窃取**

 **Redline stealer通过以下操作对受害者的桌面截屏：**

■Redline
stealer对获得的屏幕比例信息进行处理，通过在内存中加载gdi32.dll动态链接库，然后使用GetDeviceCaps的方法获取每个像素点的位数来计算出屏幕大小；

■在计算出屏幕大小后，屏幕截取程序开始工作，将截图出来的图像文件以png格式输出，再发送给C2服务器。

![图片](https://image.3001.net/images/20221129/1669721609_6385ee091d35e9c06ed03.png!small)

##  **16** **任务执行**

 **Redline stealer为操作者提供了额外的运行RAT/beacons之类的payload的能力** 。Redline
stealer通常通过payload或OS命令从C2服务器获得任务列表。

![图片](https://image.3001.net/images/20221129/1669721627_6385ee1b8a397a0444069.png!small)

Redline stealer提供了以下 **4种** 功能来在目标系统中执行附加任务：

 **■通过cmd执行命令**

该功能能够使操作者通过cmd.exe执行命令：

![图片](https://image.3001.net/images/20221129/1669721638_6385ee26edc85472ee78a.png!small)

 **■下载并执行payload**

该功能能够使Redline stealer在网络上下载并执行payload：

![图片](https://image.3001.net/images/20221129/1669721648_6385ee30cedc1dce854d3.png!small)

 **■仅下载功能**

该功能仅下载payload但不执行，若需要执行payload，则需要使用仅执行功能：

![图片](https://image.3001.net/images/20221129/1669721659_6385ee3bda8703dbc58d8.png!small)

 **■仅执行功能**

该功能仅执行payload但不下载，该功能可以跟在仅下载功能后使用：

![图片](https://image.3001.net/images/20221129/1669721672_6385ee4875e608dfc0ac2.png!small)

##  **17** **通信**

Redline
stealer使用http//tempuri[.]org/Entity/Id<1-24>作为命令来控制，若没有提供正确的口令，该域名会被重定向到bing.com。

![图片](https://image.3001.net/images/20221129/1669721693_6385ee5d27581c8468cd1.png!small)

##  **小 结**

综上所述，Redline
Stealer是一种恶意窃取密码的软件，会窃取受害者设备中的敏感数据，例如密码、保存的银行卡详信息、加密货币钱包以及V（虚拟）P（专用）N（网络）服务的凭证。目前Redline
Stealer已被大量利用，这背后的主要原因是它有效地利用了现代 Web 浏览器难以解决广泛可用的安全漏洞。

对此， **专家方面建议** **不要轻易点击可能具有钓鱼企图的邮件** ，这是此类恶意软件被植入的主要方法。

