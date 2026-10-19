iOS坐标系探究

[ 落影loyinglin](https://www.jianshu.com/u/815d10a4bdce)关注赞赏支持

# iOS坐标系探究

### 前言

app在渲染视图时，需要在坐标系中指定绘制区域。  
这个概念看似乎简单，事实并非如此。

> When an app draws something in iOS, it has to locate the drawn content in a
> two-dimensional space defined by a coordinate system.  
>  **This notion might seem straightforward at first glance, but it isn’t**.

### 正文

我们先从一段最简单的代码入手，在drawRect中显示一个普通的UILabel；  
为了方便判断，我把整个view的背景设置成黑色：

    
    
    - (void)drawRect:(CGRect)rect {
        [super drawRect:rect];
        CGContextRef context = UIGraphicsGetCurrentContext();
        NSLog(@"CGContext default CTM matrix %@", NSStringFromCGAffineTransform(CGContextGetCTM(context)));
        UILabel *testLabel = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, 100, 28)];
        testLabel.text = @"测试文本";
        testLabel.font = [UIFont systemFontOfSize:14];
        testLabel.textColor = [UIColor whiteColor];
        [testLabel.layer renderInContext:context];
    }
    

这段代码首先创建一个UILabel，然后设置文本，显示到屏幕上，没有修改坐标。  
所以按照UILabel.layer默认的坐标(0, 0)，在左上角进行了绘制。

  

UILabel绘制

接着，我们尝试使用CoreText来渲染一段文本。

    
    
    - (void)drawRect:(CGRect)rect {
        [super drawRect:rect];
        CGContextRef context = UIGraphicsGetCurrentContext();
        NSLog(@"CGContext default matrix %@", NSStringFromCGAffineTransform(CGContextGetCTM(context)));
        NSAttributedString *attrStr = [[NSAttributedString alloc] initWithString:@"测试文本" attributes:@{
                                                                                                      NSForegroundColorAttributeName:[UIColor whiteColor],
                                                                                                      NSFontAttributeName:[UIFont systemFontOfSize:14],
                                                                                                      }];
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString((__bridge CFAttributedStringRef) attrStr); // 根据富文本创建排版类CTFramesetterRef
        UIBezierPath * bezierPath = [UIBezierPath bezierPathWithRect:CGRectMake(0, 0, 100, 20)];
        CTFrameRef frameRef = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), bezierPath.CGPath, NULL); // 创建排版数据
        CTFrameDraw(frameRef, context);
    }
    

首先用NSString创建一个富文本，然后根据富文本创建CTFramesetterRef，结合CGRect生成的UIBezierPath，我们得到CTFrameRef，最终渲染到屏幕上。  
但是结果与上文不一致：文字是上下颠倒。

  

CoreText的文本绘制

  

从这个不同的现象开始，我们来理解iOS的坐标系。

### 坐标系概念

在iOS中绘制图形必须在一个二维的坐标系中进行，但在iOS系统中存在多个坐标系，常需要处理一些坐标系的转换。  
先介绍一个图形上下文(graphics context)的概念，比如说我们常用的CGContext就是Quartz
2D的上下文。图形上下文包含绘制所需的信息，比如颜色、线宽、字体等。用我们在Windows常用的画图来参考，当我们使用画笔🖌在白板中写字时，图形上下文就是画笔的属性设置、白板大小、画笔位置等等。

iOS中，每个图形上下文都会有三种坐标：  
1、绘制坐标系（也叫用户坐标系），我们平时绘制所用的坐标系；  
2、视图（view）坐标系，固定左上角为原点（0，0）的view坐标系；  
3、物理坐标系，物理屏幕中的坐标系，同样是固定左上角为原点；

  

根据我们绘制的目标不同（屏幕、位图、PDF等），会有多个context；

  

Quartz常见的绘制目标

不同context的绘制坐标系各不相同，比如说UIKit的坐标系为左上角原点的坐标系，CoreGraphics的坐标系为左下角为原点的坐标系；

### CoreGraphics坐标系和UIKit坐标系的转换

