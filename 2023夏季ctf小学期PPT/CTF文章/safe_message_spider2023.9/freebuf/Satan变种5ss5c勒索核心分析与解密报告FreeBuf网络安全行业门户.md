# **样本简介**  

撒旦(Satan)病毒是一款恶意勒索程序，首次出现2017年1月份。Satan病毒的开发者通过网站允许用户生成自己的Satan变种，并且提供CHM和带宏脚本Word文档的下载器生成脚本进行传播。Satan勒索病毒主要用于针对服务器的数据库文件进行加密，非常具有针对性。

近期Satan勒索病毒家族在低调几个月后又重新活跃起来，此次捕获到的样本为该黑产团伙释放的母体新变种，最终造成加密的格式为：[5ss5c@mail.ru]c.zip.JAVRIXREHPPDEX8GL1U94XRS04TVJ59C7LT3E2MY，提供的联系邮箱为：5ss5c@mail.ru，加密文件扩展名为：.5ss5c。

该变种本地运行后，实际加密的进程为cpt.exe。

![image.png](https://image.3001.net/images/20200414/1586830228_5e951b94a6cf6.png!small)  

生成的勒索信已经全部使用中文进行描述，如下。  

![image.png](https://image.3001.net/images/20200414/1586830242_5e951ba281b83.png!small)  

文件最终加密的结果，如下。  

![image.png](https://image.3001.net/images/20200414/1586830253_5e951badafacf.png!small)![image.png](https://image.3001.net/images/20200414/1586830257_5e951bb154bb2.png!small)  

##  **样本分析**

继上一篇分析报告对母体恶意文件进行了分析，发现其实质为一种下载器downloader，且附带蠕虫功能，接下来就对此次出现的Satan变种5ss5c勒索核心进行分析。该勒索软件下载来源自黑客的自建服务端，原始后缀非exe文件，为dat后缀文件，下载到本地后发现实质为PE文件，地址：http[:]//58.221.158.90[:]88/car/cpt.dat
黑客对程序的图标进行了伪装，右键查看详细信息处发现非常明显的说明这是一个编码器，版本1.0.0.1，那么接下来还会更新吗？笔者目前不得而知，寄希望于它别更新了。

![image.png](https://image.3001.net/images/20200414/1586831285_5e951fb537a47.png!small)  

同样是之前母体使用过的壳，32位PE文件，编译时间为2020年1月11日19:54:25。  

![image.png](https://image.3001.net/images/20200414/1586831295_5e951fbfaa302.png!small)  

对其脱壳后，查询时还是提示存在壳（实质已经脱壳成功），经分析发现后续关键的加密部分还存在控制流混淆的部分（大量jmp指令），从而阻止分析人员对其关键部分进行静态分析。  

![image.png](https://image.3001.net/images/20200414/1586831309_5e951fcdda366.png!small)  

暂未识别出是由什么编译器或者语言编写的恶意文件，Exeinfo与PEiD也未能识别（后续仔细研究后笔者发现存在VS2015与STL的痕迹，猜测是C++）。  

![image.png](https://image.3001.net/images/20200414/1586831324_5e951fdc571e3.png!small)  

经分析后，先找到关键的代码。  

![image.png](https://image.3001.net/images/20200414/1586831332_5e951fe4c19d0.png!small)  

勒索软件一开始会和普通的勒索软件一样也会设置自启动，首先会创建注册表子键
SOFTWARE\Microsoft\Windows\CurrentVersion\Run 方便后续可以开机自启动，继续执行勒索进程。  

![image.png](https://image.3001.net/images/20200414/1586831374_5e95200ed9436.png!small)

  

设置键值为5ss5cStart，启动的路径为"C:\Users\onion\Desktop\System\cpt.unp.exe"（这里为恶意文件实际所在的系统绝对路径）。  

![image.png](https://image.3001.net/images/20200414/1586831385_5e9520191e230.png!small)

![image.png](https://image.3001.net/images/20200414/1586831389_5e95201d2450c.png!small)  

之后会判断是否存在相关进程（并不是一开始就创建互斥量），如果存在相关进程就直接退出，如当前进程列表里存在cpt.exe进程就先会创建互斥量5ss5c_CRYPT，后续存在多个相同进程则直接退出，保证只允许一个进程运行。  

![image.png](https://image.3001.net/images/20200414/1586831401_5e9520293b0f0.png!small)![image.png](https://image.3001.net/images/20200414/1586831404_5e95202c1f90c.png!small)![image.png](https://image.3001.net/images/20200414/1586831407_5e95202fa0f6d.png!small)  

接着开始进行生成勒索信（_如何解密我的文件_.txt）的流程，这里随机生成的key经处理后会是后续使用到的加密密钥，如下。  

![image.png](https://image.3001.net/images/20200414/1586831415_5e952037e42a1.png!small)  

产生的原理是通过STL内的随机数生成器（RNG）随机生成不超过0x50大小的数据作为位置来取硬编码ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+}{:<>?的值（类似于对其base64编码，对数据进行转换生成可见字符）进行拼接，之后对该生成的字符串进行处理，最后使用硬编码在本地的RSA公钥采用OpenSSL里的加密函数对其加密（会先组合硬编码在程序里的字符串组合成pem文件格式，OpenSSL之后从pem文件中来读取RSA公钥），最终生成勒索信中的用户【解密凭证】。

以下是通过随机数生成器得到随机数后作为位置来获取对应的字符拼接成的200个字节的字符串，后续再组合其余信息会被硬编码在本地的RSA公钥加密后会附加在被加密文件末尾，后续每个加密文件末尾都会存在相同的附加的0x200（512）个字节大小的数据。

![image.png](https://image.3001.net/images/20200414/1586831427_5e95204367520.png!small)  

随机生成在本地的5ss5c_token值作为请求时的参数值通过http请求来访问黑客的服务端，之后每一流程执行完毕后的结果作为请求的参数值会再次发送http请求至服务端。  

![image.png](https://image.3001.net/images/20200414/1586831436_5e95204cd2b81.png!small)  

接着会结束指定的服务与进程，避免加密该服务或进程涉及的文件时导致失败，服务有如下：

"MySQL"、"MySQLa"、"SQLWriter"、"SQLSERVERAGENT"、"MSSQLFDLauncher"、"MSSQLSERVER"、"UxSms"。

需要结束的进程有如下：

"sql"、"oracle"、"sqlservr.exe"、"mysqld.exe"、"nmesrvc.exe"、"sqlagent.exe"、"fdhost.exe"、"fdlauncher.exe"、"reportingservicesservice.exe"、"omtsreco.exe"、"tnslsnr.exe"、"oracle.exe"、"emagent.exe"、"perl.exe"、"sqlwriter.exe"、"mysqld-nt.exe"、"mysqld-nt.exe"。

经分析发现勒索软件会优先寻找硬编码在程序内部的路径下面（主要是涉及到数据相关的路径）是否有符合条件的文件，之后再进行全盘搜索。![image.png](https://image.3001.net/images/20200414/1586831447_5e9520576515d.png!small)![image.png](https://image.3001.net/images/20200414/1586831450_5e95205a66974.png!small)![image.png](https://image.3001.net/images/20200414/1586831453_5e95205d3f8e9.png!small)

  

会将之前在可用磁盘下搜索到的所有可用文件夹路径，写入创建的文件tmp里，后续会根据文件里的路径逐一进行加密，加密过程中系统里新增的文件不会被加密，因为tmp文件里没有更新。

![image.png](https://image.3001.net/images/20200414/1586831468_5e95206c84d41.png!small)![image.png](https://image.3001.net/images/20200414/1586831486_5e95207e40dab.png!small)![image.png](https://image.3001.net/images/20200414/1586831490_5e952082f0d10.png!small)  

勒索软件在FindSql（寻找数据）该流程操作执行完后（实质是寻找特定的数据库文件，因为这类文件的数据很重要，说明黑客此次的目标也很明确，首先就想针对性的进行加密，以求他们的“效益”最大化），再次使用递归函数的方式遍历所有文件与文件夹，找到符合的路径写入tmp文件内。  

![image.png](https://image.3001.net/images/20200414/1586831631_5e95210fe72be.png!small)  

通过获取之前生成的相应字段值进行拼接后，组合成新的文件名，之后使用MoveFileA函数对文件进行重命名，通过后续的分析发现并不会删除源文件，会打开同一个文件两次，第一次会读取文件，会将加密完成的数据写入第二次打开的文件里，造成数据覆写，估计是防止一些磁盘恢复软件对文件进行恢复。  

![image.png](https://image.3001.net/images/20200414/1586831640_5e952118be351.png!small)  

如下示例中，勒索软件会对同一个文件分别打开两次，会将已加密完成的数据写入第二次打开的文件里。  

![image.png](https://image.3001.net/images/20200414/1586831648_5e95212004b02.png!small)  

加密前会设置文件属性，设置为normal属性，其中“只读”、“隐藏”、“系统”、“存档”为文件的四种基本属性，因为文件去掉全部属性后（四种基本属性），将自动标记为normal，估计是为了防止某些文件加密失败。  

![image.png](https://image.3001.net/images/20200414/1586831656_5e95212806858.png!small)  

至此，核心勒索的行为流程分析就结束了。

## **研究加密流程与缺陷**

作为安全研究人员，我们要回答的常见问题是勒索软件是否可以解密？这意味着，如果勒索软件存在弱点或缺陷就很有可能让用户不支付昂贵的勒索费用来恢复文件。

###  **新增文件不加密**

本地实际测试后，发现只会加密之前扫描生成的tmp文件里的目录下的文件，不在该文件内容里的不会主动去加密，也就是说新增文件不会被加密，整体流程运行完毕后勒索进程会自动退出，退出之前会启动记事本程序给用户进行勒索信息提示。

整个勒索进程执行并完全退出后，经查看，让笔者产生奇怪的一点是桌面的有一部分文件实质为重新命名而已，内容并未加密，不知道是否是由于程序本身存在的bug造成加密未完成而进程提前退出了，目前这个暂不得知（所幸，受害者至少还能挽救一点点）。

![image.png](https://image.3001.net/images/20200414/1586831672_5e952138c3748.png!small)  

###  **卷影复制服务**

卷影复制服务（shadow volume
copy）是Windows操作系统中的一项技术，可在文件使用过程中创建快照。由于测试加密前已对测试系统设置过系统还原，接下来测试下勒索软件是否会删除卷影服务。经测试，该勒索软件没有删除系统可用的卷影，之后使用相关工具可以根据已经设置的卷影时间来恢复部分文件（用户平时安全意识与习惯较好的，也能挽救一点点）。

![image.png](https://image.3001.net/images/20200414/1586831683_5e952143d6659.png!small)  

###  **已加密的文件格式**

从加密的文件来看，最后的0x200个字节是一致的，附加的0x200个字节数据为之前使用RSA公钥加密的产生的随机数（同时里面包含后续AES使用的加密密钥）与其余信息，除了最后0x200个字节为额外添加的之外，原文件大小对16取模后最后的余数不会加密，也就是图里的W-YCX63-B98R2与ressure.不会被加密（因为如果需要解密就需要注意这个特性）。

![image.png](https://image.3001.net/images/20200414/1586831692_5e95214ce8f96.png!small)  

###  **加密密钥**

密钥的产生与存放过程如下，采用健壮的随机数生成器来产生加密密钥。

![image.png](https://image.3001.net/images/20200414/1586831703_5e95215732ff9.png!small)  

后经分析，勒索软件采用了OpenSSL库的AES算法进行文件加密。  

![image.png](https://image.3001.net/images/20200414/1586831713_5e952161f16ab.png!small)  

轮密钥产生与最终加密过程如下  

![image.png](https://image.3001.net/images/20200414/1586831727_5e95216f886d6.png!small)

![image.png](https://image.3001.net/images/20200414/1586831732_5e95217419506.png!small)  

###  **加密密钥的产生**

现在主要需要分析的是加密的密钥如何生成的？

首先可以先判断下AES使用的加密模式，测试是否为ECB加密模式，可以设置加密的数据全为0，得到的加密结果如图，ECB加密模式进行文件加密，无IV值，相同块的加密结果会是一致的，地址288FF68作为需加密的明文，288FF58为加密后的密文。

![image.png](https://image.3001.net/images/20200414/1586831752_5e952188f3c2d.png!small)

  
再次本地测试如下，经处理后最终使用的密钥是：qobt<r#XC6Rm4H&AX&8ieRNbV{87w6RX，本地测试加密成功，与勒索加密结果一致。  

![image.png](https://image.3001.net/images/20200414/1586831766_5e9521966742d.png!small)![image.png](https://image.3001.net/images/20200414/1586831770_5e95219ad9714.png!small)  

最后的附加数据，属于全局数据，在对文件加密前就已生成。  

![image.png](https://image.3001.net/images/20200414/1586831779_5e9521a3c4f79.png!small)  

会进行加密的文件类型如下：7z、bak、sql、mdf、mdb、ora、dbf、rar、ldf、myd、myi、dmp、xls、xlsx、docx、pptx、eps、txt、ppt、csv、rtf、pdf、db、vdi、vmdk、vmx、pem、pfx、cer、psd。![image.png](https://image.3001.net/images/20200414/1586831796_5e9521b4858ab.png!small)  

会对每个文件进行加密时都开启一个线程，关键的地方是存放密钥使用了全局变量，导致在进程地址5F1338
处存在原始的加密密钥。经分析，采用了AES-256-ECB加密文件，而加密密钥前十六个字节为固定的qobt<r#XC6Rm4H&A，被硬编码在程序内部。  

![image.png](https://image.3001.net/images/20200414/1586831816_5e9521c8cb1ac.png!small)  

后十六个字节为之前STL里随机数生成器生成并处理得到的200个字节（通过分析，可以进一步缩小范围为ascii可见字符，一共是95个字符），取前十六个字节的数据，在95个字符中，随机取16个字符进行组合（一共的组合5.5187673699045114e+17），理论上可以暴力枚举，比如得到所有可能的结果后，可以对其分段再分开暴力枚举来验证密钥是否正确，比单纯一台PC跑所有结果会更快些。  

![image.png](https://image.3001.net/images/20200414/1586831825_5e9521d1a150a.png!small)  

由于之前经过分析发现加密的密钥所在的地址会固定在005F1338，可以尝试勒索进程还在运行过程中对其进程内存进行dump。比如可通过查看虚拟机的内存文件，发现该部分数据还存在，如下。  

![image.png](https://image.3001.net/images/20200414/1586831834_5e9521da4ff7f.png!small)![image.png](https://image.3001.net/images/20200414/1586831850_5e9521eacb217.png!small)  

分析勒索进程退出后是否会对内存里的密钥进行清空？

本地在进程退出后采用工具进行物理内存dump，然后实际查看并实验（存在一定的概率与巧合，笔者实验了很多次最后只有第一次是成功的（非常巧合），如下图，需要在进程结束的一瞬间去对其物理内存dump，针对已中勒索的机器，这种情况并不现实，用户发觉时早已过了段时间）。使用物理内存dump方法寻找密钥的概率非常低，经多次测试验证发现需要非常巧合的时间，比如进程刚退出时，立马对其物理内存dump，或者非常巧合，进程还未退出，这时就可以对其物理内存（进程内存）dump，就很有可能获取到加密密钥进而解密。

![image.png](https://image.3001.net/images/20200414/1586831862_5e9521f6d737e.png!small)![image.png](https://image.3001.net/images/20200414/1586831867_5e9521fb866d3.png!small)

![image.png](https://image.3001.net/images/20200414/1586831874_5e952202d3818.png!small)  

经上面的分析可知，勒索软件使用同一个密钥加密全部文件。这里给一个思路，实际的解密演示可在进程运行时提取加密密钥，并在结束后自行绕过黑客而解密文件，但是由于之前使用了健壮的随机数来确定加密密钥，但是由于限定了可见字符作为密钥范围，所以理论上比起以往无意义的碰撞枚举，使用密钥与已知样例数据进行解密枚举碰撞最终得到加密密钥是存在可能的，如下是进程中存在的加密密钥。  

![image.png](https://image.3001.net/images/20200414/1586831895_5e952217c8b59.png!small)  

解密演示脚本如下  

![image.png](https://image.3001.net/images/20200414/1586831966_5e95225e71cef.png!small)  

枚举碰撞获取密钥演示脚本如下  

![image.png](https://image.3001.net/images/20200414/1586832002_5e9522828383e.png!small)  

解密结果如下，该加密文件解密后与未加密前的内容完全一致。  

![image.png](https://image.3001.net/images/20200414/1586832018_5e95229288fec.png!small)  

  

##  **整体流程图**

![image.png](https://image.3001.net/images/20200414/1586832027_5e95229b88274.png!small)  

##  **威胁情报**

HASH

853358339279b590fb1c40c3dc0cdb72

C&C

61.186.243.2:8082

## **解决方案**

深信服下一代防火墙AF、终端检测响应平台EDR、安全态势感知平台SIP等安全产品均能有效检测防御此恶意软件，已经部署相关产品的用户可以进行安全扫描，检测清除此恶意软件，如图所示：

![image.png](https://image.3001.net/images/20200414/1586832042_5e9522aae1eb9.png!small)

