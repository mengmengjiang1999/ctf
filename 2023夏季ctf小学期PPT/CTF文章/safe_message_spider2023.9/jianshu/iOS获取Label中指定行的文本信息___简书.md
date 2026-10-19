iOS获取Label中指定行的文本信息

[ 芮淼一线](https://www.jianshu.com/u/321ee974f45c)关注赞赏支持

# iOS获取Label中指定行的文本信息

iOS 获取一串字符中指定行数的文本，及其文本行数

    
    
    #import "NSString+Label.h"
    #import <CoreText/CoreText.h>
    
    static CGFloat textRowsRangeMaxHeight = 100000;
    
    @implementation NSString (Label)
    
    
    /** 设置获取文本行数时固定的高度，默认100000 */
    + (void)setTextRowsRangeMaxHeight:(CGFloat)height
    {
        textRowsRangeMaxHeight = height;
    }
    
    /**
     功能：获取文本中每一行文字的Range数组，注意：这儿的行数特指文本渲染的行数。
     参数：
         text：支持NSString，NSAttributedString
         font：text为NSString时需要设置的字体
         width：文本需要显示的宽
     返回值：使用NSValue包装的NSRange数组，数组的长度表示文字渲染行数。
     */
    + (nullable NSArray<NSValue *> *)getTextAllRowsRangeWith:(id)text font:(nullable UIFont *)font width:(CGFloat)width
    {
        if ([text length] < 1) {
            return nil;
        }
        NSAttributedString *attStr = nil;
        if ([text isKindOfClass:NSString.class]) {
            CTFontRef myFont = CTFontCreateWithName(( CFStringRef)([font fontName]), [font pointSize], NULL);
            NSMutableAttributedString *mAttStr = [[NSMutableAttributedString alloc] initWithString:text];
            NSDictionary *par = @{(NSString *)kCTFontAttributeName:(__bridge  id)myFont,
                                  (NSString *)kCTKernAttributeName:[NSNumber numberWithFloat:0.0],
            };
            [mAttStr addAttributes:par range:NSMakeRange(0, mAttStr.length)];
            CFRelease(myFont);
            attStr = mAttStr;
        }else if ([text isKindOfClass:NSAttributedString.class]){
            attStr = (NSAttributedString *)text;
        }else{
            return nil;
        }
    
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString((__bridge CFAttributedStringRef)attStr);
        CGMutablePathRef path = CGPathCreateMutable();
        CGPathAddRect(path, NULL, CGRectMake(0,0,width,textRowsRangeMaxHeight));
        CTFrameRef frame = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), path, NULL);
    
    //    CGContextSetTextMatrix (context, CGAffineTransformIdentity);
    //    CGContextTranslateCTM(context, 0.0f, rect.size.height);
    //    CGContextScaleCTM(context, 1.0f, -1.0f);
    //    CTFrameDraw(frame, context);
    
    
        NSArray *lines = (NSArray *)CTFrameGetLines(frame);
        NSMutableArray *linesArray = [[NSMutableArray alloc]init];
        for (id line in lines) {
            CTLineRef lineRef = (__bridge  CTLineRef)line;
            CFRange lineRange = CTLineGetStringRange(lineRef);
            NSRange range = NSMakeRange(lineRange.location, lineRange.length);
            NSValue* value = [NSValue valueWithRange:range];
            [linesArray addObject:value];
        }
    
        CGPathRelease(path);
        CFRelease(frame);
        CFRelease(frameSetter);
    
    //    NSLog(@"ranges:%@",linesArray);
        return linesArray;
    }
    
    
    @end
    
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [EXCEL批量读取TXT中指定字符到指定单元格](https://www.jianshu.com/p/31e04a8c19cf)

在工作中或者生活中，有没有遇到这样一种情形：要总结这一段时间的数据，需要将各个txt文本中对应的数据整理到一张表格...

[tobbyvic](https://www.jianshu.com/u/4f32cb2c373e)阅读 2,394评论 0赞 3

  * [Document-Based App Programming Guide for iOS (一)](https://www.jianshu.com/p/4e0fe8b3a62e)

UIKit框架为管理多个文档的应用程序提供支持，每个文档包含存储在应用程序沙箱或iCloud中的文件中的唯一数据集...

[nicedayCoco](https://www.jianshu.com/u/8c2409cd7dfb)阅读 3,370评论 0赞 1

  * [iOS网络编程读书笔记](https://www.jianshu.com/p/7e5ae7b4f0b7)

iOS网络编程读书笔记 Facade Tester客户端门面模式的实例(被动版本化) 被动版本化，所以硬编码URL...

[melouverrr](https://www.jianshu.com/u/56347667d08a)阅读 1,485评论 3赞 7

  * [【shell笔记>文本处理】初识sed与gawk](https://www.jianshu.com/p/a5edaa886f75)

博文阅读 学习内容： 学习sed编辑器gawk编辑器入门sed编辑器基础 shell脚本最常见的一个用途就是处理文...

[王诗翔](https://www.jianshu.com/u/b6608e27dc74)阅读 1,221评论 1赞 9

  * [iOS集合视图编程指南](https://www.jianshu.com/p/7d02305c8d76)

翻译自“Collection View Programming Guide for iOS” 0 关于iOS集合视...

[lakerszhy](https://www.jianshu.com/u/6e94d9bb5a0a)阅读 3,439评论 1赞 22

 