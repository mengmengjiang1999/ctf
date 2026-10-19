本期斗哥将带来Anoid逆向之动态分析smali篇。

## 0X01 smali语言简述

smali语言是Dalvik的反汇编语言因Android虚拟机Dalvik不是执行java虚拟机JVM编译后生成的class文件，而是执行再重新整合打包后生成的dex文件，dex文件反编译之后就是smali代码。

接触过Android逆向的小伙伴都会遇到smali语言，简单的逆向过程 [apk -> smali ->
java]。有的逆向工具无法将smali语言反编译成java源码，只逆向到smali语言这层。或者反编译成java源码无法运行(smali宽松型语言）。![1](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-2018110110172689.png)

## 0X02 smali语言语法

####原始数据类型：

    
    
    //smali----java
    B----byte
    C----char
    D----double
    F----float
    I----int
    J----long
    S----short
    V----void
    Z----boolean
    [XXX-----array
    Lxxx/yyy----object
    

####基础语法：

    
    
    语法：
    
    .field 　定义变量
    
    .method　　方法
    
    .parameter　　方法参数
    
    .prologue　　方法开始
    
    .line 12　　此方法位于第12行
    
    invoke-super　　调用父函数
    
    const/high16  v0, 0x7fo3　　把0x7fo3赋值给v0
    
    invoke-direct　　调用函数
    
    return-void　　函数返回void
    
    .end method　　函数结束
    
    new-instance　　创建实例
    
    iput-object　　对象赋值
    
    iget-object　　调用对象
    
    invoke-static　　调用静态函数
    

####smali跳转语句：

    
    
    "if-eq vA, vB, :cond_**" 如果vA等于vB则跳转到:cond_**
    
    "if-ne vA, vB, :cond_**" 如果vA不等于vB则跳转到:cond_**
    
    "if-lt vA, vB, :cond_**" 如果vA小于vB则跳转到:cond_**
    
    "if-ge vA, vB, :cond_**" 如果vA大于等于vB则跳转到:cond_**
    
    "if-gt vA, vB, :cond_**" 如果vA大于vB则跳转到:cond_**
    //le 小于等于
    //eqz 等于0
    //nez 不等于0
    //ltz 小于0
    //gez 大于等于0
    //gtz 大于0
    //lez 小于等于0
    

####例子：

    
    
    //smali
    .method public onClick(View)V
              .registers 12
    00000000  const/4             v9, 3
    00000002  const/4             v8, 2
    00000004  const/4             v7, 0
    00000006  const/4             v6, 1
    00000008  iget                v5, p0, MainActivity->flag:I
    0000000C  if-ne               v5, v6, :12
    00000032  const               v5, 0x7F0C0050
    00000050  move-result-object  v3
    00000052  check-cast          v3, TextView
    00000056  iput                v7, p0, MainActivity->m:I
    0000005A  new-instance        v0, Random
    0000005E  invoke-direct       Random-><init>()V, v0
    00000064  invoke-virtual      Random->nextInt(I)I, v0, v9
    0000006A  move-result         v5
    0000006C  iput                v5, p0, MainActivity->n:I
    00000070  new-array           v1, v9, [String
    00000074  const-string        v5, "CPU: Paper"
    00000078  aput-object         v5, v1, v7
    0000007C  const-string        v5, "CPU: Rock"
    00000080  aput-object         v5, v1, v6
    00000084  const-string        v5, "CPU: Scissors"
    00000088  aput-object         v5, v1, v8
    0000008C  iget                v5, p0, MainActivity->n:I
    00000090  aget-object         v5, v1, v5
    00000094  invoke-virtual      TextView->setText(CharSequence)V, v3, v5
    0000009A  iget-object         v5, p0, MainActivity->P:Button
    0000009E  if-ne               p1, v5, :B0
    :A2
    000000A2  const-string        v5, "YOU: Paper"
    000000A6  invoke-virtual      TextView->setText(CharSequence)V, v2, v5
    000000AC  iput                v7, p0, MainActivity->m:I
    :B0
    000000B0  iget-object         v5, p0, MainActivity->r:Button
    000000B4  if-ne               p1, v5, :C6
    :B8
    000000B8  const-string        v5, "YOU: Rock"
    000000BC  invoke-virtual      TextView->setText(CharSequence)V, v2, v5
    000000C2  iput                v6, p0, MainActivity->m:I
    :C6
    000000C6  iget-object         v5, p0, MainActivity->S:Button
    000000CA  if-ne               p1, v5, :DC
    :CE
    000000CE  const-string        v5, "YOU: Scissors"
    000000D2  invoke-virtual      TextView->setText(CharSequence)V, v2, v5
    000000D8  iput                v8, p0, MainActivity->m:I
    :DC
    000000DC  iget-object         v5, p0, MainActivity->handler:Handler
    000000E0  iget-object         v6, p0, MainActivity->showMessageTask:Runnable
    000000E4  const-wide/16       v8, 1000
    000000E8  invoke-virtual      Handler->postDelayed(Runnable, J)Z, v5, v6, v8, v9
    000000EE  goto                :10
    .end method
    
    
    
    //java
    public void onClick(View arg11) {
        int v9 = 3;
        int v8 = 2;
        if(this.flag != 1) {
            this.flag = 1;
            this.findViewById(0x7F0C0052).setText("");
            View v2 = this.findViewById(0x7F0C0050);
            View v3 = this.findViewById(0x7F0C0051);
            this.m = 0;
            this.n = new Random().nextInt(v9);
            String[] v1 = new String[v9];
            v1[0] = "CPU: Paper";
            v1[1] = "CPU: Rock";
            v1[v8] = "CPU: Scissors";
            ((TextView)v3).setText(v1[this.n]);
            if(arg11 == this.P) {
                ((TextView)v2).setText("YOU: Paper");
                this.m = 0;
            }
    
            if(arg11 == this.r) {
                ((TextView)v2).setText("YOU: Rock");
                this.m = 1;
            }
    
            if(arg11 == this.S) {
                ((TextView)v2).setText("YOU: Scissors");
                this.m = v8;
            }
    
            this.handler.postDelayed(this.showMessageTask, 1000);
        }
    }
    

## 0X03 动态调试smali

IntelliJ IDEA/Android Studio
利用smalidea插件可实现动态调试smali代码下载smalidea插件（[https://bitbucket.org/JesusFreke/smali/downloads/）](https://bitbucket.org/JesusFreke/smali/downloads/%EF%BC%89)添加smalidea插件[File->Settings->Plugins]![1](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101161352907.png)点击Install plugin from
disk添加下载好插件![2](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101224605983.png)加载插件后关闭Android
Studio再重新打开导入源码（apk逆向的smali）![2](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101234440796.png)选择要加载smali源码![3](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101112211968.png)连续next![5](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101234509508.png)加载后就能看到smali![6](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101162950971.png)将存放smali文件的文件夹设置为项目源码![7](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101230751957.png)给项目添加相应的SDK[File->Project
Structure]![8](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101232547223.png)运行模拟器并启动要调试的APP开启模拟器端口转发![9](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101233634750.png)使用`adb shell
ps`命令查看程序APP的运行的端口与名称![10](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101233649838.png)![11](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101233735955.png)添加远程调试环境![12](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101234638539.png)![13](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101234900554.png)开启程序端口调试转发tcp后的端口为上图添加的端口，jdwp后的端口为在apk中运行的APP端口![14](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181102001646273.png)为smali打上断点，运行Debug[Run->Debug],开始调试![14](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101235320790.png)![15](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181101235051468.png)

## 0X04 小小总结

本期的Anoid逆向之动态分析smali篇就分享到这里啦！欢迎给斗哥留言探讨！

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20181107/1541571799_5be284d7bbc5f.jpg!small)