CoreText基于CoreGraphics，所以坐标系也是CoreGraphics的坐标系。  
我们回顾下上文提到的两个渲染结果，我们产生如下疑问：  
UIGraphicsGetCurrentContext返回的是CGContext，代表着是左下角为原点的坐标系，用UILabel（UIKit坐标系）可以直接renderInContext，并且“测”字对应为UILabel的（0，0）位置，是在左上角？  
当用CoreText渲染时，坐标是（0，0），但是渲染的结果是在左上角，并不是在左下角；并且文字是上下颠倒的。  
为了探究这个问题，我在代码中加入了一行log：  
`NSLog(@"CGContext default matrix %@",
NSStringFromCGAffineTransform(CGContextGetCTM(context)));`  
其结果是`CGContext default matrix [2, 0, 0, -2, 0, 200]`；  
CGContextGetCTM返回是CGAffineTransform仿射变换矩阵：  

  
一个二维坐标系上的点p，可以表达为(x, y, 1)，乘以变换的矩阵，如下：

  

把结果相乘，得到下面的关系

此时，我们再来看看打印的结果[2, 0, 0, -2, 0, 200]，可以化简为  
x' = 2x, y' = 200 - 2y  
因为渲染的view高度为100，所以这个坐标转换相当于把原点在左下角（0，100）的坐标系，转换为原点在左上角（0，0）的坐标系！通常我们都会使用UIKit进行渲染，所以iOS系统在drawRect返回CGContext的时候，默认帮我们进行了一次变换，以方便开发者直接用UIKit坐标系进行渲染。

我们尝试对系统添加的坐标变换进行还原：  
先进行`CGContextTranslateCTM(context, 0, self.bounds.size.height);`  
对于x' = 2x, y' = 200 - 2y，我们使得x=x,y=y+100；（self.bounds.size.height=100）  
于是有x' = 2x, y' = 200-2(y+100) = -2y;  
再进行`CGContextScaleCTM(context, 1.0, -1.0);`  
对于x' = 2x, y' = -2y，我们使得x=x, y=-y;  
于是有 x'=2x, y' = -2(-y) = 2y；

    
    
    - (void)drawRect:(CGRect)rect {
        [super drawRect:rect];
        CGContextRef context = UIGraphicsGetCurrentContext();
        CGContextTranslateCTM(context, 0, self.bounds.size.height);
        CGContextScaleCTM(context, 1.0, -1.0);
        NSLog(@"CGContext default matrix %@", NSStringFromCGAffineTransform(CGContextGetCTM(context)));
        NSAttributedString *attrStr = [[NSAttributedString alloc] initWithString:@"测试文本" attributes:@{
                                                                                                      NSForegroundColorAttributeName:[UIColor whiteColor],
                                                                                                      NSFontAttributeName:[UIFont systemFontOfSize:14],
                                                                                                      }];
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString((__bridge CFAttributedStringRef) attrStr); // 根据富文本创建排版类CTFramesetterRef
        UIBezierPath * bezierPath = [UIBezierPath bezierPathWithRect:CGRectMake(0, 0, 100, 20)];
        CTFrameRef frameRef = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), bezierPath.CGPath, NULL); // 创建排版数据
        CTFrameDraw(frameRef, context);
    }
    

通过log也可以看出来`CGContext default matrix [2, 0, -0, 2, 0, 0]；`  
最终结果如下，文本从左下角开始渲染，并且没有出现上下颠倒的情况。  

这时我们产生新的困扰：  
用CoreText渲染文字的上下颠倒现象解决，但是修改后的坐标系UIKit无法正常使用，如何兼容两种坐标系？  
iOS可以使用`CGContextSaveGState()`方法暂存context状态，然后在CoreText绘制完后通过`CGContextRestoreGState
()`可以恢复context的变换。

    
    
    - (void)drawRect:(CGRect)rect {
        [super drawRect:rect];
    
        CGContextRef context = UIGraphicsGetCurrentContext();
        NSLog(@"CGContext default matrix %@", NSStringFromCGAffineTransform(CGContextGetCTM(context)));
        CGContextSaveGState(context);
        CGContextTranslateCTM(context, 0, self.bounds.size.height);
        CGContextScaleCTM(context, 1.0, -1.0);
        NSAttributedString *attrStr = [[NSAttributedString alloc] initWithString:@"测试文本" attributes:@{
                                                                                                      NSForegroundColorAttributeName:[UIColor whiteColor],
                                                                                                      NSFontAttributeName:[UIFont systemFontOfSize:14],
                                                                                                      }];
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString((__bridge CFAttributedStringRef) attrStr); // 根据富文本创建排版类CTFramesetterRef
        UIBezierPath * bezierPath = [UIBezierPath bezierPathWithRect:CGRectMake(0, 0, 100, 20)];
        CTFrameRef frameRef = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), bezierPath.CGPath, NULL); // 创建排版数据
        CTFrameDraw(frameRef, context);
        CGContextRestoreGState(context);
        
        
        NSLog(@"CGContext default CTM matrix %@", NSStringFromCGAffineTransform(CGContextGetCTM(context)));
        UILabel *testLabel = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, 100, 20)];
        testLabel.text = @"测试文本";
        testLabel.font = [UIFont systemFontOfSize:14];
        testLabel.textColor = [UIColor whiteColor];
        [testLabel.layer renderInContext:context];
    }
    

