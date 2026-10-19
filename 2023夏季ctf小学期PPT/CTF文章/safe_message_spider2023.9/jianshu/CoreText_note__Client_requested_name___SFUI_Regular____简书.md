CoreText note: Client requested name".SFUI-Regular"

[Sweet丶](https://www.jianshu.com/u/0dbbbbc2a943)关注赞赏支持

# CoreText note: Client requested name ".SFUI-Regular"

打印台出打印信息：  
`CoreText note: Client requested name ".SFUI-Regular", it will get
TimesNewRomanPSMT rather than the intended font. All system UI font access
should be through proper APIs such as CTFontCreateUIFontForLanguage() or
+[UIFont systemFontOfSize:].`  
`CoreText note: Set a breakpoint on CTFontLogSystemFontNameRequest to debug.`

问题的解决方法：

  

添加符号断点.png

CTFontLogSystemFontNameRequest符号断点.png

添加号符号断点看哪个地方使用了`".SFUI-Regular"`，改掉就好了。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CoreText note: Client requested name".SFUI-Reg...](https://www.jianshu.com/p/e401a6c5eca0)

控制台打印报错： 处理方式： 全局搜索 CTFontCreateWithName，fontName 由".SFUI...

[汗青fullstack](https://www.jianshu.com/u/927e90be6e26)阅读 5,891评论 1赞 2

  * [iOS 添加第三方字体库](https://www.jianshu.com/p/1dc16ac18d16)

资源: ( 注意: 请不要修改下载的字体库名称, 修改了可能不好用, 我也不知道原因, 如果你知道原因, 请告诉我...

[哈哈秦](https://www.jianshu.com/u/15f63c04f179)阅读 1,456评论 4赞 2

  * [iOS 13 CoreText performance note 问题适配](https://www.jianshu.com/p/877d5fc2a0f2)

原因应该是Apple为了提升性能升级了底层的字体，导致以前的字体不匹配，所以要成功调用对应的Api,需要按照上诉日...

[流年划过颜夕](https://www.jianshu.com/u/ba3fcd2509d7)阅读 2,244评论 0赞 3

  * [iOS-CoreAnimation提供的不同功能的CAlayer](https://www.jianshu.com/p/95957d931d94)

一、CAShapelayer 我们知道可以不使用图片情况下利用CGpath去构建任意形状的阴影。其实我们也可...

[小猫仔](https://www.jianshu.com/u/56ada7bab1bc)阅读 1,202评论 0赞 4

  * [CoreText简单设置](https://www.jianshu.com/p/55cf31dea156)

UILabel * textLabel = [[UILabel alloc]initWithFrame:CGRec...

[零度远](https://www.jianshu.com/u/6600a9f17873)阅读 543评论 0赞 0

 