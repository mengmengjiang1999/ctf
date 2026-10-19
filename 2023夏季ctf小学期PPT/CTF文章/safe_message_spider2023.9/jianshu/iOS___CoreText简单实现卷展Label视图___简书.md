iOS | CoreText简单实现卷展Label视图

[ 清無](https://www.jianshu.com/u/484e1c9f1ae9)关注赞赏支持

# iOS | CoreText简单实现卷展Label视图

### 开发背景

  * 公司最近项目中有一个如下图的需求，在Github找了好久没有发现类似的Demo，于是思考了几天，成功实现了这种效果。

需求效果：点击`更多`文本跳转到其他页面

  * 然后我经过改造，实现了类似于可折叠的Label效果，并支持转屏自动绘制。如下图所示：

最终效果 - 竖屏

最终效果 - 横屏

### 实现过程

  * 主要思路是利用CoreText系统库进行的富文本绘制；

  * 在最后一行时，通过不断让index减1，然后获得subAttrText，再加上`...更多`文本进行计算文本所占的行数lines，直到行数为1行；

  * 最后进行drawAttrText的绘制，并回调返回计算后的totalHeight，让控制器更新heightConstraint约束；

##### 1.drawRect

    
    
    -(void)drawRect:(CGRect)rect{
        [super drawRect:rect];
        
        if (!_attributedText) {
            return;
        }
        
        [self drawTextWithCompletion:^(CGFloat height, NSAttributedString *drawAttributedText) {
            [self addSubview:self.contentView];
            self.contentView.frame = CGRectMake(0, 0, self.bounds.size.width, height);
            self.contentView.attributedText = drawAttributedText;
            // 回调
            _action ? _action(HYExpandableLabelActionDidLoad, @(height)) : nil;
        }];
    }
    

##### 2.指定行数绘制

  * CGPathRef 绘制区域

    
    
    CGRect rect = CGRectMake(0, 0, self.bounds.size.width, .size.height);
    CGPathRef path = CGPathCreateWithRect(rect, nil);
    

  * CTFrameRef

    
    
    CTFramesetterRef setter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)_attributedText);
    CTFrameRef ctFrame = CTFramesetterCreateFrame(setter, CFRangeMake(0, _attributedText.length), path, NULL);
    

  * CTLines

    
    
    NSArray *lines = (NSArray*)CTFrameGetLines(ctFrame);
    

  * CTLine Origins 每一行的绘制原点

    
    
    CGPoint ctOriginPoints[lines.count];
    CTFrameGetLineOrigins(ctFrame, CFRangeMake(0, 0), ctOriginPoints);
    

  * 计算绘制文本drawAttrText和总高度

    
    
    NSMutableAttributedString *drawAttributedText = [NSMutableAttributedString new];
        
        for (int i=0; i<lines.count; i++) {
            if (lines.count > _maximumLines && i == _maximumLines) {
                break;
            }
            CTLineRef line = (__bridge CTLineRef)lines[i];
            
            CGPoint lineOrigin = ctOriginPoints[i];
            
            CFRange range = CTLineGetStringRange(line);
            NSAttributedString *subAttr = [_attributedText attributedSubstringFromRange:NSMakeRange(range.location, range.length)];
    
            if (lines.count > _maximumLines && i == _maximumLines - 1) {
                // 最后一行特殊处理
            }
            else{
                [drawAttributedText appendAttributedString:subAttr];
                
                totalHeight += [self heightForCTLine:line];
            }
        }
    

  * 最后一行的处理

    
    
    NSMutableAttributedString *drawAttr = [[NSMutableAttributedString alloc] initWithAttributedString:subAttr];
    
    for (int j=0; j<drawAttr.length; j++) {
        NSMutableAttributedString *lastLineAttr = [[NSMutableAttributedString alloc] initWithAttributedString:[drawAttr attributedSubstringFromRange:NSMakeRange(0, drawAttr.length-j)]];
        
        [lastLineAttr appendAttributedString:self.clickAttributedText];
        
        NSInteger number = [self numberOfLinesForAttributtedText:lastLineAttr withOriginPoint:lineOrigin];
        // 当满足为一行时，break
        if (number == 1) {
            [drawAttributedText appendAttributedString:lastLineAttr];
            
            CTLineRef moreLine = CTLineCreateWithAttributedString((__bridge CFAttributedStringRef)self.clickAttributedText);
            CGSize moreSize = CTLineGetBoundsWithOptions(moreLine, 0).size;
            // 点击区域
            self.clickArea = CGRectMake(self.bounds.size.width-moreSize.width, totalHeight, moreSize.width, moreSize.height);
            
            totalHeight += [self heightForCTLine:line];
            break;
        }
    }
    

  * 回调

    
    
    completion(totalHeight, drawAttributedText);
    