渲染结果如下，控制台输出的两个matrix都是`[2, 0, 0, -2, 0, 200]`；  

### 遇到的问题

#### 1、UILabel.layer在renderInContext的时候frame失效

初始化UILabel时设定了frame，但是没有生效。  
`UILabel *testLabel = [[UILabel alloc] initWithFrame:CGRectMake(20, 20, 100,
28)];`  
这是因为frame是在上一层view中坐标的偏移，在renderInContext中坐标起点与frame无关，所以需要修改的是bounds属性：  
`testLabel.layer.bounds = CGRectMake(50, 50, 100, 28);`

#### 2、renderInContext和drawInContext的选择

在把UILabel.layer渲染到context的时候，应该采用drawInContext还是renderInContext？

虽然这两个方法都可以生效，但是根据画线部分的内容来判断，还是采用了renderInContext，并且问题1就是由这里的一句`Renders in the
coordinate space of the layer`，定位到问题所在。

#### 3、如何理解CoreGraphics坐标系不一致后，会出现绘制结果异常？

我的理解方法是，我们可以先不考虑坐标系变换的情况。  
如下图，上半部分是普通的渲染结果，可以很容易的想象；  
接下来是增加坐标变换后，坐标系变成原点在左上角的顶点，相当于按照下图的虚线进行了一次垂直的翻转。

也可以按照坐标系变换的方式去理解，将左下角原点的坐标系相对y轴做一次垂直翻转，然后向上平移height的高度，这样得到左上角原点的坐标系。

### 附录

[Drawing and Printing Guide for
iOS](https://developer.apple.com/library/archive/documentation/2DDrawing/Conceptual/DrawingPrintingiOS/GraphicsDrawingOverview/GraphicsDrawingOverview.html)  
[Quartz 2D Programming
Guide](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/drawingwithquartz2d/dq_overview/dq_overview.html)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Core Graphics 学习 (一) 坐标系,Path,简单路径绘制](https://www.jianshu.com/p/25b4dffca675)

Core Graphics 也叫 Quartz 2D, 是 iOS,TVOS,macOS应用开发中先进的二维绘制引...

[toro宇](https://www.jianshu.com/u/dae3c1571f2e)阅读 1,774评论 0赞 1

  * [【IOS开发进阶系列】动画专题](https://www.jianshu.com/p/717fcb542aa2)

1 CALayer IOS SDK详解之CALayer（一） http://doc.okbase.net/Hell...

[Kevin_Junbaozi](https://www.jianshu.com/u/dfae73bde753)阅读 4,621评论 3赞 23

  * [iOS开发系列--打造自己的“美图秀秀”](https://www.jianshu.com/p/dbfabcc1b261)

\--绘图与滤镜全面解析 概述 在iOS中可以很容易的开发出绚丽的界面效果，一方面得益于成功系统的设计，另一方面得益...

[韩七夏](https://www.jianshu.com/u/8c113f14f2e3)阅读 2,514评论 2赞 10

  * [iOS绘图和打印编程指导(二)-关于iOS绘图的一些概念](https://www.jianshu.com/p/98fc279130fe)

高质量的图形是用户界面的关键部分. 提供良好的图形不仅使你的APP看起来漂亮, 而且让你的APP看起来就是iOS系...

[陵无山](https://www.jianshu.com/u/8ebc1c60d171)阅读 915评论 0赞 0

  * [iOS-Core-Animation之六----专用图层](https://www.jianshu.com/p/fe1eeb12bbf3)

>复杂的组织都是专门化的 >Catharine R. Stimpson 到目前为止，我们已经探讨过`CALayer...

[夜空下最亮的亮点](https://www.jianshu.com/u/1c148336322c)阅读 814评论 0赞 2

 