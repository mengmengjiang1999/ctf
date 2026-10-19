## **一、前言**

信息系统的保密性、完整性、可用性、可控性和不可否认性是信息系统安全5大特征，作为个人电脑操作系统开发商，微软不断的在各类新系统上推陈出新，最主要的便是在Windows2000开始引入的一类系统程序接口DPAPI。DPAPI面向各类系统内部应用及第三方应用软件提供可信加密信道，其中包括高强度且可自定义的数据加密和解密服务。随着windows系统支持认证方式的不断变换，windows加密体系也在不断的发展更新。

##  **二、DPAPI**

由于绝大多数应用程序都为用户提供各类账户服务，而登录所需凭证密码则成为黑色产业和黑客最为青睐的东西，如若每次登录需重新输入密码或者使用OTP短信动态验证码等方式，又容易造成用户易用性上的损失，因此就需要一种信息处理机制能够加密存储相关凭证，使用时又不需要用户手动输入信息以达到隐藏登录的目的，在此情况下微软数据保护接口（Data
Protection Application Programming
Interface，简称DPAPI）应运而生。该接口调用系统加解密函数，通过由windows系统用户密码加密的系统用户密钥对用户凭证加密。目前使用DPAPI的应用包括Chrome及ie自动填充密码和cookie、sqlsever、Outlook，同时也包括windows内部功能如EFS、WIFI、凭据管理器、域注册和域内通信等等。

实际DPAPI
内部加密调用流程纷繁复杂且微软官方也未公布过其内部实现细节，那又如何理解其中原理呢？在DPAPI中调用的算法和密钥又是什么呢？下面分开给大家介绍：

###  **1\. windows系统加解密算法**

