在github下载的示例app，下载地址：<https://github.com/num1r0/android_crackmes/blob/master/crackme_0x01/app.apk>

app安装后运行如下图

![1648536903348-e3c3fa0d-0598-4c9b-9771-ccb5c163e80e.png](https://image.3001.net/images/20220401/1648794804_62469cb4d9eb37295be58.png!small)

输入密码，密码成功系统给出flag密码失败提示重新重新尝试

![1648536935998-b848ee2f-542d-46c3-a7ab-8bf75c4004b6.png](https://image.3001.net/images/20220401/1648794805_62469cb57890d5752c50e.png!small)

# 1 静态分析

使用apk分析工具对apk进行反编译分析，此处使用的是“apk改之理3.5.0（少月版）”，大佬写的工具很好用，导入 apk文件后自动对应于进行反编译。

![1648537520854-5146056a-9786-40a5-9beb-f7d0324da5fc.png](https://image.3001.net/images/20220401/1648794806_62469cb6163f3e96c00c4.png!small)

app文档结构比较简单，主要文件夹就是res资源目录、和代码目录。

## 1.1 查看androidmainfest.xml

![1648537733059-1ef6c598-331b-4d94-afd9-4d6b558f3892.png](https://image.3001.net/images/20220401/1648794806_62469cb6af0d2a21508f4.png!small)

查看可以确认，程序相对较简单，默认启动com.entebra.crackme0x01.MainActivity直接运行。没有 其他可以启动的activity

## 1.2 MainActivity文件分析

查看入门代码

![1648538240584-3ac6a407-aba4-46ce-a3e2-e70ab8fe9a4d.png](https://image.3001.net/images/20220401/1648794807_62469cb738117e1ef14c6.png!small)

定义description和name变量

通过constructor函数对变量进行初始化赋值，完成constructor函数后description的值为Level：Beginner，name的值为CrackMe
0x01

经过初始化函数后，进入android入口函数onCreate,由于函数比较简单，因此把完整代码贴出来

    
    
    method protected onCreate(Landroid/os/Bundle;)V  #函数无返回值
        .locals 2
    
        .line 21
        #调用父类对p0进行初始化
        invoke-virtual {p0}, Lcom/entebra/crackme0x01/MainActivity;->getSupportActionBar()Landroid/support/v7/app/ActionBar;
    
        move-result-object v0
    
        .line 22
            #调用ActionBar->hide
        invoke-virtual {v0}, Landroid/support/v7/app/ActionBar;->hide()V
    
        .line 23
            #调用父类oncrate初始化窗口
        invoke-super {p0, p1}, Landroid/support/v7/app/AppCompatActivity;->onCreate(Landroid/os/Bundle;)V
    
        const p1, 0x7f09001b
    
        .line 24
            #调用setContentView函数
        invoke-virtual {p0, p1}, Lcom/entebra/crackme0x01/MainActivity;->setContentView(I)V
    
        const p1, 0x7f070078
    
        .line 26
            #定义p1然后调用对应findViewById函数获取View对象
        invoke-virtual {p0, p1}, Lcom/entebra/crackme0x01/MainActivity;->findViewById(I)Landroid/view/View;
    
        move-result-object p1
    
        check-cast p1, Landroid/widget/Button;
    
        const v0, 0x7f070055
    
        .line 27
            #同上获取View对象
        invoke-virtual {p0, v0}, Lcom/entebra/crackme0x01/MainActivity;->findViewById(I)Landroid/view/View;
    
        move-result-object v0
    
        check-cast v0, Landroid/widget/EditText;
    
        .line 29
            #初始化MainActivity$1 #传入之前MainActivity、EditText
        new-instance v1, Lcom/entebra/crackme0x01/MainActivity$1;
        invoke-direct {v1, p0, v0}, Lcom/entebra/crackme0x01/MainActivity$1;-><init>(Lcom/entebra/crackme0x01/MainActivity;Landroid/widget/EditText;)V
    #监控鼠标点击，调用onclick函数
        invoke-virtual {p1, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V
    
        return-void

## 1.3 MainActivity$1

查看MainActivity$1文件，

![1648541901173-6e3e740e-f875-4e26-accd-9141b32bad9d.png](https://image.3001.net/images/20220401/1648794807_62469cb7b05f127b594cd.png!small)

初始化基本就是同步了标题和actiity，主要关注onclick函数

![1648542037869-7e76a4ba-0a22-4efc-beed-e4648a6c5e06.png](https://image.3001.net/images/20220401/1648794808_62469cb833d005d267a84.png!small)

定义p1 flagGuard对象，并进行初始化

![1648542180445-a4de539d-397e-4d2b-9f7e-831db5314f55.png](https://image.3001.net/images/20220401/1648794808_62469cb8bedc098ab1f05.png!small)

在初始化flagGuard对象时执行的动作如下：

  

flagGuard对象初始化时具备3个属性，并对个属性进行赋值如下：

pad= "abcdefghijklmnopqrstuvwxyz"

scr_flag= "abcdefghijklmnopqrstuvwxyz"

flag=""

初始化flaguard对象后，处理显示内容，获取editable等内容

![1648542521015-509f904c-3ba9-43a7-ae78-ca8c703b7204.png](https://image.3001.net/images/20220401/1648794809_62469cb938913ead0d0dc.png!small)

初始化完显示内容后，调用flagGuard对象的getFlag函数

![1648542604384-68d2f983-3ab3-47ec-894b-831f8a62f7a3.png](https://image.3001.net/images/20220401/1648794809_62469cb995f35f0aedb14.png!small)

### 1.3.1 getFlag函数

跟进getFlag函数内容，getflag函数内容如下

    
    
    # virtual methods
    .method public getFlag(Ljava/lang/String;)Ljava/lang/String; #返回字符串类型
        .locals 1
    
        .line 11
        #初始化Data对象
        new-instance v0, Lcom/entebra/crackme0x01/Data;
        invoke-direct {v0}, Lcom/entebra/crackme0x01/Data;-><init>()V
    
        #调用data对象的getData函数
        .line 12
        invoke-virtual {v0}, Lcom/entebra/crackme0x01/Data;->getData()Ljava/lang/String;
    
        #将getData返回的字符串进行equals对比，
        move-result-object v0
    
        invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    
        move-result p1
    # 判断equals结果，如果结果为假跳转到吗到cond_0否则继续执行
        if-eqz p1, :cond_0
    # 调用FlagGuard对象的unscramble()函数并返回一个字符串
        .line 13
        invoke-direct {p0}, Lcom/entebra/crackme0x01/FlagGuard;->unscramble()Ljava/lang/String;
    
        move-result-object p1
    #返回unscramble函数返回的结果
        return-object p1
    
        :cond_0
        #重置p1变量为空并返回
        const/4 p1, 0x0
    
        return-object p1
    .end method
    

通过以上整理发现getFlag函数主要是获取Data的getdata内容，判断该内容是否相等，确定返回内容

#### 1.3.1.1 Data对象

data对象初始化后初始化secret属性为s3cr37_p4ssw0rd_1337

![1648544176485-86598538-7adb-44f9-8985-eda9aa3c082b.png](https://image.3001.net/images/20220401/1648794809_62469cb9eb3df600e61bf.png!small)

getdata和初始化属性功能是一样的。

![1648544328906-368999dd-daf0-444c-895e-cf9bfa226c6a.png](https://image.3001.net/images/20220401/1648794810_62469cba5f1a96629164b.png!small)

继续跟进FlagGuard的unscramble函数。

### 1.3.2 unscramble函数

可以确定该函数会返回一段字符串

    
    
    .method private unscramble()Ljava/lang/String;
        .locals 9
    
        .line 21
            #初始化stringBuilder对象
        new-instance v0, Ljava/lang/StringBuilder;
    
        invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V
    
       #设置v1的值为1337.0
        const-wide v1, 0x4094e40000000000L    # 1337.0
    
        .line 22
            #将double类型转换为字符串
        invoke-static {v1, v2}, Ljava/lang/String;->valueOf(D)Ljava/lang/String;
    
        move-result-object v1
    #对v2进行赋值
        const-string v2, "\\."
            #对字符串进行split，返回数组
    
        invoke-virtual {v1, v2}, Ljava/lang/String;->split(Ljava/lang/String;)[Ljava/lang/String;
    
        move-result-object v1
    
        const/4 v2, 0x0
    
        aget-object v1, v1, v2
        #将v1数组转化成Integer并返回
    
        invoke-static {v1}, Ljava/lang/Integer;->valueOf(Ljava/lang/String;)Ljava/lang/Integer;
    
        move-result-object v1
    #将v1转化成int
        invoke-virtual {v1}, Ljava/lang/Integer;->intValue()I
    
        move-result v1
    #定义字符串变量 v3
        const-string v3, "qw4r_q0c_nc4nvx3_0i01_srq82q8mx"
    
        .line 23
    #将字符串转换为字符数组                                                                         
        invoke-virtual {v3}, Ljava/lang/String;->toCharArray()[C
    
        move-result-object v3
    #获取v数组长度
        array-length v4, v3
    
        :goto_0
        if-ge v2, v4, :cond_2
    
        aget-char v5, v3, v2
    
        const-string v6, "Char: "
    
        .line 24
        invoke-static {v5}, Ljava/lang/String;->valueOf(C)Ljava/lang/String;
    
        move-result-object v7
    #输出androidlog
        invoke-static {v6, v7}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    
        const-string v6, "abcdefghijklmnopqrstuvwxyz"
    
        .line 26
        invoke-virtual {v6, v5}, Ljava/lang/String;->indexOf(I)I
    
        move-result v6
    
        const-string v7, "indexOf: "
    
        .line 27
        invoke-static {v6}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;
    
        move-result-object v8
    
        invoke-static {v7, v8}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    
        if-gez v6, :cond_0
    
        .line 29
        invoke-static {v5}, Ljava/lang/String;->valueOf(C)Ljava/lang/String;
    
        move-result-object v5
    
        goto :goto_1
    
        :cond_0
        sub-int/2addr v6, v1
    
        const-string v5, "abcdefghijklmnopqrstuvwxyz"
    
        .line 31
        invoke-virtual {v5}, Ljava/lang/String;->length()I
    
        move-result v5
    
        rem-int/2addr v6, v5
    
        if-gez v6, :cond_1
    
        const-string v5, "abcdefghijklmnopqrstuvwxyz"
    
        .line 33
        invoke-virtual {v5}, Ljava/lang/String;->toCharArray()[C
    
        move-result-object v5
    
        const-string v7, "abcdefghijklmnopqrstuvwxyz"
    
        invoke-virtual {v7}, Ljava/lang/String;->length()I
    
        move-result v7
    
        add-int/2addr v6, v7
    
        aget-char v5, v5, v6
    
        invoke-static {v5}, Ljava/lang/String;->valueOf(C)Ljava/lang/String;
    
        move-result-object v5
    
        goto :goto_1
    
        :cond_1
        const-string v5, "abcdefghijklmnopqrstuvwxyz"
    
        .line 35
        invoke-virtual {v5}, Ljava/lang/String;->toCharArray()[C
    
        move-result-object v5
    
        aget-char v5, v5, v6
    
        invoke-static {v5}, Ljava/lang/String;->valueOf(C)Ljava/lang/String;
    
        move-result-object v5
    
        :goto_1
        const-string v6, "letter "
    
        .line 37
        invoke-static {v6, v5}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    
        .line 38
        invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    
        add-int/lit8 v2, v2, 0x1
    
        goto :goto_0
    
        :cond_2
        const-string v1, "FLAG: "
    
        .line 40
        invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    
        move-result-object v2
    
        invoke-static {v1, v2}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    
        .line 41
        invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    
        move-result-object v0
    
        return-object v0
    .end method

该函数主要功能是通过指定的算法返回一个字符串。

运行完毕程序结束，在getData时返回的应该是密码，将密码输入app尝试

![1648795020_62469d8c0bc8ffaff6387.png!small?1648795020636](https://image.3001.net/images/20220401/1648795020_62469d8c0bc8ffaff6387.png!small?1648795020636)

输入密码后系统正常后续内容。

![1648795051_62469dabdae01f3e4fa06.png!small?1648795052486](https://image.3001.net/images/20220401/1648795051_62469dabdae01f3e4fa06.png!small?1648795052486)

备注：移动安全入门学习随笔，如不正确大佬勿喷。

PS：具体知识建议学习大佬教程

