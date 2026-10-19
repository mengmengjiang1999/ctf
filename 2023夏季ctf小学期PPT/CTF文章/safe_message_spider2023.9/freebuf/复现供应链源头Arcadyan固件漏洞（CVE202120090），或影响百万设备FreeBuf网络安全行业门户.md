## 0x00前言

Tenable在2021年8月3日公布了编号为CVE-2021-20090的漏洞细节，攻击者可以利用此漏洞接管受影响设备的控制权。CVE-2021-20090为认证绕过漏洞，最初被发现存在于Buffalo路由器中，但很快被发现实际存在于中国台湾厂商Arcadyan生产的某固件中，导致使用该固件的设备均受到该漏洞的影响。影响范围如下表所示：

厂商| 设备| 版本  
---|---|---  
  
ADB

|

ADSL wireless IAD router

|

1.26S-R-3P  
  
Arcadyan

|

ARV7519

|

00.96.00.96.617ES  
  
Arcadyan

|

VRV9517

|

6.00.17 build04  
  
Arcadyan

|

VGV7519

|

3.01.116  
  
Arcadyan

|

VRV9518

|

1.01.00 build44  
  
ASMAX

|

BBR-4MG / SMC7908 ADSL

|

0.08  
  
ASUS

|

DSL-AC88U (Arc VRV9517)

|

1.10.05 build502  
  
ASUS

|

DSL-AC87VG (Arc VRV9510)

|

1.05.18 build305  
  
ASUS

|

DSL-AC3100

|

1.10.05 build503  
  
ASUS

|

DSL-AC68VG

|

5.00.08 build272  
  
  

Beeline

|

  

Smart Box Flash

|

  

1.00.13_beta4  
  
British Telecom

|

WE410443-SA

|

1.02.12 build02  
  
Buffalo

|

WSR-2533DHPL2

|

1.02  
  
Buffalo

|

WSR-2533DHP3

|

1.24  
  
Buffalo

|

BBR-4HG

|  
  
  
Buffalo

|

BBR-4MG

|

2.08 Release 0002  
  
Buffalo

|

WSR-3200AX4S

|

1.1  
  
Buffalo

|

WSR-1166DHP2

|

1.15  
  
Buffalo

|

WXR-5700AX7S

|

1.11  
  
Deutsche Telekom

|

Speedport Smart 3

|

010137.4.8.001.0  
  
HughesNet

|

HT2000W

|

0.10.10  
  
KPN

|

ExperiaBox V10A (Arcadyan VRV9517)

|

5.00.48 build453  
  
KPN

|

VGV7519

|

3.01.116  
  
O2

|

HomeBox 6441

|

1.01.36  
  
Orange

|

LiveBox Fibra (PRV3399)

|

00.96.00.96.617ES  
  
Skinny

|

Smart Modem (Arcadyan VRV9517)

|

6.00.16 build01  
  
SparkNZ

|

Smart Modem (Arcadyan VRV9517)

|

6.00.17 build04  
  
Telecom (Argentina)

|

Arcadyan VRV9518VAC23-A-OS-AM

|

1.01.00 build44  
  
TelMex

|

PRV33AC

|

1.31.005.0012  
  
TelMex

|

VRV7006

|

  
  
  
Telstra

|

Smart Modem Gen 2 (LH1000)

|

0.13.01r  
  
Telus

|

WiFi Hub (PRV65B444A-S-TS)

|

v3.00.20  
  
Telus

|

NH20A

|

1.00.10debug build06  
  
Verizon

|

Fios G3100

|

1.5.0.10  
  
Vodafone

|

EasyBox 904

|

4.16  
  
Vodafone

|

EasyBox 903

|

30.05.714  
  
Vodafone

|

EasyBox 802

|

20.02.226  
  
因手头有一台ASUS DSL-AC87VG路由器，精准命中CVE-2021-20090的影响列表，遂尝试对漏洞进行了复现。

