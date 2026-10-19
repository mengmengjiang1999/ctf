网络钓鱼是非常常见的攻击行为，攻击者经常利用其来窃取登录凭据与信用卡信息。HTML
附件也是此类攻击中最常见的附件之一，因为此类附件通常被认为比其他文件类型来说更没那么可疑。

HTML
附件可能包含将用户重定向到网络钓鱼页面、下载恶意软件或通过网络钓鱼表单窃取登录凭据的链接。为了逃避检测，攻击者通常会使用多重重定向跳转、混淆代码等方式对敏感信息进行处理。

近期，研究人员发现此类攻击在全球激增。根据遥测数据，多个行业的增长率都超过 1030%。

## 在野钓鱼样本

研究人员一直在跟踪各种 HTML 作为附件的攻击行动，以下是在野发现的一小部分样本：

  * 样本1：伪造 DocuSign 请求的电子邮件，要求受害者对 HTML 进行电子签名，打开就会跳转钓鱼网站
  * 样本2：包含嵌套的电子邮件附件，其中包含恶意 HTML 文件
  * 样本3：伪装成来自人力资源部门的电子邮件，HTML 附件伪装成员工福利政策宣传
  * 样本4：伪装成会议纪要文件的 HTML 附件
  * 样本5：伪装成虚假的电话会议通知
  * 样本6：伪装成合法 eFax 消息的恶意 HTML 附件

