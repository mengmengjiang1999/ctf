## 一、背景

**最近一段时间国外安全研究人员在相关安全社交网站上公布了多个Emotet银行木马最新的变种样本，深信服EDR安全团队对此事进行了相关跟进，获取到了相应的样本，并对其中一个最新的变种样本进行了详细分析。**

Emotet银行木马首次发现是在2014年6月份，此银行木马主要通过垃圾邮件的方式进行传播感染目标用户，是一款比较著名且复杂的银行木马。

## 二、样本运行流程

![图片.png](https://image.3001.net/images/20180809/1533799771_5b6bed5bba111.png!small)

## 三、样本分析

邮件附件DOC样本(重命名为Emotet.doc)，如下所示：

![图片.png](https://image.3001.net/images/20180809/1533799791_5b6bed6f3d93e.png!small)

打开文档之后，如下：

![图片.png](https://image.3001.net/images/20180809/1533799800_5b6bed7842d57.png!small)

使用VBA编辑器，查看里面包含宏代码，如下：

![图片.png](https://image.3001.net/images/20180809/1533799807_5b6bed7f20628.png!small)![图片.png](https://image.3001.net/images/20180809/1533799813_5b6bed85f3931.png!small)

提取里面的VBA，如下：

![图片.png](https://image.3001.net/images/20180809/1533799823_5b6bed8f9d92b.png!small)

里面包含自动可执行的恶意宏代码，相应的宏代码如下：

![图片.png](https://image.3001.net/images/20180809/1533799831_5b6bed975d55c.png!small)

宏代码的结构表，如下：

![图片.png](https://image.3001.net/images/20180809/1533799839_5b6bed9f57b86.png!small)

动态调试，解密出相应的宏代码，如下：

![图片.png](https://image.3001.net/images/20180809/1533799854_5b6bedae7bea9.png!small)

是一段混淆过的cmd命令脚本,此CMD脚本运行之后会调用powershell脚本，相应的powershell脚本，如下：

![图片.png](https://image.3001.net/images/20180809/1533799863_5b6bedb70b09f.png!small)

重新整理之后，如下：

![图片.png](https://image.3001.net/images/20180809/1533799872_5b6bedc0e74c1.png!small)

此powershell脚本会遍历相应的恶意服务器网站，然后从网站下载相应的恶意程序，并重命名为727.exe，运行DOC之后，如下：

![图片.png](https://image.3001.net/images/20180809/1533799879_5b6bedc7eb83a.png!small)

## 727.exe分析

1.核心代码是经过加密的，如下所示：

![图片.png](https://image.3001.net/images/20180809/1533799889_5b6bedd151314.png!small)

2.通过动态调试分析，如下：

![图片.png](https://image.3001.net/images/20180809/1533799896_5b6bedd8485c4.png!small)

3.获取操作系统的位数，名称及版本信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533799904_5b6bede09f4d1.png!small)

4.在内存进行PE文件解密操作，然后执行到内存中PE文件入口点，如下：

![图片.png](https://image.3001.net/images/20180809/1533799912_5b6bede8683c2.png!small)

5.创建互斥变量PEMA94，如下：

![图片.png](https://image.3001.net/images/20180809/1533799919_5b6bedef9bb83.png!small)

6.通过GetModuleFileName获取文件路径，如下：

![图片.png](https://image.3001.net/images/20180809/1533799928_5b6bedf810b45.png!small)

7.调用CreateProcess启动程序，创建子进程，如下：

![图片.png](https://image.3001.net/images/20180809/1533799935_5b6bedff20b31.png!small)

8.创建完子进程之后，通过ExitProcess退出父进程，如下：

![图片.png](https://image.3001.net/images/20180809/1533799942_5b6bee06bbb4d.png!small)

运行之后相应的进程信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533799950_5b6bee0e81674.png!small)

对创建的子进程相关分析

1.通过GetWindowsDirectory获取Windows目录下，如下：

![图片.png](https://image.3001.net/images/20180809/1533799958_5b6bee16543a7.png!small)

2.获取磁盘信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533799969_5b6bee21d8061.png!small)

3.创建互斥变量Global\M1A9E9938，如下：

![图片.png](https://image.3001.net/images/20180809/1533799978_5b6bee2a06a95.png!small)

4.创建窗口，如下：

![图片.png](https://image.3001.net/images/20180809/1533799986_5b6bee3257221.png!small)

捕获窗口消息，执行消息循环操作，如下：

![图片.png](https://image.3001.net/images/20180809/1533799993_5b6bee394d6c9.png!small)

5.设置相应的注册表项，如下：

![图片.png](https://image.3001.net/images/20180809/1533800000_5b6bee4047554.png!small)

设置的注册表项，如下：

![图片.png](https://image.3001.net/images/20180809/1533800008_5b6bee48bc55f.png!small)

6.通过GetComputerNameW获取计算机名，拼接成随机字符串，如下：

![图片.png](https://image.3001.net/images/20180809/1533800018_5b6bee525ad12.png!small)

7.在临时目录创建44E0.tmp程序，如下：

![图片.png](https://image.3001.net/images/20180809/1533800027_5b6bee5b5ef26.png!small)

8.在系统目录创建tvoutduplex程序，如下：

![图片.png](https://image.3001.net/images/20180809/1533800036_5b6bee641d14d.png!small)

9.创建tvoutduplex服务，如下：

![图片.png](https://image.3001.net/images/20180809/1533800043_5b6bee6bbbb44.png!small)

创建的相应的服务，如下：

![图片.png](https://image.3001.net/images/20180809/1533800050_5b6bee7227b11.png!small)

10.枚举相应的服务状态，如下：

![图片.png](https://image.3001.net/images/20180809/1533800058_5b6bee7a03499.png!small)

11.然后启动服务进程，如下：

![图片.png](https://image.3001.net/images/20180809/1533800065_5b6bee8181d83.png!small)

12.销毁创建的窗口，如下：

![图片.png](https://image.3001.net/images/20180809/1533800072_5b6bee8830cd3.png!small)

13.退出子进程，如下所示：

![图片.png](https://image.3001.net/images/20180809/1533800081_5b6bee911e665.png!small)

运行之后相应的进程信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533800089_5b6bee99be52b.png!small)

## tvoutduplex样本分析

1.获取计算机操作系统版本信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533800097_5b6beea151d66.png!small)

2.遍历主机中的进程，获取进程信息，如下：

![图片.png](https://image.3001.net/images/20180809/1533800104_5b6beea86ae9c.png!small)

获取到的主机进程列表，如下：

![图片.png](https://image.3001.net/images/20180809/1533800110_5b6beeaebb1e1.png!small)

3.然后将之前获取的主机用户名，操作系统版本以及进程列表信息拼接成字符串，通过算法进行加密，如下：

![图片.png](https://image.3001.net/images/20180809/1533800118_5b6beeb6d8cea.png!small)

4.获取远程服务器地址，如下：

![图片.png](https://image.3001.net/images/20180809/1533800125_5b6beebde5a7d.png!small)

5.通过GetTickCount获取随机数字，如下：

![图片.png](https://image.3001.net/images/20180809/1533800132_5b6beec45984b.png!small)

然后拼接之成加密的数据，如下：

![图片.png](https://image.3001.net/images/20180809/1533800140_5b6beecc42a92.png!small)

最后通过Cookie发送到远程恶意服务器，下载相应的恶意模块，如下：

![图片.png](https://image.3001.net/images/20180809/1533800147_5b6beed33d1de.png!small)

6.恶意服务器地址，会随机改变，如下：

![图片.png](https://image.3001.net/images/20180809/1533800154_5b6beeda733d5.png!small)

得到的相关的恶意服务器地址，见IOC表

7.读取相应的恶意服务器网站数据，如下：

![图片.png](https://image.3001.net/images/20180809/1533800162_5b6beee2ea7b8.png!small)

读取到的数据，如下：

![图片.png](https://image.3001.net/images/20180809/1533800170_5b6beeeae62ce.png!small)

## 网络流量分析

1.下载Emotet母体样本，流量如下：

![图片.png](https://image.3001.net/images/20180809/1533800178_5b6beef26d678.png!small)

下载相应的Emotet母体样本，如下：

![图片.png](https://image.3001.net/images/20180809/1533800188_5b6beefca1653.png!small)

2.上传主机的相关信息，流量如下：

![图片.png](https://image.3001.net/images/20180809/1533800201_5b6bef09ae954.png!small)

3.返回的相应的数据包，如下：

![图片.png](https://image.3001.net/images/20180809/1533800209_5b6bef119d36f.png!small)

## 四、解决方案

深信服EDR已经能有效检测御防此类银行木马家族及其变种，同时深信服EDR安全团队提醒广大用户：

1.不要点击来源不明的邮件附件，不从不明网站下载软件

2.及时给主机打补丁，修复相应的高危漏洞

3.对重要的数据文件定期进行非本地备份

4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等

5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码

6.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能

## 五、相关IOC

### MD5

18080C897FEE73EFED43FD054CD8941F

509048748DA8071701D37B2E85698C09

99E71C359A0278A11FD3702D51157997

### IP

50.23.215.155

206.198.226.9

207.150.220.204

78.100.162.222

63.230.124.249

186.71.61.91

5.32.119.58

80.69.56.6

149.62.173.247

103.59.201.76

108.170.54.171

49.62.173.247

3.230.124.249

80.69.56.5

208.97.32.81

173.197.222.214

190.143.132.114

186.71.61.91

190.131.167.194

208.104.22.125

190.131.6.100

204.184.25.164

98.190.202.177

### DNS

vdtogt.nl

viciousenterprises.com

unclebudspice.com

thesilveramericaneagle.com

valiunas.com

### URL

<http://vdtogt.nl/amyQ>

<http://viciousenterprises.com/qXUuXq>

<http://unclebudspice.com/80d>

<http://thesilveramericaneagle.com/tb>

<http://valiunas.com/G8CooI>

<http://63.230.124.249:443/>

<http://82.28.208.186/>

<http://78.100.163.222/>

<http://24.224.45.166:8080/>

<http://149.62.173.247:8080/>

<http://108.170.54.171:8080>

<http://208.97.32.81:8080/>

<http://208.104.22.125:990/>

<http://80.69.56.5:50000/>

<http://173.197.222.214:443/>

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

