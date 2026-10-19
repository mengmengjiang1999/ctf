# 本文转载自看雪论坛【作者】rdsnow

不得不说，最近的 Python 蛮火的，我也稍稍了解了下，并试着用 Python 爬取网站上的数据

不过有些数据是要登陆后才能获取的，我们每年都要到某教师教育网学习一些公需科目，就拿这个网站试试，关键是对网站的分析

打开浏览器，输入网站网址[
http://www.jste.net.cn](https://bbs.ichunqiu.com/thread-36907-1-1.html?from=beef)[](http://www.jste.net.cn/)
，按F12调出浏览器的开发者工具，选中 Network ，并勾选 Preserve log，防止切换网页时信息丢失

![image.png](https://image.3001.net/images/20180402/15226536367045.png!small)

网页上输入账号，密码输入“123456”，验证码输入“abcde”，验证码不要输正确的，否则密码错5次，会被网站锁定账号30个小时，验证码倒是可以随便错

登陆后（当然登陆不上，会跳转到另一个登陆页面），在开发者工具中看到与服务器的数据交换

![image.png](https://image.3001.net/images/20180402/15226536524277.png!small)  

第一个是get验证码图片的，第二个就是向网站提交数据的，点一下第二个信息  

![image.png](https://image.3001.net/images/20180402/15226536672402.png!small)  

这是个 Post
请求，重点看红框中的提交数据，randomCode就是输入的验证码了，x,y应该是点击的按钮控件的位置了，有cookie后就没有提交这个数据了，可以忽视，returnURL、appId，encrypt每次都是一样的，也不用管他，重点是
reqId 和 req 这两个 key 的值了，reqId猜想是点击按钮时取到的时间戳，可以复制这个数据到验证下 Unix时间戳(Unix
timestamp)转换工具 单位选毫秒，确实是刚刚提交数据的时间，就剩下一个数据了，这个key的数值很长，下面来寻找这个数据是从哪里的来的

可以看到 login.jsp 下可以看到 encode.js、string.js、des.js 从名字上就能看出这几个是用来加密提交数据的，右键
login.jsp，选择 “Open in Sources panel”

![image.png](https://image.3001.net/images/20180402/15226537006674.png!small)  

![image.png](https://image.3001.net/images/20180402/15226537232555.png!small)  

可以跳转到 "源" 选项卡，看到 ’login.jsp‘ 的源码，如果格式混乱，比如所有代码在一行中，不便于观看，可以点击界面下方  

![image.png](https://image.3001.net/images/20180402/15226538607653.png!small)  

的中括号，开发者工具会自动给你重新格式化代码。

仔细分析 login.jsp 的代码，看到

function doOk(frm) { var el = frm.elements["loginName"]; var loginName =
el.value.replace(/ /g, ""); el.value = loginName; if (isEmpty(loginName)) {
alert("请输入登录名"); el.focus(); return false; } el = frm.elements["pwd"];
el.value = el.value.replace(/ /g, ""); var pwd=el.value; if
(isEmpty(el.value)) { alert("请输入登录密码"); el.focus(); return false; } var d =
new Date(); pwd = encode(loginName, pwd);//密码第一次加密，可以跟进
frm.elements["encrypt"].value = "1"; var validCode="";
el=frm.elements["randomCode"]; if(el){ el.value=el.value.replace(/ /g,""); if
(isEmpty(el.value)) { alert("请输入登录密码"); el.focus(); return false; }
validCode=el.value; } loginName=encodeURI(loginName);//避免中文问题 进行URL编码 var
reqId=(new Date()).getTime()+"";//获取时间戳给 reqId var
str=strEnc(loginName+"\n"+pwd,reqId,validCode);//关键加密代码，可以跟进分析
frm.elements["loginName"].disabled="true"; frm.elements["pwd"].value=pwd;
frm.elements["pwd"].disabled="true"; frm.elements["req"].value=str;
frm.elements["reqId"].value=reqId; return true; }  

找到这段代码，其中主要是对输入检查的部分，重点看这两处  

pwd = encode(loginName, pwd);  

此处对密码进行第一次加密  

loginName=encodeURI(loginName);//避免中文问题var reqId=(new Date()).getTime()+"";var
str=strEnc(loginName+"\n"+pwd,reqId,validCode);  

第一行：将用户名进行 URL 的格式编码

第二行，取时间戳赋值给 reqId

第三行传入用户名，加密后的密码和验证码进行验证，函数返回值赋给变量 str，正是提交数据的 req 的值

在两个加密函数入口设置断点，开发者工具设置断点的，只要在这个代码的行号上点击鼠标就行了，设好断点后，再次输入用户名密码和验证码，重新提交，程序被断下：

![image.png](https://image.3001.net/images/20180402/15226545079968.png!small)  

F11单步进入第一个断点，这里需要点击界面下面的中括号重新格式化下代码，单步跟进后看到：  

var _$_7151 = ["encode", "ABCDEFGHIJKLMNOP", "QRSTUVWXYZabcdef",
"ghijklmnopqrstuv", "wxyz0123456789+/", "=", "", "charCodeAt", "charAt",
"length", "join", "reverse", "split"];window[_$_7151[0]] = function(c, e) {
function a(p) { var q = _$_7151[1] + _$_7151[2] + _$_7151[3] + _$_7151[4] +
_$_7151[5]; p = encodeURI(p); var r = _$_7151[6]; var g, h, j = _$_7151[6];
var k, l, m, o = _$_7151[6]; var b = 0; do { g = p[_$_7151[7]](b++);//第一个字符 h
= p[_$_7151[7]](b++);//第二个字符 j = p[_$_7151[7]](b++);//第三个字符 k = g >> 2; //得到 k
l = ((g & 3) << 4) | (h >> 4);//得到 i m = ((h & 15) << 2) | (j >> 6);//得到 m o =
j & 63; //得到 o if (isNaN(h)) { //如果没有第二个字符 m = o = 64 //则取表中的第64个字符替换 } else {
if (isNaN(j)) { //如果没有第三个字符 o = 64 //则取表中的第64个字符替换 } } ;r = r +
q[_$_7151[8]](k) + q[_$_7151[8]](l) + q[_$_7151[8]](m) + q[_$_7151[8]](o); g =
h = j = _$_7151[6]; k = l = m = o = _$_7151[6] } while (b <
p[_$_7151[9]]);;return r } var d = c[_$_7151[9]]; var f =
a(e)[_$_7151[12]](_$_7151[6])[_$_7151[11]]()[_$_7151[10]](_$_7151[6]); for
(var b = 0; b < (d % 2 == 0 ? 1 : 2); b++) { f =
a(f)[_$_7151[12]](_$_7151[6])[_$_7151[11]]()[_$_7151[10]](_$_7151[6]) }
;return f}  

这个函数返回的 f 就是密码第一次加密后的结果了，这个代码是用什么工具变成这样的不太清楚，如果出现 _$_7151[n] 这样的字符可以查询代码最上面的列表

代换，大致过程不详说，跟一遍就知道了，就是循环从密码中取三个字符 g、h、j，然后将三个字符的ascii码左移或右移，或和其他结果加加减减，得到的结果
k、l、m、o 查询表格替换字符，如果密码长度不是 3 的整数倍，则查表结果用 “=” 替换，将循环得到的查表结果依次连接，并反序，得到一个密码加密后的密码

至少将密码进行两次这样的加密计算，如果用户名的长度是奇数，再进行一次加密，加密的过程只需要复制代码到 python 中，修改成 python
的格式就可以了。

步过了对密码的第一次加密后，继续步进上面设下的第二个断点

function strEnc(data,firstKey,secondKey,thirdKey){ var leng = data.length;//取
data 的长度 var encData = ""; var
firstKeyBt,secondKeyBt,thirdKeyBt,firstLength,secondLength,thirdLength;
if(firstKey != null && firstKey != ""){ firstKeyBt = getKeyBytes(firstKey);//取
firstkey 在每个字符之间插入一个字节的 0 firstLength = firstKeyBt.length;//取得插入 0 后的长度 }
if(secondKey != null && secondKey != ""){ secondKeyBt =
getKeyBytes(secondKey);//取 secondkey 在每个字符之间插入一个字节的 0 secondLength =
secondKeyBt.length;//取得插入 0 后的长度 } if(thirdKey != null && thirdKey != ""){
//登陆过程中，并没用到 thirdkey，即 thirdKey = None thirdKeyBt = getKeyBytes(thirdKey);//取
thirdkey 在每个字符之间插入一个字节的 0 thirdLength = thirdKeyBt.length;//取得插入 0 后的长度 }
if(leng > 0){ if(leng < 4){ 如果 data 的长度＜4，因为跳过，代码用省略号替换 //省去一些代码…… }else{ var
iterator = parseInt(leng/4);//data 的长度除 64，得到循环次数 var remainder = leng%4;
//data 的长度是否是 64 位的整数倍，保存余数 var i=0; for(i = 0;i < iterator;i++){ //开始循环 var
tempData = data.substring(i*4+0,i*4+4); //循环取 data 的64 位 var tempByte =
strToBt(tempData);//转换成 bits var encByte ; if(firstKey != null && firstKey
!="" && secondKey != null && secondKey != "" ){ var tempBt; var x,y; tempBt =
tempByte; for(x = 0;x < firstLength ;x ++){ tempBt =
enc(tempBt,firstKeyBt[x]);//循环从firstkey 中取得64 位做密钥，依次对 data 中的某一段加密 } for(y =
0;y < secondLength ;y ++){ tempBt =
enc(tempBt,secondKeyBt[y]);//循环从second中取得64 位做密钥，依次对 data 中的某一段加密 } encByte =
tempBt;//保存加密结果 } //………… if(remainder > 0){ //如果 data 有多余的长度，不足64 位 var
remainderData = data.substring(iterator*4+0,leng); var tempByte =
strToBt(remainderData);//将余下的分到4个16位的数组中 var encByte ; if(firstKey != null &&
firstKey !="" && secondKey != null && secondKey != "" && thirdKey != null ){
var tempBt; var x,y,z; tempBt = tempByte; for(x = 0;x < firstLength ;x ++){
tempBt = enc(tempBt,firstKeyBt[x]);循环从firstkey 中取得64 位做密钥，依次对 data 中的某一段加密 }
for(y = 0;y < secondLength ;y ++){ tempBt =
enc(tempBt,secondKeyBt[y]);循环从secondkey中取得64 位做密钥，依次对 data 中的某一段加密 } encByte =
tempBt;//保存加密结果 } encData += bt64ToHex(encByte);//将加密后的文本转为16进制文本 } } } return
encData;//返回加密结果}  

这是一段循环进行 DES 加密的代码，先将data, firstkey, secondkey进行字符间插入一个字节的0, 然后不是 64
位整数倍长度的从上面代码看，相当于在后面补上 0 了  
从data中取出一段64位数据，循环用 firstkey 和 second 中的 64 位做密钥，层层加密，得到的结果和 data 中其他 64
位加密的结果串联后就是 req 的值了  
因为 key 都是 64 位的，再加上本身 sources 中也看到了 DES.js 文件，所以 enc(tempBt,secondkeyBt)应该就是
DES 算法了。  
但是自己写代码模拟登陆确发现结果和自己跟的结果不同，从代码中看，DES 采用了 ECB 模式，不是 CBC 模式，PAD_mode
也没问题，都64位，不需要 DES 自己填充啊。没办法，只得硬着头皮继续跟进 DES 加密的代码

我们知道，DES 加密需要先对 key 进行 置换，得到 56 位密钥，标准的 DES 都有个置换表，正常的 DES 置换表是这样的

Permutation and translation tables for DES __pc1 = [56, 48, 40, 32, 24, 16, 8,
0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43,
35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 60, 52, 44,
36, 28, 20, 12, 4, 27, 19, 11, 3 ]  

即将 key 的第 56 位放到第 0 位，第 48 位放到第 1 位…………最后置换出 56 位的 key，再分成 2 个28 密钥，循环左移和右移，然后
对 IP 置换后的 data 加密，进行 Sbox 盒替换 和 Pbox 替换，再进行一次 IP-1 置换得到密文，解密算法一样。

但跟进 DES 加密函数没多久就发现问题了，找到密钥置换的函数

var keys = generateKeys(keyByte);  

并跟进：  

function generateKeys(keyByte){ var key = new Array(56); var keys = new
Array(); keys[ 0] = new Array(); keys[ 1] = new Array(); keys[ 2] = new
Array(); keys[ 3] = new Array(); keys[ 4] = new Array(); keys[ 5] = new
Array(); keys[ 6] = new Array(); keys[ 7] = new Array(); keys[ 8] = new
Array(); keys[ 9] = new Array(); keys[10] = new Array(); keys[11] = new
Array(); keys[12] = new Array(); keys[13] = new Array(); keys[14] = new
Array(); keys[15] = new Array(); var loop =
[1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1];//看到了循环移位的表，没看到置换表 for(i=0;i<7;i++){
for(j=0,k=7;j<8;j++,k--){ key[i*8+j]=keyByte[8*k+i];//用了这个循环生成 56 位  }
}//省略代码}  

这里修改了标准的置换表，用了一个嵌套循环生成 56 位密钥，即把

原来 key 的 56 位 --> 第 0 位，48 位 --> 第 1 位，40 位 --> 第 2 位，…………0 位--> 第 7 位

原来 key 的 57 位 --> 第 8 位，49 位 --> 第 9 位，41 位 --> 第 10 位，………… 1 位 -->第 15 位

…………

最后丢弃原 key 的第 63，55，47，39，31，23，15，7 位（位置号从 0 开始）

在 python 中不能直接使用标准的 DES库了，可以把标准库中的 pyDes.py 文件拷贝到工程同目录下，改名为 Des,py，并导入工程

from Des import *  

另外在 Des.py 中找到 key 的置换表，修改成  

__pc1 = [ 56, 48, 40, 32, 24, 16, 8, 0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50,
42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36, 28, 20,
12, 4, 61, 53, 45, 37, 29, 21, 13, 5, 62, 54, 46, 38, 30, 22, 14, 6 ]  

就可以正常使用 Des 了

最后附上 python 代码：

from Des import *from urllib.parse import quotefrom time import time,
sleepfrom PIL import Imageimport requestsimport sysfrom bs4 import
BeautifulSoups = requests.session()headers = { 'Cache-Control': 'max-age=0',
'Connection': 'keep-alive', 'Referer':
'<http://www.jste.net.cn/uids/login.jsp>', 'User-Agent': 'Mozilla/5.0 (Windows
NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \ Chrome/58.0.3029.110
Safari/537.36 SE 2.X MetaSr 1.0'}def custom_encode(data): #
懒得注释了，直接从js中拷贝出来，改成python的代码 tab =
'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' data_bytes
= list(data.encode()) while len(data_bytes) % 3 != 0: data_bytes.append(0) b =
0 length = len(data_bytes) r = '' while b < length: g = data_bytes[b] h =
data_bytes[b + 1] j = data_bytes[b + 2] k = g >> 2 m = ((g & 3) << 4) | (h >>
4) n = ((h & 15) << 2) | (j >> 6) o = j & 63 third_char = '=' if h == 0 else
tab[n] fourth_char = '=' if j == 0 else tab[o] r = r + tab[k] + tab[m] +
third_char + fourth_char b = b + 3 return r[::-1] # 反序输出def
encode_pwd(str_name, str_pwd): encoded_pwd = custom_encode(str_pwd)
encoded_pwd = custom_encode(encoded_pwd) # 先连续对密码加密两次 if len(str_name) % 2 ==
1: encoded_pwd = custom_encode(encoded_pwd) # 如果用户名长度是奇数，则再加密一次 return
encoded_pwddef strenc(data, firstkey, secondkey): bts_data =
extend_to_16bits(data) # 将data长度扩展成64位的倍数 bts_firstkey =
extend_to_16bits(firstkey) # 将 first_key 长度扩展成64位的倍数 bts_secondkey =
extend_to_16bits(secondkey) # 将 second_key 长度扩展成64位的倍数 i = 0 bts_result = []
while i < len(bts_data): bts_temp = bts_data[i:i + 8] # 将data分成每64位一段，分段加密 j,
k = 0, 0 while j < len(bts_firstkey): des_k = des(bts_firstkey[j: j + 8], ECB)
# 分别取出 first_key 的64位作为密钥 bts_temp = list(des_k.encrypt(bts_temp)) j += 8
while k < len(bts_secondkey): des_k = des(bts_secondkey[k:k + 8], ECB) # 分别取出
second_key 的64位作为密钥 bts_temp = list(des_k.encrypt(bts_temp)) k += 8
bts_result.extend(bts_temp) i += 8 str_result = '' for each in bts_result:
str_result += '%02X' % each # 分别加密data的各段，串联成字符串 return str_resultdef
extend_to_16bits(data): # 将字符串的每个字符前插入 0，变成16位，并在后面补0，使其长度是64位整数倍 bts =
data.encode() filled_bts = [] for each in bts: filled_bts.extend([0, each]) #
每个字符前插入 0 while len(filled_bts) % 8 != 0: # 长度扩展到8的倍数 filled_bts.append(0) #
不是8的倍数，后面添加0，便于DES加密时分组 return filled_btsdef get_rand_code(): random_code_url
= r'<http://www.jste.net.cn/uids/genImageCode?rnd=>' time_stamp =
str(int(time() * 1000)) random_code_url += time_stamp try: req =
s.get(random_code_url, headers=headers, stream=True) with
open('rand_code.jpg', 'wb') as f: for chunk in
req.iter_content(chunk_size=1024): f.write(chunk) except
requests.RequestException: print('网络链接错误，请稍后重试/(ㄒoㄒ)/~~') sys.exit() with
Image.open('rand_code.jpg')as img: img.show()def login_site(reqid, randomcode,
reqkey): post_data = { 'randomCode': randomcode, 'returnURL': None, 'appId':
'uids', 'site': None, 'encrypt': 1, 'reqId': reqid, 'req': reqkey } try: req =
s.post('<http://www.jste.net.cn/uids/login.jsp>', headers=headers,
data=post_data) print('Status Code：%s' % req.status_code) #
不知道为什么浏览器上登陆成功返回的是302，这里返回200 if 'Set-Cookie' in req.headers.keys(): #
还好，看到response中出现Set-Cookie，就登陆成功了 return True else: return False except
requests.RequestException: print('网络链接错误，请稍后重试/(ㄒoㄒ)/~~') return Falsedef
main(): print(''.center(100, '-')) uname = input('请输入你的用户名：') pwd =
input('请输入你的登陆密码：') get_rand_code() secondkey = input('请输入看到的验证码：') #
取得验证码，作为second_key，提交数据时作为 randomCode 的值 firstkey = str(int(time() * 1000)) #
取得提交时的时间戳，作为first_key，提交数据时候作为 reqId 的值 crypt_pwd = encode_pwd(uname, pwd) #
对输入的密码进行第一次加密 data = quote(uname) + '\n' \+ crypt_pwd #
用户名URI编码后和密码加密后的文本链接等待被DES加密 post_req = strenc(data, firstkey, secondkey) #
主要是DES计算，作为 req 的值提交数据 if login_site(reqid=firstkey, randomcode=secondkey,
reqkey=post_req) is True: print(''.center(100, '-'))
print('登陆成功，O(∩_∩)O哈哈~...') try: req =
s.get('<http://www.jste.net.cn/train/credit_hour/top.jsp>') # 打开一个网页测试一下 soup
= BeautifulSoup(req.text, 'html5lib') # 网页为多框架，测试下访问TOP框架中的文本
print(soup.select('.b')[0].text.replace('\n', '').replace(' ', '')) except
requests.RequestException: print('网络链接错误，请稍后重试/(ㄒoㄒ)/~~')if __name__ ==
'__main__': # 启动程序 main()  

测试效果：  

![image.png](https://image.3001.net/images/20180402/15226546215346.png!small)  

最后思考了下，很多网站的数据都是明码提交的，或者是简单的加密提交的，这个网站在加密上花了一些工夫

但是js脚本最大的问题就是别人可以看到源码，虽然网站登陆成功后立即删除了js文件，但是只要出现了就会被发现，我网上搜索了下隐藏源码的办法，但是水平才菜了，没学过
java ，也没看懂。

最后补充下：DES加密的数据 data 是用户名的" URL格式 + 换行 + 密码第一次加密得到的文本“

firstkey 是提交时得到的时间戳，secondkey 就是输入的验证码

