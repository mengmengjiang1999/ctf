iOS 之 异步绘制原理

[ 枫叶无处漂泊](https://www.jianshu.com/u/228807de778b)关注赞赏支持

# iOS 之 异步绘制原理

### 一、异步绘制产生背景

  * UIView 中有一个 CALayer 的属性，负责 UIView 具体内容的显示。

  * 具体过程是系统会把 UIView 显示的内容（包括 UILabel 的文字，UIImageView 的图片等）绘制在一张画布上，完成后倒出图片赋值给 CALayer 的 contents 属性，完成显示。

这其中的工作都是在主线程中完成的，这就导致了主线程频繁的处理 UI 绘制的工作，如果要绘制的元素过多，过于频繁，就会造成卡顿。

解决方案使用异步绘制就是：

  * 把UIView 显示的内容（包括 UILabel 的文字，UIImageView 的图片等）绘制生成的bitmap在子线程完成。

  * 然后在回到主线程把bitmap赋值给view.layer.content属性。

### 二、异步绘制流程

那么是否可以将复杂的绘制过程放到后台线程中执行，从而减轻主线程负担，来提升UI流畅度呢？

可以的，系统给我们留下的异步绘制的口子，请看下面的流程图，它是我们进行基本绘制的基础:

异步绘制流程图.png

  1. 首先 UIView 调用 setNeedsDisplay 方法

  2. 其实是调用其 layer 属性的同名方法（view.layer setNeedsDisplay）

  3. 这时 layer 并不会立刻调用 display 方法,而是要等到当前 runloop 即将结束的时候调用 display，进入到绘制流程。

  4. 在 UIView 中 layer.delegate 就是 UIView 本身，UIView 并没有实现 displayLayer: 方法，所以进入系统的绘制流程，我们可以通过实现 displayLayer: 方法来进行异步绘制。

> 所以去实现displayLayer方式，实现开启异步绘制入口，

> 在“异步绘制入口”去开辟子线程，然后在子线程中实现和系统类似的绘制流程。

### 三、系统绘制流程

先从下面的系统绘制流程图来了解一下系统绘制流程：

  

系统绘制流程.png

  * 首先 CALayer 会在内部创建 一个上下文环境(CGContextRef)

  * 然后判断 layer 是否有代理：

    * 没有代理的话，就调用 layer 的 drawInContext: 方法

    * 有代理的话，调用 delegate 的drawLayer : inContext 方法，这个方法实现是系统完成。

    * 然后在合适的时机回调代理，调用drawRect默认操作是什么都不做（而之所以有这个接口,就是为了让我们在系统绘制之后,还可以做些自定义的绘制工作）。

  * 最后无论是哪个分支都把 backing store(上下文环境) 的 bitmap 位图提交到 GPU，

  * 也就是将生成的 bitmap 位图赋值给 layer.content 属性。

下面看一下异步绘制的时序图能更好的理解异步绘制流程：

异步绘制时序图.png

  * 首先在主线程调用setNeedsdispay方法

  * 系统会在runloop将要结束的时候调用[CAlayer display]方法

  * 如果我们的代理实现了dispayLayer这个方法，会调用dispayLayer这个方法。我们可以去子线程里面进行异步绘制。子线程主要做的工作：

    * 创建上下文
    * UI控件的绘制工作
    * 生成对应的图片（bitmap）
  * 主线程可以做其他工作

  * 异步绘制完事之后，回到主线程，把绘制的bitmap赋值view.layer.contents属性中

### 四、面试考点

#### 一、我们调用[UIView setNeedsDisplay]方法的时候，不会立马发送对应视图的绘制工作，为什么？

  * 调用[UIView setNeedsDisplay]后，

  * 然后会调用系统的同名方法[view.layer setNeedsDisplay]方法并在当前view上面打上一个脏标记

  * 当前Runloop将要结束的时候才会调用[CALyer display]方法，然后进入到视图真正的绘制工作当中。

#### 二、是否知道异步绘制？如何进行异步绘制？

  * 基于系统开的口子[layer.delegate dispayLayer:]方法。
  * 并且实现/遵从了dispayLayer这个方法，我们就可以进行异步绘制：  
1）代理负责生产对应的bitmap  
2）设置bitmap作为layer.contents属性的值

### 五、异步绘代码：

    
    
    #import <UIKit/UIKit.h>
    
    NS_ASSUME_NONNULL_BEGIN
    
    @interface AsyncDrawLabel : UIView
    
    @property (nonatomic, copy) NSString *text;
    @property (nonatomic, strong) UIFont *font;
    
    @end
    
    NS_ASSUME_NONNULL_END
    
    
    
    #import "AsyncDrawLabel.h"
    #import <CoreText/CoreText.h>
    
    @implementation AsyncDrawLabel
    
    - (void)setText:(NSString *)text {
        _text = text;
    }
    
    - (void)setFont:(UIFont *)font {
        _font = font;
    }
    
    
    // 除了在drawRect方法中, 其他地方获取context需要自己创建[https://www.jianshu.com/p/86f025f06d62] coreText用法简介:[https://www.cnblogs.com/purple-sweet-pottoes/p/5109413.html]
     
    - (void)displayLayer:(CALayer *)layer {
        CGSize size = self.bounds.size;
        CGFloat scale = [UIScreen mainScreen].scale;
        // 异步绘制，切换至子线程
        dispatch_async(dispatch_get_global_queue(0, 0), ^{
            UIGraphicsBeginImageContextWithOptions(size, NO, scale);
            // 获取当前上下文
            CGContextRef context = UIGraphicsGetCurrentContext();
            [self draw:context size:size];
            UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
            UIGraphicsEndImageContext();
            // 子线程完成工作，切换至主线程显示
            dispatch_async(dispatch_get_main_queue(), ^{
                self.layer.contents = (__bridge id)image.CGImage;
            });
        });
    }
    
    - (void)draw:(CGContextRef)context size:(CGSize)size {
        // 将坐标系上下翻转，因为底层坐标系和 UIKit 坐标系原点位置不同。
        CGContextSetTextMatrix(context, CGAffineTransformIdentity);
        // 文本沿着Y轴移动
        CGContextTranslateCTM(context, 0, size.height); // 原点为左下角
        // 文本反转成context坐标系
        CGContextScaleCTM(context, 1, -1);
        // 创建绘制区域
        CGMutablePathRef path = CGPathCreateMutable();
        CGPathAddRect(path, NULL, CGRectMake(0, 0, size.width, size.height));
        // 创建需要绘制的文字
        NSMutableAttributedString *attrStr = [[NSMutableAttributedString alloc]initWithString:self.text];
        [attrStr addAttribute:NSFontAttributeName value:self.font range:NSMakeRange(0, self.text.length)];
        // 根据attStr生成CTFramesetterRef
        CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)attrStr);
        CTFrameRef frame = CTFramesetterCreateFrame(framesetter, CFRangeMake(0, attrStr.length), path, NULL);
        // 将frame的内容绘制到content中
        CTFrameDraw(frame, context);
    }
    

