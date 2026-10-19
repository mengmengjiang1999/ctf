![Dfj8xB7X0AAFyUN.jpg](https://image.3001.net/images/20180709/15311069079338.jpg!small)

**几个星期前，Youtube上名为JerryRigEverything的人上传了一段针对[Tapplock
智能蓝牙指纹挂锁的拆解视频](https://www.youtube.com/watch?v=RxM55DNS9CE)。视频显示，只要用一个GoPro相机固定粘附底座就可以把
Tapplock 后盖取下，然后再利用螺丝刀就能把 Tapplock 的锁扣轻松打开。**

有点不可思议，这段视频引发了我对 Tapplock
智能挂锁的安全性好奇，这款具备指纹识别、手机蓝牙和莫尔斯码解锁的智能挂锁，在方便的同时，它安全性如何呢？由此我对 Tapplock
进行了一番研究，最终我实现了2秒之内对Tapplock的解锁。

## 演示视频：

## 硬件构成

Tapplock智能挂锁由淬火钢和耐用压铸的Zamak-3锌合金打造而成。![02.png](https://image.3001.net/images/20180709/15311054548893.png!small)Zamak-3锌合金常用于儿童玩具、门把手、男士剃须刀等压铸产品，严格来说，这种金属材质强度不高，且在400℃以下就能熔化变形，对于结实的锁体来说，这不是一个好的材质选择。Zamak-3便于制作一些外观精致且感觉牢固的精细铸件，也仅只是看着安全牢固而已。

## 加密机制

Tapplock智能挂锁选用了 AES
128位的加密算法，加密强度算是很高的了。![03.png](https://image.3001.net/images/20180709/15311054756020.png!small)

这种加密强度与军用级别相当，但于对 IoT
黑客们来说，这种对称加密还是存在着一些缺点，尤其在这里的Tapplock使用说明中，完全没有密钥配对、交换和共享的规定，甚至在安全性说明中连基本的身份认证都没有。所以，类似这种应用场景中，AES-128加密还存在不足。

此外，针对Tapplock挂锁的安全性，也有诸多争议，就比如这里的 “牢不可破的Tapplock没那么安全可靠”，文章中罗列了好多针对 Tapplock
软硬件的安全测试，最终发现Tapplock并不那么安全。

Tapplock官方宣称自己的挂锁 “非常强悍”，但实际在Abloy Protec门锁面前，估计就没法比了。Tapplock官方还宣称自己的挂锁
"几乎牢不可破"，但最终却被一把4英寸的螺栓切割器瓦解。看来，一切都是的吹嘘的营销策略。

## 安全测试

以上各路安全测试也激起了我的好奇心，那就买一把Tapplock智能挂锁来实际测测吧，80欧元的价格付款，14小时之后，一款Tapplock智能挂锁就送到我家了。首先，我先按照
JerryRigEverything 的方法，用一个GoPro相机粘附底座粘住了 Tapplock 后盖。

经过30分钟的充分粘合后，用力拉粘附底座，可惜怎么也弄不开Tapplock后盖。原来，在后盖内还有一个伸到后盖项部的弹簧梢，是专门为了防止后盖的松动或转动而设计的。这个弹簧梢有可能被破坏，但是只靠一个相机粘附底座可能是不行的。但
JerryRigEverything
的Tapplock测试用锁，没有这个伸出的弹簧梢，但我们购买的Tapplock测试用锁是有这个弹簧梢的，所以，我们使劲拉住相机粘附底座最后也没能按JerryRigEverything的方法打开Tapplock后盖。

## 使用低功耗蓝牙（BLE）控制 Tapplock

现在，我们转向低功耗蓝牙（BLE）进行测试，意外的是，我们通过这里发现了一些不可思议的事。一般来说，我喜欢阅读一些费时且深入有创意的 IoT
破解文章，但这里我们就不绕了，直奔主题吧。在不到45分钟的时间里，我们需要完成对 Tapplock 的破解解锁。

首先，我们发现，Tapplock 手机APP的HTTP通信中，竟然没有传输加密机制，这是2018年啊，又不是古时候，完全令人吃惊。

![04.png](https://image.3001.net/images/20180709/1531105533455.png!small)从以上网络分析中可看到，当我每次用BLE连接
Tapplock 时，就会有一个 “随机” 字符串被发送给Tapplock端，这些字符串貌似是与 Tapplock
进行交流的命令。![05.png](https://image.3001.net/images/20180709/15311055461869.png!small)但也值得注意的是，无论我执行多少次对
Tapplock 的连接请求，这些字符串数据都是不变的。从以下蓝牙利用工具gatttool的命令行执行中可以看到，Tapplock
还容易受到重放攻击。![06.png](https://image.3001.net/images/20180709/15311055587198.png!small)由于
Tapplock
手机APP允许用户与其它人共用Tapplock挂锁，或是在某个期限内撤销使用权许可。由此，我把该测试用锁与其他用户进行了共享，然后抓取其中的BLE通信数据发现，这种用户间共享Tapplock的做法，完全与正常单一用户对Tapplock的控制一样，也就是，即使你撤销了其他共享用户的解锁权限，但其他用户一样可以在此之前，可以通过通信数据抓包方式获取到解锁认证的所有信息，利用该信息可以实现对Tapplock的认证解锁，和单一控制用户没啥区别。这就有点像智能门铃
Ring Smart Doorbell 的问题一样，不可能撤销另一具备高解锁权限的用户。

## 没有出厂重置设置

Tapplock
智能挂锁没有配备应有的出厂重置机制，使用账户只能删除其相应的挂锁信息，而不能删除相应的解锁数据。留存的解锁数据是发送到服务端或是从服务端发送给Tapplock的，因此，处于网络中适当位置的攻击者可以拦截这些解锁数据，利用这些数据间接实现Tapplock开锁。

这可不是小问题，废话少说，能开锁才是重点，现在我们需要来分析一下那些随机数据是如何实现开锁的。

## 完全控制

经过几分钟的研究分析，我发现了与Tapplock挂锁开锁过程配对的具体函数方法：

    
    
     public void regularPair(String str, byte[] bArr, byte[] bArr2) {      bArr = getCMD(CMD_PAIRING_REGULAR, bArr, bArr2);
          send(str, bArr);
          str = TAG;
          bArr2 = new StringBuilder();
          bArr2.append("Regular pair called, send ");
          bArr2.append(BluetoothTool.byteToStr(bArr));
          Log.e(str, bArr2.toString());
       }  
    

该方法中向Tapplock挂锁发送了包含两个双字节数组的固定命令CMD_PAIRING_REGULAR。这两个双字节数组会读取以下相应信息：

> this.bluetoothCenterManager.regularPair(lockMacAddress,
> BluetoothTool.strToBytes(lockInfo.getKey1()),
> BluetoothTool.strToBytes(lockInfo.getSerialNo()));

有效信息也就是Key1 和
SerialNo，它们是从哪里发送来的呢？原来当锁发生初始配对时，以上信息经keyAndSerialNo方法，间接转化为Tapplock挂锁的蓝牙MAC地址。keyAndSerialNo方法如下：

    
    
    public static String keyAndSerialNo(String str, String str2) {
          str = AndroidTool.md5(str.toUpperCase()).toUpperCase();
          if (str2.equals(KEY_ONE) {
             str = str.substring(0, 8);
          } else if (str2.equals(KEY_TWO) {
             str = str.substring(8, 16);
          } else if (str2.equals(SERIAL_NO) {
             str = str.substring(16, 24);
          }
          return str;
       }  
    

这里，它会把Tapplock挂锁的蓝牙MAC地址大写，然后把它转化为一个MD5哈希值，其中0到7个字符为key1，16到23个字节为SerialNo序列号。

是的，解锁Tapplock唯一需要知道的就是Tapplock的蓝牙MAC地址，而这个MAC地址却是由Tapplock广播出来的。我直接被这种糟糕的安全性震惊了，于是乎，我又重新订购了一个Tapplock，并确认了Tapplock挂锁和其APP的真实性。

最后，我编写了一个攻击脚本来扫描Tapplock挂锁并能实现解锁，用该脚本可以不到2秒的时间就能解锁任何一款Tapplock，完全不需要任何高深的知识和技巧。后期，我会将该脚本移植到一个Android应用程序中，使整个解锁操作更方便快捷。总体来说，实现对Tapplock挂锁的开锁成本非常低廉。Tapplock智能挂锁的这种安全性让人汗颜，这种做法算是对消费者的不尊重，我也是无语了。![07.png](https://image.3001.net/images/20180709/15311056615206.png!small)

## 物理安全性

Tapplock声称具备防垫片功能，它在锁栓中采用了传统的做法，也就是在锁扣中延伸出了另外一级咬合口，这样能避免攻击者用垫片开启闩锁。但是Tapplock的咬合口相对比较细薄，且离压力的接合点有些远。

![08.png](https://image.3001.net/images/20180709/15311069702148.png!small)

另外，用一个12寸的螺栓切割器，不到10秒就能把Tapplock锁栓搞定：

![09.png](https://image.3001.net/images/20180709/15311069834288.png!small)

## 漏洞上报

作为一款智能挂锁，Tapplock
的安全机制其实非常明确，那就是避免攻击者开锁。而锁的安全程度取决于其自身的威胁模型设计，正确的安全设计多少能减缓攻击者对锁的攻击过程，而且不会出现可被利用的安全纰漏。而作为
IoT 时代的智能挂锁，Tapplock的安全性简直堪忧，不出2秒钟就能被开锁搞定。但当我把这个问题反馈给Tapplock官方之后，它们竟然回复我：

> “Thanks for your note. We are well aware of these notes.”
>
> 谢谢你的上报提醒，我们已经知晓了这些问题。

啊，原来Tapplock官方在知晓这些问题的同时，不但不修复，而且还继续售卖这些锁具，也不让消费者知晓。这完全有些让我震惊。就在我发布该文章不久后，网上又惊现了[通过
API 解锁Tapplock的发文](https://medium.com/@evstykas/totally-pwning-the-tapplock-smart-lock-the-api-way-c8d89915f025)。

好在几天之后，Tapplock官方[就此发声](https://tapplock.com/notice/20180612/)，提醒用户要及时更新手机APP和锁具固件版本，同时警告用户要小心某些攻击场景。  

***参考来源：[pentestpartner](http://www.example.com)，clouds 编译，转载请注明来自
FreeBuf.COM**  

