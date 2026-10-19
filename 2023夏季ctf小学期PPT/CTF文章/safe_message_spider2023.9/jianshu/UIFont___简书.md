UIFont

[ 大刘](https://www.jianshu.com/u/148b1cad85ce)关注赞赏支持

# UIFont

Created by 大刘
[liuxing8807@126.com](https://links.jianshu.com/go?to=mailto%3Aliuxing8807%40126.com)

关于字体的设计，可参见：
[Apple](https://links.jianshu.com/go?to=https%3A%2F%2Fdeveloper.apple.com%2Flibrary%2Farchive%2Fdocumentation%2FStringsTextFonts%2FConceptual%2FTextAndWebiPhoneOS%2FIntroduction%2FIntroduction.html%23%2F%2Fapple_ref%2Fdoc%2Fuid%2FTP40009542)

font_1.png

font.familyName和font.fontName是字体家族和字体名字

    
    
    UIFont *font = [UIFont fontWithName:@"Courier-Bold" size:18];
    NSLog(@"%@", font.familyName); // 字体家族：Courier
    NSLog(@"%@", font.fontName);   // 字体名字：Courier-Bold
    

**systemFontSize**

    
    
    NSLog(@"system fontSize: %f", UIFont.systemFontSize); // 14, 系统字体默认大小
    

**pointSize**

pointSize: The receiver’s point size, or the effective vertical point size for
a font with a nonstandard matrix.  
字体的pointSize可以理解成在竖直方向字体所占的点个距离，比如字体大小是80，则Label的高度为80在竖直方向上是可以容纳下这个字体的。  
这个pointSize其实也就是在创建字体时指定的fontSize, 比如：

    
    
    UIFont *font = [UIFont systemFontOfSize:30];
    NSLog(@"pointSize: %f", font.pointSize); // 30
    

**其他**

结合上面图示了解其他常见属性意义

    
    
    // ==== pointSize ====
    // The receiver’s point size, or the effective vertical point size for a font with a nonstandard matrix.
    UIFont *font = [UIFont systemFontOfSize:30];
    // 释义：The receiver’s point size, or the effective vertical point size for a font with a nonstandard matrix.
    NSLog(@"pointSize: %lf", font.pointSize); // 30
    // 释义：The top y-coordinate, offset from the baseline, of the receiver’s longest ascender.
    NSLog(@"ascent: %lf", font.ascender); // 28.564453
    // 释义：The bottom y-coordinate, offset from the baseline, of the receiver’s longest descender.
    NSLog(@"descent: %lf", font.descender); // -7.236328
    // 释义：The receiver’s leading information.
    NSLog(@"leading: %lf", font.leading); // 0
    // 释义：The receiver’s cap height information.
    NSLog(@"capHeight: %lf", font.capHeight); // capHeight: 21.137695
    // 释义：The x-height of the receiver.
    NSLog(@"xHeight: %lf", font.xHeight); // xHeight: 15.234375
    // 释义：The height of text lines (measured in points).
    NSLog(@"lineHeight: %lf", font.lineHeight); // 35.800781
    

### 使用非系统字体

  1. 把字体导入XCode
  2. 在Plist中添加对应的字体

### UIFont扩展

在项目中常常由设计师指定字体，可以加入扩展方便调用，比如：

    
    
    NS_ASSUME_NONNULL_BEGIN
    
    @interface UIFont (DaLiu)
    
    /// For [UIFont fontWithName:@"PingFangSC-Regular" size:size]
    /// Syntactic sugar of code: [UIFont fontWithName:@"PingFangSC-Regular" size:size]
    /// example: UIFont.pingFangSC(11)
    /// call UIFont.pingFangSC_Regular inner
    @property (nonatomic, class, readonly) UIFont* (^pingFangSC)(CGFloat size);
    
    /// For [UIFont fontWithName:@"PingFangSC-Regular" size:size]
    @property (nonatomic, class, readonly) UIFont* (^pingFangSC_Regular)(CGFloat size);
    
    /// For [UIFont fontWithName:@"PingFangSC-Medium" size:size];
    @property (nonatomic, class, readonly) UIFont* (^pingFangSC_Medium)(CGFloat size);
    
    @end
    
    NS_ASSUME_NONNULL_END
    
    
    
    #import "UIFont+DaLiu.h"
    
    @implementation UIFont (DaLiu)
    
    + (UIFont * _Nonnull (^)(CGFloat))pingFangSC {
        return [self pingFangSC_Regular];
    }
    
    + (UIFont * _Nonnull (^)(CGFloat))pingFangSC_Regular {
        return ^UIFont *(CGFloat size) {
            return [UIFont fontWithName:@"PingFangSC-Regular" size:size];
        };
    }
    
    + (UIFont * _Nonnull (^)(CGFloat))pingFangSC_Medium {
        return ^UIFont *(CGFloat size) {
            return [UIFont fontWithName:@"PingFangSC-Medium" size:size];
        };
    }
    
    @end
    

使用时调用`UIFont.pingFangSC(15)`即可

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS开发中通过UIFont设置不同的字体和字重](https://www.jianshu.com/p/be8518b587c8)

最近在开发一个引导页面，而现在UI图是使用蓝湖蓝湖进行标注的，如下图： 图中的1和3是不同字体不同字重的，而我...

[小蜜蜂Bee](https://www.jianshu.com/u/63a43b4286de)阅读 9,976评论 0赞 6

  * [UIFont学习](https://www.jianshu.com/p/00ce41cd4ecb)

关于字体有两种描述方式，一种是UIFont或者CTFont（在IOS7之后两者可直接进行桥接），另外一个方式使用U...

[高思阳](https://www.jianshu.com/u/3079f3eb0fd8)阅读 2,548评论 0赞 1

  * [【转】UIFont的lineHeight与pointSize](https://www.jianshu.com/p/7655620a93e0)

转载自：https://blog.csdn.net/chenyong05314/article/details/7...

[棒棒德](https://www.jianshu.com/u/2a2f1e3269a9)阅读 607评论 0赞 0

  * [玩转swift -- UIKit 之 UIFont](https://www.jianshu.com/p/2dd3e144d759)

一、简介 UIFont类提供了用于获取和设置字体信息的接口。类提供了访问字体的特点，还提供了访问，这是在布局过程中...

[王隆帅](https://www.jianshu.com/u/1a9cd48c3cf0)阅读 7,040评论 0赞 14

  * [UIFont](https://www.jianshu.com/p/2b1c26bd672c)

UIFont的主要属性列表 属性名/类型 获得字体的family名称例:NSString *str = font....

[以太死多](https://www.jianshu.com/u/2fe4ea7f58ac)阅读 4,153评论 0赞 3

 