> [本文作者：MSTLab-> EvilChen](https://bbs.ichunqiu.com/thread-34304-1-1.html?from=beef)  
>

# 0x00 前言

首先，本来想写NDK的，但是还是先把这个流程过一遍吧，这个流程是必不可少的。  
其次，RMB真的是一个好东西。

## 导航

由于本人为了节省时间，不想贴太多的代码，所以总结了一个导航栏目。并且在栏目中有内容的说明。帮助了解。希望一起进步。  
 **[博客系列导航](https://bbs.ichunqiu.com/thread-34304-1-1.html?from=beef)**  
为了练习方便，顺便把apk进行了一个整理。  
 **[练习传送门](https://bbs.ichunqiu.com/thread-34304-1-1.html?from=beef)**

## 内容

1.内购基础

# 0x01 内购知识

## 基本知识

### 什么是内购？

内购就是游戏内部购买。

### SDK厂商

1.移动  
2.电信  
3.联通  
4.支付宝  
5.微信  
6.其他

### 其他破解

拇指玩  
网侠手机站  
7723  
爱吾  
7yw趣游  
软天空  
西西软件园  
葫芦侠三楼

### 游戏平台

1.某咕游戏

# 0x02 经验总结

## 关键点通用总结

### 通用1

最古老的方法就是搜索关键字：  
“成功“  
“失败”

## 绕过通用

### switch

（1）覆盖switch失败转为成功。  
（2）更改switch跳转  
（3）最后一种我最喜欢作用，思路最明确，使用goto进行跳转。跳转到成功即可。

## 某咕游戏总结

方法 ：onResult

## 移动总结

onbillingfinish（）  
dobilling（）  
onresult（）

## 联通总结

payCallback（）  
PayResult（）

## 电信总结

paySuccess（）

## 支付宝总结

支付失败  
9000  
ResultStaus

#  **0x03 某咕游戏破解实例**

也不能说是因为篇幅问题吧，就是有点犯懒，不想截取一些简单的步骤。所以能简写就简写，这样能多分析几个实例。

实例是我刚找的。

原版apk： **[练习传送门](https://bbs.ichunqiu.com/thread-34304-1-1.html?from=beef)**
在这里找，编号：2001

## 实例分析（1）

暂停：2018年2月12日00:34:05  
原因：吵到我爸睡觉了。

开始时间： 2018年2月12日14:58:17

### 第一步：试玩。

自己玩

![1.png](https://image.3001.net/images/20180228/15198112037110.png!small)  

### 第二步：反编译，搜索关键字。

1.搜索“成功”

这里搜索到了三条数据

![2.png](https://image.3001.net/images/20180228/15198112425034.png!small)  

点进去之后是这样一个方法：

    
    
    .method public static d()V
        .locals 4
    
        const/4 v3, 0x1
    
        const/4 v2, 0x0
    
        sget v0, Lcom/xy/kom/d/bk;->i:I
    
        invoke-static {v0}, Lcom/xy/kom/g/p;->b(I)Z
    
        sget v0, Lcom/xy/kom/d/bk;->h:I
    
        invoke-static {v0}, Lcom/xy/kom/g/p;->c(I)Z
    
        sget-boolean v0, Lcom/xy/kom/d/bk;->G:Z
    
        if-eqz v0, :cond_4
    
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->m:Lcom/xy/kom/g/p;
    
        invoke-virtual {v0}, Lcom/xy/kom/g/p;->x()Ljava/util/ArrayList;
    
        move-result-object v0
    
        invoke-static {}, Lcom/xy/kom/g/f;->l()Lcom/xy/kom/g/f;
    
        move-result-object v1
    
        invoke-virtual {v0, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
    
        :goto_0
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->m:Lcom/xy/kom/g/p;
    
        invoke-virtual {v0}, Lcom/xy/kom/g/p;->t()V
    
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->r:Lcom/xy/kom/d/ei;
    
        if-eqz v0, :cond_0
    
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->r:Lcom/xy/kom/d/ei;
    
        invoke-virtual {v0, v2}, Lcom/xy/kom/d/ei;->a(I)V
    
        :cond_0
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        const/4 v1, 0x6
    
        invoke-virtual {v0, v1}, Lcom/xy/kom/GameActivity;->a(I)V
    
        invoke-static {}, Lcom/xy/kom/d/bk;->h()V
    
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        const-string v1, "\u8d2d\u4e70\u6210\u529f\uff01\u9053\u5177\u5df2\u53d1\u653e"
    
        invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;
    
        move-result-object v0
    
        invoke-virtual {v0}, Landroid/widget/Toast;->show()V
    
        sget-object v0, Lcom/xy/kom/GameActivity;->N:Lcom/xy/kom/e/a;
    
        invoke-virtual {v0, v3}, Lcom/xy/kom/e/a;->a(I)V
    
        sput-boolean v3, Lcom/xy/kom/GameActivity;->M:Z
    
        invoke-static {}, Lcom/xy/kom/a/h;->f()I
    
        move-result v0
    
        const/16 v1, 0xd
    
        if-ne v0, v1, :cond_2
    
        sget v0, Lcom/xy/kom/GameActivity;->h:I
    
        const/4 v1, 0x2
    
        if-ne v0, v1, :cond_2
    
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->m:Lcom/xy/kom/g/p;
    
        invoke-virtual {v0}, Lcom/xy/kom/g/p;->w()Ljava/util/ArrayList;
    
        move-result-object v0
    
        invoke-interface {v0}, Ljava/util/List;->size()I
    
        move-result v1
    
        sget-object v2, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v2, v2, Lcom/xy/kom/GameActivity;->m:Lcom/xy/kom/g/p;
    
        invoke-virtual {v2}, Lcom/xy/kom/g/p;->l()I
    
        move-result v2
    
        if-ne v1, v2, :cond_1
    
        sget-object v1, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v1, v1, Lcom/xy/kom/GameActivity;->r:Lcom/xy/kom/d/ei;
    
        invoke-interface {v0}, Ljava/util/List;->size()I
    
        move-result v2
    
        add-int/lit8 v2, v2, -0x1
    
        invoke-interface {v0, v2}, Ljava/util/List;->get(I)Ljava/lang/Object;
    
        move-result-object v0
    
        check-cast v0, Lcom/xy/kom/g/f;
    
        invoke-virtual {v1, v0}, Lcom/xy/kom/d/ei;->b(Lcom/xy/kom/g/f;)V
    
        :cond_1
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->r:Lcom/xy/kom/d/ei;
    
        sget-object v1, Lcom/xy/kom/d/bk;->d:Lcom/xy/kom/g/f;
    
        invoke-virtual {v0, v1}, Lcom/xy/kom/d/ei;->a(Lcom/xy/kom/g/f;)V
    
        invoke-static {}, Lcom/xy/kom/d/bk;->m()V
    
        :cond_2
        sget-boolean v0, Lcom/xy/kom/d/bk;->G:Z
    
        if-nez v0, :cond_3
    
        const/4 v0, 0x0
    
        sput-object v0, Lcom/xy/kom/d/bk;->d:Lcom/xy/kom/g/f;
    
        :cond_3
        return-void
    
        :cond_4
        sget-object v0, Lcom/xy/kom/GameActivity;->A:Lcom/xy/kom/GameActivity;
    
        iget-object v0, v0, Lcom/xy/kom/GameActivity;->m:Lcom/xy/kom/g/p;
    
        invoke-virtual {v0}, Lcom/xy/kom/g/p;->x()Ljava/util/ArrayList;
    
        move-result-object v0
    
        sget-object v1, Lcom/xy/kom/d/bk;->d:Lcom/xy/kom/g/f;
    
        invoke-virtual {v0, v1}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
    
        goto/16 :goto_0
    .end method

  
![3.png](https://image.3001.net/images/20180228/15198113766880.png!small)  

这里找到一个调用成功的方法。我们继续溯源查看。

发现是一个onResult方法。

  
![4.png](https://image.3001.net/images/20180228/15198113891353.png!small)  

解决方法：  
（1）覆盖switch失败转为成功。  
（2）更改switch跳转  
（3）最后一种我最喜欢作用，思路最明确，使用goto进行跳转。跳转到成功即可。

恩，改完之后汇编，整个游戏就破解好了。  
没什么好说的。

### 测试成果。

是成功的，懒的玩。不想发图，自己测试吧，有疑问可以找我。

## 实例分析（2）

之前没有找好，现在去找找。  
找练习的APK的时候主要注意三点。  
（1）最好是单机  
（2）选择大小的时候选小一点的，恩，反编译快。我们的目的是为了练习。  
（3）无壳，现阶段可定脱不了壳。

找到了一个什么酷跑什么的游戏。  
三步走

### 第一步 试玩

原版apk：[练习传送门](http://blog.csdn.net/qq_36869808/article/details/79290420)在这里找，编号：2002

拿到游戏，首先就要玩一下是不，人家怎么购买的你总要知道吧。说不定会有新的发现。

  
![5.png](https://image.3001.net/images/20180228/151981142253.png!small)

### 反编译破解

搜索关键字“成功失败”

![6.png](https://image.3001.net/images/20180228/15198114212186.png!small)

点开之后进去，发现，原来还是一个onResult。

    
    
    .method public onResult(ILjava/lang/String;Ljava/lang/Object;)V
        .locals 3
        .param p1, "paramAnonymousInt"    # I
        .param p2, "paramAnonymousString"    # Ljava/lang/String;
        .param p3, "paramAnonymousObject"    # Ljava/lang/Object;
    
        .prologue
        goto :pswitch_0
        .line 26
        packed-switch p1, :pswitch_data_0
    
        .line 37
        const-string v0, "Unity"
    
        new-instance v1, Ljava/lang/StringBuilder;
    
        const-string v2, "\u8d2d\u4e70\u9053\u5177\uff1a["
    
        invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    
        invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        const-string v2, "]\u53d6\u6d88\uff01"
    
        invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    
        move-result-object v1
    
        invoke-static {v0, v1}, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
    
        .line 38
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$0()Ljava/lang/String;
    
        move-result-object v0
    
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$1()Ljava/lang/String;
    
        move-result-object v1
    
        const-string v2, "cancel"
    
        invoke-static {v0, v1, v2}, Lcom/unity3d/player/UnityPlayer;->UnitySendMessage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    
        .line 41
        :goto_0
        return-void
    
        .line 29
        :pswitch_0
        const-string v0, "Unity"
    
        new-instance v1, Ljava/lang/StringBuilder;
    
        const-string v2, "\u8d2d\u4e70\u9053\u5177\uff1a["
    
        invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    
        invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        const-string v2, "]  \u6210\u529f\uff01"
    
        invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    
        move-result-object v1
    
        invoke-static {v0, v1}, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
    
        .line 30
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$0()Ljava/lang/String;
    
        move-result-object v0
    
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$1()Ljava/lang/String;
    
        move-result-object v1
    
        const-string v2, "success"
    
        invoke-static {v0, v1, v2}, Lcom/unity3d/player/UnityPlayer;->UnitySendMessage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    
        goto :goto_0
    
        .line 33
        :pswitch_1
        const-string v0, "Unity"
    
        new-instance v1, Ljava/lang/StringBuilder;
    
        const-string v2, "\u8d2d\u4e70\u9053\u5177\uff1a["
    
        invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    
        invoke-virtual {v1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        const-string v2, "] \u5931\u8d25\uff01"
    
        invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        move-result-object v1
    
        invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    
        move-result-object v1
    
        invoke-static {v0, v1}, Landroid/util/Log;->v(Ljava/lang/String;Ljava/lang/String;)I
    
        .line 34
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$0()Ljava/lang/String;
    
        move-result-object v0
    
        invoke-static {}, Lcom/huibang/paopao/MainActivity;->access$1()Ljava/lang/String;
    
        move-result-object v1
    
        const-string v2, "fail"
    
        invoke-static {v0, v1, v2}, Lcom/unity3d/player/UnityPlayer;->UnitySendMessage(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    
        goto :goto_0
    
        .line 26
        nop
    
        :pswitch_data_0
        .packed-switch 0x1
            :pswitch_0
            :pswitch_1
        .end packed-switch
    .end method

  

![7.png](https://image.3001.net/images/20180228/15198114212775.png!small)  

咪咕整个支付流程大概就是这个样子。（我猜的）

原本游戏（隐藏不可见）—咪咕支付接口（可见）——咪咕支付处理（不可见）——返回结果（可见）——回馈给原本游戏（不可见）

我们搞的其实就是在返回结果上动手脚。

### 测试

测试我做了，但是截图不了，有兴趣的可以自己去做下尝试。

## 总结

咪咕游戏最明显的一个特征就是
onResult（）这个方法，只要改了这个方法，那么就可以轻松搞定了。当然你也可以通过其他手段找到它的特征。不过经验是可以提高效率哒嘛。

# 0x04 结束语

## 说明

这些只是对方法的一个总结，在总结的时候，可能没有时间整理实例了，但是在之后有时间或者遇到的话，那么我们就可以从这里找到方法去破解内购等。当然也包括了二次破解等说明。  
之后如果需要则进行补充。

