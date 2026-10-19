## 0x01、前言

这是某专属src的app资产，比较冷门，无意间收集到了

当初因为一些原因，搁置了下来，没有进行测试

现在手头有空了，回过头来看看

## 0x02、开始 && 经过

此app可认为给部分公司内的人员使用，故无注册功能

开局只有一个登录框

![](./img/2772565094072763932.png)

使用burp抓登陆包时，发现了加密数据包

一连抓了两个，判断加密参数对变化

![](./img/2833137135736498881.png)

![](./img/7590028386058164001.png)

大致可以推断出sign是随着request_data中credential对变化而变化的

把app拖入jdax，很幸运，没有进行任何混淆处理

### 对credential的定位

快速定位credential的加密处

![](./img/4647579450634849336.png)

login、reset、update，根据经验判断，果断点击第一个

![](./img/446190889878304427.png)

我们发现request_data的其他参数基本都是固定的

可以看到credential的加密与CipherUtil中的encryptTokenpassword方法相关，再次点击进入

![](./img/7488181784737285248.png)

convertAuthUsername方法本质上返回一个string，并无卵用

根据代码逻辑分析，可知

str1->username

str2->id_card

str3->password

str4->old_password，也就是空

这里唯一没法判断的是str2，但是根据经验推测，id_card是身份证号，而这种数据应该是登陆后保存在本地才能获取的，初始化登陆时多半为空

直接果断编写hook脚本，看看是否跟我们猜想的一样

    
    
    function credital_encrypt(){
        Java.perform(function(){
            console.log("Fucking credital...")
            Java.use("com.richfit.qixin.utils.CipherUtil").encryptTokenpassword.implementation = function(str1,str2,str3,str4){
                //str1->username; str2->""; str3->password; str4->""
                var res = this.encryptTokenpassword("test1","","123456","")
                //send(res);
                console.log(res);
                return res;
                }
            })
    }
    function main(){
        credital_encrypt();
    }
    setImmediate(main);
    

这里我采用了attach方式启动，更加方便

![](./img/8989478373966692249.png)

果不其然，生成的结果与原数据包中的credential一模一样（数据包2）

### 对sign的定位

接下来再定位sign

![](./img/2869055275762177329.png)

现在的app中很多关键词都会被集成写入某个类中，jdax自带的交叉引用搜索也有时候不灵

所以这里换用关键词sign_method

![](./img/6283906476009222894.png)

点击进入

![](./img/3785788531462877725.png)

与原猜想相符合，sign关键词被写入了类中

sign为字符串64c8d2a0e0b2c0bbb611130862cd7b62+str2+str2.length的md5加密值

而str2也在下面指明了是request_data的值，那一切也就迎刃而解了

编写hook脚本

    
    
    function md5_encrypt(){
        Java.perform(function(){
            console.log("Fucking Md5...")
            Java.use("com.richfit.rfutils.utils.MD5Utils").digest.implementation = function(a){
                var res = this.digest('64c8d2a0e0b2c0bbb611130862cd7b62{"login_type":"manual","credential":"7S809HYx8eUGDAwKEo2TWUUUrVpj4XgTswTOyU8aS9pdqd+SZqDVP16ieWLj5QzmgXQx4gESwAddmNFSgY1ePclyxnA13JJ8gXQx4gESwAdSOJnrVtdBwjyuh1SMWDnvM6oFcq35MPhnLn91ABYP5hkfnlYuHaO9BSeaVdv2e2Y=","device_type":"android","is_brief":"true"}253')
                //send(res);
                console.log(res);
                return res;
                }
            })
    }
    function main(){
        md5_encrypt();
    }
    setImmediate(main);
    

返回结果

![](./img/1386565752014522006.png)

与原md5值相同，说明我们的hook思路是正确的

现在我们能对整个数据包进行加密解密的工作

到此完结

## 0x03、结束

本文利用了一个简单的例子，起到抛砖引玉的作用，并未真正进行漏洞挖掘

接下来我们的测试就方便很多了，比如利用Brida、编写burp插件帮助我们进行测试，但不是本文的重点，故不进行讲述

