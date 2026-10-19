BezierPath曲线 动态绘制文字

[ 跃文](https://www.jianshu.com/u/1ed1c958bcae)关注赞赏支持

# BezierPath曲线 动态绘制文字

#### 直接看代码

    
    
    - (void)drawTextAnimate {
        
        CAShapeLayer * shapeLayer = [CAShapeLayer layer];
        
        CGSize size = self.view.frame.size;
        CGFloat height = 250;
        
        shapeLayer.frame = CGRectMake(0, (size.height - height)/2, size.width , height);
        shapeLayer.geometryFlipped = YES;
        shapeLayer.strokeColor = [UIColor blackColor].CGColor;
        shapeLayer.fillColor = [UIColor whiteColor].CGColor;;
        shapeLayer.lineWidth = 1;
        shapeLayer.lineJoin = kCALineJoinRound;
        [self.view.layer addSublayer:shapeLayer];
        
        //贝尔兹曲线
        NSString * tempStr = @"动态绘制文字显示";
        
        UIBezierPath *path = [self bezierPathWithText:tempStr attributes:@{NSFontAttributeName : [UIFont boldSystemFontOfSize:30]}];
        shapeLayer.bounds = CGPathGetBoundingBox(path.CGPath);
        shapeLayer.path = path.CGPath;
        
        [shapeLayer removeAllAnimations];
        
        CABasicAnimation *pathAnimation = [CABasicAnimation animationWithKeyPath:@"strokeEnd"];
        pathAnimation.duration = 0.3f * tempStr.length;
        pathAnimation.fromValue = [NSNumber numberWithFloat:0.0f];
        pathAnimation.toValue = [NSNumber numberWithFloat:1.0f];
        [shapeLayer addAnimation:pathAnimation forKey:@"strokeEnd"];
    
    }
    
    - (UIBezierPath *)bezierPathWithText:(NSString *)text attributes:(NSDictionary *)attrs {
        
        NSAssert(text!= nil && attrs != nil, @"参数不能为空");
    
        NSAttributedString * attrStrs = [[NSAttributedString alloc] initWithString:text attributes:attrs];
        CGMutablePathRef paths = CGPathCreateMutable();
        CTLineRef line = CTLineCreateWithAttributedString((CFAttributedStringRef)attrStrs);
        CFArrayRef runArray = CTLineGetGlyphRuns(line);
        
        for (CFIndex runIndex = 0; runIndex < CFArrayGetCount(runArray); runIndex++)
        {
            CTRunRef run = (CTRunRef)CFArrayGetValueAtIndex(runArray, runIndex);
            CTFontRef runFont = CFDictionaryGetValue(CTRunGetAttributes(run), kCTFontAttributeName);
            
            for (CFIndex runGlyphIndex = 0; runGlyphIndex < CTRunGetGlyphCount(run); runGlyphIndex++)
            {
                CFRange thisGlyphRange = CFRangeMake(runGlyphIndex, 1);
                CGGlyph glyph;
                CGPoint position;
                CTRunGetGlyphs(run, thisGlyphRange, &glyph);
                CTRunGetPositions(run, thisGlyphRange, &position);
    
                CGPathRef path = CTFontCreatePathForGlyph(runFont, glyph, NULL);
                CGAffineTransform t = CGAffineTransformMakeTranslation(position.x, position.y);
                CGPathAddPath(paths, &t,path);
                CGPathRelease(path);
            }
        }
        CFRelease(line);
        
        UIBezierPath *path = [UIBezierPath bezierPath];
        [path moveToPoint:CGPointZero];
        [path appendPath:[UIBezierPath bezierPathWithCGPath:paths]];
        
        CGPathRelease(paths);
        
        return path;
    }
    
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [史上最全的贝塞尔曲线(Bezier)全解(二):Android中曲线的简单绘制](https://www.jianshu.com/p/2b136da858a8)

上一篇中我简单的介(粘)绍(贴)了一下贝塞尔曲线(Bezier)曲线的原理和公式,但是作为数学界排的上名号的渣渣,...

[桑小年](https://www.jianshu.com/u/f0fae5ff900a)阅读 2,498评论 0赞 1

  * [《自定义控件：xfermode+贝塞尔曲线实现动态水波纹》](https://www.jianshu.com/p/2152577448cf)

1.效果 换了大王之后，顺带就下拉联通手机营业厅App，刚开始用，出于好奇每天都会看看今天自己通过免流用了多少流量...

[Oneminute](https://www.jianshu.com/u/8cb904bd595d)阅读 1,260评论 2赞 41

  * [二阶贝赛尔曲线绘制文字+弹跳动画实现](https://www.jianshu.com/p/6ff56cb76c8f)

分析 该控件由两个部分组成，水果图片ImageView和底部沿着Path绘制的文字，ImageView从最高点一边...

[coder_sunzhan](https://www.jianshu.com/u/7749e78dbbf3)阅读 528评论 0赞 3

  * [为什么男人可能低估女性的性冲动？](https://www.jianshu.com/p/d8b2c12ca7f4)

文：Jacqueline Howard, CNN 译：心理咨询师Mr.杨 在对女性对性趣进行评估时，大多数男人都可...

[Psychonline](https://www.jianshu.com/u/f1b86e2c1513)阅读 1,477评论 2赞 2

  * [coey sun在简书的第一天](https://www.jianshu.com/p/8af646e19c61)

在微博上看到一个曾经的挚友带着女朋友在环澳旅行，通过简书开心地分享着他和她开心的时刻，注意到了这个app，觉得有趣...

[coey_sun](https://www.jianshu.com/u/6b4285feff5f)阅读 90评论 0赞 0

 