文字排版入门—— 排版基础、CoreText和图文混排

[ 落影loyinglin](https://www.jianshu.com/u/815d10a4bdce)关注赞赏支持

# 文字排版入门—— 排版基础、CoreText和图文混排

### 一、排版概念

#### 1、Characters and Glyphs（字符和字形）

字符是文字的最小单元，以这段文字为例，每个字都是一个字符；需要注意，字符是一个抽象的概念；  
当文字真正绘制出来时需要选择字体，以“A”这个字母为例，当字母'A'印刷出来或者显示到屏幕，可能有多种字体，每种字体都有一种字形'A'：

  

但是，字符和字形不是一一对应，也不是一对多的关系！  
在某些字体中，相同的字符可能会包括多个的字形：  
“é” = “e” + “´” （一个字符由两个字形组合而成）  
一个字形，也可以容纳多个字符，如下：（右边的字形是连写ff，包括两个字符f）

  

上图的连字符是一种上下文相关的字形，一个字符的字形由受到下一个字符的影响。

#### 2、字型(Typefaces)和字体(Fonts)

Typeface指一系列风格接近的字体，而Font是一系列具有一致大小、样式的字形组成的字体；通常多个字体会组成一个字型，如图：

  

这是多个字体组成的字型(字体族)

#### 3、字体属性

字体属性指的是字符的字形大小和布局。同一字体中的字符属性大致相同，常用属性包括：baseline(字符基线)、ascent(字形最高点和baseline的距离)、descent(字形最低点和baseline的距离)、leading(行间距)等。  

  
**字符属性的详细介绍：**  
_text direction_ ：文字的排版顺序，像English是从左上角开始，从左到右；也有文字的排版是从右到左或者是从上到下的排版等；  
_line breaking_ ：在字符串中找到一个点，截取出一段文本用于显示一行；  
_baseline_ ：所有字形的虚拟基准线，如下图蓝色部分：（也会有部分字形跨过基准线，比如说g）  

_left-side bearing_ ：如图，是字符之间默认的间隙；（同理还有 _right-side bearing_ ）  
_descent/ascent_ ：字形的上下部分；  
_bounding rectangle_ ：字形的可见部分；  
_kerning_ ：文字默认排版时，宽度由advance
width指定，默认会留有一小部分间隔；也可以通过设置字间距（kerning），手动调整字形之间的距离。  

_point size_ ：ascent+descent就是字体的pointSize；  
_leading_ ：两行字形之间的距离；  
_line height_ ：行高，ascent+descent+leading=line height；  
_margins_ ：文字和边界的距离；  
_Alignment_ ：多行文字的对齐方式，常见有下面三种：  

  
另外一种同样常见的排版方式是两端对齐（justified）：  

综上，常见的排版概念的分布如下：

### 二、NSAttributeString

在介绍NSAttributeString之前，我们先了解一个概念——`Text Attributes`（文本属性），常见的属性有：

  * character attributes：字体、颜色等具体到某个字符的属性，通常会键值对的方式存在NSDictionary中，例如`@{NSFontAttributeName:[UIColor redColor]}`；
  * temporary attributes：对于某种排版的临时字符属性，不会持久化，比如说跨行的连字符'-'；
  * paragraph attributes：行间距、段间距、边界margin等段落属性，段落属性会影响多行文本的排版，具体属性可以见NSParagraphStyle；
  * glyph attributes：排版引擎渲染时的加粗等字形属性，通常是一个integer值，代表字符在排版引擎中的具体使用值（开发者通常不需要关心）；
  * document attributes：整个文档(字符串)的属性，例如说我们常用的属性`@{NSDocumentTypeDocumentAttribute:NSHTMLTextDocumentType}`，说明该字符是HTML的格式，类似的还有：

    
    
     NSAttributedStringDocumentType const NSPlainTextDocumentType;
     NSAttributedStringDocumentType const NSRTFTextDocumentType;
     NSAttributedStringDocumentType const NSRTFDTextDocumentType;
     NSAttributedStringDocumentType const NSHTMLTextDocumentType;
    

NSAttributeString就是上述属性的结合体，描述一段字符串的属性。  
如下图，这里描述的是针对`This is a`这段字符的字体颜色和字体大小属性：  

NSAttributeString并不是NSString的子类，但是却有一个.string属性可以获取到富文本对应的string；  
那么， **为什么NSAttributeString不做成NSString的子类** ？  
首先从字面意思来看，NSAttributeString很容易就被当成NSString的子类，导致会写出NSAttributeString==NSString的这类判断，将NSAttributeString不写成NSString子类可以避免这一类问题；  
更为重要的是，NSAttributeString是描述string的各种属性，而NSString是单纯的字符串。

NSAttributeString的属性在生成之后便无法修改，如果需要修改某些属性，则需要使用NSMutableAttributeString。  
NSAttributeString有两种方法可以读取对应某个字符的属性：

    
    
    attributesAtIndex:effectiveRange:
    attributesAtIndex:longestEffectiveRange:inRange:
    

**为什么需要有两种方法？**  
attribute是针对一段字符的属性，而一个字符串往往会有多个attribute；  
如果把字符串中的每个字符看成一维数轴上的点，那么attribute就是一个点或者两个点之间的线段，NSAttributeString由许许多多的线段组成；  
当我们获取某个点的属性，实际上就是询问所有的线段中，经过这个点的线段（属性）有哪些。  
所以为了优化速度，可以通过指定effectiveRange，缩小遍历的范围。如果想知道该属性的最大覆盖范围，则使用带longestEffectiveRange的方法，但是需要手动设置遍历range，否则会遍历整个字符串的属性。

如下，4个点代表4个字符，一个红色的线段表示一个(0, 3)的属性，蓝色的线段表示(1, 3)的属性；  
当我们获取第2个点的属性时，因为红色和蓝色线段都经过第2个点，所以会返回两个属性；  
当我们获取第1个点的属性时，只有红色的线段经过第1个点，则只会返回一个属性；

最后注意，当Attribute在赋值给NSAttributeString之后不应该修改，比如说下面的段属性设置，当我们把这个dict赋值给NSAttributeString之后，就不应该修改paragraphStyle的值（否则可能会发生未知的问题）。

    
    
       NSMutableParagraphStyle *paragraphStyle = [[NSMutableParagraphStyle alloc] init];
        paragraphStyle.lineBreakMode = NSLineBreakByWordWrapping;
        paragraphStyle.lineSpacing = 1.0;
        paragraphStyle.alignment = NSTextAlignmentJustified;
        dict[NSParagraphStyleAttributeName] = paragraphStyle;
    

### 三、CoreText

在了解排版概念和NSAttributeString后，再来看CoreText。  
CoreText是一个高效处理字符和字形转换和进行文字排版的框架，API基于C语言。  
当我们需要排版时，可以对字符串设置各种格式，生成NSAttributeString；  
然后用NSAttributeString去创建CTFramesetter类，CTFramesetter会处理排版信息，然后生成排版后的结果CTFrame；  
CTFrame是一段或者多段文本，每段文本又由多行文字组成，每行的表示为CTLine；  
CTLine是一行文本，每行文本由多个CTRun组成，CTRun是一小段连续的字形；  
CTTypeSetter负责上下文相关排版处理，比如说换行，每个CTFrame中都会有一个CTTypeSetter；  
他们之间的关系图如下：

  

总的来说，CTFramesetter是生成CTFrame的工厂类，初始化参数是attributed
string，会在内部创建CTTypesetter并进行实际的排版；CTLine类似每一行的文字，CTRun是一行中具有相同属性的连续字形，比如说“我正在
**分享** 阅读器”，就会由三个CTRun组成，分别是“我正在”、“ **分享** ”、“阅读器”（因为“分享”两个字加粗了，否则就会是一个CTRun）。

#### 1、CTFont

CTFontRef是CoreText的字体，可以读取字体的版权信息（copyright）、fontFamily、style等信息；  
`CTFontCreateWithName()`用于创建字体，但是只有CTFontManager中已注册的字体能够返回（默认字体大小12）；  
CTFont提供的方法还有很多，列举一些比较常用的：  
对字符和字形进行转换，返回true代表全部转换成功，返回false则代表字体不包含某些字形（没有成功mapping的字形结果为0）；

    
    
    bool CTFontGetGlyphsForCharacters(
        CTFontRef       font,
        const UniChar   characters[_Nonnull],
        CGGlyph         glyphs[_Nonnull],
        CFIndex         count );
    

获取字体的ascent、descent、leading、bounding box等属性：

    
    
    CGFloat CTFontGetAscent( CTFontRef font );
    CGFloat CTFontGetDescent( CTFontRef font );
    CGFloat CTFontGetLeading( CTFontRef font );
    CGRect CTFontGetBoundingBox( CTFontRef font );
    

可以直接对某些字形进行渲染，参数font提供字体相关属性，glyphs数组提供字形，positions数组提供位置（可以通过CTLine生成）；

    
    
    void CTFontDrawGlyphs(
        CTFontRef       font, 
        const CGGlyph   glyphs[_Nonnull],
        const CGPoint   positions[_Nonnull],
        size_t          count, 
        CGContextRef    context );
    

#### 2、CTLineRef

行的排版数据，一个很常见的生成方式是通过NSAttributeString；（这种方式的好处在于便捷，不需要手动创建typesetter；但是同样因为没有显式创建typesetter，无法配置换行参数；这个API多用于一行文本的排版）

    
    
    CTLineRef CTLineCreateWithAttributedString(
        CFAttributedStringRef attrString );
    

有时候我们需要对CTLine进行截断，下面的方法是对line进行截断，width是指定的行宽，truncationType是截断的规则（A...B，AB...和...AB这三种样式），truncationToken是截断用的填充符号（通常是...的省略号，为Null时则只截断，不做填充）

    
    
    CTLineRef _Nullable CTLineCreateTruncatedLine(
        CTLineRef line,
        double width,
        CTLineTruncationType truncationType,
        CTLineRef _Nullable truncationToken );
    

CTLine是由多个CTRun组成，每个CTRun又包括多个字形，下面三个方法可以获取CTLine的一些数据：

    
    
    CFIndex CTLineGetGlyphCount(
        CTLineRef line ); // 获取字形数量
    CFArrayRef CTLineGetGlyphRuns(
        CTLineRef line ); // 获取所有的CTLine
    CFRange CTLineGetStringRange(
        CTLineRef line ); // 获取创建CTLine时的range
    

在对一行排版的时候，有时候我们希望两端对齐，此时可以用下面的方法实现：  
line是需要对齐的行，justificationFactor是调整的系数（范围0到1，假如文字长度是100，限定宽度是300，则填充的空白区域为200*justificationFactor），justificationWidth是目标宽度，如果line的长度超过了justificationWidth，则会返回NULL；

    
    
    CTLineRef _Nullable CTLineCreateJustifiedLine(
        CTLineRef line,
        CGFloat justificationFactor,
        double justificationWidth );
    

有时候我们只是希望对齐文本，并不想填充空白字符，此时上面的方法并不合适，需要改用CTLineGetPenOffsetForFlush；line是要排版的行，flushFactor是0~1的浮点数（0表示靠左，1表示靠右，0.5表示居中），flushWidth表示对齐的宽度；

    
    
    double CTLineGetPenOffsetForFlush(
        CTLineRef line,
        CGFloat flushFactor,
        double flushWidth );
    

CTLine可以直接绘制，line是绘制的行，context是上下文；（CGContextSetTextPosition设置的位置对CTFrameDraw没有作用，但是和CTLineDraw
配合使用则效果非常好）

    
    
    void CTLineDraw(
        CTLineRef line,
        CGContextRef context ) ;
    

CTLine测量相关的方法，CTLineGetTypographicBounds可以获取一个CTLine的大小，参数会回调ascent、descent、leading的大小，返回值是宽度，综合起来就是CTLine的大小，如下面的getLineBounds方法，可以获取一行文本的Rect；

    
    
    double CTLineGetTypographicBounds(
        CTLineRef line,
        CGFloat * _Nullable ascent,
        CGFloat * _Nullable descent,
        CGFloat * _Nullable leading );
    
    // DEMO
    + (CGRect)getLineBounds:(CTLineRef)line point:(CGPoint)point {
        CGFloat ascent = 0.0f;
        CGFloat descent = 0.0f;
        CGFloat leading = 0.0f;
        CGFloat width = (CGFloat)CTLineGetTypographicBounds(line, &ascent, &descent, &leading);
        CGFloat height = ascent + descent;
        return CGRectMake(point.x, point.y - descent, width, height);
    }
    

另外一种获取Rect的方案是直接用下面的方法：（options种类很多，通常填0就好）

    
    
    CGRect CTLineGetBoundsWithOptions(
        CTLineRef line,
        CTLineBoundsOptions options );
    

还有一种size是ImageBounds，表示计算这行文字绘制成图片所需要的最小size；上面的size是用于排版的size（带有各种边距），而imageBounds是尽可能小的size（理想状态）。

    
    
    CGRect CTLineGetImageBounds(
        CTLineRef line,
        CGContextRef _Nullable context );
    

CoreText不是UIKit，点击的事件需要自己手动计算和处理，CTLineGetStringIndexForPosition传入行信息和位置信息，可以传出该位置对应的字符索引；（注意位置是基于左下角原点坐标系，如果是UIKit的坐标则需要做坐标系变换）

    
    
    CFIndex CTLineGetStringIndexForPosition(
        CTLineRef line,
        CGPoint position );
    

计算当行中，某个字符相对的x坐标；（secondaryOffset通常用不到，传NULL即可）

    
    
    CGFloat CTLineGetOffsetForStringIndex(
        CTLineRef line,
        CFIndex charIndex,
        CGFloat * _Nullable secondaryOffset ) ;
    

#### 3、CTRunRef

排版时个格式相同的基础单位，包括一个或多个字形，通过CTRunGetGlyphCount可以获取；

    
    
    CFIndex CTRunGetGlyphCount(
        CTRunRef run );
    

CTRunRef包括多个文字相关属性，可以通过CTRunGetAttributes获取；（属性可能是来自NSAttributeString，也可能来自于内部排版引擎的生成）

    
    
    CFDictionaryRef CTRunGetAttributes(
        CTRunRef run );
    

CTRunRef有一个很方便的地方，便是可以直接拿到字符对应的字形：  
CTRunGetGlyphsPtr可以拿到对应字形列表（但是返回值可能为NULL，即使存在字形）；  
CTRunGetGlyphs是更推荐的做法，创建buffer然后传入CoreText，直接获取对应的字形；（字形其实就是一个unsigned
short的类型）

    
    
    const CGGlyph * _Nullable CTRunGetGlyphsPtr(
        CTRunRef run );
    void CTRunGetGlyphs(
        CTRunRef run,
        CFRange range,
        CGGlyph buffer[_Nonnull] );
    

CTRun可以获取到每个字符对应的位置，同样有两个方法：  
同样推荐使用CTRunGetPositions，原因同上（CTRunGetPositionsPtr可能有值的时候也会返回NULL）

    
    
    const CGPoint * _Nullable CTRunGetPositionsPtr(
        CTRunRef run );
    void CTRunGetPositions(
        CTRunRef run,
        CFRange range,
        CGPoint buffer[_Nonnull] );
    

CTRunRef可以获取生成时的Range，以便定位到这段文字在整体的位置；

    
    
    CFRange CTRunGetStringRange(
        CTRunRef run );
    

在排版时，有两个方法：

  * CTRunGetTypographicBounds 获取这个CTRun的最小排版size；
  * CTRunGetImageBounds 获取这个CTRunRef的最小显示size；

    
    
    double CTRunGetTypographicBounds(
        CTRunRef run,
        CFRange range,
        CGFloat * _Nullable ascent,
        CGFloat * _Nullable descent,
        CGFloat * _Nullable leading );
    CGRect CTRunGetImageBounds(
        CTRunRef run,
        CGContextRef _Nullable context,
        CFRange range )
    

一个CTLine里面会包括多个CTRun，每个CTRun都包括各自的位置信息，在排版的时候可以通过CTRunGetTextMatrix获取相应的位置，再通过CGContextSetTextMatrix设置到CGContext；

    
    
    CGAffineTransform CTRunGetTextMatrix(
        CTRunRef run );
    

最终绘制的方法是CTRunDraw，传入CTRun和CGContextRef以及CFRange即可。

    
    
    void CTRunDraw(
        CTRunRef run,
        CGContextRef context,
        CFRange range );
    

举个例子，下面是一段绘制CTRun的样例代码：

    
    
    - (void)drawInContext:(CGContextRef)context
    {
            if (!_run || !context)
            {
                    return;
            }
            
            CGAffineTransform textMatrix = CTRunGetTextMatrix(_run);
            
            if (CGAffineTransformIsIdentity(textMatrix))
            {
                    CTRunDraw(_run, context, CFRangeMake(0, 0));
            }
            else
            {
                    CGPoint pos = CGContextGetTextPosition(context);
                    
                    // set tx and ty to current text pos according to docs
                    textMatrix.tx = pos.x;
                    textMatrix.ty = pos.y;
                    
                    CGContextSetTextMatrix(context, textMatrix);
                    
                    CTRunDraw(_run, context, CFRangeMake(0, 0));
                    
                    // restore identity
                    CGContextSetTextMatrix(context, CGAffineTransformIdentity);
            }
    };
    

#### 4、CTRunDelegate

CTRunDelegate是CTRun的delegate，我们可以手动设置CTRun的Ascent、Descent、Width属性，这是图文混排的基础；插入一个空白的字符，将其字符的大小设置为(width,
height)，留出对应的大小空白区域，然后在排版结束完在对应的位置插入UIImageView就实现了图文混排的效果；  
下面是一段插入特定宽高字符的示例代码：

    
    
    static CGFloat ascentCallback(void * refCon){
        SSEmptyLayoutData *data = (__bridge SSEmptyLayoutData *)refCon;
        return data.size.height;
    }
    
    static CGFloat descentCallback(void * refCon){
        return 0;
    }
    
    static CGFloat widthCallback(void * refCon){
        SSEmptyLayoutData *data = (__bridge SSEmptyLayoutData *)refCon;
        return data.size.width;
    }
    
    - (void)insert {
        CTRunDelegateCallbacks callbacks;
        memset(&callbacks, 0, sizeof(CTRunDelegateCallbacks));
        callbacks.version = kCTRunDelegateVersion1;
        callbacks.getAscent = ascentCallback;
        callbacks.getDescent = descentCallback;
        callbacks.getWidth = widthCallback;
        CTRunDelegateRef delegate = CTRunDelegateCreate(&callbacks, (__bridge void *)(layoutData));
        CFAttributedStringSetAttribute((CFMutableAttributedStringRef)space,
                                       CFRangeMake(0, 1),
                                       kCTRunDelegateAttributeName,
                                       delegate);
        CFRelease(delegate);
    }
    

#### 5、CTFrameRef

CTFrame是由多行文本组成的布局frame，由framesetter生成。  
CTFrameGetStringRange可以获取frame中的字符串范围（创建frame时候填的参数），如果CTFramesetterCreateFrame填的是(0,
0)，则会按照实际的数字返回，例如填的是(3, 0)，生成的frame有50个字符，那么返回的range是(3, 50)；  
同理，CTFrameGetVisibleStringRange可以获取可见字符的range，规则同上；

    
    
    CFRange CTFrameGetStringRange(
        CTFrameRef frame );
    CFRange CTFrameGetVisibleStringRange(
        CTFrameRef frame );
    

同时，还有方法可以获取Frame的Path、FrameAttribute等属性

    
    
    CFDictionaryRef _Nullable CTFrameGetFrameAttributes(
        CTFrameRef frame );
    CGPathRef CTFrameGetPath(
        CTFrameRef frame );
    

更为常见的是读取CTLine的信息，可以调用CTFrameGetLines直接返回所有的CTLine，也可以调用CTFrameGetLineOrigins返回每一行的起始位置（注意CoreText的坐标原点是左下角）；

    
    
    CFArrayRef CTFrameGetLines(
        CTFrameRef frame );
    void CTFrameGetLineOrigins(
        CTFrameRef frame,
        CFRange range,
        CGPoint origins[_Nonnull] );
    

最后，CTFrame同样支持直接渲染

    
    
    void CTFrameDraw(
        CTFrameRef frame,
        CGContextRef context );
    

#### 6、CTTypesetterRef

CTTypesetter是基础的排版类，可以通过AttributeString创建，并根据需要附加options（通常用不到）；  
typesetter通常用于创建多行文本的换行和其他上下文相关的字符处理；（CTLineRef也可以排版，但是只有自己当前行的信息）

    
    
    CTTypesetterRef CTTypesetterCreateWithAttributedString(
        CFAttributedStringRef string );
    CTTypesetterRef _Nullable CTTypesetterCreateWithAttributedStringAndOptions(
        CFAttributedStringRef string,
        CFDictionaryRef _Nullable options );
    

typesetter很常用的方法是断行，传入需要换成的stringRange，和行的偏移offset，便会对typesetter内的字符进行处理，生成一行CTLine（如果参数不合法，比如超过边界则会返回NULL）；  
如果不想控制offset，可以调用下面的方法，offset默认为0；

    
    
    CTLineRef CTTypesetterCreateLineWithOffset(
        CTTypesetterRef typesetter,
        CFRange stringRange,
        double offset );
    CTLineRef CTTypesetterCreateLine(
        CTTypesetterRef typesetter,
        CFRange stringRange );
    

上面的换行方法需要传入stringRange，这个range由哪里生成？  
CTTypesetterSuggestLineBreakWithOffset方法传入typesetter，开始的位置startIndex，行的宽度width，以及行位置偏移offset，会返回这行文本的长度；（配合startIndex，就组成了一个range）  
同理，CTTypesetterSuggestLineBreak适用于offset为0的时候；

    
    
    CFIndex CTTypesetterSuggestLineBreakWithOffset(
        CTTypesetterRef typesetter,
        CFIndex startIndex,
        double width,
        double offset );
    CFIndex CTTypesetterSuggestLineBreak(
        CTTypesetterRef typesetter,
        CFIndex startIndex,
        double width );
    

需要注意，当我们用typesetter排版的时候，attributestring中的换行属性(linebreaking选项)并不生效，CTTypesetterSuggestLineBreak方法不会截断一个单词（类似NSLineBreakByWordWrapping），而CTTypesetterSuggestClusterBreak则类似NSLineBreakByCharWrapping；（注意，这些截断并不会生成省略号，如果有需要截断成ABC...的样式，需要用CTLine的方法）

    
    
    CFIndex CTTypesetterSuggestClusterBreakWithOffset(
        CTTypesetterRef typesetter,
        CFIndex startIndex,
        double width,
        double offset );
    CFIndex CTTypesetterSuggestClusterBreak(
        CTTypesetterRef typesetter,
        CFIndex startIndex,
        double width );
    

#### 7、CTFramesetterRef

排版生成类，每个CTFramesetterRef内都会有一个CTTypesetterRef来负责换行、字符处理等，可以通过CTTypesetterRef创建；

    
    
    CTFramesetterRef CTFramesetterCreateWithTypesetter( 
        CTTypesetterRef typesetter ); 
    

也可以通过NSAttributeString来创建；

    
    
    CTFramesetterRef CTFramesetterCreateWithAttributedString( 
        CFAttributedStringRef string );  
    

CTFramesetterRef可以产生排版结果（用于渲染），stringRange的len=0时，表示填充字符到path放不下，frameAttributes是frame相关属性，比如从上到下填充，还是从左到右；

    
    
    CTFrameRef CTFramesetterCreateFrame( 
        CTFramesetterRef framesetter, 
        CFRange stringRange, 
        CGPathRef path, 
        CFDictionaryRef _Nullable frameAttributes ); 
    

如果有需要访问CTTypesetterRef，则可以直接从CTFramesetterRef读取；

    
    
    CTTypesetterRef CTFramesetterGetTypesetter(
        CTFramesetterRef framesetter );
    

一个更常见的场景，是计算CTFramesetterRef所占用的大小，已创建排版所用的CGPath，可以用下面的方法，constraints是目标区域的最大size（可以将其height设置为CGFLOAT_MAX表示不限制），fitRange会返回最终填充的字符长度，返回值的size是计算的size；

    
    
    CGSize CTFramesetterSuggestFrameSizeWithConstraints(
        CTFramesetterRef framesetter,
        CFRange stringRange,
        CFDictionaryRef _Nullable frameAttributes,
        CGSize constraints,
        CFRange * _Nullable fitRange ) ;
    

### 四、CoreText排版

经过漫长的学习，我们终于了解排版的基础知识和CoreText常用类，接下来看看CoreText的实际应用。

#### 1、正常的文字排版（CTFrame）

最常见的排版过程是先创建NSAttributeString，然后创建CTFramesetterRef，接着是生成绘制的区域UIBezierPath，用这两个生成CTFrameRef，最后调用CTFrameDraw进行绘制；

    
    
        NSString *str = @"一二三四五六七八九十一二三四五六七八九十\n一二三四五六七八九十一二三四五六七八九十一二三四五六七八九十";
        CFMutableAttributedStringRef attrString = (__bridge CFMutableAttributedStringRef)[self getNormalMutableAttributeStrWithStr:str];
    
        CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString(attrString);
        UIBezierPath * bezierPath = [UIBezierPath bezierPathWithRect:CGRectMake(30, 0, self.topDrawView.width / 2, self.topDrawView.height / 2)];
        CTFrameRef frameRef = CTFramesetterCreateFrame(frameSetter,
                                                       CFRangeMake(0, 0),
                                                       bezierPath.CGPath, NULL);
        CTFrameDraw(frameRef, context);
    

最终绘制的效果：

#### 2、CTLine的排版

CTLine的排版首先是创建NSAttributeString，接着创建CTTypesetterRef（与CTFrame不同，CTFrame是用CTFramesetter来处理），在用setter进行分行处理，得到每一行的CTLine；  
拿到CTLine之后，我们可以进行对齐操作，也可以进行左对齐和右对齐，最后设置行的起始位置，进行绘制；

    
    
        NSString *str = @"Guangdong has recently published Several Policies and Measures for Promoting Scientific and Technological Innovation";
        CFAttributedStringRef attrString = (__bridge CFAttributedStringRef)[self getAttributeStrWithStr:str];
        
        CTTypesetterRef typesetter = CTTypesetterCreateWithAttributedString(attrString);
        
        CFIndex start = 0;
        CGPoint textPosition = CGPointMake(0, 55);
        double width = self.topDrawView.width;
        
        BOOL isCharLineBreak = NO;
        BOOL isJustifiedLine = NO;
        float flush = 0; // centered，可以调整这里的数字0是左对齐，1是右对齐，0.5居中
        while (start < str.length) {
            CFIndex count;
            if (isCharLineBreak) {
                count = CTTypesetterSuggestClusterBreak(typesetter, start, width);
            }
            else {
                count = CTTypesetterSuggestLineBreak(typesetter, start, width);
            }
            CTLineRef line = CTTypesetterCreateLine(typesetter, CFRangeMake(start, count));
            if (isJustifiedLine) {
                line = CTLineCreateJustifiedLine(line, 1, width);
            }
            double penOffset = CTLineGetPenOffsetForFlush(line, flush, width);
            CGContextSetTextPosition(context, textPosition.x + penOffset, self.topDrawView.height - textPosition.y);
            CTLineDraw(line, context);
            textPosition.y += CTLineGetBoundsWithOptions(line, 0).size.height;
            start += count;
        }
    

上面的代码有三个参数，分别可以设置换行方式、是否两端对齐和调整对齐方式；

默认的换行方式以及不不进行对齐操作：

Cluster的换行方式以及进行对齐操作：

#### 3、CTRun的排版

CTRun绘制的前面步骤可以使用CTFrame、也可以使用CTLine，最终是通过`CTLineGetGlyphRuns`从CTLine拿到CTRun的数组；这里以一行文本为例，重点关注一行文本中多个CTRun如何进行绘制；  
方式1：  
遍历CTRun数组，对于每一个CTRun直接调用`CTRunDraw`进行绘制；

    
    
                CTRunDraw(run, context, CFRangeMake(0, 0));
    

方式2：  
对于每个CTRun，我们读取CTRun的中每个字形的位置和字形信息，再读取CTRun的属性包括字体颜色、大小、背景去设置CGContext，最后通过`CGContextShowGlyphsAtPositions`进行绘制。

    
    
                CFIndex glyphCount = CTRunGetGlyphCount(run);
                CGPoint *positions = calloc(glyphCount, sizeof(CGPoint));
                CTRunGetPositions(run, CFRangeMake(0, 0), positions);
                CGGlyph *glyphs = calloc(glyphCount, sizeof(CGGlyph));
                CTRunGetGlyphs(run, CFRangeMake(0, 0), glyphs);
                CFDictionaryRef attrDic = CTRunGetAttributes(run);
                CTFontRef runFont = CFDictionaryGetValue(attrDic, kCTFontAttributeName);
                CGFontRef cgFont = CTFontCopyGraphicsFont(runFont, NULL);
                CGColorRef fontColor = (CGColorRef)CFDictionaryGetValue(attrDic, NSForegroundColorAttributeName);
                CGFloat fontSize = CTFontGetSize(runFont);
                CGContextSetFont(context, cgFont);
                CGContextSetFontSize(context, fontSize);
                [(__bridge UIColor *)fontColor setFill];
                // CGColorGetComponents(fontColor) 获取到的颜色是空的，包括CGColorGetAlpha
                //        CGContextSetFillColor(context, CGColorGetComponents(fontColor));
                CGContextShowGlyphsAtPositions(context, glyphs, positions, glyphCount);
                free(positions);
                free(glyphs);
    

排版效果：

#### 4、图文混排

图文混排是CTFrame、CTLine、CTRun的综合运用，原理是通过给NSAttributeString中添加一个空白字符，同时设置这个字符宽高为图片的size，最终排版的时候会预留出来一个与图片大小一致的空白区域；再通过CoreText的方法读取这个空白区域的位置，在对应的位置绘制对应的图片。  
整个过程：

1、创建NSMutableAttributedString，初始化原始的排版数据，插入带特定大小的空白字符，生成空白字符的代码：

    
    
    static CGFloat ascentCallback(void * refCon){
        NSValue *data = (__bridge NSValue *)refCon;
        return [data CGSizeValue].height;
    }
    
    static CGFloat descentCallback(void * refCon){
        return 0;
    }
    
    static CGFloat widthCallback(void * refCon){
        NSValue *data = (__bridge NSValue *)refCon;
        return [data CGSizeValue].width;
    }
    
    - (NSAttributedString *)getEmtpyAttributeString {
        CTRunDelegateCallbacks callbacks;
        memset(&callbacks, 0, sizeof(CTRunDelegateCallbacks));
        callbacks.version = kCTRunDelegateVersion1;
        callbacks.getAscent = ascentCallback;
        callbacks.getDescent = descentCallback;
        callbacks.getWidth = widthCallback;
        CGSize size = CGSizeMake(50, 50);
        CTRunDelegateRef delegate = CTRunDelegateCreate(&callbacks, (__bridge void *)([NSValue valueWithCGSize:size]));
        NSMutableAttributedString *space = [[NSMutableAttributedString alloc] initWithString:@" " attributes:
      @{NSBackgroundColorAttributeName:[UIColor colorWithRed:0.5 green:1 blue:0.5 alpha:0.5],
        NSForegroundColorAttributeName:[UIColor greenColor],
        }];
        CFAttributedStringSetAttribute((CFMutableAttributedStringRef)space,
                                       CFRangeMake(0, 1),
                                       kCTRunDelegateAttributeName,
                                       delegate);
        CFRelease(delegate);
        return space;
    }
    

2、遍历排版结果，从CTFrame中拿到CTLine的数组，再从每个CTLine中拿到CTRun的数组，再从CTRun读取delegate的信息，判断是否为特定的空白字符；

    
    
        // 计算图片所在位置
        CFArrayRef linesArr = CTFrameGetLines(frameRef);
        for (int i = 0; i < CFArrayGetCount(linesArr); ++i) {
            CTLineRef line = CFArrayGetValueAtIndex(linesArr, i);
            CFArrayRef runsArr = CTLineGetGlyphRuns(line);
            for (int j = 0; j < CFArrayGetCount(runsArr); ++j) {
                CTRunRef run = CFArrayGetValueAtIndex(runsArr, j);
                CTRunDelegateRef delegate = CFDictionaryGetValue(CTRunGetAttributes(run), kCTRunDelegateAttributeName);
                if (!delegate) {
                    continue;
                }
                NSValue *data = CTRunDelegateGetRefCon(delegate);
                if (!data) {
                    continue;
                }
                // 找到添加的特殊字符
                CGSize size = [data CGSizeValue];
                CGFloat offsetX;
                CTLineGetOffsetForStringIndex(line, CTRunGetStringRange(run).location, &offsetX);
                
                CGPoint lineOrigin;
                CTFrameGetLineOrigins(frameRef, CFRangeMake(i, 1), &lineOrigin); // 获取第i行的位置
                
                UIImage *image = [UIImage imageNamed:@"abc"];
                CGContextDrawImage(context, CGRectMake(lineOrigin.x + offsetX + marginX, lineOrigin.y, size.width, size.height), image.CGImage);
                // 如果用UIKit的方法进行绘制，会出现上下颠倒的情况
    //            [image drawInRect:CGRectMake(lineOrigin.x + offsetX + marginX, lineOrigin.y, size.width, size.height)];
            }
        }
    

3、创建图片并用前面找到的位置进行绘制，注意UIKit和CG坐标系的不同，如果直接使用UIImage的draw方法会出现上下颠倒的情况，所以这里使用CGContextDrawImage的绘制方式避免上下颠倒；

最终的绘制效果：

  

> 思考题：为什么图片底部会有一个浅绿色的区域？

### 五、一些讨论

#### iOS中的unichar、char和unicode的区别

char是基础的字符类型，一个字节；  
unichar是iOS定义的类型，实际是unsigned short，也就是UInt16；  
unicode与前两者的维度不同，指的是一种字符集，与其类似的概念是ASCII码；至于常见UTF8，是一种unicode的编码方式。

我们来看一段c的代码：  
这里的len会是多少？

    
    
        char s[] = "测试名字";
        int len = strlen(s);
        NSLog(@"len:%d", len);
    

结果：len:12。因此可以知道，当我们直接访问s[0]时，并不能读取到"测"字。

换一段oc的代码：  
这里的len会输出多少？当我们访问str的第一个字符时会返回什么？

    
    
        NSString *str = @"测试名字";
        NSLog(@"len:%d", str.length);
    

结果：len:4。当我们用`characterAtIndex`读取str第一个字符时，返回的是"测"字。

    
    
    (lldb) p [str characterAtIndex:0]
    (unichar) $0 = U+6d4b u'测'
    

**为什么会有这些不同的长度和字符读取结果？**

字符是一个虚拟的概念，要将字符存到字节流里面去，需要对其进行编码；同理，当我们拿到一串字节流，比如说上面的s[]数组（12Bytes的字节流），需要用特定的编码格式去读取。  
Xcode里面用的c字符串是用UTF8来编码，存到s[]字符数组中的长度是12；  
NSString的length是返回UTF16的长度，并不是字符的长度；可以尝试往字符中添加emoji表情或者其他占两个UInt16的字符，会发现length与字符长度不同，同样也无法用`characterAtIndex`读到对应的字符；

>
> 这样也是为什么我们在OC中无法像c语言一样，直接用str[0]去访问NSString的第一个字符，而是使用characterAtIndex的接口去获取（并且返回的是UTF16编码的字符）；  
>  另外，在iOS中NSUnicodeStringEncoding的编码方式就是NSUTF16StringEncoding。

关于Unicode更详细的介绍，见[百科](https://links.jianshu.com/go?to=https%3A%2F%2Fbaike.baidu.com%2Fitem%2FUnicode%2F750500%3Ffr%3Daladdin)。

#### FillColor和StrokeColor的区别

在用CGContext绘制的时候，经常需要设置颜色，常用的有下面两种：

    
    
    CG_EXTERN void CGContextSetFillColor(CGContextRef cg_nullable c,
        const CGFloat * cg_nullable components);
    CG_EXTERN void CGContextSetStrokeColor(CGContextRef cg_nullable c,
        const CGFloat * cg_nullable components);
    

那么Fill和Stroke两种颜色有什么区别？先看看英文的定义：

> Fill sets the color **inside the object** and stroke sets the color of the
> line drawn **around the object**.

用中文来表达，就是一个是填充颜色，一个是描边颜色。  
在iOS中，我们通过`NSForegroundColorAttributeName`和`NSStrokeColorAttributeName`这两个attribute来设置填充颜色。

    
    
        [stringAttributes setObject: [UIColor grayColor] forKey: NSForegroundColorAttributeName];
        [stringAttributes setObject: [NSNumber numberWithFloat: 0] forKey: NSStrokeWidthAttributeName];
        [stringAttributes setObject: [UIColor redColor] forKey: NSStrokeColorAttributeName];
    

当StrokeWidth为负数的时候，FillColor和StrokeColor同时存在，如下：

  

Fill灰色，Stroke红色，StrokeWidth=-3

  

当StrokeWidth为正数的时候，FillColor不生效，仅有StrokeColor，如下：

  

Fill灰色，Stroke红色，StrokeWidth=3

  
当StrokeWidth为0的时候，FillColor生效，StrokeColor无效果，如下：  

Fill灰色，Stroke红色，StrokeWidth=0

#### 图文混排中底部绿色区域

图文混排其实是排版时插入一个特殊的空白字符，并设定字符的宽高为特定size，预留对应size的空白，再算出对应位置的坐标，绘制上对应的图片。

  

根据测量，文字中图片的size确实为预设的文字大小，底部的浅绿色区域其实是排版时，一行的descent区域。  
回顾下我们设置图片宽高的代码：

    
    
    static CGFloat ascentCallback(void * refCon){
        NSValue *data = (__bridge NSValue *)refCon;
        return [data CGSizeValue].height;
    }
    
    static CGFloat descentCallback(void * refCon){
        return 0;
    }
    
    static CGFloat widthCallback(void * refCon){
        NSValue *data = (__bridge NSValue *)refCon;
        return [data CGSizeValue].width;
    }
    

实际上我们只设置了ascent为图片的高，width为图片的宽，descent设置的为0。但是一个CTLine往往包括多个文字，整行的descent实际上是所有字符的descent的最大值。同样的，一行的ascent也是行内所有字符的ascent最大值。

### 总结

本文详细介绍了CoreText的基础概念以及实际运用，如果理解完CoreText框架和文字排版、图文混排等知识，那么已经足够支撑做起一个阅读器啦，恭喜你。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CoreText实现图文混排](https://www.jianshu.com/p/6db3289fb05d)

系列文章： CoreText实现图文混排 CoreText实现图文混排之点击事件 CoreText实现图文混排之文...

[老司机Wicky](https://www.jianshu.com/u/a56ec10f6603)阅读 39,270评论 221赞 431

  * [CoreText(图文混排)详解+Demo](https://www.jianshu.com/p/ad4796df3dd6)

写这篇文章之前，在网上找了不少资料，也看了不少大牛们的文章；在这结合我自己对CoreText的理解，今晚整理...

[和之一](https://www.jianshu.com/u/412852c5fd0b)阅读 11,296评论 12赞 83

  * [iOS Text Part2:CoreText 图文混排](https://www.jianshu.com/p/82b510025a9e)

0\. 基本知识准备 0.1 字形( Glyph)基本了解 基础原点(Origin)首先是位于基线上处于基线最左侧的...

[破弓](https://www.jianshu.com/u/5394c122dfd8)阅读 2,754评论 4赞 24

  * [Swift之CoreText排版神器(长篇高能)](https://www.jianshu.com/p/e52a38e60e7c)

CoreText是一个进阶的比较底层的布局文本和处理字体的技术，CoreText API在OS X v10.5 和...

[smalldu](https://www.jianshu.com/u/d61ef5da631a)阅读 12,447评论 18赞 127

  * [CoreText图文混排](https://www.jianshu.com/p/6979e963a1d7)

最近在网上看了一些大牛的文章，自己也试着写了一下，感觉图文混排真的很强大。 废话不多说，开始整 先上效果图跟代码，...

[AllureJM](https://www.jianshu.com/u/65287fd16ea3)阅读 822评论 0赞 1

 