# **前言：**

客户仅提供官网下载地址给我们测试。但是由于官网的版本不是最新的，APP会强制你升级。而升级后的APP，是进行加固后的，无法使用frida进行hook，注入进程。那同样也无法使用SSL
Unpinning进行限制客户端校验证书。新版app使用查壳软件显示未加壳，但是查看源代码明显少了很多代码，且很多都是变量声明而已。

#  **绕过更新：**

我们要想能对APP渗透测试，一般都是需要抓包和解密的。首先使用burp进行抓包代理，官网版本的APP（以下统称旧版APP），是可以轻松抓到APP的包的（该条请求为检验APP最新版本的请求）。但是内容使用了加密，具体什么加密是不得而知。

![img](https://image.3001.net/images/20221114/1668390424_63719e1834d2e8b989520.jpg!small)

获取到请求密文：

    
    
    vVAK0jos5eT9gmQJaHOaYbqZ1mgXoBH3bee3MTF3G5wNRHRoPPOYokZLT4MQqaPDN%2BLeEYpIzzDJeErDHcDfhY8muosLfOaw35W3BuCxDNtuNFB86RumMBtOcQXT08qw

响应包未json，urldecode后为：

    
    
    {"duration":"0ms","note":"","code":1,"resultDES":"UX/jHk6yqix2yxZIrf0rSIuOjCy6oGxjCPUfBL2avG+DWy/++NW16+YQHVFQ+Nj2w9VOWGcH4OxFtGxbR6K7I6pY0Q9hkP9gc0K0JLZ5O+PwOW72nzissCiLG+cHqadKHzkPOQDdBUuBoa4W1Jz7fQ=="}

通过desStr和resultDES，一开始我猜测他为des加密，具体是不是，后续再说。

先进入APP，但是一进入APP就提示更新：

![img](https://image.3001.net/images/20221114/1668390425_63719e199ab4312279c42.jpg!small)

通过前言，我们知道是不能更新的。（当然不乏某些技术大佬也可以把新版APP搞定，我技术有限，感觉旧版的比较容易搞）。那我们就明确了目标，要先绕过更新校验。

 **对于不了解hook*** *和frida的同学，我这边推荐先去网上了解下，还有安装之类的，再来看此篇文章。

首先我们明确一下思路，要怎么绕过这个更新校验呢？

（1）直接反编译，修改APP的版本信息为99.99之类的；

（2）通过修改版本验证请求，使用http层面去绕过；

（3）使用hook，去重写更新函数，或者绕过更新函数；

第一点要app能支持反编译且不存在校验签名。第二点要能知道加密密文的密钥。所以我选择第三种：

通过jadx搜索更新，发现了两处，成功获取到源代码。

![img](https://image.3001.net/images/20221114/1668390427_63719e1bb5c6d487e3eb7.jpg!small)

类名分别为：com.xxxx.AppUpdate和com.xxxx.WelcomeActivity，通过代码审计可以看到，是先调用的WelcomeActivity，WelcomeActivity再去调用的AppUpdate：

![img](https://image.3001.net/images/20221114/1668390429_63719e1d37f6468c0ddef.jpg!small)

跟踪进入AppUpdate，调用的checkNativeAppVersion()：

![img](https://image.3001.net/images/20221114/1668390430_63719e1ed99bedfadd10e.jpg!small)

通过上述代码，我们可以看到，这边就是用于判断是否升级的函数。

    
    
    public void onResponse(Call call, Response response) throws IOException {  
    try {  
    JSONObject jSONObject = new JSONObject(C.s2(new JSONObject(URLDecoder.decode(response.body().string(), DataUtil.UTF8)).getString("resultDES"), Config.WHITE_KEY, Config.IV.getBytes()));  
    if (jSONObject.optInt("code", -1) > 0) {  
    JSONObject optJSONObject = jSONObject.optJSONObject("object");  
    if (optJSONObject == null) {  
    return;  
    }  
    if (WakedResultReceiver.CONTEXT_KEY.equals(optJSONObject.optString("isUpdate", ChatConfig.CARD_TYPE))) {  
    nativeAppVersionInterface.updateApp(optJSONObject.optString("desc", "当前有新版本，是否需要更新"), optJSONObject.optString(ClientCookie.VERSION_ATTR, ""));  
    } else {  
    nativeAppVersionInterface.noUpdateApp();  
    }  
    } else {  
    nativeAppVersionInterface.showError(jSONObject.optString("note"));  
    }  
    } catch (JSONException e) {  
    e.printStackTrace();  
    nativeAppVersionInterface.showError(e.getMessage());  
    }  
    }

当JSONObject.optInt("code", -1) >
0时，是会去进行升级的，否则则执行nativeAppVersionInterface.noUpdateApp()。

这边分析完后，其实我们就可以写js进行hook操作了。

我们的hook思路可以这样设置了：

重写checkNativeAppVersion函数，执行执行nativeAppVersionInterface.noUpdateApp()。

Ps：因为我一开始直接重写了checkNativeAppVersion，只执行了console.log(“enter
checkNativeAppVersion”)，没有对APP进行启动，这样就会直接卡死在启动页。

附上js代码：

    
    
    ​  
    if(Java.available){  
    console.log('success');  
    Java.perform(function(){  
    var appUpdate = Java.use("com.xxxx.AppUpdate");  
    appUpdate.checkNativeAppVersion.implementation = function(a,b,c,d,e,f){  
    console.log("enter AppUpdate");//判断是否进入该hook函数，进入会执行该命令  
    f.noUpdateApp();//直接执行不需要更新函数，APP会自动进入  
    }  
    });  
    }

使用命令：frida -U -l .\xxx.js -f 包名 --no-pause

![img](https://image.3001.net/images/20221114/1668390432_63719e20499203f1207e5.jpg!small)

成功进入：

![img](https://image.3001.net/images/20221114/1668390433_63719e21583856f7d7029.jpg!small)

#  **解密：**

已经成功进入该APP，但是如果想成功进行渗透测试的话，还需要能解开APP的加密。通过des字段，初步判断为des加密，再回头看看刚刚更新的那个请求，是有用c.s2()函数进行操作的，大概率s2就是解密函数。

    
    
    JSONObject jSONObject = new JSONObject(C.s2(new JSONObject(URLDecoder.decode(response.body().string(), DataUtil.UTF8)).getString("resultDES"), Config.WHITE_KEY, Config.IV.getBytes()));

可以看到s2的三个参数，即前面响应包中的json字段里面的resultDES参数，然后其次是Config.WHITE_KEY,
Config.IV两个参数，其中Config.IV是以字节数组的形式进行传参的。通过跳转可以看到配置文件的参数。

![img](https://image.3001.net/images/20221114/1668390434_63719e2259c0c183ca17b.jpg!small)

然后呢，因为获取到密钥和偏移量iv，这样的话des就可以解了。但是问题是解不开。后续的思路就是如果可以直接hook这两个加解密函数的话，是不是就可以不用管他的加解密了。

![img](https://image.3001.net/images/20221114/1668390435_63719e235cae11f9ce3ee.jpg!small)

s1和s2函数不在java层，那我们就需要hook native层的代码。Hook
so文件。首先我们先把安装包后缀apk改成zip，然后解压。就可以找到wkb-1.2.2.so的文件了。（路径为lib/arm64-v8a/wkb-1.2.2.so，前面的arm64根据自己测试机的CPU架构进行选择。）直接用ida打开，在导出函数里面搜索des：

![img](https://image.3001.net/images/20221114/1668390436_63719e249fbea1464225d.jpg!small)

里面有很多des的相关函数。可使用以下js进行hook导出函数：

    
    
    ​  
    if(Java.available){  
    console.log('success');  
    Java.perform(function(){  
    var point = Module.findExportByName("libwkb-1.2.2.so","desDecryptByteArray");  
    Interceptor.attach(point,{  
    onEnter: function(args){  
    console.log("Hook start");  
    console.log("args[0]=" + args[0]); //打印我们java层第一个传入的参数  
    console.log("args[1]=" + args[1]); //打印我们java层传入的第二个参数  
    },  
    onLeave: function(retval){ //onLeave: function(retval)是该函数执行结束要执行的代码，其中retval参数即是返回值  
    console.log("return:" + retval); //打印返回值  
    }  
    });  
    });  
    }

但是这边很奇怪的是，通过函数findExportByName找到的地址都是为null，一开始以为是还没加载到so文件，但是后续进入APP后还是一样为null。（有知道的大佬可以说下）

![img](https://image.3001.net/images/20221114/1668390438_63719e26438a2e25ef365.jpg!small)

这就比较蛋疼了，得手动计算地址。首先先获取so文件的地址，看能不能获取到，若不行，则表示未加载so文件。

    
    
    var soAddr = Module.findBaseAddress("libwkb-1.2.2.so");  
    console.log("soAddr:" + soAddr);

![img](https://image.3001.net/images/20221114/1668390439_63719e2742402f1b77e82.jpg!small)

有地址出来，说明so文件是存在的，可以正常调用。那么这边就要去计算函数偏移量。之前在网上看到别人的一个公式：

 **函数地址=so*** *初始地址+函数偏移量+1**

但是我后面尝试了好几个，好像不同手机不同的计算方法，也可能我操作的有问题。我这边的函数地址就是：

 **函数地址=so*** *初始地址+函数偏移量**

不用加一。我自己是用这个方法测试计算的：找到一个导出函数可以被查询到的，比如我这边使用的就是JNI_OnLoad函数：

![img](https://image.3001.net/images/20221114/1668390440_63719e283567d0c37d704.jpg!small)

![img](https://image.3001.net/images/20221114/1668390441_63719e29393f1772c8004.jpg!small)

获取JNI_OnLoad的地址为0x79d5d7883c，然后使用这个地址减去so的地址：

 **0x79d5d7883c** **− 0x79d5d67000 = 1183c**

差值刚好为JNI_OnLoad的偏移量，所以我这边就不用再进行加一操作了。

这样我们就可以成功hook任意函数了。通过我一个个尝试发现，以下函数一个都没调用过：

![img](https://image.3001.net/images/20221114/1668390442_63719e2a49d3d21b57be6.jpg!small)

然后呢，我查找了s2函数的用例，发现被decodeSm4的函数调用过。

![img](https://image.3001.net/images/20221114/1668390444_63719e2c26591e8461125.jpg!small)

我就尝试了一下，hook了sm4EncryptByteArr：

![img](https://image.3001.net/images/20221114/1668390445_63719e2d59ba7a0a21dcb.jpg!small)

![img](https://image.3001.net/images/20221114/1668390446_63719e2e7f1c4ee9ebbc8.jpg!small)

附上js：

    
    
    var soAddr = Module.findBaseAddress("libwkb-1.2.2.so");  
    var point = soAddr.add(0x136f0);  
    Interceptor.attach(point,{  
    onEnter: function(args){  
    console.log("Hook start");  
    console.log("args[0]=" + args[0]); //打印我们java层第一个传入的参数  
    console.log("args[2]=" + Java.vm.getEnv().getStringUtfChars(args[2], null).readCString()); //打印我们java层传入的第三个参数  
    console.log("args[3]=" + Java.vm.getEnv().getStringUtfChars(args[3], null).readCString()); //打印我们java层传入的第四个参数  
    },  
    onLeave: function(retval){ //onLeave: function(retval)是该函数执行结束要执行的代码，其中retval参数即是返回值  
    console.log("return:" + Java.vm.getEnv().getStringUtfChars(retval, null).readCString()); //打印返回值  
    // retval.replace(0); //替换返回值为0  
    // return retval;  
    }  
    });

Ps：通过ida里面的参数，我们可以看到第二个参数为类，我们就没给他打印出来。

我人傻了，一开始的des字眼和偏移量这些都符合des的加密方式，误导了我好久，一直往des方向去找。

 **尾声：**

其实很早我就已经解密成功了，直接通过java层，刚刚发现调用s2的decodeSm4函数，直接hook那边即可成功获取请求和响应的明文：

![img](https://image.3001.net/images/20221114/1668390447_63719e2fa9ee4d616b149.jpg!small)

但是若通过js去操作修改数值，实在太麻烦了，要获取密钥和加密方式，通过脚本自动去加解密，所以我才会去hook
native层，获取到密钥。因为上述密钥Config.WHITE_KEY，其实是还有一层加密的，通过hook
decodeWhiteKey函数的返回值，成功获取了密钥。

![img](https://image.3001.net/images/20221114/1668390449_63719e312f6b8c32bdedb.jpg!small)

![img](https://image.3001.net/images/20221114/1668390450_63719e32b4124f5509e34.jpg!small)

其实后续我也尝试去修改版本号绕过，但是事实证明，代码存在验签：

![09fb86b8fbc058e8ecab0e5a8a04be6](https://image.3001.net/images/20221114/1668390451_63719e33ded3662308d14.jpg!small)

可以看到，把版本号修改为99.9.99，成功绕过了更新检测，但是他还存在一个盗版验签检测：

![5db5880584da7a62dea2030e6c00a57](https://image.3001.net/images/20221114/1668390453_63719e350f9be9385c738.jpg!small)

验签代码一样需要用hook去绕过。所以前面说的方法一也是行不通的。然后我又突发奇想，有没有可能他密文里面就包含版本信息，那如果我使用99.9.99的版本，抓取密文，然后再安装旧版APP，在他去请求版本更新时，替换密文，是不是可以绕过呢？经过尝试，结果是：可以。他的版本校验就是在服务端，这种方法也可以绕过。

#  **总结：**

不用轻易相信别人留下的信息，还是得根据自己的分析得出结论。其实后续我一直在想为什么那个字段是des呢，感觉之前是des加密，后续金融行业都进行了国密改造，然后字段并未更改，导致这种现象，当然只是猜测。至此，已完成对这APP的抓包和加解密。

