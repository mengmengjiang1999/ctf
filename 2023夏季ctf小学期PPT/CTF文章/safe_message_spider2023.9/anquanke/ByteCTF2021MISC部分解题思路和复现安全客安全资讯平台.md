# ByteCTF2021 MISC部分 解题思路和复现

阅读量 **258713**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-29 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t018f197b23b8fbb1f2.png)

来写写ByteCTF2021的misc部分的解题思路，有些是比赛的时候出的，有些带点脑洞是赛后复现的，总体来说质量还不错

## HearingNotBelieving

音频题，看频谱图前半部分是二维码

![](https://p1.ssl.qhimg.com/t0150e8fda9ca322c0a.png)

![](https://p5.ssl.qhimg.com/t01e477dfea2078ad73.png)

手动补全即可

![](https://p5.ssl.qhimg.com/t01060a1cacb2e9cc53.png)

![](https://p5.ssl.qhimg.com/t017e517f77dda23fe0.png)

m4yB3_

后面音频听着像慢扫电视

![](https://p2.ssl.qhimg.com/t012747250ce5dfa211.png)

继续手撸，纯体力活啦

![](https://p4.ssl.qhimg.com/t01d7a4dc9c36921fe8.png)

![](https://p0.ssl.qhimg.com/t017a1231034303cdc9.png)

故flag为:ByteCTF{m4yB3_U_kn0W_S57V}

## BabyShark

看到baby，一开始试图全局搜索bytectf从而获得flag

![](https://p5.ssl.qhimg.com/t012c3c88cd72e47b5b.png)

结果找到一个这个，追踪进去发现是一个Kotlin的apk

![](https://p0.ssl.qhimg.com/t01d309fd810a092e46.png)

导出后反编译失败，说没找到classes.dex

重新检查流量包的数据，发现多了数据WRTE…..

![](https://p2.ssl.qhimg.com/t01470841807101a2ee.png)

![](https://p0.ssl.qhimg.com/t01ac073d7b1515d700.png)

从而导致压缩包解析错误

![](https://p2.ssl.qhimg.com/t010b54fc2e3282db9f.png)

从这，压缩包内的文件路径被WRTE块截断，从而不难看出wrte是24字节的冗余数据，手动剔除

![](https://p0.ssl.qhimg.com/t01f461103d314beee1.png)

手动删除完毕，再反编译

    
    
    package com.bytectf.misc1;
    
    import android.os.Build;
    import android.os.Bundle;
    import android.os.Environment;
    import android.os.StrictMode;
    import androidx.appcompat.app.AppCompatActivity;
    import androidx.core.app.ActivityCompat;
    import dalvik.system.DexClassLoader;
    import java.io.File;
    import java.io.IOException;
    import java.lang.reflect.Method;
    import okhttp3.HttpUrl;
    import okhttp3.OkHttpClient;
    import okhttp3.Request;
    
    public class MainActivity extends AppCompatActivity {
        /* access modifiers changed from: protected */
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView((int) C0095R.layout.activity_main);
            if (Build.VERSION.SDK_INT > 9) {
                StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder().permitAll().build());
            }
            String decrypt = AesUtil.decrypt(getAESKey(getPBResp(), loadPBClass(getPBClass()).getMethods()[37]), "8939AA47D35006FB2B5FBDB9A810B25294B5D4D76E4204D33BA01F7B3F9D99B1");
        }
    
        public Class loadPBClass(String jarFilePath) {
            try {
                return new DexClassLoader(new File(jarFilePath).getAbsolutePath(), getDir("dex", 0).getAbsolutePath(), (String) null, getClassLoader()).loadClass("com.bytectf.misc1.KeyPB").getClasses()[0];
            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }
    
        public String getPBClass() {
            if (ActivityCompat.checkSelfPermission(this, "android.permission.READ_EXTERNAL_STORAGE") != 0) {
                ActivityCompat.requestPermissions(this, new String[]{"android.permission.READ_EXTERNAL_STORAGE"}, 1);
                return HttpUrl.FRAGMENT_ENCODE_SET;
            } else if (ActivityCompat.checkSelfPermission(this, "android.permission.WRITE_EXTERNAL_STORAGE") != 0) {
                ActivityCompat.requestPermissions(this, new String[]{"android.permission.WRITE_EXTERNAL_STORAGE"}, 1);
                return HttpUrl.FRAGMENT_ENCODE_SET;
            } else if (Environment.getExternalStorageState().equals("mounted")) {
                return Environment.getExternalStorageDirectory().getAbsolutePath() + "/PBClass.dex";
            } else {
                return HttpUrl.FRAGMENT_ENCODE_SET;
            }
        }
    
        public long getAESKey(byte[] pb_bytes, Method parseFrom) {
            try {
                Object respObj = parseFrom.invoke((Object) null, new Object[]{pb_bytes});
                return ((Long) respObj.getClass().getMethod("getKey", new Class[0]).invoke(respObj, new Object[0])).longValue();
            } catch (Exception e) {
                e.printStackTrace();
                return -1;
            }
        }
    
        public byte[] getPBResp() {
            byte[] pb_res = new byte[0];
            try {
                return new OkHttpClient().newCall(new Request.Builder().url("http://192.168.2.247:5000/api").build()).execute().body().bytes();
            } catch (IOException e) {
                e.printStackTrace();
                return pb_res;
            }
        }
    }
    

主要是这里，其中getPBResp()中的api的结果可以从流量包中得到

![](https://p3.ssl.qhimg.com/t01e5e2f05dd1da9d63.png)

然后难点就在于密钥生成的时候调用了getPBClass()，进而调用了PBClass.dex，这里的dex不能直接获取，但是要是换个思路，安卓下的PB，很容易想到ProtoBuf，想不到的话百度也不难搜到

![](https://p5.ssl.qhimg.com/t01022927058335f29a.png)

而且，不难发现反编译得到的com.google包内就存在protobuf

![](https://p4.ssl.qhimg.com/t0165aab642023e59aa.png)

那么就拿通过api得到的17字节的数据去解一下

![](https://p5.ssl.qhimg.com/t018fdbba80995c9687.png)

显然1对应的就是符合long长度的key，去解一下

![](https://p2.ssl.qhimg.com/t0131de31377c0c59c3.png)

![](https://p4.ssl.qhimg.com/t01cd516753a98dc5d7.png)

## Lost Excel

excel文件，要溯源是谁泄露的，不难想到水印，先单独导出excel的水印图片后，发现0通道存在色点，但中间是有污染的

![](https://p5.ssl.qhimg.com/t014f4487361b71c3f8.png)

给了一个hint，提示说Block size = 8. Notice repeating patterns.

既然已经存在空域隐写了，再来频域转换可能性不大，故只考虑像素的规律

结合块大小为8，这里暂且先考虑是8*8的像素块，用ps分割一下看看

![](https://p3.ssl.qhimg.com/t01ddacf04941551702.png)

我们可以看到，刚巧每个8*8的像素块中最多有1个黑色块，且图中被红色框出的两块可以很明显的看出是重复的，所以其实我们只需使用上半部分即可，这样就可以避免掉原本中间被污染案的部分，再结合黑色像素块出现的位置(四种情况)可以对应转四进制，脚本如下

    
    
    import cv2
    
    img = cv2.imread(r'1.png')[:, :, 0]
    h, w = img.shape
    for j in range(0, h, 8):
        for i in range(0, w, 8):
            block = img[j:j + 8, i:i + 8]
            if block[0, 0] == 0:
                print(0, end='')
            elif block[0, 4] == 0:
                print(1, end='')
            elif block[4, 0] == 0:
                print(2, end='')
            elif block[4, 4] == 0:
                print(3, end='')
    print('')
    

得到四进制，这里再转一下ascii

![](https://p2.ssl.qhimg.com/t016231ce9293fdc7f9.png)

得到flag ByteCTF{ExcelHiddenWM}

## frequently

拿到流量包，大致看看首先是dns的流量很奇怪

![](https://p1.ssl.qhimg.com/t013329c8e9fe586c4a.png)

这个神似base64的域名不难想到有dns tunnel数据啊

还有一个io的也可以试试转01

这里先看看dns tunnel

![](https://p3.ssl.qhimg.com/t0166d3c0e8fc79d6b2.png)

值得注意的是流量中存在红色框中重复的，也有蓝色框中重复但id不同不能剔除的，故分别导出域名和id然后比对过滤

> .\tshark.exe -r frequently.pcap -T fields -e dns.qry.name -Y “dns and
> ip.src==8.8.8.8 and frame.len!=91” > 0.txt
>
> .\tshark.exe -r frequently.pcap -T fields -e dns.id -Y “dns and
> ip.src==8.8.8.8 and frame.len!=91” > 1.txt

然后结合起来剔除重复

    
    
    dns = open(r'0.txt').read().splitlines()
    id = open(r'1.txt').read().splitlines()
    idli=[]
    for i in range(len(dns)):
        if id[i] not in idli:
            idli.append(id[i])
            print(dns[i].split('.')[0],end='')
    print('')
    

得到base64了，decode一下

![](https://p2.ssl.qhimg.com/t01642194bf054724fe.png)

很明显的png图片啊，导出看看

![](https://p4.ssl.qhimg.com/t01dd812d370df49a0d.png)

恶俗出题壬….搁这放诱捕器呢

再有io对应转10

![](https://p3.ssl.qhimg.com/t01aae2df236f776ecf.png)

这里可看到长度都是91且源ip都是8.8.8.8，以此过滤

> .\tshark.exe -r frequently.pcap -T fields -e dns.qry.name -Y “dns and
> ip.src==8.8.8.8 and frame.len==91” > res.txt

![](https://p0.ssl.qhimg.com/t011a410a9be70ee8c4.png)

oi对应转01

    
    
    s = open(r'res.txt').read().splitlines()
    for i in s:
        print(1, end='') if 'i' in i else print(0, end='')
    print('')
    

>
> 010101000110100001100101001000000110011001101001011100100111001101110100001000000111000001100001011100100111010000100000011011110110011000100000011001100110110001100001011001110011101000100000010000100111100101110100011001010100001101010100010001100111101101011110010111110101111001100101011011100100101000110000011110010010011001111001001100000111010101110010

![](https://p1.ssl.qhimg.com/t01670e193d78a32aeb.png)

ok得到前半部分

然后继续，再去看看有什么流比较可疑

![](https://p4.ssl.qhimg.com/t01e9250bca5c99210f.png)

这里可以看到udp流有足足900+，且这里蓝色框中有一个内网ip向10.2.173.238发送过udp流，而10.2.173.238正是刚才发送dns解析的，故再来看看10.2.160.1

![](https://p1.ssl.qhimg.com/t01c45f0d727812bee6.png)

可以看到他发送了一堆dhcp报文

且报文的option字段还存在dns服务器是bytedance.net，十分可疑

![](https://p1.ssl.qhimg.com/t01dc49d1f16a9d09c6.png)

进一步查看，他的租约期太短了吧，才几分钟

![](https://p2.ssl.qhimg.com/t01125ed275d1a7ccfe.png)

而且每次的租约时间都不同

![](https://p1.ssl.qhimg.com/t01148609aa803b6c72.png)

故我们考虑获得dhcp.option.ip_address_lease_time字段（即租约时间）来看看

> .\tshark.exe -r frequently.pcap -T fields -e
> dhcp.option.ip_address_lease_time -Y “ip.src==10.2.160.1” > res.txt

得到

> 115  
>  115  
>  101  
>  49  
>  102  
>  95  
>  119  
>  73  
>  116  
>  104  
>  95  
>  109  
>  49  
>  115  
>  99  
>  94  
>  95  
>  94  
>  125

简单转一下ascii

![](https://p0.ssl.qhimg.com/t016784ae3943a80f27.png)

结合一下就行了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Rightp4th777** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259842](/post/id/259842)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [bytectf](/tag/bytectf)

 **+1** __8赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=ic08ENeoQ2qY7EqDIKXCOdg&s=40&t=1609048005)
Rightp4th777

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