![image.png-1271.5kB](https://image.3001.net/images/20230630/1688088499_649e2fb3a81431c784736.png!small)各种钓鱼邮件

## HTML 附件的实现原理

HTML 附件通常会使用各种混淆技术并在加载最终钓鱼页面前显示一个中间页面，这是该攻击活动的主要特征。

执行时 HTML 文件会创建一个网页，其中包含两个隐藏的 input 标签与一个 script 标签。其中一个 input 标签带有 base64
编码的目标用户电子邮件地址，script 标签会动态创建另一个 script 标签并将其附加到文档的开头。动态创建的 script 标签的 src
属性被设置为使用 atob() 函数进行 base64 编码的 URL，解码后的 URL 用于加载额外的 JavaScript 代码。

![image.png-1068.7kB](https://image.3001.net/images/20230630/1688088501_649e2fb5289ef472aabf2.png!small)HTML
附件变种

上图右侧为钓鱼页面的基础版本，可以发现它向以 mj.js 结尾的 URL 发送请求。此外，还包含 ID 为 b64e 与 b64u 的 div
标签，分别为受害者的电子邮件 ID 与 C&C 服务器的 URL。

![image.png-304.1kB](https://image.3001.net/images/20230630/1688088502_649e2fb6739b2db64c1d0.png!small)C&C
服务器的请求

收到的响应分为两部分，下图为响应的第一部分。其中解码后包含中间加载页面的 base64 编码数据，在加载最终钓鱼页面之前，加载的中间页面会显示几秒钟。

![image.png-572.1kB](https://image.3001.net/images/20230630/1688088503_649e2fb79829bf3e8ae8c.png!small)响应的第一部分

代码块 1 是一个函数，会返回一个包含 base64 编码日期的数组，该日期分为三部分。代码块 2 声明了各种变量，prer 与 pre2 变量包含
HTML 的 base64 编码数据，创建对应的标签内容。代码块 3 声明了对数据进行解码并将其写入 HTML 页面的 body 标签与 head
标签的函数。代码块 4 使用 eval 函数执行解码后的数据，代码块 5 用于调用代码块 3 中声明的函数。执行代码后，就可以看到如下所示的加载页面：

![image.png-589.6kB](https://image.3001.net/images/20230630/1688088504_649e2fb8777cf73ea5b9c.png!small)中间加载页面

中间加载页面是这种攻击的关键特征之一，攻击者试图通过这种方式增加延迟来逃避检测。

![image.png-214kB](https://image.3001.net/images/20230630/1688088506_649e2fba4bac06316e256.png!small)最终页面的
base64 编码

响应的第二部分中，变量 pr1 与 pr2 包含执行 POST 请求以获取最终页面的 base64 编码数据。首先经过 base64 解码，再通过 eval
执行。base64 解码后如下所示：

![image.png-378.3kB](https://image.3001.net/images/20230630/1688088507_649e2fbb16ae1a7ee7850.png!small)加载最终页面的解码代码

代码块 4 会创建一个带有 4 个参数的 POST 请求。Scte 为电子邮件 ID，而 data11、data22 和 data33
合并后为包含钓鱼页面执行时间的 base64 编码数据。Conf 为带有 id conf 的 div 标签，在原始 HTML 附件中就存在。解码后的
base64 数据为：`{"back":"default","title":"default","caption":"default"}`。

执行就会发送请求：

![image.png-299.8kB](https://image.3001.net/images/20230630/1688088508_649e2fbc8b7e07ef5740b.png!small)发送请求接收最终页面

最终页面加载受害公司的图标与背景前，会以电子邮件地址为参数发出 POST 请求：

![image.png-456.4kB](https://image.3001.net/images/20230630/1688088509_649e2fbd6e19b4a024433.png!small)使用受害者电子邮件地址发送请求

上图的请求以 JSON 数据响应，其中包含指向最终页面的背景图片与受害者公司图标的 URL。

![image.png-418.7kB](https://image.3001.net/images/20230630/1688088510_649e2fbe66800e5e53525.png!small)最终请求的代码

上图显示了请求的相应代码，页面会根据 JSON 对象收到的数据，动态更改页面以加载受害者的公司图标与背景图片。

下图列举了部分受害者看到的最终页面：

![image.png-592.5kB](https://image.3001.net/images/20230630/1688088511_649e2fbfdbc893055236b.png!small)钓鱼页面

一旦用户输入密码，就会将数据发送到攻击者的服务器上，如下所示：

![image.png-516.1kB](https://image.3001.net/images/20230630/1688088513_649e2fc17624bf8ae60c6.png!small)发送的请求信息

## HTML 附件：不断进化的逃避策略

攻击者会定期更新 HTML 文件代码以逃避检测，各种变种的 HTML 代码都执行类似的攻击行为。大多数变种的 HTML 附件文件大小在 3KB 到 5KB
间。

### 变种1：访问 DOM 树

该变种正在访问 DOM 树以构建最终的网络钓鱼脚本：

![image.png-917.2kB](https://image.3001.net/images/20230630/1688088514_649e2fc293121ecdef90d.png!small)变种代码

![image.png-811.7kB](https://image.3001.net/images/20230630/1688088515_649e2fc397a8b1764132f.png!small)变种代码

样本使用混淆脚本执行加载中间页面的初始 Payload，在 b64e 的 div 标签中包含电子邮件地址，在 b64u 的 div 标签中包含第二阶段
Payload 的 URL。

![image.png-1083.3kB](https://image.3001.net/images/20230630/1688088517_649e2fc52d887297d7a85.png!small)变种代码

### 变种2：使用 onload 触发与 eval

该变种使用 onload 触发 eval 与 atob 函数执行网络钓鱼 Payload：

![image.png-438.1kB](https://image.3001.net/images/20230630/1688088518_649e2fc62444c3c7dadfe.png!small)变种代码

上图中包含 base64 编码的数据，首先通过 eval 函数进行 base64 解码再执行。通过 body 标签的 onload 属性触发执行。

![image.png-866kB](https://image.3001.net/images/20230630/1688088519_649e2fc7bfe2a59eb19a0.png!small)变种代码

### 变种3：使用 onload 触发访问 DOM

该变种没有使用 script 标签，而是使用 onload 触发执行访问 DOM 元素的代码。

![image.png-1112.9kB](https://image.3001.net/images/20230630/1688088521_649e2fc92e220d7ea61ef.png!small)变种代码

样本代码通过 onload 属性触发，访问 ID 为 temp1 和 temp2 的 div 元素。div 元素包含类名称，也是 base64
编码的字符串。生成的脚本最终如下所示：

![image.png-562.4kB](https://image.3001.net/images/20230630/1688088522_649e2fca4b69efed1e393.png!small)变种代码

生成的代码执行逻辑类似，只是访问的类名称的脚本不同。也会访问 base64 编码字符串的值，并将其组合起来。

![image.png-234.3kB](https://image.3001.net/images/20230630/1688088523_649e2fcb8b909ce5bfa27.png!small)变种代码

样本经过多层 Unicode 编码，解码后与前述代码类似：

![image.png-152.5kB](https://image.3001.net/images/20230630/1688088524_649e2fcc4c42ca24aae9a.png!small)变种代码

脚本反转字符串并解码 base64 数据，使用 decodeURIComponent 对特殊字符进行转义，然后使用 document.write 将其写入
HTML 文件。

### 变种4：使用 onerror 触发与 eval

变种使用 onerror 触发 eval 与 atob 函数加载网络钓鱼 Payload：

![image.png-486.1kB](https://image.3001.net/images/20230630/1688088525_649e2fcd0bdf0ec38b8bd.png!small)变种代码

上图中，样本包含 base64 编码的字符串。解码后通过 eval 函数执行：

![image.png-485.5kB](https://image.3001.net/images/20230630/1688088529_649e2fd1856f5a7922775.png!small)变种代码

解码后通过 eval 执行的，是由 onerror 属性触发的。由于来源路径被设置为 x，img 标签的 onerror 属性在加载图像时出错，从而触发执行
onerror 属性中的代码。

解码后的 base64 字符串中的代码如下所示：

![image.png-488.2kB](https://image.3001.net/images/20230630/1688088530_649e2fd2a5a81005ba23a.png!small)变种代码

样本混淆隐藏了原始代码，去混淆后如下所示：

![image.png-615.5kB](https://image.3001.net/images/20230630/1688088531_649e2fd3eefc55a6a8763.png!small)变种代码

### 变种5：使用 URI 编码

属于该变种的样本使用 URI 编码与 HTML 标签（例如 svg、video 与 h5）：

![image.png-697.5kB](https://image.3001.net/images/20230630/1688088533_649e2fd50d3a2329a34ad.png!small)变种代码

与前述代码中使用 base64 编码字符串不同，该样本的变种使用 URI 编码的字符串。解码后可以看到另一个混淆的脚本，与其他变种行为类似。

如下使用 h5 标签的 onanimatestart 属性来触发执行：

![image.png-1160.3kB](https://image.3001.net/images/20230630/1688088534_649e2fd6036db67871697.png!small)变种代码

如下使用 style 标签的 onload 属性来触发执行：

![image.png-1259.6kB](https://image.3001.net/images/20230630/1688088535_649e2fd76ce24719ae058.png!small)变种代码

如下使用 video 标签的 onloadstart 属性来触发执行：

![image.png-213.5kB](https://image.3001.net/images/20230630/1688088536_649e2fd8723b952a0c8b6.png!small)变种代码

## 邮件安全遥测数据

如下所示，此类攻击的主要目标是美国、韩国与德国。

![image.png-180.5kB](https://image.3001.net/images/20230630/1688088537_649e2fd94b1d5834c8deb.png!small)国别分布

按行业划分，高科技、制造业与医疗保健行业发现的攻击最多，这些行业不仅经常处理敏感信息还拥有复杂的 IT 架构与攻击面。

![image.png-124.2kB](https://image.3001.net/images/20230630/1688088538_649e2fda3015429303d21.png!small)行业分布

从 2022 年第四季度到 2023 年第一季度，此类攻击活动激增。攻击者趁着年底的假期，针对在线购物、零售与金融机构的攻击大幅度增加。

![image.png-151kB](https://image.3001.net/images/20230630/1688088539_649e2fdb051f53000f976.png!small)检测趋势

## 结论

近年来，使用 HTML 附件的网络钓鱼攻击一直在持续增长。近期攻击活动激增显示，攻击者的技术越来越复杂。只有不断改进策略与技术，才能提高网络钓鱼的成功率。

## IOC

> d96e5c5dcea235e9c09c0888e599ec65  
> d24f61d477b1316c6def56884c37e2b8  
> ce7f2eae6ff89583701190617f793ee6  
> ca932194d4b07951469d1edd61121781  
> ad30bcf6b4810a164a94e20eeff5baa3  
> 9d43f9a6b6c300dfa27fd5323bbed60e  
> 735951849ba066a36758e88df07a0340  
> 6566752f8346445cb3c1866fa340e322  
> 3656c01ce5f8cc2e2d3f727c19575480  
> 1bedb92af8650aa0313893fb0cdc671c  
> 83bfd80edf2e092d9d5d7756abcc624e  
> 86c78d6ed2fb2b04741a232bb24e5a82  
> 7d43031c91bcaab993df375d3a47d114  
> c96fb3ec71f00bac34d106b832cf30d4  
> 64efa7e5d18c73ec9dae63c4efac197f  
> 962a7b5661e81cd3462181a65b664436  
> 92d58240601c8807e8eda8d2477dda6a  
> c40ab475570d8913724b23e3c520be60  
> 4d992e66aac3d0b81910c7a2726106df  
> 52e7c55329436499921a946fe72b2376  
> abe0b0079a242387e5b3a8b8426a7529  
> 3dff9b0c904647920e973ab51c3f5d9b  
> b080fdcf422750467c5987ee24ad7e0a  
> 805aeb114220d1753e1cd2415bf9aa86  
> 86e65eeb38870b086844e3d84779a6a0  
> abc2580647f8ed60f377b924d8808050  
> 53b0a816113e47d666c32752584ea818  
> 967dcc52ced38d05bed89ddc45b74627  
> ac2b3e3e06c6fc7ec62b2c1167b4f499  
> cb2f0b3f97a28bb6ecf15f3354c70fd0  
> f9afd7559538e4cf687a0d52bfc1b694  
> 7b29e71ff9e278a436786ad6af5fcc01  
> 4f3ce8ec6a45364ea73b68fe4573853e  
> f4a390d23d4fd03a665f3bcd2be957cb  
> 675ec70065d13710bb40f82b1e28a9a7  
> d2d8806d7477b590ff364ca28c5c69ac  
> db3d5e9ff6103b584afef2cdd9184ce0  
> fd3a5edbdc33ca5e7a08893f82070c7b  
> 9e636130b641183b9710183586a97079  
> 7c1971c557a613708fd60928091a9c59  
> 279f96beee54968500f7ef3971252e7a  
> cc9781d1480106249abeaf4e522accfa  
> 45b940ae7617afb4bd7dce6fae870c90  
> c6277045498542a232ceba8abee99223  
> dde98bd04562ecfa0b90477c060d8a9c  
> 41e57e23156a64a9d8ddbc514e317000  
> c899a0a561ea3a8fb7eb7687bde05da8  
> 40fbc6662a306bf142d7019ddaeac7b5  
> 73d4c7ba717423f44345340f309a8990  
> c6fcc1fca35cef0be981bad42a485aab  
> 142a48f90c60d8553cf2b9fe11e3af22  
> d9f2fb38f9432526dd978dbc306f4e8a  
> f111b336e29e4ab019e0d9e549a20bfa  
> 0fe8c873ada4bbe9bbb84c019ca25780  
> 15de0b72f3263ef052b2aa3fdf7ccc5a  
> 4289e249328ff40b6b964cd4dcb0c257  
> 30b972c81e092bddbd66f1373e5c67a5  
> 30190af9969914693c5da00d24efccb2  
> b655c416a6a395a28a934894260adf70  
> f30430554f1eebeffbf4b0a6c9da16ce  
> 0bb00fd7b6acbe024d0a5cfacef65d02  
> bb93f7c4f449d7b4ceb69a624a5da721  
> f75bbabc887d1ef4a9b3e28d921c90a8  
> b9b6251f872d599437e08be2a6d61619  
> d13e3e448aea9f12b099255b8b5da0ce  
> 1d72f4838603d4812a7865e69b24cd10  
> 9c6601b8af57f2536b3dc34f63a9bf7e  
> 755edc95125ec4cbbff4cd3859a03050  
> 978b6fe89366b35d01340a183cac9894  
> bce84588ad7778157326f856a4f2f235  
> cba0b485cde78df1ca38cb7557294d1a  
> d59c8fee6f99185d4e4e57a465635fa1  
> 1e921ed48263d7b1076b06a777cec3f2  
> 2cf1252f2966c23759fbd38eaaa8648e  
> 2846e281e165221fa52d9970266ce2f2  
> b5e05e93f0246f328bdabf8b3c6fb6cd  
> 7a4dd6388d2792991286915baa9a8788  
> 9b406af8bed6bffac8d3a5f2f7f7f6ed  
> 3982f8fddf4e36d16cf6891357cf1b39  
> a52277aa2779e13a62a35688afed8949  
> cfe18d98355d586e8e5ebac5dc71899b  
> 3b76c708955fbae140759536ec56cf18  
> d3a9878c9670ebfca4e2c650111e2055  
> a4374458883f532b43f26076b23b2d1e  
> 88064803236433ff644725ebf6d740d7  
> 9e10802468e485b61b6f80a6fbea2dd5  
> 5550931e322c6165b22fe3085d8dc8ba  
> 2cd6294d0b06e605033f089c1ca7f875  
> 4ecbbbd4ab5ee837f97cd0ff76e1d89a  
> 6c76973166555650cb631fdc2569ac70  
> 8aa4a2d553c4dc323d349a46d7caad6d  
> 457fbb3ff1a7fe0187988eea1a2e9fc9  
> d2c638b88c71b02dd596759e86cdc829  
> 7b79cd9fe6e662a2021958d0db42522a  
> 8c6b3c7c743d2cefe07b3bdb545338f6  
> 168d2d263607abfc273171ab5af2cb62  
> 44574424ad95a36e71f4a4e3f900c51c  
> 127484f819d2ee4d3cd148b83bb9436b  
> 768165bfc4c00012bfef3368a4985122  
> b44411afb06a6de63df6367382d120f5  
> f1d8bab2b9c827176f5ffb1c802d2826  
> 0b67c02c51c1d50cf5e01803beed8060  
> ce1a59c3ea32749e0a2295cec8ffcbae  
> 0707c7baa96ada6db316e83d3bc12888  
> 3de3a6297e7057c7baf570390cb9d1fb  
> 7fb7b8623e9a7419d2420e407096fd1a  
> 77fea63af13b83e196c8332ca16fb77f  
> 6266a4fefec6f8a96624f3643eab8903  
> 1405113d7a4ee555af923ecc55f4ede3  
> 93703df53e5ec8d038283441358b42d9  
> 6a34741672895cac3d14e2f95a0152fc  
> 331f415cd1c7986577912763c1940ed9  
> fb75fe28b9edc83d2b91b8436ff3cfc3  
> 234beae64b562bb94338e209d8a96a78  
> 809dbc9cd1493b3a6e222241477609e4  
> a6a68f4763eb9deefbf27b30a444de69  
> ff4a93d8a695f63b3626fbe0b8430156  
> 2f6a00c04c6e09b8857cc99a7f94619e  
> 6af6a355cc54d74d3edf22fe0ebc8102  
> 7a3aa92d70349b73bdc98db72be20049  
> 54152826cbc5f5bbfe6bb49963c0bdba  
> e47b3e89a7026f579377be7c6ea8d5fd  
> 3484ffc5d34cb55a7c75e06b8a0869bc  
> bd26e92f91c1f7daeeeae06a36d8ed7b  
> d02d0fc3378734cd7208505e12704b6d  
> 8623f472c59fe873c4f4eee019bb1be0  
> ef49340924f783c54b979b3abdd0bc33  
> 613a57a0e10dcb6d2dd25a27901b8fe5  
> a55114019ec824b21f0474658c2ce9c7  
> 18ba0bc8af26c5c47477700145dfcc63  
> f73015c873e19860afcdca5e129e2e5b  
> 7fc7fe70813787aebbe1c1bcfd1b85c6  
> 210441349458f57375a661d5e7fa71fe  
> b6827a772b09ad9f99ddef2aaeee129a  
> 1333aba4d073ca570e228f553eeb11f2  
> 87f6be16e59f37b27449121e53c017ca  
> 52dab9d79be01bcf8f51281c4b469089  
> 3e93a6b9bd12f520be389fd27cfd9390  
> 8e1459288da4a48b2e39994fcdac206c  
> 331262b151205851747464a5c0d75699  
> f5f8770dbcad6b1bbfd480b259e7db7e  
> 7dbaaceb735bec4e8a54a6d1d2146396  
> ad4bfffff0ea91d2fde7099d2b104f11  
> c55aa8da3c68f9ad8b4198142db5d996  
> 27df775d0c11538e4570ab0e61ccf315  
> 3653f2c22d285d1cd36a5d7a4a35762e  
> 20c927ae0d2cf48f88909e9d18324998  
> 429c2c539e29b0a66f10c08998cefd39  
> e12f16891ab0c4d4203bca3377d4e3de  
> 1a0a81cf0f9b719014768d36062c8414  
> de58e5b6571c78f4090b549d5131835f  
> 13b28e771ad85f4b03667bb3d47f56a4  
> 5507a8c0279b17a1793ae6fc5487b4c3  
> 4b97f81aee5c2f592bbcec507f971dd3  
> 244f485f9ad7d27a2976bc928bd76d51  
> 44bf454eda2bdecf130d6b46a8ccb108  
> 2446951faaab65095f137818a3bba4e8  
> a094da476fd8241de202d80df41b8103  
> 2d77191715f8af8c496d8094aa20cb8f  
> 70922fbea28d6d8ee1cacec63b0543d9  
> 52b6fe417449548946da25922a84adf0  
> 05f8ea8d95e689ef4c8fbb5a27c9dbb3  
> 581f72429222243151dd9bad3c34ccaf  
> c539b37904e1c36d72fde533ff56cf67  
> 4b1c110f622f5d16cf762d86aaf41ca7  
> 8d051b4ee368cf632f6522e5d7b1a906  
> 3458c29c51a0d0070af8d6bbd57bebe4  
> 521221f4dadd6478560e03ef48d2543a  
> 8c28cefb554887ec4e32332c3de6e8f6  
> 929b7c3558c0d0d5b9856f7ded22a5a4  
> 1940983b7ddecdc4c2ff3402f4e1abf4  
> a331b32161dd7dd4aba45fb2b7a037f9  
> hxxps://beautiful-> pascal[.]181-215-68-142[.]plesk[.]page/host16/admin/js/mj[.]php?ar=  
> hxxps://psbsrep[.]com/hmmmchuloo/host16/admin/js/mj[.]php?ar=  
> hxxps://d349-jp[.]com/sl-1/admin/js/mj[.]php?ar=  
> hxxps://democart[.]trixieservices[.]com/xt/1212/host16/admin/js/mj[.]php?ar=  
> hxxps://onlyymgc[.]com/host16/admin/js/mj[.]php?ar=  
> hxxps://naitnewswatch[.]ca/nr92/host16/admin/js/mj[.]php?ar=  
> hxxp://bonus-leon[.]higgsid[.]store/host16/admin/js/mj[.]php?ar=  
> hxxps://condipaf[.]com[.]br/wp-includes/MON22/host16/admin/js/mj[.]php?ar=  
> hxxps://braesidecarsales[.]co[.]zw/wp-content/app/appp/admin/js/mj[.]php?ar=  
> hxxps://formativa[.]com[.]ec/aulavirtual/koss/admin/js/mj[.]php?ar=  
> hxxps://saloneglobalcom-b7ce8f[.]ingress-erytho[.]ewp[.]live/wp-> admin/host7/admin/js/mj[.]php?ar=  
> hxxps://saloneglobalcom-b7ce8f[.]ingress-erytho[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxps://schmidtautodetailing[.]com/off1ce/host6/admin/js/mj[.]php?ar=  
> hxxps://negtechnoloyg[.]com/robocop/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://tdc-propartiescom-b7ce8f[.]ingress-daribow[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxp://thefiirmpmcom-b7ce8f[.]ingress-erytho[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxps://46berrierscom-b7ce8f[.]ingress-comporellon[.]ewp[.]live/wp-> admin/host7/admin/js/mj[.]php?ar=  
> hxxps://watchitsre[.]co/us/host10/admin/js/mj[.]php?ar=  
> hxxps://thefiirmpmcom-b7ce8f[.]ingress-erytho[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php/ar=cGRm  
> hxxps://dahbimastectin[.]com/pen/secur3/admin/js/mj[.]php?ar=  
> hxxps://tradestation-paper[.]com/admin/js/mj[.]php?ar=  
> hxxp://michelearris[.]com/wp-content/plugins/host7/admin/js/mj[.]php?ar=  
> hxxps://mymatgar[.]com/vmla/host15/admin/js/mj[.]php?ar=  
> hxxp://watchitsre[.]co/us/host10/admin/js/mj[.]php?ar=  
> hxxps://tdc-propartiescom-b7ce8f[.]ingress-daribow[.]ewp[.]live/wp-> admin/host7/admin/js/mj[.]php?ar=  
>
> hxxps://deirefhwc[.]sa[.]com/paymentremmitance/secured/accessauthorized/admin/js/mj[.]php?ar=  
> hxxps://mcare[.]co[.]in/host6/admin/js/mj[.]php?ar=  
> hxxp://mzlofalolpia[.]com/mkpza/host8/admin/js/mj[.]php?ar=  
> hxxps://fxcalc[.]mds[.]com[.]cy/host7/admin/js/mj[.]php?ar=  
> hxxps://ajax-nl[.]com/file10/host10/admin/js/mj[.]php?ar=  
> hxxps://invistajaimoveis[.]com[.]br/host12[.]mod/admin/js/mj[.]php?ar=  
> hxxps://bosee[.]peaceofcode[.]net/binbosse/peace/admin/js/mj[.]php?ar=  
> hxxps://dfsolucoesinfo[.]com/monks/host10/admin/js/mj[.]php?ar=  
> hxxps://blueskys[.]info/ddy/host10/admin/js/mj[.]php?ar=  
> hxxp://dahbimastectin[.]com/owah/secur3/admin/js/mj[.]php?ar=  
> hxxp://emeeramaontinwrldecp[.]com/wsdas/admin/js/mj[.]php?ar=  
> hxxps://stefanielange[.]com[.]py/host9/admin/js/mj[.]php?ar=  
> hxxps://mzlofalolpia[.]com/mkpza/host8/admin/js/mj[.]php?ar=  
> hxxps://jblech[.]com/wp-admin/ttshc/host9/admin/js/mj[.]php?ar=  
> hxxps://bitstamp[.]tv/host9/admin/js/mj[.]php?ar=  
> hxxps://purposetrust[.]revx[.]se/wp-> includes/allliu/host7/admin/js/mj[.]php?ar=  
> hxxps://48berrierscom-b7ce8f[.]ingress-florina[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxps://bella-instruments[.]com/admin/11/host16/admin/js/mj[.]php?ar=  
> hxxp://wasdpcs[.]com/secure/host7/admin/js/mj[.]php?ar=  
> hxxps://loyaukee[.]hk/secure/host7/admin/js/mj[.]php?ar=  
> hxxps://thefiirmpmcom-b7ce8f[.]ingress-erytho[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxps://michelearris[.]com/wp-content/plugins/host7/admin/js/mj[.]php?ar=  
> hxxp://thesslcgroup[.]org/host13/admin/js/mj[.]php?ar=  
> hxxps://adaexchange[.]za[.]com/ismettacusa/host10/admin/js/mj[.]php?ar=  
> hxxp://brlnet[.]in/wz/host10/admin/js/mj[.]php?ar=  
> hxxps://greenleafsolutions[.]in/vtn/host16/admin/js/mj[.]php?ar=  
> hxxps://schneiderp[.]cf/[.]well-known/0ffice/host8/admin/js/mj[.]php?ar=  
> hxxps://thesslcgroup[.]org/host13/admin/js/mj[.]php?ar=  
> hxxp://ducks[.]ajolotec[.]com/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://maxtaxpros[.]com/csc/host15/admin/js/mj[.]php?ar=  
> hxxp://whitesomcponwmc[.]com/wnclrm/andlw/admin/js/mj[.]php?ar=  
> hxxp://diamondlookup[.]sa[.]com/brick/host7/admin/js/mj[.]php?ar=  
> hxxps://mahmoodonline[.]com/j5/admin/js/mj[.]php?ar=  
> hxxps://auburnexcellbrady[.]com/O/host15/admin/js/mj[.]php?ar=  
> hxxps://lismorecountryhouse[.]com/views/host6/admin/js/mj[.]php?ar=  
> hxxps://medialabpro[.]com/oha/don/host16/admin/js/mj[.]php?ar=  
> hxxps://otcsalliance[.]sa[.]com/online/admin/js/mj[.]php?ar=  
> hxxps://mahmoodonline[.]com/sch/admin/js/mj[.]php?ar=  
> hxxps://brlnet[.]in/wz/host10/admin/js/mj[.]php?ar=  
> hxxp://tranmualitic[.]co/us/host10[.]9/admin/js/mj[.]php?ar=  
>
> hxxps://asiapacificrefinery[.]com/images/appp/admin/js/mj[.]php?ar%C2%B2ZmaWNl&b64e=KEQTKCU&b64u=pVonVfWif&conf%C3%9BZDLi&call=urPdmZI  
> hxxps://asiapacificrefinery[.]com/modules/app/admin/js/mj[.]php?ar=  
> hxxps://movie2gg[.]sa[.]com/on/line/admin/js/mj[.]php?ar=  
> hxxps://mysamaaj[.]com/new/jsn/host8/admin/js/mj[.]php?ar=  
> hxxps://parchamalzahra[.]ir/hjh/host15/admin/js/mj[.]php?ar=  
> hxxps://evomg[.]gremscd[.]pro/host16/admin/js/mj[.]php?ar=  
> hxxps://bigmancaves[.]za[.]com/abriba/host7/admin/js/mj[.]php?ar=  
> hxxp://eventbanditz[.]com/wp-> content/themes/seotheme/host7/admin/js/mj[.]php?ar=  
> hxxps://millenniumservices[.]net/wz/host7/admin/js/mj[.]php?ar=  
> hxxp://cassinaweb[.]com/wacs/host15/admin/js/mj[.]php?ar=  
> hxxps://thulasmanga[.]co[.]za/host9/admin/js/mj[.]php?ar=  
> hxxps://jameslynchltd[.]com/host9/admin/js/mj[.]php?ar=  
> hxxp://fabegallardo[.]com/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://shekeeperreal[.]com/host12[.]mod/admin/js/mj[.]php?ar=  
> hxxps://crawfordssqcom-b7ce8f[.]ingress-bonde[.]ewp[.]live/wp-> admin/host6/admin/js/mj[.]php?ar=  
> hxxps://flowlinevalve[.]com/wp-content/img/host10/admin/js/mj[.]php?ar=  
> hxxps://asiapacificrefinery[.]com/includes/rtir/admin/js/mj[.]php?ar=  
> hxxps://tykes[.]co[.]za/host10/admin/js/mj[.]php?ar=  
> hxxps://ortigueiramais[.]com[.]br/wp-> content/upgrade/host15/admin/js/mj[.]php?ar=  
> hxxp://citsolar[.]mx/wp/host12[.]mod/admin/js/mj[.]php?ar=  
> hxxps://newageagric[.]com/host/admin/js/mj[.]php?ar=  
> hxxps://thesslcgroup[.]com/host8/admin/js/mj[.]php?ar=  
> hxxps://emdghouseltd4[.]pro/host16/admin/js/mj[.]php?ar=  
> hxxp://www[.]wasdpcs[.]com/secure/host7/admin/js/mj[.]php?ar=  
> hxxps://www[.]icuberestobar[.]com/host6/admin/js/mj[.]php?ar=  
> hxxps://inelca[.]cl/wp/admin/js/mj[.]php?ar=  
> hxxps://enfoquedeportivo[.]com/zz/host7/admin/js/mj[.]php?ar=  
> hxxp://cliffordandblu[.]com/wp-> includes/SimplePie/Parse/pate/procs/admin/js/mj[.]php?ar=  
> hxxps://asiapacificrefinery[.]com/plugins/apppp/admin/js/mj[.]php?ar=  
> hxxps://jkhjk5[.]ml/ayoo/host7/admin/js/mj[.]php?ar=  
> hxxps://asiapacificrefinery[.]com/images/appp/admin/js/mj[.]php?ar=  
> hxxp://managerkinetic[.]com/host8/admin/js/mj[.]php?ar=  
> hxxp://loyaukee[.]hk/secure/host7/admin/js/mj[.]php?ar=  
> hxxp://eadikesghtalapurcareers[.]com/sckox/admin/js/mj[.]php?ar=  
> hxxps://cayeconstruction[.]com/memo/host6/admin/js/mj[.]php?ar=  
> hxxps://www[.]dfsolucoesinfo[.]com/monks/host10/admin/js/mj[.]php?ar=  
> hxxps://practical-> raman[.]20-1-155-236[.]plesk[.]page/csc/name/admin/js/mj[.]php?ar=  
> hxxp://agentsmanage[.]com/cgi/host9/admin/js/mj[.]php?ar=  
> hxxp://renesys[.]in/host/host/buns/host7/admin/js/mj[.]php?ar=  
> hxxps://mandemutworld[.]com/onlne/aa/admin/js/mj[.]php?ar=  
> hxxp://emdghouseltd4[.]pro/host16/admin/js/mj[.]php?ar=  
> hxxp://www[.]thesslcgroup[.]org/sam/admin/js/mj[.]php?ar=  
> hxxps://renesys[.]in/host/host/buns/host7/admin/js/mj[.]php?ar=  
> hxxps://loyaukee[.]hk/securehost7/admin/js/mj[.]php?ar=  
> hxxps://managerkinetic[.]com/host8/admin/js/mj[.]php?ar=  
> hxxps://bisaenak[.]fun/wp-content/upgrade/host7/admin/js/mj[.]php?ar=  
> hxxps://peoliongoal[.]live/host10/admin/js/mj[.]php?ar=  
> hxxps://dgmmotors[.]com/WZziZ/dec/host16/admin/js/mj[.]php?ar=  
> hxxps://decoraora[.]com/zz/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://www[.]rgtc[.]co[.]in/application/host/admin/js/mj[.]php?ar=  
> hxxps://10goldclub[.]com/reports/host6/host6/admin/js/mj[.]php?ar=  
> hxxps://www[.]wasdpcs[.]com/secure/host7/admin/js/mj[.]php?ar=  
> hxxps://valcaproductions[.]com/host8/admin/js/mj[.]php?ar=  
> hxxp://dfsolucoesinfo[.]com/monks/host10/admin/js/mj[.]php?ar=  
> hxxps://ducks[.]ajolotec[.]com/host10[.]9/admin/js/mj[.]php?ar=  
> hxxp://spn[.]continetalmanged[.]com/host8/admin/js/mj[.]php?ar=  
> hxxps://tranmualitic[.]co/us/host10[.]9/admin/js/mj[.]php?ar=  
> hxxp://rankkarachi[.]com/database/host10/admin/js/mj[.]php?ar=  
> hxxps://negtechnoloyg[.]com/skytecaerial/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://emilyncrawford[.]com/dorr/host9/admin/js/mj[.]php?ar=  
> hxxps://www[.]rgtc[.]co[.]in/application/host/admin/js/mj[.]php?ar  
> hxxps://phoenix-iq[.]com/host15/admin/js/mj[.]php?ar=  
> hxxps://theparrotlounge[.]com/wzxvz/host10/admin/js/mj[.]php?ar=  
> hxxps://emeeramaontinwrldecp[.]com/wsdas/admin/js/mj[.]php?ar=  
> hxxps://loudmediagroup[.]gr/H/host9/admin/js/mj[.]php?ar=  
> hxxps://samfarmhouse[.]com/ope2/host15/admin/js/mj[.]php?ar=  
> hxxp://mandemutworld[.]com/onlne/aa/admin/js/mj[.]php?ar=  
> hxxps://itejui[.]com/file/host10/admin/js/mj[.]php?ar=  
> hxxp://tqlgistics[.]com/mpact-consulting/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://wp[.]storebh[.]com[.]br/xzouri/host7/admin/js/mj[.]php?ar=  
> hxxps://mandemutworld[.]com/onlne/bb/bbb/admin/js/mj[.]php?ar=  
> hxxps://cherawfpc[.]org/wp-> includes/SimplePie/procd/acro/admin/js/mj[.]php?ar=  
> hxxps://braesidecarsales[.]co[.]zw/wp-admin/app/admin/js/mj[.]php?ar=  
> hxxps://utak[.]hargitamegye[.]ro/wp-admin/host15/admin/js/mj[.]php?ar=  
> hxxp://atarpacific[.]com/host15/admin/js/mj[.]php?ar=  
> hxxps://jioplustu[.]pro/hos15t/admin/js/mj[.]php?ar=  
> hxxps://vinyl-stars[.]com/host10[.]9/admin/js/mj[.]php?ar=  
> hxxps://makoukamkeriane[.]test4-mcacademy[.]com/wp-> includes/offce/host6/admin/js/mj[.]php?ar=  
> hxxps://activatebcarbon[.]com/circassia/host15/admin/js/mj[.]php?ar=  
> hxxps://dcs-reparationmachineacoudre[.]fr/wp-> includes/alloy/host6/admin/js/mj[.]php?ar=  
> hxxps://legalanimestore[.]com[.]br/host7/admin/js/mj[.]php?ar=  
> hxxp://mandemutworld[.]com/onlne/bb/bbb/admin/js/mj[.]php?ar=  
> hxxps://lopesfinance[.]com/bin/host6/admin/js/mj[.]php?ar=  
> hxxp://loudmediagroup[.]gr/host16/admin/js/mj[.]php?ar=  
> hxxps://mail[.]sorderatoluca[.]com/wp-> content/secure/host9/admin/js/mj[.]php?ar=  
> hxxp://activatebcarbon[.]com/circassia/host15/admin/js/mj[.]php?ar=  
> hxxps://mysamaaj[.]com/vcj/host7/admin/js/mj[.]php?ar=  
> hxxp://legalanimestore[.]com[.]br/host7/admin/js/mj[.]php?ar=  
> hxxp://dcs-reparationmachineacoudre[.]fr/wp-> includes/alloy/host6/admin/js/mj[.]php?ar=  
> hxxps://ownyourodd[.]com/host7/admin/js/mj[.]php?ar=  
> hxxps://nftmap[.]sa[.]com/host7/admin/js/mj[.]php?ar=  
> hxxps://thesslcgroup[.]org/host9/admin/js/mj[.]php?ar=  
> hxxps://cococasserfr[.]com/wp-admin/ver/host9/admin/js/mj[.]php?ar=  
> hxxps://buyandsave[.]co[.]business/wp-> admin/css/colors/sunrise/host6/admin/js/mj[.]php?ar=  
> hxxps://veceliogrogan[.]com/host8/admin/js/mj[.]php?ar=  
>
> hxxp://176[.]32[.]230[.]52/safabrications1[.]co[.]uk/mon/host9/admin/js/mj[.]php?ar=  
> hxxps://dooberlimo[.]com/11111/host15/admin/js/mj[.]php?ar=  
> hxxps://everesstgrp[.]com/host10/admin/js/mj[.]php?ar=  
> hxxps://thesslcgroup[.]org/host10/admin/js/mj[.]php?ar=  
> hxxp://samfarmhouse[.]com/ope2/host15/admin/js/mj[.]php?ar=  
> hxxps://loudmediagroup[.]gr/host16/admin/js/mj[.]php?ar=  
> hxxp://sharing-belge[.]fr/wp-admin/maint/host7/admin/js/mj[.]php?ar=  
> hxxp://thesslcgroup[.]org/host10/admin/js/mj[.]php?ar=  
> hxxps://parkvaleltd[.]com/host9/admin/js/mj[.]php?ar=  
> hxxps://rankkarachi[.]com/database/host10/admin/js/mj[.]php?ar=

## 参考来源

> [Trellix](https://www.trellix.com/en-us/about/newsroom/stories/research/the-> anatomy-of-html-attachment-phishing.html)