介绍windows系统的加密算法，又不得不从微软加密技术说起。繁杂庞大的微软加密技术包括 CryptoAPI（cryptography
application programming interface,简称CryptoAPI）、加密服务提供商 ( cryptographic service
provider，简称CSP）
、CryptoAPI工具、CAPICOM、WinTrust、颁发和管理证书，以及开发可自定义的公钥基础结构等等模块，可以说是囊括了大部分密码学场景。

其中CryptoAPI便是系统提供的用来对数据加解密的接口，而后面的CSP则是真正实现加密解密签名等动作的模块，每一个CSP包是一组实现标准加密和签名算法的硬件和软件的组合，如windows默认调用的CSP包名为PROV_RSA_FULL，其中包含的算法如图1所示，通常使用USB方式插入的加密机等硬件一般也是通过在系统中注册一个新的CSP包以供使用。在实际加密中，通过CryptoAPI进行运算时，可以采用参数方法对使用的加密算法（CSP包）进行控制。前文提到的DPAPI则是微软为方便开发人员及用户调用对CryptoAPI封装后提供的接口，更易于使用。

![](https://image.3001.net/images/20211122/1637562727_619b3967b0d8e0c5c2749.png!small)图1
windows默认CSP包PROV_RSA_FULL

###  **2\. windows系统密钥**

介绍完算法，就要介绍算法所使用密钥，首先了解到的是windows用户体系中有多种用户组，包括管理员用户、普通用户、来宾（Guest）用户等等，不同的用户使用SID（Security
Identifiers）也就是安全标识符区分，每个用户在创建时均会生成一个密钥，加密后存放在用户目录％APPDATA％\Microsoft\Protect\％SID％下，而系统主密钥则加密存放在％WINDIR％\System32\Microsoft\Protect\S-1-5-18\User下，在使用DPAPI进行加解密时用调用当前用户的密钥进行运算，也防止黑客获取某一用户命令执行权限后威胁其他用户安全。

密钥文件包括数个数据单元块，这里就不具体阐述。值得一提的是，加密采用的迭代次数、安全散列算法类型和对称加密算法类型在不同的系统有不同的配置，如在Windows7下，PBKDF2迭代次数为5600，散列算法为SHA-512，加密算法为AES-256。

微软为了防止长期采用一个用户主密钥导致的泄密风险，为每个用户主密钥设置了90天的有效期，超过90天会生成新的用户主密钥替换使用，但密钥更新后原有加密内容又如何解密呢？实际上用户目录下加密状态的用户主密钥文件是由用户密码和用户SID生成的会话密钥对用户主密钥加密得出的，目录下会存放所有历史用户主密钥和正在使用的用户主密钥，由Preferred文件中的GUID指向正在使用的用户主密钥。但如果用户主动更改密码，系统会Hook系统安全进程lsass.exe，使用新的用户密码重新生成会话密钥，并对所有用户主密钥重新加密（如图2）。同时还存在一个历史凭证文件CREDHIST，当修改密码时旧密码的sha-1散列会用新的密码加密，从而形成一个密码链以供系统解密旧用户主密钥加密的密钥。

各类解密用户主密钥以及相关利用工具网络上已经出现很多，如mimikatz、lsadump、laZagne、dpapilab、dpapick等等。

![](https://image.3001.net/images/20211122/1637563065_619b3ab9a22ea55818d14.png!small)图2
用户配置目录下加密状态的用户主密钥既Preferred文件

了解了加密算法和加密所使用密钥后，系统是如何使用DPAPI加密的呢，根据逆向Win10系统下DPAPI所调用的dpapi.dll可看出DPAPI一共提供了6个函数（如图3）：

  * CryptProtectData()&CryptUnprotectData()：数据加解密，加密文件落地；
  * CryptProtectMemory()&CryptUnprotectMemory()：内存加解密，重启进程失效；
  * CryptUpdateProtectedState()：用于用户的安全标识符(SID)更改后迁移当前用户的主密钥，也可用于在用户从一个域移到另一个域后保存加密数据；
  * CryptResteMachineCredentials()：重置机器证书认证相关函数。

![](https://image.3001.net/images/20211122/1637564011_619b3e6b7336cec8273e0.jpg!small)图3
dpapi.dll提供函数

Dpapi调用的是CryptProtectData()&CryptUnprotectData()，调用时使用用户密码解密用户主密钥文件获得用户主密钥，使用用户主密钥以及调用时传入的参数生成会话密钥，然后将上一步生成的会话密钥加密待加密数据得出结果，而CryptProtectMemory()&CryptUnprotectMemory()基于内存的加解密函数适用的场景较少，暂且不提。

加密示例，如图4图5：

![](https://image.3001.net/images/20211122/1637563191_619b3b3746adf8e00d73c.png!small)图4
CryptProtectData()&CryptUnprotectData()

![](https://image.3001.net/images/20211122/1637563209_619b3b496992bb40f08de.png!small)图5
CryptProtectMemory()&CryptUnprotectMemory()

如windows的wifi功能就使用了DPAPI加密wifi连接密码，其中wifi配置文件保存在了C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces下，每个wifi信息均保存在了单独文件中，如图6为名称为“**的iPhone”，其中wifi密码keyMaterial为加密状态，使用工具解密即可获得该wifi密码，如图7。

![](https://image.3001.net/images/20211122/1637563258_619b3b7aa8c7fe9af3b8a.png!small)图6
某一wifi信息

![](https://image.3001.net/images/20211122/1637563272_619b3b88a2fd51f1d680a.png!small)图7
wifi密码

##  **三、windows加密的未来**

了解了DPAPI以及CrytoAPI，就基本理解了windows加密体系，但随着windows不断更新，所面临的应用场景越来越复杂，原有的密码认证方式已经逐渐被Windows
Hello生物特征授权机制所替代，包括图片密码、PIN码、人脸、指纹等生物认证方式；原有的加密机制已经不足以满足现有业务安全需求，故而在CrytoAPI1.0原有基础上推出了CrytoAPI2.0，称为CNG（Cryptography
API: Next Generation），有关DPAPI模块也伴随Windows8的发布升级为DPAPI2.0，称为DPAPI-NG或CNG
DPAPI，在原有基础上增加对Windows Hello机制的支持同时也面向云计算需求，使用户能够安全地共享机密 (密钥、密码、密钥材料)
和消息，目前支持主体有Active Directory林中的组以及各类Web 凭据等。

CNG相较于CrytoAPI除了完美支持原有加密机制外，还有以下几方面的提升：

  * 新的加密配置系统以及随机数生成器，支持更好的加密灵活性
  * 更安全灵活的进程线程安全机制
  * 提供了更好的内核模式支持以及内核模式加密API
  * 拓展算法支持包括椭圆曲线加密(ECC)等，以此为基础甚至未来可能支持国密算法
  * 更安全的Microsoft 软件密钥存储提供程序(KSP)等等

落到具体实现，承载DPAPI-NG的相关DLL通常以"ncrypt"开头：ncrypt.dll、ncryptrov.dll和ncryptslp.dll，这些dll负责的API会与lsass进程和DPAPI共同提供服务。

下面以PIN码登录功能为例，如果你没有在机器上启用PIN码登录，%windir%\ServiceProfiles\LocalService\下是不会存在AppData等目录，只有当开启PIN码登录后系统才会创建相关目录。当然在实际系统内部调用时，CNG同样会调用。

以PIN码登录为例，调用DPAPI-NG的完整流程包括：

  * 在%windir%\ServiceProfiles\LocalService\AppData\Local\Microsoft\Ngc目录下保存了PIN码登录相关功能的数据加密块（如图8），其中加密数据保存在\Protectors\1\1dat中，所调用加密算法为RSA，加密使用的公私钥对（非真正使用的公私钥）通过\Protectors\1\2.dat中保存的GUID指向%windir%\ServiceProfiles\LocalService\AppData\Roaming\Microsoft\Crypto\Keys中保存的4组公私钥对数据集中的1组（3对RSA和1对ECS，如图9），在数据集中保存着RSA加密的相关加密配置参数；
  * 在Keys目录下保存着的RSA私钥（非实际加密私钥，真正私钥会在后文中出现），这个RSA私钥是经过DPAPI加密的结果，通过DPAPI解密可以获得由Salt、hash轮数以及一个完整的DPAPI的元数据；
  * Windows Hello PIN码通过哈希及字符串变化可以获得一个PinHash，将PinHash以及静态字符串“xT5rZW5qVVbrvpuA”作为DPAPI解密参数，解密后可以获得RSA算法中的p、q、n和e，通过这几个参数可以组成一个真正的RSA私钥，使用这个私钥可解密dat中的加密数据，可以获得一个108B的数据块，其中中间32B大小的数据称为DecrytPIN，重复1、2、3步，将这个DecrytPIN重新当作1中的加密数据，调用Keys下的公私钥组GUID保存在1.dat中，完成这两次循环后便能得出最终的一个AES加密密钥；
  * 用户密码是通过DPAPI和AES组合加密后保存在%windir%\System32\config\systemprofile\AppData\Local\Microsoft\Vault\下，该目录下保存着DPAPI加密参数，通过DPAPI解密即可获得AES向量IV以及通过AES加密的用户密码，使用3中循环获得的AES密钥解密即可获得用户密码。

![](https://image.3001.net/images/20211122/1637563375_619b3bef8d9f4be7ef04f.png!small)图8
Windows Hello PIN码相关目录

![](https://image.3001.net/images/20211122/1637563390_619b3bfe1994d9397aa3f.png!small)图9
RSA公私钥

其中两次RSA循环解密调用的函数均使用ncrypt.dll中的函数，即为DPAPI-NG相较于DPAPI新增处理方式，也是windows通过DPAPI-NG针对用户身份认证的方式，整个过程如图10。

![](https://image.3001.net/images/20211122/1637563411_619b3c13ec801247a3026.png!small)图10
DPAPI-NG加解密过程

##  **四、结束语**

随着设备、软件的日新月异，各种认证方式的推陈出新，以及各类病毒木马、渗透方法的不断升级，只有更深入到系统内部实现进行研究，才能更好的保护用户以及信息系统的安全。

## 参考链接

[1]https://www.insecurity.be/blog/2020/12/24/dpapi-in-depth-with-tooling-standalone-dpapi/#DPAPI_Master_Keys

[2]https://docs.microsoft.com/zh-cn/windows/win32/seccrypto/cryptography-portal

[3]https://docs.microsoft.com/zh-cn/windows/win32/seccng/cng-features

[4]https://rcoil.me/2019/07/%E3%80%90%E7%9F%A5%E8%AF%86%E5%9B%9E%E9%A1%BE%E3%80%91DPAPI%20%E8%AF%A6%E8%A7%A3/

