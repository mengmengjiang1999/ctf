iOS 给UILabel添加点击事件

[ QiShare](https://www.jianshu.com/u/3db23baa08c7)关注赞赏支持

# iOS 给UILabel添加点击事件

> 级别：★☆☆☆☆  
>  标签：「UILabel」「TTTAttributedLabel 基本使用」「TTTAttributedLabel 实现」  
>  作者： [WYW](https://www.jianshu.com/u/2f31928b08bf)  
>  审校： [QiShare团队](https://www.jianshu.com/c/b3bd94559163)

* * *

> 前言：笔者最近需要实现给 UILabel 中的链接添加点击事件的功能。使用
> [so.com](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.so.com) 查了下，发现
> [TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)
> 的封装程度比较好。整理了
> [TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)
> 的基本使用，及部分实现。

### TTTAttributedLabel 的基本使用

#### 把 `TTTAttributedLabel.h` 及 `TTTAttributedLabel.m` 放到项目中

#### 遵守 `TTTAttributedLabelDelegate` 协议

    
    
    // 遵守TTTAttributedLabelDelegate协议
    @interface ViewController () <TTTAttributedLabelDelegate>
    

#### 创建 TTTAttributedLabel 实例及相应配置

创建 TTTAttributedLabel 实例，添加相应配置。

    
    
    - (void)setupTTTAttributedLabel {
        
        TTTAttributedLabel *attriLabel = [[TTTAttributedLabel alloc] initWithFrame:CGRectZero];
        attriLabel.font = [UIFont systemFontOfSize:32.0];
        attriLabel.numberOfLines = 0;
        // Automatically detect links when the label text is subsequently changed
        attriLabel.enabledTextCheckingTypes = NSTextCheckingTypeLink;
        // Delegate methods are called when the user taps on a link (see `TTTAttributedLabelDelegate` protocol)
        attriLabel.delegate = self;
        // Repository URL will be automatically detected and linked
        attriLabel.text = @"Fork me on GitHub! (https://github.com/mattt/TTTAttributedLabel/)";
        NSRange range = [attriLabel.text rangeOfString:@"me"];
        // Embedding a custom link in a substring
        [attriLabel addLinkToURL:[NSURL URLWithString:@"http://github.com/mattt/"] withRange:range];
        [self.view addSubview:attriLabel];
        attriLabel.frame = CGRectMake(20.0, 100.0, 300.0, 200.0);
    }
    

#### 实现TTTAttributedLabelDelegate 代理方法

在如下代理方法中查看当前点击的链接。

    
    
    //! 实现代理方法
    - (void)attributedLabel:(TTTAttributedLabel *)label didSelectLinkWithURL:(NSURL *)url {
        
        NSLog(@"url信息：%@", url);
    }
    

### TTTAttributedLabel 部分实现

设置 `attriLabel.text = @"Fork me on GitHub!
(https://github.com/mattt/TTTAttributedLabel/)";` 查看了 TTTAttributedLabel
的大概实现流程。

#### 设置 TTTAttributedLabel 用户交互可用。

    
    
    self.userInteractionEnabled = YES;
    

#### TTTAttributedLabel 链接指定了默认链接样式

TTTAttributedLabel 为链接指定了默认链接样式为蓝色和带下划线。

相关代码为：

    
    
    NSMutableDictionary *mutableLinkAttributes = [NSMutableDictionary dictionary];
    [mutableLinkAttributes setObject:[NSNumber numberWithBool:YES] forKey:(NSString *)kCTUnderlineStyleAttributeName];
    if ([NSMutableParagraphStyle class]) {
        [mutableLinkAttributes setObject:[UIColor blueColor] forKey:(NSString *)kCTForegroundColorAttributeName];
    } else {
        [mutableLinkAttributes setObject:(__bridge id)[[UIColor blueColor] CGColor] forKey:(NSString *)kCTForegroundColorAttributeName];
    }
    self.linkAttributes = [NSDictionary dictionaryWithDictionary:mutableLinkAttributes];
    

#### 使用 `NSDataDetector` 检测 `label.text` 中的链接

    
    
    NSArray *results = [dataDetector matchesInString:[(NSAttributedString *)text string] options:0 range:NSMakeRange(0, [(NSAttributedString *)text length])];
    

`NSArray<NSTextCheckingResult *> *` 类型的 `results` 数组中会有 `label` 中文本的链接信息。

如

    
    
    <__NSArrayM 0x2830a6310>(
    <NSLinkCheckingResult: 0x283ed27c0>{20, 44}{https://github.com/mattt/TTTAttributedLabel/}
    )
    
    
    
    // label.text中的URL
    (lldb) po ((NSLinkCheckingResult *)[results lastObject]).URL
    https://github.com/mattt/TTTAttributedLabel/
    
    
    
    // label.text中的URL 的range
    (lldb) po ((NSLinkCheckingResult *)[results lastObject]).range
    location=20, length=44
    

#### "自动检测"链接

当我们设置了 `attriLabel.text = @"Fork me on GitHub!
(https://github.com/mattt/TTTAttributedLabel/)";`
时，会发现`https://github.com/mattt/TTTAttributedLabel/` 自动变为链接形式。自动检测出
`label.text` 中的文本中有 `url` 信息是依次在 `- (NSArray
*)addLinksWithTextCheckingResults:(NSArray *)results attributes:(NSDictionary
*)attributes` 及 `- (void)addLinks:(NSArray *)links` 的实现中做的处理。

  * 首先通过在`- (NSArray *)addLinksWithTextCheckingResults:(NSArray *)results attributes:(NSDictionary *)attributes` 方法中封装链接文本属性信息媒介 `TTTAttributedLabelLink` 。

  * 再通过在`- (void)addLinks:(NSArray *)links` 方法中根据 `TTTAttributedLabelLink` 传递过来的文本属性及url 位置信息，设置 `label.attributedText` 以达到能够自动检测出 `label.text` 中的 `url` 的目的。

另外我们自行添加addLinkToURl

    
    
    - (void)addLinks:(NSArray *)links {
        ...
        self.attributedText = mutableAttributedString;
        ...
    }
    

#### 添加链接到指定 `range`

以 `[attriLabel addLinkToURL:[NSURL URLWithString:@"http://github.com/mattt/"]
withRange:range];` 为例。可以发现 TTTAttributedLabel 内部实现是

`[self addLinkWithTextCheckingResult:[NSTextCheckingResult
linkCheckingResultWithRange:range URL:url]];` 直到

`[self addLinkWithTextCheckingResult:result attributes:self.linkAttributes];`
就和上述的“自动检测”链接的内容是一样的。

#### 点击Label 的链接文字后，查找到对应 `url`

这部分内容主要分为 `touchesBegan` 方法中查找点击的位置的链接， `touchesMoved` 方法中比对触摸到Label
上的位置变动后，当前位置的链接和 `touchesBegan` 方法中找到的链接是否还一样，最后在 `touchesEnded`
中把点击的链接以为block 和 代理的方式传递出去。

下边简单说明下笔者查看touchesBegan方法中查找点击链接的内容。

  * 获取到当前点击的点

    
    
    [touch locationInView:self]
    

  * 在 `- (TTTAttributedLabelLink *)linkAtPoint:(CGPoint)point` 方法中获取到当前点链接 
    * 首先在 `- (CFIndex)characterIndexAtPoint:(CGPoint)p` 方法中找到点击的位置的字符的索引
    * 然后通过 `- (TTTAttributedLabelLink *)linkAtCharacterIndex:(CFIndex)idx` 方法中找到对应字符的索引的TTTAttributedLabelLink实例（其中包含当前点击点的链接信息）

相应代码，详情见
[TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)

    
    
    [self linkAtPoint:[touch locationInView:self]];
    TTTAttributedLabelLink *result = [self linkAtCharacterIndex:[self characterIndexAtPoint:point]];
    

#### 获取到当前点击位置的字符的索引

笔者感觉其中难理解的地方为获取到当前点击位置的字符的索引。相关内容如下：

把当前点的坐标转换为对应 UILabel 中的文字坐标转换为针对于UILabel 自身坐标系的点坐标；

    
    
    p = CGPointMake(p.x - textRect.origin.x, p.y - textRect.origin.y);
    

另一个是把iOS 做左上角为原点坐标转换为CT 坐标系的左下角为原点坐标的调整。

    
    
    p = CGPointMake(p.x, textRect.size.height - p.y);
    

  * 根据当前label相对自身坐标系 frame 及 属性字符串 创建CT坐标系所需的frame

    
    
        CGMutablePathRef path = CGPathCreateMutable();
        CGPathAddRect(path, NULL, textRect);
        CTFrameRef frame = CTFramesetterCreateFrame([self framesetter], CFRangeMake(0, (CFIndex)[self.attributedText length]), path, NULL);
    

  * 确定UILabel 当前在CT 坐标系显示占用的行数 `CFArrayGetCount(lines)`

    
    
    NSInteger numberOfLines = self.numberOfLines > 0 ? MIN(self.numberOfLines, CFArrayGetCount(lines)) : CFArrayGetCount(lines);
    

  * 遍历CT 坐标中文字的每一行，找到当前点击点所在的行，计算出点击点相对于当前行的坐标，并计算出当前索引。

    
    
    CGPoint relativePoint = CGPointMake(p.x - lineOrigin.x, p.y - lineOrigin.y);
    idx = CTLineGetStringIndexForPosition(line, relativePoint);
    

其中还有ascent（字形最高点到baseline的推荐距离） 和descent（字形最低点到baseline的推荐距离）
相关的内容等。笔者不了解，有兴趣的话，可以查看CoreText相关内容，如[深入理解Core
Text排版引擎](https://www.jianshu.com/p/6ed98368ceed)

    
    
        CFIndex idx = NSNotFound;   
    
        CGPoint lineOrigins[numberOfLines];
        CTFrameGetLineOrigins(frame, CFRangeMake(0, numberOfLines), lineOrigins);
    
        for (CFIndex lineIndex = 0; lineIndex < numberOfLines; lineIndex++) {
            CGPoint lineOrigin = lineOrigins[lineIndex];
            CTLineRef line = CFArrayGetValueAtIndex(lines, lineIndex);
    
            // Get bounding information of line
            CGFloat ascent = 0.0f, descent = 0.0f, leading = 0.0f;
            CGFloat width = (CGFloat)CTLineGetTypographicBounds(line, &ascent, &descent, &leading);
            CGFloat yMin = (CGFloat)floor(lineOrigin.y - descent);
            CGFloat yMax = (CGFloat)ceil(lineOrigin.y + ascent);
    
            // Apply penOffset using flushFactor for horizontal alignment to set lineOrigin since this is the horizontal offset from drawFramesetter
            CGFloat flushFactor = TTTFlushFactorForTextAlignment(self.textAlignment);
            CGFloat penOffset = (CGFloat)CTLineGetPenOffsetForFlush(line, flushFactor, textRect.size.width);
            lineOrigin.x = penOffset;
    
            // Check if we've already passed the line
            if (p.y > yMax) {
                break;
            }
            // Check if the point is within this line vertically
            if (p.y >= yMin) {
                // Check if the point is within this line horizontally
                if (p.x >= lineOrigin.x && p.x <= lineOrigin.x + width) {
                    // Convert CT coordinates to line-relative coordinates
                    CGPoint relativePoint = CGPointMake(p.x - lineOrigin.x, p.y - lineOrigin.y);
                    idx = CTLineGetStringIndexForPosition(line, relativePoint);
                    break;
                }
            }
        }
    

本文说明了[TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)
的基本使用及部分实现。有兴趣的读者请下载[TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)
查看详情。

### 参考学习网址

  * [TTTAttributedLabel](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FTTTAttributedLabel%2FTTTAttributedLabel)
  * [深入理解Core Text排版引擎](https://www.jianshu.com/p/6ed98368ceed)

* * *

> 推荐文章：  
>  [用SwiftUI给视图添加动画](https://www.jianshu.com/p/f4dc970e5a96)  
>  [用SwiftUI写一个简单页面](https://www.jianshu.com/p/a89d09f86cce)  
>  [iOS 控制日志的开关](https://www.jianshu.com/p/b45fdbf99ac2)  
>  [iOS App中可拆卸一个framework的两种方式](https://www.jianshu.com/p/d6c288d12769)  
>  [自定义WKWebView显示内容（一）](https://www.jianshu.com/p/2bbbb45f856e)  
>  [Swift 5.1 (7) - 闭包](https://www.jianshu.com/p/cf8329da2c44)  
>  [Swift 5.1 (6) - 函数](https://www.jianshu.com/p/bb341ca89aad)  
>  [Swift 5.1 (5) - 控制流](https://www.jianshu.com/p/f74545af8414)  
>  [Xcode11 新建工程中的SceneDelegate](https://www.jianshu.com/p/6d6573fbd60b)  
>  [iOS App启动优化（二）—— 使用“Time
> Profiler”工具监控App的启动耗时](https://www.jianshu.com/p/526b9308e741)  
>  [iOS App启动优化（一）—— 了解App的启动流程](https://www.jianshu.com/p/024b3d847fe0)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS开发系列--网络开发](https://www.jianshu.com/p/2ae3d4892dda)

iOS开发系列--网络开发 概览 大部分应用程序都或多或少会牵扯到网络开发，例如说新浪微博、微信等，这些应用本身可...

[lichengjin](https://www.jianshu.com/u/18732638cbb2)阅读 3,334评论 2赞 7

  * [Some Aspects of Comprehension of Daily Scrum](https://www.jianshu.com/p/3c868d9271ca)

Scrum Scrum is a framework for developing and sustaining ...

[寒十四](https://www.jianshu.com/u/76b3035d22db)阅读 155评论 0赞 0

  * [爱吃洋葱头的老妇](https://www.jianshu.com/p/b06fb7f9eccb)

有一位老妇，她特别喜爱吃洋葱头。她长着一只像洋葱头的鼻子，当她嘴馋的时候，又恰好家里的洋葱头断顿，她会摸着鼻子说：...

[楚莲若](https://www.jianshu.com/u/df85d15de98c)阅读 336评论 2赞 6

  * [基本使用](https://www.jianshu.com/p/4b5adeaa7e83)

本文参考：https://morvanzhou.github.io/tutorials/machine-learn...

[小董不太懂](https://www.jianshu.com/u/7352fcd21b7e)阅读 346评论 0赞 2

  * [柜子里的猫](https://www.jianshu.com/p/8d7449024f89)

王青在回家的路上捡了一只猫，脏兮兮的，浑身都是泥。对于他为什么要捡它回家，他解释为爱心泛滥，不忍心看着它淋着雨。 ...

[我是小阿旭吖](https://www.jianshu.com/u/c1eaa97254e8)阅读 315评论 0赞 0

 