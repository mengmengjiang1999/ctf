ios 获取Text行数和每行显示的内容

[ 奔跑吧小蚂蚁](https://www.jianshu.com/u/64bd3497941e)关注赞赏支持

# ios 获取Text行数和每行显示的内容

    
    
    - (NSArray *)getLinesArrayOfStringInLabel:(NSString *)string font:(UIFont *)font andLableWidth:(CGFloat)lableWidth{
        
        CTFontRef myFont = CTFontCreateWithName(( CFStringRef)([font fontName]), [font pointSize], NULL);
        NSMutableAttributedString *attStr = [[NSMutableAttributedString alloc] initWithString:string];
        [attStr addAttribute:(NSString *)kCTFontAttributeName value:(__bridge  id)myFont range:NSMakeRange(0, attStr.length)];
        CFRelease(myFont);
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString(( CFAttributedStringRef)attStr);
        CGMutablePathRef path = CGPathCreateMutable();
        CGPathAddRect(path, NULL, CGRectMake(0,0,lableWidth,100000));
        CTFrameRef frame = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), path, NULL);
        NSArray *lines = ( NSArray *)CTFrameGetLines(frame);
        NSMutableArray *linesArray = [[NSMutableArray alloc]init];
        for (id line in lines) {
            CTLineRef lineRef = (__bridge  CTLineRef )line;
            CFRange lineRange = CTLineGetStringRange(lineRef);
            NSRange range = NSMakeRange(lineRange.location, lineRange.length);
            NSString *lineString = [string substringWithRange:range];
            CFAttributedStringSetAttribute((CFMutableAttributedStringRef)attStr, lineRange, kCTKernAttributeName, (CFTypeRef)([NSNumber numberWithFloat:0.0]));
            CFAttributedStringSetAttribute((CFMutableAttributedStringRef)attStr, lineRange, kCTKernAttributeName, (CFTypeRef)([NSNumber numberWithInt:0.0]));
            [linesArray addObject:lineString];
        }
        
        CGPathRelease(path);
        CFRelease( frame );
        CFRelease(frameSetter);
        return (NSArray *)linesArray;
    }
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [ios 获取Text行数和每行显示的内容](https://www.jianshu.com/p/daed65d034e1)

该方法主要使用了CoreText中的内容，了解更多CoreText的内容请看CoreText系列 下面是具体代码

[crazy丶LT](https://www.jianshu.com/u/39c4c14cd9f0)阅读 3,662评论 1赞 5

  * [iOS 获取label每行显示内容数组及行数](https://www.jianshu.com/p/0cc3d4c99a38)

开发时，经常会需要用到label行数来做某些操作，如下方法，给label添加分类方法，可以获得一个该label当前...

[Irene_球球](https://www.jianshu.com/u/bbc5f993995d)阅读 1,270评论 0赞 0

  * [偶遇简书](https://www.jianshu.com/p/b19c4b4d9e73)

在这个速度的时代，偶尔写写文字，也许不一定用，只是为了沉淀沉淀心情。 夜深人静时，常常问自己，真的甘心每天重复这毫...

[城镇第十幼儿园](https://www.jianshu.com/u/1239db19de10)阅读 271评论 0赞 3

  * [5\. MyBatis延迟加载](https://www.jianshu.com/p/584e6604b0fa)

5.1 什么是延迟加载 resultMap可以实现高级映射（使用association、collection实现...

[飞扬code](https://www.jianshu.com/u/56c07f802b57)阅读 185评论 0赞 2

  * [厚积方能勃发——喵喵T-1助力数百所中小学打造三维实验室新方案（附高校名单）](https://www.jianshu.com/p/b5d7772919c1)

杭州非白三维科技有限公司，是国内优秀的机器视觉及三维重建的团队。 作为三维扫描行业的领军企业，为先进智造贡献年轻力...

[三维研究院](https://www.jianshu.com/u/7e15e0b06f93)阅读 207评论 0赞 0

 