简单的调用：

    
    
    #import "ViewController.h"
    #import "AsyncDrawLabel.h"
    
    @interface ViewController ()
    
    @end
    
    @implementation ViewController
    
    - (void)viewDidLoad {
        [super viewDidLoad];
        // Do any additional setup after loading the view.
        
        AsyncDrawLabel *label = [[AsyncDrawLabel alloc] initWithFrame:CGRectMake(100, 100, 200, 100)];
        label.backgroundColor = [UIColor yellowColor];
        label.text = @"异步绘制text";
        label.font = [UIFont systemFontOfSize:16];
        [self.view addSubview:label];
        [label.layer setNeedsDisplay]; // 不调用的话不会触发displayLayer方法
    }
    
    @end
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [2021-iOS面试整理](https://www.jianshu.com/p/634771ada547)

类 分类的作用？ 声明私有方法，分解体积。分类的特点？ 运行时决议，可以为系统类添加分类分类可以添加哪些内容？分类...

[Alex1989](https://www.jianshu.com/u/96f1ee75f34e)阅读 1,980评论 0赞 26

  * [iOS 面试宝典 没有比这更全的了（持续更新）](https://www.jianshu.com/p/3b7f3f596bcb)

1.ios高性能编程 (1).内层 最小的内层平均值和峰值(2).耗电量 高效的算法和数据结构(3).初始化时...

[欧辰_OSR](https://www.jianshu.com/u/f2a07930242f)阅读 28,206评论 8赞 265

  * [面试题](https://www.jianshu.com/p/971865470673)

Swift1> Swift和OC的区别1.1> Swift没有地址/指针的概念1.2> 泛型1.3> 类型严谨 对...

[cosWriter](https://www.jianshu.com/u/8626d3f52ac7)阅读 10,701评论 1赞 32

  * [CALayer](https://www.jianshu.com/p/9df31d11e242)

CALayer通过四个属性来确定大小和位置, 分别为:frame、bounds、position、anchorPo...

[一川烟草i蓑衣](https://www.jianshu.com/u/31daa01d783c)阅读 273评论 0赞 1

  * [CALayery以及图像的显示](https://www.jianshu.com/p/a6bc5b7e0142)

UIView和CALayer之间的关系 UIView绘制原理 图像显示原理UI卡顿、掉帧的原因解决方案 离屏渲染何...

[Mark_Guan](https://www.jianshu.com/u/68bedf0c5c86)阅读 1,218评论 0赞 9

 