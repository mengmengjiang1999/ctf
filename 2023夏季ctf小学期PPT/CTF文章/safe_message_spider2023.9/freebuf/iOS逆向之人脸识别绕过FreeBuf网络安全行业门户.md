***本文不涉及任何漏洞，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x00前言

**达到目的的手段有很多种，也许存在优劣之分，我只是选择了其中一种我认为好玩的方式。人脸识别校验状态存储在服务端，因此即使通过该种方法绕过客户端人脸识别，由于并未获得合法session，因此无任何危害，仅做为IOS逆向学习思路。**

## 0x01 准备

本文所使用环境：

越狱IOS手机1个（本文所用为12.4.4）

appstore下载的app一个:

![](https://image.3001.net/images/20200515/1589505104_5ebdec50313fc.png!small)

登录时存在人脸识别：

![](https://image.3001.net/images/20200515/1589505124_5ebdec64a8d26.png!small)

![](https://image.3001.net/images/20200515/1589505144_5ebdec78b3a60.png!small)

## 0x02 脱壳

apple在上架应用时，appstore会为上架的app加一层壳。在加壳状态下进行分析极为困难。但该层壳较为简单，可以通过各种自动化工具进行脱壳。如Clutch，CrackerXI+等。

    
    
    Clutch -i        #查看包名   
    Clutch -d 包名    #脱壳

因为本文所用IOS版本为12.4.4，Clutch存在兼容性问题，故使用CrackerXI+进行脱壳，脱出未加壳版本：

![](https://image.3001.net/images/20200515/1589505238_5ebdecd698de8.png!small)

在CrackerXI+中选择该app脱壳后：

![](https://image.3001.net/images/20200515/1589505279_5ebdecffa1312.png!small)

把未加壳的ipa包下载到本地：

![](https://image.3001.net/images/20200515/1589505303_5ebded174476c.png!small)

## 0x03 破解

ipa实际上是个压缩包，可以直接通过压缩软件打开，解压其中的二进制文件：

用ida反编译ios中的二进制文件

分析代码后发现:XXXXBaseViewController loginSuccessIsNeedBind:WithInfo:

是登录后，人脸识别的函数，伪代码：

    
    
    void __cdecl -[XXXXAPPBaseViewController loginSuccessIsNeedBind:WithInfo:](XXXXAPPBaseViewController *self, SEL a2, bool a3, id a4)  
    {  
      BOOL v4; // w22  
      XXXXAPPBaseViewController *v5; // x21  
      __int64 v6; // x19  
      void *v7; // x0  
      void *v8; // x0  
      void *v9; // x23  
      void *v10; // x0  
      void *v11; // x20  
      XXXXAPPLoginHelper *v12; // x0  
      void *v13; // x23  
      __int64 v14; // x1  
      __int64 v15; // x1  
      __int64 v16; // x0  
      struct objc_object *v17; // x0  
      void *v18; // x0  
      void *v19; // x22  
      void *v20; // x0  
      void *v21; // x23  
      int v22; // w24  
      void *v23; // x0  
      void *v24; // x0  
      __int64 v25; // x22  
      void *v26; // x0  
      __int64 v27; // x23  
      const char *v28; // x1  
      void **v29; // [xsp+0h] [xbp-70h]  
      __int64 v30; // [xsp+8h] [xbp-68h]  
      __int64 (__fastcall *v31)(); // [xsp+10h] [xbp-60h]  
      void *v32; // [xsp+18h] [xbp-58h]  
      XXXXAPPBaseViewController *v33; // [xsp+20h] [xbp-50h]  
      __int64 v34; // [xsp+28h] [xbp-48h]  
      __int64 v35; // [xsp+30h] [xbp-40h]  
      bool v36; // [xsp+38h] [xbp-38h]  
    ​  
      v4 = a3;//赋值v4  
      v5 = self;  
      v6 = objc_retain(a4, a2);  
      v7 = objc_msgSend(&OBJC_CLASS___UIApplication, "sharedApplication");  
      v8 = (void *)objc_retainAutoreleasedReturnValue(v7);  
      v9 = v8;  
      v10 = objc_msgSend(v8, "delegate");  
      v11 = (void *)objc_retainAutoreleasedReturnValue(v10);  
      objc_release(v9);  
      if ( (unsigned int)-[XXXXAPPBaseViewController needInputIDCardInfomation:](v5, "needInputIDCardInfomation:", v6) )  
      {  
        +[PCUtil setObject:forKey:](&OBJC_CLASS___PCUtil, "setObject:forKey:", CFSTR("1"), CFSTR("maybeNeedBackLoginGuide"));  
        v12 = +[XXXXAPPLoginHelper sharedInstance](&OBJC_CLASS___XXXXAPPLoginHelper, "sharedInstance");  
        v13 = (void *)objc_retainAutoreleasedReturnValue(v12);  
        v29 = _NSConcreteStackBlock;  
        v30 = 3254779904LL;  
        v31 = sub_1000B05E4;  
        v32 = &unk_10263F2D8;  
        v33 = v5;  
        v36 = v4;  
        v34 = objc_retain(v11, v14);  
        v35 = objc_retain(v6, v15);  
        objc_msgSend(  
          v13,  
          "setCompleteGuideBlock:",  
          &v29,  
          _NSConcreteStackBlock,  
          3254779904LL,  
          sub_1000B05E4,  
          &unk_10263F2D8,  
          v5);  
        objc_release(v13);  
        objc_release(v35);  
        v16 = v34;  
    LABEL_9:  
        objc_release(v16);  
        goto LABEL_10;  
      }  
      if ( v4 ) //判断v4(bool)值,确定是否进入人脸识别  
      {  
        v17 = +[PNCMBankGlobal sharedData](&OBJC_CLASS___PNCMBankGlobal, "sharedData");  
        v18 = (void *)objc_retainAutoreleasedReturnValue(v17);  
        v19 = v18;  
        v20 = objc_msgSend(v18, "bindType");  
        v21 = (void *)objc_retainAutoreleasedReturnValue(v20);  
        v22 = (unsigned __int64)objc_msgSend(v21, "isEqualToString:", CFSTR("FACE"));  
        objc_release(v21);  
        objc_release(v19);  
        v23 = objc_msgSend(v11, "rootVC");  
        v24 = (void *)objc_retainAutoreleasedReturnValue(v23);  
        v25 = (__int64)v24;  
        v26 = objc_msgSend(v24, "navigationController");  
        v27 = objc_retainAutoreleasedReturnValue(v26);  
        if ( v22 )  
          v28 = "goToFaceCheckBindVC:info:";  
        else  
          v28 = "goSmsOrUKBindInfoVC:info:";  
        objc_msgSend(v5, v28, v27, v6);  
        objc_release(v27);  
        v16 = v25;  
        goto LABEL_9;  
      }  
      -[XXXXAPPBaseViewController AfterBindSuccess:isNeedBind:](v5, "AfterBindSuccess:isNeedBind:", v6, 0LL);  
    LABEL_10:  
      objc_release(v11);  
      objc_release(v6);  
    }

分析代码发现：

    
    
    void __cdecl -[XXXXAPPBaseViewController loginSuccessIsNeedBind:WithInfo:](XXXXAPPBaseViewController *self, SEL a2, bool a3, id a4)  
    v4 = a3;  
    //...  
    if ( v4 )   
    {  
    //...  
    //人脸识别函数  
    //...  
    }

因此即理想状态为：

只需使if(v4)判断永假，即可永不进入登录后的人脸识别，而v4又来源于v3，因此只要使v3为0或在赋值时强制赋0值，即可。

因此即理想状态为：

    
    
    void __cdecl -[XXXXAPPBaseViewController loginSuccessIsNeedBind:WithInfo:](XXXXAPPBaseViewController *self, SEL a2, bool a3, id a4)  
    v4 = 0;//v4 = a3;  
    //...  
    if ( v4 )   
    {  
    //...  
    //人脸识别函数  
    //...  
    }

查看v4 = a3对应汇编代码：

![image-20200515003508829](https://image.3001.net/images/20200515/1589505704_5ebdeea8a9804.png!small)

利用keypatch插件修改

    
    
    MOV             X22, X2  
    修改为  
    MOV             X22, #0

![image-20200515003840764](https://image.3001.net/images/20200515/1589505714_5ebdeeb245c39.png!small)

修改后：

![image-20200515004323112](https://image.3001.net/images/20200515/1589505785_5ebdeef9ea497.png!small)

即修改地址000B03A8

F6 03 02 AA->16 00 80 D2

修改后：

![image-20200515004422610](https://image.3001.net/images/20200515/1589505807_5ebdef0fe1966.png!small)

伪代码：

    
    
    void __cdecl -[XXXXAPPCBBaseViewController loginSuccessIsNeedBind:WithInfo:](XXXXAPPCBBaseViewController *self, SEL a2, bool a3, id a4)  
    {  
      XXXXAPPCBBaseViewController *v4; // x21  
      __int64 v5; // x19  
      void *v6; // x0  
      void *v7; // x0  
      void *v8; // x23  
      void *v9; // x0  
      __int64 v10; // x20  
      XXXXAPPCBLoginHelper *v11; // x0  
      void *v12; // x23  
      __int64 v13; // x1  
      __int64 v14; // x1  
      void **v15; // [xsp+0h] [xbp-70h]  
      __int64 v16; // [xsp+8h] [xbp-68h]  
      __int64 (__fastcall *v17)(); // [xsp+10h] [xbp-60h]  
      void *v18; // [xsp+18h] [xbp-58h]  
      XXXXAPPCBBaseViewController *v19; // [xsp+20h] [xbp-50h]  
      __int64 v20; // [xsp+28h] [xbp-48h]  
      __int64 v21; // [xsp+30h] [xbp-40h]  
      char v22; // [xsp+38h] [xbp-38h]  
    ​  
      v4 = self;  
      v5 = objc_retain(a4, a2);  
      v6 = objc_msgSend(&OBJC_CLASS___UIApplication, "sharedApplication");  
      v7 = (void *)objc_retainAutoreleasedReturnValue(v6);  
      v8 = v7;  
      v9 = objc_msgSend(v7, "delegate");  
      v10 = objc_retainAutoreleasedReturnValue(v9);  
      objc_release(v8);  
      if ( (unsigned int)-[XXXXAPPCBBaseViewController needInputIDCardInfomation:](v4, "needInputIDCardInfomation:", v5) )  
      {  
        +[PCUtil setObject:forKey:](&OBJC_CLASS___PCUtil, "setObject:forKey:", CFSTR("1"), CFSTR("maybeNeedBackLoginGuide"));  
        v11 = (XXXXAPPCBLoginHelper *)+[XXXXAPPCBLoginHelper sharedInstance](&OBJC_CLASS___XXXXAPPCBLoginHelper, "sharedInstance");  
        v12 = (void *)objc_retainAutoreleasedReturnValue(v11);  
        v15 = _NSConcreteStackBlock;  
        v16 = 3254779904LL;  
        v17 = sub_1000B05E4;  
        v18 = &unk_10263F2D8;  
        v19 = v4;  
        v22 = 0;  
        v20 = objc_retain(v10, v13);  
        v21 = objc_retain(v5, v14);  
        objc_msgSend(  
          v12,  
          "setCompleteGuideBlock:",  
          &v15,  
          _NSConcreteStackBlock,  
          3254779904LL,  
          sub_1000B05E4,  
          &unk_10263F2D8,  
          v4);  
        objc_release(v12);  
        objc_release(v21);  
        objc_release(v20);  
      }  
      else  
      {  
        -[XXXXAPPCBBaseViewController AfterBindSuccess:isNeedBind:](v4, "AfterBindSuccess:isNeedBind:", v5, 0LL);  
      }  
      objc_release(v10);  
      objc_release(v5);  
    }

可以看到，已经无人脸识别相关函数。

patch到2进制文件：

![](https://image.3001.net/images/20200515/1589505850_5ebdef3ad2e26.png!small)

![](https://image.3001.net/images/20200515/1589505859_5ebdef43a1c6c.png!small)

## 0x04 安装

将修改后的二进制文件拖入ipa压缩包中覆盖原始文件

![](https://image.3001.net/images/20200515/1589505881_5ebdef5945134.png!small)

![](https://image.3001.net/images/20200515/1589505889_5ebdef612cb90.png!small)

将修改后的ipa放入手机中：

![](https://image.3001.net/images/20200515/1589505898_5ebdef6aded0d.png!small)

使用ReProvision工具签名安装：

![](https://image.3001.net/images/20200515/1589505927_5ebdef879d404.png!small)

![](https://image.3001.net/images/20200515/1589505936_5ebdef9010a90.png!small)

签名：

![](https://image.3001.net/images/20200515/1589505954_5ebdefa298a1e.png!small)

成功签名：

![](https://image.3001.net/images/20200515/1589505968_5ebdefb0427b2.png!small)

## 0x05 完成

直接输入账号密码即可登录，无需人脸识别即可进入设置指纹、手势密码页面，然后可登录成功。

![](https://image.3001.net/images/20200515/1589505989_5ebdefc52a83c.png!small)

![](https://image.3001.net/images/20200515/1589506003_5ebdefd37a2b9.png!small)

但登录后由于人脸识别验证在服务端，客户端中并无数据，因此无实际危害。

![](https://image.3001.net/images/20200515/1589506017_5ebdefe1d4c2a.png!small)

## 0x06 后记

道路千万条，逆向最为强！

> 高清原始文件：
>
> 链接:<https://pan.baidu.com/s/1B9WVlTXcvZHrepxaQlS98A>提取码: p4en

 ***本文作者：LDrakura，转载请注明来自FreeBuf.COM**