##### 3.全部文本绘制

  * 全部文本绘制（即展开文本）绘制相对来说较为简单，只需将clickAttrText追加到attrText后，然后绘制

  * CTFrameRef、CTLines等的获取和上面一样，下面主要说下totalHeight计算及clickArea的计算

    
    
    for (int i=0; i<lines.count; i++) {
            CTLineRef line = (__bridge CTLineRef)lines[i];
            totalHeight += [self heightForCTLine:line];
            // 绘制最后一行时
            if (i == lines.count - 1) {
                CTLineRef moreLine = CTLineCreateWithAttributedString((__bridge CFAttributedStringRef)self.clickAttributedText);
                
    // 计算`收起`文本的origin.x值
                NSArray *runs = (NSArray*)CTLineGetGlyphRuns(line);
                CGFloat w = 0;
                for (int i=0; i<runs.count; i++) {
                    if (i == runs.count - 1) {
                        break;
                    }
                    CTRunRef run = (__bridge CTRunRef)runs[i];
                    w += CTRunGetTypographicBounds(run, CFRangeMake(0, 0), NULL, NULL, NULL);
                }
                
                CGSize moreSize = CTLineGetBoundsWithOptions(moreLine, 0).size;
                CGFloat h = moreSize.height + lines.count * _lineHeightErrorDimension;
                self.clickArea = CGRectMake(w, totalHeight - h, moreSize.width, h);
            }
        }
    

### 用法

    
    
    @property (weak, nonatomic) IBOutlet HYExpandableLabel *expandableLabel;
    // 高度值约束
    @property (weak, nonatomic) IBOutlet NSLayoutConstraint *expandableLabelHeightCons;
    
    - (void)viewDidLoad {
        [super viewDidLoad];
        
        _expandableLabel.attributedText = [[NSAttributedString alloc] initWithString:@"测试文本😁"  attributes: @{ NSFontAttributeName:[UIFont systemFontOfSize:14] }];
            
        __block typeof(self)weakSelf = self;
        _expandableLabel.action = ^(HYExpandableLabelActionType type, id info) {
            if (type == HYExpandableLabelActionDidLoad) {
                NSLog(@"_expandableLabel Did Calculated");
    // 更新布局
                weakSelf.expandableLabelHeightCons.constant = [info floatValue];
                [weakSelf.view layoutIfNeeded];
            }
        };
    }
    

### Github

[https://github.com/BackWorld/HYExpandableLabel](https://link.jianshu.com?t=https://github.com/BackWorld/HYExpandableLabel)

> 如果对你有帮助，别忘了加个`关注` 或 点个`赞`哦😁

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS开发常用三方库集合OC版(三方库、插件、博客等等)](https://www.jianshu.com/p/4145a80dec45)

Swift版本点击这里欢迎加入QQ群交流: 594119878最新更新日期：18-09-17 About A cu...

[ylgwhyh](https://www.jianshu.com/u/e94387132cd6)阅读 23,613评论 7赞 248

  * [iOS WebSocket长链接（Swift）](https://www.jianshu.com/p/48941c44ad32)

WebSocket-Swift Starscream的使用 WebSocket 是 HTML5 一种新的协议。它实...

[神合](https://www.jianshu.com/u/5567c741f6a7)阅读 20,846评论 8赞 179

  * [优秀第三方](https://www.jianshu.com/p/8bd0e2d2de99)

发现 关注 消息 iOS 第三方库、插件、知名博客总结 作者大灰狼的小绵羊哥哥关注 2017.06.26 09:4...

[肇东周](https://www.jianshu.com/u/5eb359cf9cd4)阅读 10,680评论 4赞 57

  * [美漫汉化教程——fhey-修图教程（一）](https://www.jianshu.com/p/ea5d5a5fb102)

我邀请+转载，作者fhey ——— fhey-修图教程（一） 应墨问大大的要求来写个修图教程~ 感觉汉化组里修图一...

[墨问非名](https://www.jianshu.com/u/5d98f0cc5d37)阅读 6,019评论 1赞 5

  * [不懂车的小白看过来](https://www.jianshu.com/p/17e69b720c42)

我们都知道不管是国产的手动挡还是国外的手动挡，都不是用的中文标识所以导致很多不懂英文的司机根本不知道什么挡是做什么...

[朦胧月色](https://www.jianshu.com/u/32a6c4574027)阅读 260评论 0赞 0

 