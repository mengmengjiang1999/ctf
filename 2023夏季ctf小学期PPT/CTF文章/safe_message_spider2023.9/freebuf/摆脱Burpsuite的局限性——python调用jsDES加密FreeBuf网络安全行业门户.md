  
  

原创： 3s_NwGeek  合天智汇

  
  

**目录**

 **0x00 burpsuite的局限性 2**

 **0x02 理解js中的“DES加密” 4**

 **0x03 python DES加密模块——pydes 5**

 **0x04 设计DES加密api 5**

 **0x05 python 调用js——exeacjs 9**

 **0x06 后话 9**

0x00 burpsuite的局限性

今天的渗透工作中黑盒测试遇到一个DES加密的登陆方式，遇到了很多坑，最终是通过python调用js进行des加密入手了这个站。

  
![图片.png](https://image.3001.net/images/20181212/1544604048_5c10c990c7d59.png!small)  

这次的情况是这样的，当我测试登陆的时候，发现发送登录请求时，验证码时可以复用的，原因是登陆失败时没有刷新session的值，导致图形验证码可以复用。
**测试验证码可复用的方法**
就是burpsuite抓取登陆请求包发送到repeater里面不断gogogogo，如果提示错误是验证码错误就说明漏洞不存在，但提示账号或密码错误就说明验证码可以复用。

  
![图片.png](https://image.3001.net/images/20181212/1544604054_5c10c996e6548.png!small)  

美滋滋可以暴力破解，但是看到post的数据是加密的，为什么我知道是DES加密。原因是仔细观察他的html页面源代码。发现这样一段javascript代码。

functionencryptByDES(message, key) {

var keyHex = CryptoJS.enc.Utf8.parse(key);

var encrypted = CryptoJS.DES.encrypt(message, keyHex, {

mode: CryptoJS.mode.ECB,

padding: CryptoJS.pad.Pkcs7

});

return encrypted.toString();

}

并且发现开发这把加密密钥也写进了html里面，看到发送登陆请求时调用这个des加密函数 **encryptByDES** ，

![图片.png](https://image.3001.net/images/20181212/1544604067_5c10c9a37b097.png!small)  

页面的js总是处处有惊喜。下面就进入正题说说我的 **pythondes** **加密爬坑记** 。

首先第一反应我是想到使用burpsuite进行paylaod处理暴力破解。

以前遇到的一些md5加密，sha1都可以在这里处理payload，然后简单的就可以进行加密暴力破解了。

![图片.png](https://image.3001.net/images/20181212/1544604076_5c10c9ac95f40.png!small)  

但是在这里找不到DES、RSA、AES等加密方式，这就是burpsuite的局限性。我们再来看看有什么方法可以进行此加密密码。

0x02 理解js中的“DES加密”

  
![图片.png](https://image.3001.net/images/20181212/1544604091_5c10c9bbd91f4.png!small)  

我们理解了他原本登陆的函数，我们可以在浏览器F12里的控制台，就直接可以调用他的加密函数。登陆加密的内容就是这个{"username":"admin","password":"12345678"}

encryptByDES('{"username":"admin","password":"12345678"}','232cb85*************cd354');

  
![图片.png](https://image.3001.net/images/20181212/1544604098_5c10c9c295eff.png!small)  

发现跟登陆请求包的post参数是一样的。但暴力破解总不可能这样一次次输入的。

0x03 pythonDES加密模块——pydes

然后再想想了，看python有没有DES的加密模块的，有的。Pydes模块，这里有两个坑点。

这是pydes模块官方的使用模板

importbase64

frompyDes import *

Des_Key= "12345678" #Key

Des_IV= "" #自定IV向量

defDesEncrypt(str):

k= des(Des_Key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)

EncryptStr= k.encrypt(str)

returnbase64.b64encode(EncryptStr) #转base64编码返回

第一个坑点，我发现这个模块只有des的ECB和CBC模式加密，并且填充方式只有pkcs5padding，和nomalpadding两种。我需要的是pkcs7padding！！！！

第二个坑点，正常des加密key固定是8位的，3des加密是16或者24位的。但是，页面源代码里给我的是64位！！！什么肥事！！！！无奈之下另外一个想法，去在线加密看看。

0x04 设计DES加密api

到了在线加密，找了三个网站，其他两个网站都报的是key位数错误，真的是要8位才行，但是唯独这个网站可以。之前再页面源代码中可以看到js代码DES加密方式是ECB模式的，并且是以pkcs7_padding的填充方式，加密过后是跟原来登陆请求包的加密数据是一样的。

  
![图片.png](https://image.3001.net/images/20181212/1544604116_5c10c9d4a1d3d.png!small)  

并且看到他的查询数据包，是post需要加密的内容并返回加密过后的密码的，所以打算使用python写个加密的api的http请求?然后提取密码再进行登陆的暴力破解。

  
![图片.png](https://image.3001.net/images/20181212/1544604124_5c10c9dc89e15.png!small)  

的确是可以这样加密暴力破解的。但是当我使用burpsuite快速的重放了这个数据包，就发现这方法不可行。

  
![图片.png](https://image.3001.net/images/20181212/1544604131_5c10c9e3d9442.png!small)  

  
![图片.png](https://image.3001.net/images/20181212/1544604137_5c10c9e96dfee.png!small)  

除非5秒请求一次。我在不知道账号不知道密码的情况下，还猜测不了用户存不存在的情况下，这种情况是不可取的。（如果存在的用户返回密码错误。用户不存在的时候返回账号不存在，可以根据登陆的返回结果来猜测用户存不存在）。

Api思路2

我们退一步回到该登陆页面再看看，当我们访问登陆页面的时候，一共额外加载了这几个js文件。

![图片.png](https://image.3001.net/images/20181212/1544604144_5c10c9f02d8fe.png!small)  

进去看了下真正用于des加密的三个js是如下图

![图片.png](https://image.3001.net/images/20181212/1544604150_5c10c9f63d219.png!small)  

我们可以点击它然后查看响应可以看到js的代码，都然后保存到本地，然后可以把他们写成自己的api。

  
![图片.png](https://image.3001.net/images/20181212/1544604156_5c10c9fc021d4.png!small)  

这是把他们加密的js保存下来再自己写的html页面（js顺序要正确）

<script src="core.js"></script>

<script src="tripledes"></script>

<script src="md5.js"></script>

<script src="mode-ecb.js"></script>

<script type="text/javascript">

function encryptByDES(message, key) {

var keyHex = CryptoJS.enc.Utf8.parse(key);

var encrypted = CryptoJS.DES.encrypt(message, keyHex, {

mode: CryptoJS.mode.ECB,

padding: CryptoJS.pad.Pkcs7

});

return encrypted.toString();

}

</script>

![图片.png](https://image.3001.net/images/20181212/1544604164_5c10ca043a7bc.png!small)  

于是可以写到自己网站的一个页面添加输入和输出的标签，我们直接可以输入输出加密结果了，但这还不是最优的解法，这样的话，还是要请求一次自己的网站再发一次登陆的请求。效率比直接再python加密再暴力破解低了一半！

0x05 python调用js——execjs

最后，我使用了一个python直接可以执行js代码的模块，相信除了登陆加密的用途外，其他地方都非常有用。

这个模块叫execjs，然后把三个加密的js按顺序叠加写到一个文件里就可以了。

首先加密的函数时这样的，首先读取加密的js。

 **def** get_js():#这个是获取js的函数  
f= open( **'C:\Users** **\\\** **3s_NwGeek\Desktop** **\\\** **des.js'** ,
**'r'** )  
line = f.readline()  
htmlstr = **''  
****while** line:  
htmlstr = htmlstr+line  
line = f.readline()  
**return** htmlstr  
  

这个是加密的函数。先获取js然后解析js代码再调用js的函数并传参就可以返回加密的密码了。  
 **def** DesEncrypt(str,key):#这个是des加密的函数  
  
jsstr= get_js()#获取js  
ctx= execjs.compile(jsstr)#解析js代码  
password=ctx.call( **'encryptByDES'**
,str,key)#调用encryptByDES函数，并传参原文str和加密key  
password=(password.encode( **"unicode_escape"** ).decode( **"string_escape"**
)).decode( **'unicode-escape'** ).encode( **'utf-8'** )#解码，解出来是unicode的  
**return** password

使用原来的原文进行加密，返回的结果是跟原来的请求包一样的

{"username":"admin","password":"12345678"}

iKUJ1KTtfI4NqIHAf7QQha71W4vil4uLWR1YQREFkJLsx1W/aKLcnt9Ni7PalkpP

0x06 后话

 **tips** **：**
最后直接使用协程进行暴力破解，其实事先，我把渗透调研表的联系人和负责人，还有整个部门的姓名信息，加了进去制作成一个用户字典。比如说，姓名叫张三丰，那么就会有，zhangsanfeng，zhang_sanfeng，zhang_sf,zsf。然后制作了16个用户再加常用的admin和root进行大字典的暴力破解。

排坑5小时，暴破5分钟。

最终激动的颤抖叫出来“yes！！！！！”了

![图片.png](https://image.3001.net/images/20181212/1544604177_5c10ca113f412.png!small)  

其实这个站每个月都会多家厂家做渗透，但也许看到密码加密了就pass这个方式了，但是当你肯比别人付出更多的耐心，就能比别人看到更多的风景，挖到更多的漏洞。

特别声明本文文章仅用于普及网络安全知识，提高小伙伴的安全意识的同时介绍常见漏洞的特征等，若读者因此作出危害网络安全的行为后果自负，与合天智汇以及原作者无关，
**特此声明** ！

