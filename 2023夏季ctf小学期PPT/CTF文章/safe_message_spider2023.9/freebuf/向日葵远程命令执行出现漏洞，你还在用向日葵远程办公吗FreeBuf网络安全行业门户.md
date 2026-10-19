### **0X01 程序详情**

![1645089852_620e143c12939497312a7.png!small](https://image.3001.net/images/20220217/1645089852_620e143c12939497312a7.png!small)

![1645090044_620e14fc1485b1b97dcdb.png!small](https://image.3001.net/images/20220217/1645090044_620e14fc1485b1b97dcdb.png!small)![1645090044_620e14fc1485b1b97dcdb.png!small](https://image.3001.net/images/20220217/1645090044_620e14fc1485b1b97dcdb.png!small)

向日葵为C++编写，使用UPX3.X加壳故此分析前需要进行脱壳处理（github上有UPX项目，可以直接脱）

![1645090073_620e15198740475bea6c9.png!small](https://image.3001.net/images/20220217/1645090073_620e15198740475bea6c9.png!small)![1645090073_620e1519b61eda2560cc0.png!small](https://image.3001.net/images/20220217/1645090073_620e1519b61eda2560cc0.png!small)

此外向日葵在启动的时候会随机启动一个4W+高位端口，具体在 **sub_140E0AAE8** 可看到

![1645090088_620e152894f65e9d05e53.png!small](https://image.3001.net/images/20220217/1645090088_620e152894f65e9d05e53.png!small)![1645090088_620e15285f2bd6c26ab4d.png!small](https://image.3001.net/images/20220217/1645090088_620e15285f2bd6c26ab4d.png!small)

根据这段疑似 session 的关键字在向日葵一次正常远程的日志中找到了关键字 CID

![1645090108_620e153c334568eddc541.png!small](https://image.3001.net/images/20220217/1645090108_620e153c334568eddc541.png!small)

随后载入IDA，对CID关键字进行搜索

![1645090124_620e154c797d9d466aea7.png!small](https://image.3001.net/images/20220217/1645090124_620e154c797d9d466aea7.png!small)

找到3个函数存在CID关键字字符串

sub_140E20938 、 sub_140E1C954 、 sub_140E1A1F4，往上跟发现分别对应接口

/cgi-bin/rpc 和 /cgi-bin/login.cgi

![1645090163_620e157361e86f1d33319.png!small](https://image.3001.net/images/20220217/1645090163_620e157361e86f1d33319.png!small)

其中在函数 sub_140E1C954 对应接口功能 /cgi-bin/rpc 中，传入如下参数即可在未授权的情况下获取到有效session

![1645090181_620e158555c6931cc645b.png!small](https://image.3001.net/images/20220217/1645090181_620e158555c6931cc645b.png!small)![1645090181_620e158549b8f016fb30b.png!small](https://image.3001.net/images/20220217/1645090181_620e158549b8f016fb30b.png!small)

在知道被控端的验证码和识别码的情况下传入如下参数可获取到session

![1645090197_620e15952817058c7b17d.png!small](https://image.3001.net/images/20220217/1645090197_620e15952817058c7b17d.png!small)

在知道主机的帐密的情况下通过 /cgi-bin/login.cgi
接口传入如下参数可获取到session并返回设备的公网、内网地址等信息，该接口同时可用作暴力破解

![1645090217_620e15a9da4c3068a66a1.png!small](https://image.3001.net/images/20220217/1645090217_620e15a9da4c3068a66a1.png!small)![1645090217_620e15a98e8f130c40f4e.png!small](https://image.3001.net/images/20220217/1645090217_620e15a98e8f130c40f4e.png!small)

###  **0X03 RCE-trick**

assist参数拼接导致

![1645090259_620e15d3be02a9c5c0c76.png!small](https://image.3001.net/images/20220217/1645090259_620e15d3be02a9c5c0c76.png!small)

###  **0X04 RCE1**

![1645090277_620e15e5c65f989da8247.png!small](https://image.3001.net/images/20220217/1645090277_620e15e5c65f989da8247.png!small)

ping命令拼接导致

![1645090288_620e15f0b7b645cc142aa.png!small](https://image.3001.net/images/20220217/1645090288_620e15f0b7b645cc142aa.png!small)

###  **0X05 远程重启**

![1645090363_620e163b35cdccd60776e.png!small](https://image.3001.net/images/20220217/1645090363_620e163b35cdccd60776e.png!small)

###  **0X06远程关机**

![1645090387_620e16535bd4ca503a94b.png!small](https://image.3001.net/images/20220217/1645090387_620e16535bd4ca503a94b.png!small)

###  **0X07指纹信息**

低版本向日葵特征` div="Veriftcation failure" &÷="false" && header="Cache- Control: no-cache"&& header="Content-Length: 46" &&header="Content-Type:
application/json"``

