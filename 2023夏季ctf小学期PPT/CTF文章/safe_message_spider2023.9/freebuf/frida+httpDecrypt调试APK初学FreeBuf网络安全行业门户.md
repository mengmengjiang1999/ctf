最近琢磨frida Hook，好难，想走个捷径都不行，看了酒仙桥的文章《[酒仙桥第六部队
hook从未如此丝滑](https://mp.weixin.qq.com/s?__biz=MzAwMzYxNzc1OA==&mid=2247489862&idx=1&sn=f1b97b29010120a19f5ff55aff522360)》，其中提到了[httpDecrypt
](https://github.com/lyxhh/lxhToolHTTPDecrypt/)，[t00ls](https://www.t00ls.net/articles-51070.html#tls8)，大概是看文章走马观花了，绕了弯路，避免后续踩坑记录如下：

## 1.安装MUMU模拟器，默认监听端口7555，

    
    
    adb connect 127.0.0.1:7555
    
    
    检测是否连接
    adb devices

MUMU模拟器是x86架构，在frida网站上下载对应frida-server,通过命令

    
    
    adb push frida-server /data/local/tmp

传输到MUMU

    
    
    chmod -R 777 frida-server
    ./frida-server

注意:mumu模拟器自带木有wifi功能，下载 **getWifiSetting.apk**

(链接: https://pan.baidu.com/s/1oXA1I9D3ZqdyfY4R_0nLlA 提取码: jbzy )

安装后，在wan中设置本地网络代理即可：

![1611847788_6012d86c8a48462d81934.png!small](https://image.3001.net/images/20210128/1611847788_6012d86c8a48462d81934.png!small)

## 2.运行httpDecrypt：

需要在python3环境下，直接 python3 app.py即可

![1611847870_6012d8be291b5c8af9884.png!small?1611847860227](https://image.3001.net/images/20210128/1611847870_6012d8be291b5c8af9884.png!small?1611847860227)

访问url：（如果没有应用信息，建议多刷新几次，或者修改项目文件中的时间，具体可百度）

![1611847890_6012d8d273e909ddaefb6.png!small?1611847880592](https://image.3001.net/images/20210128/1611847890_6012d8d273e909ddaefb6.png!small?1611847880592)

## 3.开启httpdecrypt之旅

### （1）选中需要操作的apk，并复制包名：

![1611847974_6012d926d90be2432a392.png!small?1611847965247](https://image.3001.net/images/20210128/1611847974_6012d926d90be2432a392.png!small?1611847965247)

### （2）填入包名至Identifier:，点击confirm

![1611847991_6012d937b73db3f87a37d.png!small?1611847982048](https://image.3001.net/images/20210128/1611847991_6012d937b73db3f87a37d.png!small?1611847982048)

### （3）点击Hooks，在match中填入包名，并点击confirm

![1611848008_6012d9487f54412120975.png!small?1611847998944](https://image.3001.net/images/20210128/1611848008_6012d9487f54412120975.png!small?1611847998944)

此时已经hooks，查看cmd下的httpdecrypt，已经hook的所有方法：

![1611848051_6012d973c2ad313861677.png!small?1611848042651](https://image.3001.net/images/20210128/1611848051_6012d973c2ad313861677.png!small?1611848042651)

### （4）运行apk，进行功能（登录）操作：

![1611848068_6012d98419669b2848c11.png!small?1611848058437](https://image.3001.net/images/20210128/1611848068_6012d98419669b2848c11.png!small?1611848058437)

在stack中，可以看到相关数据：

![1611848090_6012d99aba3872937da60.png!small?1611848081287](https://image.3001.net/images/20210128/1611848090_6012d99aba3872937da60.png!small?1611848081287)

返回hook界面，能看到我们的输入数据，已经加密后的数据，可以看到进行了base64以及ase加密：

![1611848132_6012d9c4191066051b44a.png!small?1611848122446](https://image.3001.net/images/20210128/1611848132_6012d9c4191066051b44a.png!small?1611848122446)

![1611848110_6012d9ae0ce83362efde2.png!small?1611848100320](https://image.3001.net/images/20210128/1611848110_6012d9ae0ce83362efde2.png!small?1611848100320)

![1611848149_6012d9d55d03df5517c7e.png!small?1611848140148](https://image.3001.net/images/20210128/1611848149_6012d9d55d03df5517c7e.png!small?1611848140148)

### （5）在finds功能中，输入刚刚找到的方法名：com.*.***.util.AESUtils：

![1611848172_6012d9ec75f37c1b76085.png!small?1611848162797](https://image.3001.net/images/20210128/1611848172_6012d9ec75f37c1b76085.png!small?1611848162797)

可以看到加密函数参数中，对象类型的参数具体类型为static，选择到encrypt，然后右键发送到toBurp功能：

![1611848207_6012da0fbe1838fd4b83f.png!small?1611848199918](https://image.3001.net/images/20210128/1611848207_6012da0fbe1838fd4b83f.png!small?1611848199918)

 **<
特别注意：这里的toburp功能并不是在burp中查看，而是当前web页面中的“toBurp”，之前一直以为是直接发到了burp中，知道详细看了酒仙桥的文章才发现理解错了>**

继续在toBurp功能处 点击confirm-再点击add

![1611848250_6012da3a89008a50cc236.png!small?1611848240798](https://image.3001.net/images/20210128/1611848250_6012da3a89008a50cc236.png!small?1611848240798)

  

![1611848266_6012da4a798d97663f252.png!small?1611848256955](https://image.3001.net/images/20210128/1611848266_6012da4a798d97663f252.png!small?1611848256955)

此处对象参数类型为static，所以我们选择Generate export static script。  
如果参数为动态，那我们选择Generate export instance script。  
现在可以看到，在custom中会生成代码。

![1611848291_6012da63dc76175dfce76.png!small?1611848282664](https://image.3001.net/images/20210128/1611848291_6012da63dc76175dfce76.png!small?1611848282664)

代码中，arg0是传过来的加密字符串。

点击左上角loadScript 将脚本发送到burp：

![1611848338_6012da92140175d381218.png!small?1611848328365](https://image.3001.net/images/20210128/1611848338_6012da92140175d381218.png!small?1611848328365)

现在切换至我们常用的burp，右键选择send to httpDecrypr：

![1611848355_6012daa34f57b8f120ed3.png!small?1611848345660](https://image.3001.net/images/20210128/1611848355_6012daa34f57b8f120ed3.png!small?1611848345660)

进行配置：

![1611848367_6012daaf5fbbb864736cc.png!small?1611848357729](https://image.3001.net/images/20210128/1611848367_6012daaf5fbbb864736cc.png!small?1611848357729)

选择需要解密的字符：

![1611848381_6012dabd04837e9a0dd3e.png!small?1611848372421](https://image.3001.net/images/20210128/1611848381_6012dabd04837e9a0dd3e.png!small?1611848372421)

已经成功解密：

![1611848400_6012dad00615ac58a6fc2.png!small?1611848390789](https://image.3001.net/images/20210128/1611848400_6012dad00615ac58a6fc2.png!small?1611848390789)

由于该apk传输中，password字段进行了url编码，需要在代码中进行一次编码还原：

    
    
    arg0 = decodeURIComponent(arg0);

![1611848437_6012daf5d6849d56b82b7.png!small?1611848428210](https://image.3001.net/images/20210128/1611848437_6012daf5d6849d56b82b7.png!small?1611848428210)

![1611848452_6012db04d213da3513b97.png!small?1611848443157](https://image.3001.net/images/20210128/1611848452_6012db04d213da3513b97.png!small?1611848443157)

![1611848475_6012db1b7c7e55de3c0af.png!small?1611848465861](https://image.3001.net/images/20210128/1611848475_6012db1b7c7e55de3c0af.png!small?1611848465861)

 **扩展：**

既然可以在burp中加解密，那么是否可以在实战中，直接通过python进行密码的加密传输？所幸，在作者的项目下面有个demo文件夹，下面有三个文件：

![1611848498_6012db3268f889dd404a0.png!small?1611848488735](https://image.3001.net/images/20210128/1611848498_6012db3268f889dd404a0.png!small?1611848488735)

打开testburpInterface.py：

    
    
    # coding:utf-8
    import requests
    import base64
    import json
    
    def main():
        url = "http://127.0.0.1:8088/bcall"
        methodtag = "tag94323745d0c8a4c174e41081bd50002301"
        valuse = 'HTTPDecrypt'
        print("values: {}".format(valuse))
        argsinfo = base64.b64encode(valuse.encode("utf-8")).decode("utf-8")
        argsinfo = json.dumps({"0":argsinfo})
    
        data = {"methodtag":base64.b64encode(methodtag.encode("utf-8")).decode("utf-8"),"argsinfo":argsinfo}
        print("argsinfo:{}".format(json.dumps(data)))
        result = requests.post(url=url,data=data)
        print("result: {}".format(result.text))
    
    if __name__ == '__main__':
        main()

也不知道是什么(后来翻看到对应说明手册，见下面链接)，起码知道`methodtag `对应着刚刚的js函数：本地调试下：

（https://github.com/lyxhh/lxhToolHTTPDecrypt/blob/master/docs/HDPlugin.md）

![1611848601_6012db990f875940992f1.png!small?1611848593295](https://image.3001.net/images/20210128/1611848601_6012db990f875940992f1.png!small?1611848593295)

报错了，看着cmd中界面中“httpdecrypt”应该是进行操作的字符串，那就修改成刚刚apk中被加密的字符串试试：

![1611848630_6012dbb6e4f91c7653902.png!small?1611848621473](https://image.3001.net/images/20210128/1611848630_6012dbb6e4f91c7653902.png!small?1611848621473)

果不其然，解密是成功的，那再回头试试加密函数，毕竟在实战中，用户密码是明文，在post数据时需要加密：

回头在finds中将encrypt发送至toburp中：

![1611848645_6012dbc5d12e4999e34b7.png!small?1611848636203](https://image.3001.net/images/20210128/1611848645_6012dbc5d12e4999e34b7.png!small?1611848636203)

依旧confrim，然后add一下：

![1611848676_6012dbe4cd48d9ffd0117.png!small?1611848667102](https://image.3001.net/images/20210128/1611848676_6012dbe4cd48d9ffd0117.png!small?1611848667102)

此时info中存在两个记录，选择Generate export instance script

custom中代码：

    
    
    'use strict';
    
    var rpc_result = null;
    var rpc_result_ios = null;
    rpc.exports = {
    	
    
    tag61fc8ade50b106f00cb90faf59ced1e401: function(arg0){
            Java.perform(function () {
                try{
    				// var context = Java.use('android.app.ActivityThread').currentApplication().getApplicationContext();
                    var AESUtils0c9ff62be597bd4320b9e2d149890438 = Java.use("com.***.***.util.AESUtils");
                    rpc_result = AESUtils0c9ff62be597bd4320b9e2d149890438.decrypt(arg0);
                    // send(JSON.stringify({"aa":"bb","aa1":"bbb"})+'-cusoto0oom0sc0ri0pt-')
                }catch(e){send("tag61fc8ade50b106f00cb90faf59ced1e401, " + e + "-er00roo000r-")}
            });
            return rpc_result;
        },
    // Added Function 
    tag5f1294992eeaa1cff3f6c77b1178b6c901: function(arg0){
            Java.perform(function () {
                try{
    				// var context = Java.use('android.app.ActivityThread').currentApplication().getApplicationContext();
                    var AESUtils1277f512f1925f60101b832ea2737b86 = Java.use("com.**.**.util.AESUtils");
                    rpc_result = AESUtils1277f512f1925f60101b832ea2737b86.encrypt(arg0);
                    // send(JSON.stringify({"aa":"bb","aa1":"bbb"})+'-cusoto0oom0sc0ri0pt-')
                }catch(e){send("tag5f1294992eeaa1cff3f6c77b1178b6c901, " + e + "-er00roo000r-")}
            });
            return rpc_result;
        },
    // Added Function 
    
    	
    }

存在两个函数，一个加密，一个解密：

![1611848735_6012dc1f17ea54cd301d3.png!small?1611848725946](https://image.3001.net/images/20210128/1611848735_6012dc1f17ea54cd301d3.png!small?1611848725946)

配置burp中的设置：

(httpdecrypt的burp插件在1.0之后已经不会在burp菜单栏显示，但不影响使用，若需显示在burp菜单栏，可以下载1.0之前的版本):

> 在可编辑区域调用的是Request function 1,2，不可编辑区域调用的是response function3 ,4;打开Auto后，Burp
> Scanner ，Intruder模块 也可以使用。 Auto功能 数据包加密调用的是 Request function
> 1，数据包解密调用的Request function 2，因此想要使用Auto功能，需要正确填写加解密函数位置，不要填反了。

![1611848766_6012dc3ed48ed1ee0731b.png!small?1611848757271](https://image.3001.net/images/20210128/1611848766_6012dc3ed48ed1ee0731b.png!small?1611848757271)

  

![1611848773_6012dc4592b36709ec01f.png!small?1611848763893](https://image.3001.net/images/20210128/1611848773_6012dc4592b36709ec01f.png!small?1611848763893)

依然需要记得添加：

    
    
    arg0 = decodeURIComponent(arg0);
    
    
    # coding:utf-8
    import requests
    import base64
    import json
    
    def msecret(methodtag,value):
        url = "http://127.0.0.1:8088/bcall"
        argsinfo = base64.b64encode(value.encode("utf-8")).decode("utf-8")
        argsinfo = json.dumps({"0":argsinfo})
        data = {"methodtag":base64.b64encode(methodtag.encode("utf-8")).decode("utf-8"),"argsinfo":argsinfo}
        #print("argsinfo:{}".format(json.dumps(data)))
        result = requests.post(url=url,data=data)
        #print("result: {}".format(result.text))
        return result.text
    
    def main():
        methodtag='tag5f1294992eeaa1cff3f6c77b1178b6c901'
        value="13800138000"
        password = msecret(methodtag,value)
        url='https://***************/login?phoneno=MTIz&password='+password+'&version=2.5&sign=/44YgDfbuIqfGgQT+ioYf+*******+pX8hbmDjFw='
    
        html=requests.get(url).json()
        print value,password,html["codeMsg"]
    
    if __name__ == '__main__':
        main()

![1611848878_6012dcae523ccc9589f09.png!small?1611848868596](https://image.3001.net/images/20210128/1611848878_6012dcae523ccc9589f09.png!small?1611848868596)

  