![](https://image.3001.net/images/20210831/1630395711_612ddd3f1f29fd5d263a8.jpg!small)

此外，我们还挖掘出该设备多个登录状态下的命令注入漏洞，结合CVE-2021-20090，最终实现了未授权RCE。

## 0x01准备

从ASUS官网搜索该设备，发现其固件在2018年10月后再未更新。最新版本1.05.18_build305存在CVE-2021-20090漏洞。

![](https://image.3001.net/images/20210831/1630395724_612ddd4ca29b36ae77b46.png!small)

下载该版本固件，使用`binwalk -Me`进行解包，但发现只解包出来一个.jffs2和一个.ubi的文件，是两种常见格式的文件系统。

![](https://image.3001.net/images/20210831/1630395738_612ddd5a2daec4c904b30.png!small)

从GitHub上下载相应的解包工具jefferson和ubi_reader，再通过binwalk进行解包，最终找到漏洞程序httpd。

    
    
    Install jefferson
    sudo pip install cstruct
    git clone https://github.com/sviehb/jefferson
    cd jefferson && sudo python setup.py install
    
    
    Install ubi_reader
    sudo apt-get install liblzo2-dev python-lzo
    git clone https://github.com/jrspruitt/ubi_reader
    cd ubi_reader && sudo python setup.py install

![](https://image.3001.net/images/20210831/1630395750_612ddd662312398557043.png!small)

## 0x02认证绕过漏洞分析

###  **Url Path特征绕过**

根据Juniper威胁实验室发现的在野漏洞利用细节，发现攻击者在url中通过..%2f来遍历访问/images上层路径中的文件，疑似路径遍历漏洞。

![](https://image.3001.net/images/20210831/1630395762_612ddd72ae1093fddb33c.png!small)

使用IDA加载httpd程序，字符串窗口搜索/images，并查找其交叉引用，发现存在一个函数sub_EA44中使用了该字符串，分析该函数的功能，大致是通过遍历数组，判断数组中是否存在某个元素是传入参数的子串（此处strncasecmp函数是根据数据元素的长度来进行比较的），存在则返回1，否则返回0，猜测传入的参数大概率是请求路径，而字符串/images/恰恰是数组的第一个元素，分析数组中元素的字面意思，推断都是在无需登录情况下就可以访问的路径或文件（在未登录的情况下应该也能访问一些图片、htm等文件）。

![](https://image.3001.net/images/20210831/1630395773_612ddd7de4e0f34a73b04.png!small)

![](https://image.3001.net/images/20210831/1630395785_612ddd89ae69c6b42c0f2.png!small)

继续查看该函数的交叉引用，发现如下逻辑关系，当该函数返回1时，a1+30376地址处的内容被修改为1，观察伪代码54行，发现该地址处内容与另一个函数sub_1E2F0的返回值存在‘或’的判断，如果该地址处内容为1，那么函数sub_1E2F0的返回值无论为啥，结果都为真。

![](https://image.3001.net/images/20210831/1630395796_612ddd9402351ab410005.png!small)

查看函数sub_1E2F0，在该函数中发现了对SID值的校验。并且在对路由器登录抓包过程中发现，当登录成功后，请求其他文件时，会携带一个cookie值，而cookie中就存在SID这个变量。

![](https://image.3001.net/images/20210831/1630395806_612ddd9ed962bf5488c8a.png!small)

![](https://image.3001.net/images/20210831/1630395816_612ddda8a94ad02d5b4bc.png!small)

所以只需要保证sub_EA44返回值==1即可绕过cookie SID的校验。而满足sub_EA44() ==
1只需要路径包含指定路径即可，如上图中的/images/、/lang/、/js/、/css/等。

但是，上述指定路径限制了我们访问敏感API或敏感页面。此时，结合路径穿越漏洞，可解除指定路径的限制，实现未登录状态下对任意api/url的合法访问。

我们通过分析在野漏洞利用点和设备web程序，发现由于web程序认证校验逻辑存在漏洞，当请求的路径中存在某些特定的字符串时，可直接绕过认证，成功访问原本需认证后才能访问的文件。

![](https://image.3001.net/images/20210831/1630395831_612dddb777cf69c93e2c9.png!small)

上图中我们已能成功访问router.htm文件，但由于该htm文件中会加载多个js、png等资源文件，而此时的Referer字段是[http://192.168.51.1/lang/..%2frouter.htm](http://192.168.51.1/lang/../router.htm)，所以请求时路径存在错误导致404，只需将lang/..%2f替换成空即可成功访问。

###  **Csrf_token校验绕过**

很好，现在我们能够在未登录的情况访问该设备web目录下的所有文件（测试发现无法穿越到www/的上层目录）。但这仅仅只是能够访问而已，我们想要的是调用这些页面上的功能来对路由器进行配置。在www/目录下我们发现了一个名为Main_Password.htm的文件（看到password就想瞅瞅），登录路由器访问该页面，发现该页面居然是路由器重置密码的页面。

![](https://image.3001.net/images/20210831/1630395844_612dddc47babab26cdcf4.png!small)

直接通过burp抓包，看看正常情况下重置密码时的请求信息。发现请求body中除了加密后的用户名和密码外还存在一个httoken参数，从上面的分析我们知道header中的cookie认证我们可以绕过，那么想要实现重置密码的功能，我们还得知道这个httoken是怎么得到的。

![](https://image.3001.net/images/20210831/1630395864_612dddd89bef07e2ef068.png!small)

分析请求参数的构造，发现httoken参数是通过addToken这个函数来获取的，该函数是此htm页面加载的global.js文件中的一个函数，该函数较为简单，通过ArcBase._t()来获取token值。

![](https://image.3001.net/images/20210831/1630395877_612ddde517721e8078ad7.png!small)

但查看ArcBase这个对象的定义，并未直接找到_t这个方法，好在通过全局匹配查找，发现了一行有趣的代码，这行代码在运行时会动态生成一个函数，而函数体就是teksasli这个变量。

![](https://image.3001.net/images/20210831/1630395891_612dddf3747d444ce9d3b.png!small)

继续查找teksasli的来源，发现teksasli这个变量是通过解密字符串enkripsi得到的。对该字符串进行解密，最终我们找到了生成token的函数。

![](https://image.3001.net/images/20210831/1630395906_612dde02a0d55d3bb9ef1.png!small)

分析该函数发现其先获取img标签的内容，然后从中找到字符串“data:”起始处，之后从此处向后78字符处开始提取后面的子串，最后对其进行解码（简易的Base64解码）得到token值。那么这个img标签存在哪儿呢，当我们访问htm文件时，发现在其底部存在一个img标签，按照上述方法提取其子串进行解码，发现能够解码成功，并且该token值与我们在该页面上请求所携带的token值一致。

![](https://image.3001.net/images/20210831/1630395917_612dde0d7ca6104de8b79.png!small)

![](https://image.3001.net/images/20210831/1630395927_612dde17ace66ca90bb97.png!small)

![](https://image.3001.net/images/20210831/1630395936_612dde20bb11aa4adb937.png!small)

![](https://image.3001.net/images/20210831/1630395945_612dde29e255f08beffcd.png!small)

说明这个token值是后台动态生成返回的，在IDA中我们也找到了其生成的地方。

![](https://image.3001.net/images/20210831/1630395958_612dde367b0bae5fb6a98.png!small)

###  **绕过手法总结**

至此，我们简单总结一下：

可通过在请求路径中携带特殊字符串达到路径遍历绕过认证的目的，可访问www/目录下或其子目录下的所有文件；![](https://image.3001.net/images/20210831/1630401992_612df5c8b053620795eed.png!small)

当我们在请求页面htm文件时，web后台会生成一个base64编码后的token值附加在页面的img标签中传回，前端解码拿到token值，并且在调用页面上的功能时，会将此token值附带在参数中传到web后台进行校验。

所以，通过该认证绕过漏洞我们能够做到无需登录即可调用web页面提供的任意接口，结合相关RCE漏洞，我们最终便可以实现未授权RCE。

## 0x03小结

该认证绕过漏洞原理还是比较简单的，但要调用页面上的功能接口，需要搞清楚httoken的由来，最后结合认证后的注入漏洞，达到未授权RCE效果。

 **参考资料**

  1. > <https://medium.com/tenable-techblog/bypassing-authentication-on-arcadyan-routers-with-cve-2021-20090-and-rooting-some-buffalo-ea1dd30980c2>

  2. > [https://www.freebuf.com/news/283787.html](news/283787.html)

