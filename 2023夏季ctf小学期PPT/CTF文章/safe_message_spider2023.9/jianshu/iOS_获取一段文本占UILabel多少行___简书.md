iOS 获取一段文本占UILabel多少行

[ liang1030](https://www.jianshu.com/u/7190c916c01b)关注赞赏支持

# iOS 获取一段文本占UILabel多少行

1，导入头文件

# import <CoreText/CoreText.h>

2，

    
    
    //根据文字内容、字体大小和宽度限制计算文本控件的行数
    + (NSInteger)rowsOfString:(NSString *)text withFont:(UIFont *)font withWidth:(CGFloat)width {
        if (!text || text.length == 0) {
            return 0;
        }
        CTFontRef myFont = CTFontCreateWithName(( CFStringRef)([font fontName]), [font pointSize], NULL);
        NSMutableAttributedString *attStr = [[NSMutableAttributedString alloc] initWithString:text];
        [attStr addAttribute:(NSString *)kCTFontAttributeName value:(__bridge  id)myFont range:NSMakeRange(0, attStr.length)];
        CFRelease(myFont);
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString(( CFAttributedStringRef)attStr);
        CGMutablePathRef path = CGPathCreateMutable();
        CGPathAddRect(path, NULL, CGRectMake(0,0,width,MAXFLOAT));
        CTFrameRef frame = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), path, NULL);
        NSArray *lines = ( NSArray *)CTFrameGetLines(frame);
        CFRelease(frameSetter);
        CFRelease(frame);
        return lines.count;
    }
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [你说](https://www.jianshu.com/p/06041b29d7fe)

[ 夜莺2517](https://www.jianshu.com/u/ddd5fcf8db43)阅读 127,468评论 1赞 9

  * [天气应用-我的天气app体验报告](https://www.jianshu.com/p/cb44563a2f9f)

版本：ios 1.2.1 亮点： 1.app角标可以实时更新天气温度或选择空气质量，建议处女座就不要选了，不然老想...

[我就是沉沉](https://www.jianshu.com/u/f75ccfbb78f5)阅读 6,466评论 1赞 6

  * [送你一个晚安故事](https://www.jianshu.com/p/0879191117c3)

我是黑夜里大雨纷飞的人啊 1 “又到一年六月，有人笑有人哭，有人欢乐有人忧愁，有人惊喜有人失落，有的觉得收获满满有...

[陌忘宇](https://www.jianshu.com/u/a03b8c6677f3)阅读 8,131评论 28赞 53

  * [2015.9.17-盐鸭蛋](https://www.jianshu.com/p/f5c771f46bd4)

兔子虽然是枚小硕 但学校的硕士四人寝不够 就被分到了博士楼里 两人一间 在学校的最西边 靠山 兔子的室友身体不好 ...

[待业的兔子](https://www.jianshu.com/u/e3f0aee941aa)阅读 2,347评论 2赞 9

 