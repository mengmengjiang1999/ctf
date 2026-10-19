Objective-C的NSAttributedString学习笔记

[ 寻心_0a46](https://www.jianshu.com/u/46546c30f8db)关注赞赏支持

# Objective-C的NSAttributedString学习笔记

#### NSAttributedString - 属性字符串(富文本)

**一种字符串，它的部分文本具有相关的样式属性(如视觉样式、超链接或辅助功能数据)** 。

NSAttributedString对象管理字符串和应用于字符串中单个字符或字符范围的相关属性集(例如，字体和字距)。
**字符及其属性的关联称为属性字符串**
。集群的两个公共类NSAttributedString和NSMutableAttributedString分别声明只读属性字符串和可修改属性字符串的编程接口。

**属性字符串按照名称标识属性，使用NSDictionary对象在给定名称下存储值**
。可以将任何想要的属性名/值对分配给一系列字符，由应用程序来解释自定义属性（请参阅属性字符串编程指南）。如果在CoreText框架(用来做文字处理的框架)中使用属性字符串，也可以使用该框架定义的属性Key。

可以将属性字符串与接受它们的任何api(如Core
Text)一起使用。AppKit和UIKit框架还提供了NSMutableAttributedString的一个子类，称为NSTextStorage，为扩展文本处理系统提供存储。在iOS
6和更高版本中，可以使用属性化字符串在UITextView、UITextField和一些其他控件中显示格式化文本。AppKit和UIKit还定义了基本属性字符串接口的扩展，该接口允许在当前图形上下文中绘制它们的内容。

NSAttributedString对象的默认字体是Helvetica 12
point，这可能与平台的默认系统字体不同，因此为了适合应用程序可能需要创建非默认属性的新字符串。还可以使用NSParagraphStyle类及其子类NSMutableParagraphStyle封装NSAttributedString类使用的段落或标尺属性。

**注意，使用isEqual:方法比较NSAttributedString对象会寻找完全相等的值，比较包括逐个字符串的相等检查和所有属性的相等检查。如果字符串具有许多属性(例如附件、列表和表)，则这样的比较不太可能产生匹配**
。

##### NSAttributedString常用属性

    
    
    @property (readonly, copy) NSString *string;
    

**属性描述** ： 作为调用方的字符内容的NSString对象。

#### NSAttributedString常用函数

    
    
    - (NSDictionary<NSAttributedStringKey, id> *)attributesAtIndex:(NSUInteger)location effectiveRange:(nullable NSRangePointer)range;
    

**函数描述** ： **返回给定索引处字符的样式属性字典** 。如果索引超出调用方字符的结尾，则引发NSRangeException。

参数 ：

index：要返回其属性的索引，此值必须在调用方的范围内。

range： **对NSRange结构体的引用**
，如果结构体为NULL且指定的索引处应用了样式属性，则在返回时aRange包含样式属性覆盖的范围，如果指定的索引处没有应用样式属性，则在返回时aRange包含未应用样式属性的覆盖范围。此范围不一定是覆盖的最大范围，其范围取决于实现。如果需要最大范围，请使用attributesAtIndex:longestEffectiveRange:inRange:函数。如果不需要此值，请传递NULL。

返回值：索引处字符的属性。

#### NSAttributedString (NSExtendedAttributedString) - 分类对属性字符串的扩展

##### NSAttributedString (NSExtendedAttributedString) 常用属性

    
    
    @property (readonly) NSUInteger length;
    

**属性描述** ：调用方字符串对象的长度。

##### NSAttributedString (NSExtendedAttributedString) 常用函数

    
    
    - (nullable id)attribute:(NSAttributedStringKey)attrName atIndex:(NSUInteger)location effectiveRange:(nullable NSRangePointer)range;
    

**函数描述** ： **返回在给定索引处与给定样式属性名称绑定的样式属性的值** ，并通过对 **NSRange结构体的引用**
返回该属性样式应用的范围。

参数：

attrName ： 样式属性名称。

location：要返回其样式属性值的索引。此值不能超过调用方的边界，如果索引超出调用方字符的结尾，则引发NSRangeException。

range： **对NSRange结构体的引用**
，如果结构体为NULL且给定的样式属性名称存在于索引，则在返回时aRange包含与该样式属性名称绑定的属性值的范围。如果指定的索引中不存在给定的样式属性名称，则在返回时aRange包含与该样式属性名称绑定的的属性值不存在的范围。范围不一定是与attributeName参数绑定的属性值覆盖的最大范围，它的范围依赖于实现。如果需要最大范围，使用atIndex:longestEffectiveRange:inRange:函数。如果不需要此值，则传递NULL。

返回值：在指定索引位置且与样式属性名称绑定的属性的值，如果没有这样的属性，则为nil。

    
    
    - (NSAttributedString *)attributedSubstringFromRange:(NSRange)range;
    

**函数描述** ： **返回在调用方中给定范围内的字符和属性组成的NSAttributedString对象**
。如果aRange的任何部分超出了调用方字符的末尾，则引发NSRangeException。

参数：

range：创建新属性字符串的范围，range必须位于调用方的范围内。

返回值：一个NSAttributedString对象，在调用方中截取range范围中的字符和属性组成。

    
    
    - (NSDictionary<NSAttributedStringKey, id> *)attributesAtIndex:(NSUInteger)location longestEffectiveRange:(nullable NSRangePointer)range inRange:(NSRange)rangeLimit;
    

**函数描述** ： **返回给定索引处字符的属性，并通过对NSRange结构体的引用返回属性应用的范围**
。如果索引或rangeLimit的任何部分超出调用方字符的结尾，则引发NSRangeException。如果不需要范围信息，那么使用attributesAtIndex:effectiveRange:方法来检索属性值要有效得多。

参数 ：

location ： 要返回其属性的索引。此值不能超过调用方的边界。

range：如果非空，则返回时包含样式名称和样式值与索引处的样式名称和样式值相同的最大范围，剪裁为rangeLimit。

rangeLimit：在索引处搜索属性连续存在的范围。此值不能超过调用方的边界。

    
    
    - (nullable id)attribute:(NSAttributedStringKey)attrName atIndex:(NSUInteger)location longestEffectiveRange:(nullable NSRangePointer)range inRange:(NSRange)rangeLimit;
    

**函数描述** ： **返回在给定索引处与给定样式属性名称绑定的样式属性的值，并通过对NSRange结构体的引用返回该属性样式应用的范围**
。如果索引或rangeLimit的任何部分超出调用方字符的结尾，则引发NSRangeException。如果不需要范围信息，那么使用attributesAtIndex:effectiveRange:方法来检索属性值要有效得多。

参数 ：

attributeName：样式属性名称。

location：要返回其样式属性值的索引。此值不能超过调用方的边界，如果索引超出调用方字符的结尾，则引发NSRangeException。

range： **对NSRange结构体的引用**
，如果结构体为NULL且给定的样式属性名称存在于索引，则在返回时aRange包含与该样式属性名称绑定的属性值的范围，并剪裁为rangeLimit。如果指定的索引中不存在给定的样式属性名称，则在返回时aRange包含与该样式属性名称绑定的的属性值不存在的范围，并剪裁为rangeLimit。如果不需要此值，请传递NULL。

rangeLimit：搜索attributeName的连续存在的范围。此值不能超过调用方的边界。

返回值：在指定索引位置且与样式属性名称绑定的属性的值，如果没有这样的属性，则为nil。

    
    
    - (BOOL)isEqualToAttributedString:(NSAttributedString *)other;
    

**函数描述** ：返回一个布尔值，该值 **指示调用方是否等于另一个给定的属性字符串** 。属性字符串必须在字符和属性中都匹配才能相等。

参数 ：

other：用来比较调用方的属性字符串。

返回值：如果调用方等于other，则为“YES”，否则为“NO”。

    
    
    - (instancetype)initWithString:(NSString *)str;
    

**函数描述** ： **返回一个NSAttributedString对象** ，该对象由给定字符串的字符进行初始化，没有属性信息。

参数 ：

str ： 初始化新对象的字符串。

返回值：用str字符初始化的NSAttributedString对象，返回的对象可能与原始调用方不同，并且没有属性信息。

    
    
    - (instancetype)initWithString:(NSString *)str attributes:(nullable NSDictionary<NSAttributedStringKey, id> *)attrs;
    

**函数描述** ： **返回用给定字符串和样式属性初始化的NSAttributedString对象**
。返回一个NSAttributedString对象，用str的字符串和attrs中的属性初始化。返回的对象可能与原始调用方不同。

参数 ：

str：初始化新属性字符串的字符串。

attrs：新属性字符串的属性。

返回值 ： 返回用给定字符串和属性初始化的NSAttributedString对象。

    
    
    - (instancetype)initWithAttributedString:(NSAttributedString *)attrStr;
    

**函数描述** ：返回使用另一个给定属性字符串的字符和属性初始化的NSAttributedString对象。

参数：

attrStr ： 属性字符串。

返回值：用attributedString的字符和属性初始化的NSAttributedString对象。返回的对象可能与原始调用方不同。

    
    
    - (void)enumerateAttributesInRange:(NSRange)enumerationRange options:(NSAttributedStringEnumerationOptions)opts usingBlock:(void (NS_NOESCAPE ^)(NSDictionary<NSAttributedStringKey, id> *attrs, NSRange range, BOOL *stop))block API_AVAILABLE(macos(10.6), ios(4.0), watchos(2.0), tvos(9.0));
    

**函数描述** ： **在调用方枚举属性的范围内，为属性字符串中的每个属性范围执行指定的块**
。如果此方法由NSMutableAttributedString的实例调用，则仅当改变在提供给块的范围内时，才允许进行改变（删除、添加或更改）。改变后，枚举继续进行，范围紧跟在处理过的范围之后，根据改变引起的长度变化进行调整。例如，如果使用从位置N开始的范围调用块，并且该块删除所提供范围中的所有字符，则下一次调用也将传递N作为范围的位置。

参数 ：

enumerationRange：调用方枚举属性的范围。

opts：枚举使用的选项。

block：应用于属性字符串中属性范围的块。该块有三个参数：

  *     1. attrs：按名称键入的属性值字典。
  *     2. range：属性字符串中属性值的范围。
  *     3. stop:对布尔值的引用。块可以在块内将值设置为YES，以停止对属性字符串的进一步处理。

遍历的次数根据调用方枚举属性的范围内，根据应用样式属性的范围进行拆分，如图，图中的字符串在枚举范围全覆盖的情况下，会执行三次循环：

13778663-a9bbb8b6e66975b7.png

    
    
    - (void)enumerateAttribute:(NSAttributedStringKey)attrName inRange:(NSRange)enumerationRange options:(NSAttributedStringEnumerationOptions)opts usingBlock:(void (NS_NOESCAPE ^)(id _Nullable value, NSRange range, BOOL *stop))block API_AVAILABLE(macos(10.6), ios(4.0), watchos(2.0), tvos(9.0));
    

**函数描述** ： **在调用方枚举属性的范围内，为属性字符串中的每个属性范围执行指定的块并枚举指定样式属性名称的样式属性值**
。如果此方法由NSMutableAttributedString的实例调用，则仅当改变在提供给块的范围内时，才允许进行改变（删除、添加或更改）。改变后，枚举继续进行，范围紧跟在处理过的范围之后，根据改变引起的长度变化进行调整。例如，如果使用从位置N开始的范围调用块，并且该块删除所提供范围中的所有字符，则下一次调用也将传递N作为范围的位置。

参数 ：

attrName ： 要枚举的样式属性的名称。

opts：枚举属性值的范围。

block：应用于属性字符串中指定属性的范围的块。该块有三个参数：

  *     1. value：指定属性的值。
  *     2. range：属性字符串中属性值的范围。
  *     3. stop：对布尔值的引用。块可以在块内将值设置为YES，以停止对属性字符串的进一步处理。

    
    
    //属性值的范围提供的枚举方式：
    typedef NS_OPTIONS(NSUInteger, NSAttributedStringEnumerationOptions) {
      //使枚举反向发生。
      NSAttributedStringEnumerationReverse = (1UL << 1),
      //如果提供NSAttributedStringEnumerationLongestEffectiveRangeNotRequired选项，
      //则不执行最长有效范围计算；可以使用具有相同值的连续属性运行来调用块。
      NSAttributedStringEnumerationLongestEffectiveRangeNotRequired = (1UL << 20)
    };
    

#### NSAttributedString (NSAttributedStringDocumentFormats) - 文档格式分类

##### 常用函数

    
    
    - (nullable instancetype)initWithData:(NSData *)data options:(NSDictionary<NSAttributedStringDocumentReadingOptionKey, id> *)options documentAttributes:(NSDictionary<NSAttributedStringDocumentAttributeKey, id> * __nullable * __nullable)dict error:(NSError **)error API_AVAILABLE(macos(10.0), ios(7.0));
    

**函数描述** ： **初始化给定数据对象中包含的数据并返回新的属性字符串对象** 。不应从后台线程调用HTML导入器(即，选项字典包含值为
NSHTMLTextDocumentType 的
NSDocumentTypeDocumentAttribute)，它将尝试与主线程同步，失败并超时。从主线程调用它是有效的(但如果 HTML
包含对外部资源的引用，仍然会超时，应该不惜一切代价避免这种情况)。
HTML导入机制旨在实现诸如markdown之类的东西(即文本样式、颜色等)，而不是用于一般的HTML导入。

参数 ：

data ： 从中创建字符串的数据。

options
：用于解释文档内容的文档属性。支持选项键包括NSDocumentTypeDocumentAttribute、NSCharacterEncodingDocumentAttribute和NSDefaultAttributesDocumentAttribute。如果传递空字典，则该方法将检查数据以尝试确定适当的属性。

dict ： 包含文档属性中描述的文档级属性的输入输出字典。可以为空，在这种情况下不返回文档属性。

error ： 一个输入输出变量，包含遇到的错误(如果有的话)。

##### NSAttributedStringDocumentAttributeKey - 应用于文档的属性枚举

    
    
    typedef NSString * NSAttributedStringDocumentAttributeKey NS_TYPED_EXTENSIBLE_ENUM;
    

**类型描述** ： 应用于文档的属性枚举。

    
    
    UIKIT_EXTERN NSAttributedStringDocumentAttributeKey const NSDocumentTypeDocumentAttribute API_AVAILABLE(macos(10.0), ios(7.0)); 
    

**常量描述** ： 这个属性的值是NSAttributedStringDocumentType中声明的一种文档类型。
**对于reader(读取)方法，选项中的这个键可以指定解释内容的文档类型** 。在返回时，文档属性可以包含此键，用于指示用于读取内容的实际格式。
**对于write(写入)方法，此键指定生成数据的格式** 。

    
    
    UIKIT_EXTERN NSAttributedStringDocumentAttributeKey const NSCharacterEncodingDocumentAttribute API_AVAILABLE(macos(10.0), ios(7.0));
    

**常量描述** ： 此属性的值是一个包含整数的NSNumber对象，指定文件的NSStringEncoding，纯文本的默认值是默认编码。
**这个输入选项可以指定reader(读取)数据的字符串编码** 。返回时，文档属性可以包含实际使用的编码。
**对于write(写入)方法，此值用于生成纯文本数据** 。

    
    
    UIKIT_EXTERN NSAttributedStringDocumentAttributeKey const NSDefaultAttributesDocumentAttribute API_AVAILABLE(macos(10.11), ios(7.0));
    

**常量描述** ： 这个属性的值是一个NSDictionary对象，它包含应用于普通文件的属性。由reader方法使用。
**选项中的这个键可以指定应用于整个文档内容的默认属性。在返回时，文档属性可以包含这个键，指示实际使用的属性** 。

![\\color{red}{例如处理待html超链接标签的文本：}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%E5%A4%84%E7%90%86%E5%BE%85html%E8%B6%85%E9%93%BE%E6%8E%A5%E6%A0%87%E7%AD%BE%E7%9A%84%E6%96%87%E6%9C%AC%EF%BC%9A%7D)

    
    
    - (void)viewDidLoad {
        [super viewDidLoad];
        self.navigationItem.title = @"TTTAttributedLabel";
        
        NSString *htmlText = @"<a href=https://music.163.com/#/song?id=4900975>城南花已开</a>";
        
        UILabel *testLabel = [[UILabel alloc]initWithFrame:CGRectZero];
        testLabel.font = [UIFont systemFontOfSize:15];
        [self.view addSubview:testLabel];
        
        [testLabel mas_makeConstraints:^(MASConstraintMaker *make) {
            make.center.equalTo(self.view);
        }];
        
        testLabel.attributedText = [self handleHtmlText:htmlText];
        
        
    }
    
    - (NSMutableAttributedString *)handleHtmlText:(NSString *)htmlText{
        
        NSMutableAttributedString * attrStr = [[NSMutableAttributedString alloc]
                                              initWithData:[htmlText dataUsingEncoding:
                                              NSUnicodeStringEncoding]
                                              options:@{
                                                NSDocumentTypeDocumentAttribute:
                                                NSHTMLTextDocumentType,
                                              }
                                              documentAttributes:nil error:nil];
        return attrStr;
    }
    
    @end
    

样式如图：

截屏2020-06-09下午11.26.14.png

#### NSAttributedString (NSAttributedStringAttachmentConveniences) - 附件便利性分类

    
    
    + (NSAttributedString *)attributedStringWithAttachment:(NSTextAttachment *)attachment API_AVAILABLE(macos(10.0), ios(7.0));
    

**函数描述** ： 创建带有附件的属性字符串， **例如用于图文混排**
。这是使用NSAttachmentCharacter作为基字符创建包含附件的属性字符串的方便方法。

参数 ：

attachment ：附件。

返回值 ： 包含附件的属性字符串。

![\\color{red}{例如简单的图文混排，插入图片小标签：}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%E7%AE%80%E5%8D%95%E7%9A%84%E5%9B%BE%E6%96%87%E6%B7%B7%E6%8E%92%EF%BC%8C%E6%8F%92%E5%85%A5%E5%9B%BE%E7%89%87%E5%B0%8F%E6%A0%87%E7%AD%BE%EF%BC%9A%7D)

截屏2022-09-01 16.13.12.png

这个代码就有点长了， **首先需要一个UIImage的分类，实现如下方法：**

    
    
    ///绘制带有文本、颜色、圆角的图片
    + (UIImage *)imageWithText:(NSString *)text font:(UIFont *)font fillColor:(CGColorRef)fillColor cornerRadius:(CGFloat)cornerRadius{
        //返回使用指定字体所需要的边框大小
        CGSize textSize = [text sizeWithAttributes:@{NSFontAttributeName:font}];
        //设置图片的框架矩形
        textSize.width = 8.0 + ceil(textSize.width);
        textSize.height = 2.0 + ceil(textSize.height) ;
        CGRect imageFrame = {0, 0, textSize};
        //创建基于位图的图形上下文并使其成为当前上下文。
        UIGraphicsBeginImageContext(imageFrame.size);
        //返回当前图形上下文
        CGContextRef context = UIGraphicsGetCurrentContext();
        //使用CGColor设置图形上下文中的当前填充颜色
        CGContextSetFillColorWithColor(context, fillColor);
        //使用当前图形状态中的填充颜色绘制所提供矩形中包含的区域。
        CGContextFillRect(context, imageFrame);
        //根据当前基于位图的图形上下文的内容返回图像。
        UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
        //从堆栈顶部移除当前基于位图的图形上下文。
        UIGraphicsEndImageContext();
        //设置图片圆角
        UIImage *circleImage = [image setCornerRadius:cornerRadius];
        
        UIImage *textImage = [circleImage addText:text withFont:font];
    
        return textImage;
    }
    
    ///设置图片圆角
    - (UIImage *)setCornerRadius:(CGFloat)cornerRadius {
        //创建一个临时渲染上下文，在这上面绘制原始图片
        UIGraphicsBeginImageContextWithOptions(self.size, NO, [[UIScreen mainScreen] scale]);
        //图片的框架矩形
        CGRect imageRect = {0, 0, self.size};
        //创建并返回用圆角矩形路径初始化的新UIBezierPath对象
        UIBezierPath *path = [UIBezierPath bezierPathWithRoundedRect:imageRect cornerRadius:cornerRadius];
        //将Path添加到上下文中
        CGContextAddPath(UIGraphicsGetCurrentContext(), path.CGPath);
        //裁剪上下文
        CGContextClip(UIGraphicsGetCurrentContext());
        //在指定的矩形中绘制整个图像，并根据需要进行缩放
        [self drawInRect:imageRect];
        //从当前环境当中得到重绘的图片
        UIImage *circleImag = UIGraphicsGetImageFromCurrentImageContext();
        //从堆栈顶部移除当前基于位图的图形上下文。
        UIGraphicsEndImageContext();
        //返回绘制的图片
        return circleImag;
    }
    
    ///绘制指定字体的文本到图片中
    - (UIImage *)addText:(NSString *)text withFont:(UIFont *)font {
        //  1.获取上下文
        UIGraphicsBeginImageContextWithOptions(self.size, NO, [[UIScreen mainScreen] scale]);
        //  2.绘制图片
        CGRect imageRect = {0, 0, self.size};
        //  在指定的矩形中绘制整个图像，并根据需要进行缩放
        [self drawInRect:imageRect];
        //  3.绘制文字
        CGRect textRect = CGRectInset(imageRect, 2.0, 1.0);
        //  段落样式布局对象
        NSMutableParagraphStyle *style = [[NSMutableParagraphStyle defaultParagraphStyle] mutableCopy];
        //  文字对齐方式
        style.alignment = NSTextAlignmentCenter;
        //  文字的属性
        NSDictionary *attributes = @{NSFontAttributeName: font,
                                     NSParagraphStyleAttributeName:style,
                                     NSForegroundColorAttributeName:[UIColor whiteColor]};
        //  将文字绘制上去
        [text drawInRect:textRect withAttributes:attributes];
        //  获取绘制到得图片
        UIImage *textImage = UIGraphicsGetImageFromCurrentImageContext();
        //  结束图片的绘制
        UIGraphicsEndImageContext();
        //  返回绘制的图片
        return textImage;
    }
    

然后在需要添加标签的视图中实现添加标签的方法：

    
    
    /// 带标签的富文本
    /// @param labelContentArray 标签内容数组
    /// @param labelColorArray 标签颜色数组
    /// @param contentString 要插入标签的内容
    - (NSMutableAttributedString *)carryLabelOfAttributedStringWithLabelContentArray:(NSArray<NSString *> *)labelContentArray withLabelColorArray:(NSArray<UIColor *> *)labelColorArray withContentString:(NSString *)contentString{
        //初始化要加入标签的富文本
        NSMutableAttributedString *contentAttributedString = [[NSMutableAttributedString alloc]initWithString:contentString];
        //初始化用于存放转为图片对象的标签内容数组
        NSMutableArray<UIImage *> *labelImages = [[NSMutableArray alloc] initWithCapacity:3];
        //标签内容数组不为空
        if(labelContentArray.count){
            //标签的圆角
            CGFloat const cornerRadius = 3.0;
            //标签的字体
            UIFont * const font = [UIFont systemFontOfSize:15.0 weight:UIFontWeightBold];
            //记录转为标签的图片
            UIImage *labelImage;
            //遍历标签内容数组
            for (int i = 0; i < labelContentArray.count; i++) {
                //获取标签内容
                NSString *labelContentString = labelContentArray[I];
                //获取标签颜色
                UIColor *labelColor = [UIColor blackColor];
                if (labelColorArray.count) {
                    if (i < labelColorArray.count) {
                        labelColor = labelColorArray[I];
                    } else {
                        labelColor = labelColorArray.lastObject;
                    }
                }
                //标签内容不为空
                if(labelContentString.length){
                    //获取标签图片
                    labelImage = [UIImage imageWithText:labelContentString font:font fillColor:labelColor.CGColor cornerRadius:cornerRadius];
                    //如果标签图片不为空
                    if (labelImage) {
                        //添加标签图片到标签图片数组
                        [labelImages addObject:labelImage];
                    }
                }
            }
        }else{
            //返回要加入标签的富文本
            return contentAttributedString;
        }
        //遍历标签图片数组
        for (UIImage *image in labelImages.reverseObjectEnumerator.allObjects) {
            //初始化文本与附件排版对象
            NSTextAttachment *attachment = [[NSTextAttachment alloc] init];
            //设置文本附件内容的图像
            attachment.image = image;
            //定义文本坐标系中调用方图形表示的布局界限
            attachment.bounds = CGRectMake(0, -3.0, image.size.width, image.size.height);
            //初始化空格富文本对象
            NSAttributedString *spaceString = [[NSAttributedString alloc] initWithString:@" "];
            //每次循环先插入一个空格
            [contentAttributedString insertAttributedString:spaceString atIndex:0];
            //文本与附件排版对象转为标签富文本
            NSAttributedString *labelContentAttribute = [NSAttributedString attributedStringWithAttachment:attachment];
            //插入标签富文本
            [contentAttributedString insertAttributedString:labelContentAttribute atIndex:0];
        }
        //返回插入标签富文本后的内容
        return contentAttributedString;
    }
    

添加标签：

    
    
    UILabel *testLabel = [[UILabel alloc]initWithFrame:CGRectZero];
        testLabel.font = [UIFont systemFontOfSize:20];
        testLabel.attributedText = [self carryLabelOfAttributedStringWithLabelContentArray:@[@"满减",@"返现",@"显示折扣"] withLabelColorArray:@[[UIColor redColor],[UIColor blueColor],[UIColor purpleColor]] withContentString:@"测试标签文本"];
        [self.view addSubview:testLabel];
        testLabel.translatesAutoresizingMaskIntoConstraints = NO;
        [NSLayoutConstraint activateConstraints:@[
            [testLabel.centerXAnchor constraintEqualToAnchor:self.view.centerXAnchor],
            [testLabel.centerYAnchor constraintEqualToAnchor:self.view.centerYAnchor],
        ]];
    

截屏2022-09-01 16.25.38.png

#### NSMutableAttributedString - 可变属性字符串(富文本)

**一个可变字符串对象** ，它还包含与其文本内容的各个部分相关联的属性（如视觉样式、超链接或辅助功能数据）。

NSMutableAttributedString类声明了用于改变属性字符串内容的其他方法。可以单独添加和删除字符（原始字符串）和属性，也可以整体作为属性字符串一起添加和删除。

**NSMutableAttributedString在NSAttributedString的基础上增加了两个原始方法，这些原始方法为其类中的所有其他方法提供了基础**
。原始的replaceCharactersInRange:withString:方法用字符串中的字符替换一系列字符，使该范围之外的所有属性信息保持不变。原始setAttributes:range:
方法为给定的字符范围设置属性和值，替换该范围的任何先前的属性和值。

##### NSMutableAttributedString提供的函数

    
    
    - (void)replaceCharactersInRange:(NSRange)range withString:(NSString *)str;
    

**函数描述** ： **用给定字符串的字符替换给定范围内的字符**
。新字符从range继承第一个替换字符的样式属性。如果range的长度为0，则新字符继承range前面的字符(如果有的话)的样式属性，否则继承range后面的字符的样式属性。如果range的任何部分超出调用方字符的结尾，则引发NSRangeException。

参数 ：

range ： 指定要替换的字符的范围。

str ： 一个字符串，指定替换range范围内的字符。

    
    
    - (void)setAttributes:(nullable NSDictionary<NSAttributedStringKey, id> *)attrs range:(NSRange)range;
    

**函数描述** ： **将指定范围内字符的样式属性设置为指定的样式属性**
，这些新属性替换以前与aRange中的字符关联的任何样式属性。如果range的任何部分超出调用方字符的结尾，则引发NSRangeException。

参数 ：

attributes ： 包含要设置的属性的字典。属性键可以由另一个框架提供，也可以是定义的自定义键。

range：其属性已设置的字符范围。

#### NSMutableAttributedString (NSExtendedMutableAttributedString) - 扩展分类

    
    
    - (void)addAttribute:(NSAttributedStringKey)name value:(id)value range:(NSRange)range;
    

**函数描述** ： **将具有给定名称和值的样式属性添加到指定范围内的字符**
，可以将任何希望的名称/值对分配给一系列字符。如果名称或值为nil，则引发NSInvalidArgumentException；如果range的任何部分超出了调用方字符的结尾，则引发NSRangeException。

参数 ：

name ： 指定属性名的字符串。属性键可以由另一个框架提供，也可以是定义的自定义键。

value ： 与名称关联的属性值。

range ： 应用指定属性/值对的字符范围。

    
    
    - (void)addAttributes:(NSDictionary<NSAttributedStringKey, id> *)attrs range:(NSRange)range;
    

**函数描述** ： **将给定的属性集合添加到指定范围内的字符**
，可以将任何希望的名称/值对分配给一系列字符。如果属性为nil，则引发NSInvalidArgumentException；如果aRange的任何部分位于调用方字符的末尾之外，则引发NSRangeException。

参数 ：

attrs ： 包含要添加的属性的字典。属性键可以由另一个框架提供，也可以是定义的自定义键。

range ： 应用指定属性的字符范围。

    
    
    - (void)replaceCharactersInRange:(NSRange)range withAttributedString:(NSAttributedString *)attrString;
    

**函数描述**
：调用方将给定范围内的字符和属性替换为参数给定属性字符串的字符和属性。如果range的任何部分超出调用方字符的结尾，则引发NSRangeException。

参数 ：

range ： 替换的字符和属性的范围。

attrString ： 属性字符串，其字符和属性替换指定范围内的字符和属性。

    
    
    - (void)insertAttributedString:(NSAttributedString *)attrString atIndex:(NSUInteger)loc;
    

**函数描述** ： **将给定属性字符串的字符和属性插入到调用方中给定的索引处**
。新的字符和属性从给定的索引开始，现有的字符和属性从索引到调用方的末端将按属性字符串的长度移动。如果索引超出调用方字符的结尾，则引发NSRangeException。

参数 ：

attrString ： 插入其字符和属性的字符串。

loc ： 插入字符和属性的索引。

    
    
    - (void)appendAttributedString:(NSAttributedString *)attrString;
    

**函数描述** ：将给定属性字符串的字符和属性添加到调用方的 **末尾** 。

参数 ：

attrString ： 添加字符和属性的字符串。

    
    
    - (void)deleteCharactersInRange:(NSRange)range;
    

**函数描述** ： **删除给定范围内的字符及其相关属性** 。如果aRange的任何部分超出调用方字符的结尾，则引发NSRangeException。

参数：

range ： 指定要删除的字符的范围。

    
    
    - (void)setAttributedString:(NSAttributedString *)attrString;
    

**函数描述** ： 用给定属性字符串的字符和属性替换调用方的 **全部内容** 。

参数 ：

attrString ： 属性字符串，其字符和属性替换调用方中的字符和属性。

    
    
    - (void)removeAttribute:(NSAttributedStringKey)name range:(NSRange)range;
    

**函数描述** ： **从指定范围内的字符中删除命名属性** 。如果range的任何部分超出调用方字符的结尾，则引发NSRangeException。

参数 ：

name ： 指定要删除的属性名的字符串。属性键可以由另一个框架提供，也可以是定义的自定义键。

range ：从中删除指定属性的字符范围。

![\\color{red}{例如按比例修改属性字符串字体大小 ：
}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%E6%8C%89%E6%AF%94%E4%BE%8B%E4%BF%AE%E6%94%B9%E5%B1%9E%E6%80%A7%E5%AD%97%E7%AC%A6%E4%B8%B2%E5%AD%97%E4%BD%93%E5%A4%A7%E5%B0%8F%20%EF%BC%9A%20%7D)

    
    
    //需要引入#import<CoreText/CoreText.h>
    
    - (void)viewDidLoad {
        [super viewDidLoad];
        self.navigationItem.title = @"TTTAttributedLabel";
        
        UILabel *testLabel = [[UILabel alloc]initWithFrame:CGRectZero];
        NSAttributedString *attarbuteString = [[NSAttributedString alloc]initWithString:@"城南花已开" attributes:@{
            (NSString *)kCTFontAttributeName:[UIFont systemFontOfSize:30],
        }];
        [self.view addSubview:testLabel];
        [testLabel mas_makeConstraints:^(MASConstraintMaker *make) {
            make.center.equalTo(self.view);
        }];
        
        testLabel.attributedText = NSAttributedStringByScalingFontSize(attarbuteString,0.5);
      
    }
    
    ///按比例缩放属性字符串字体大小
    static inline NSAttributedString * NSAttributedStringByScalingFontSize(NSAttributedString *attributedString, CGFloat scale) {
        //NSAttributedString转NSMutableAttributedString
        NSMutableAttributedString *mutableAttributedString = [attributedString mutableCopy];
        //为属性字符串中特定属性的每个范围执行指定的块
        [mutableAttributedString enumerateAttribute:(NSString *)kCTFontAttributeName inRange:NSMakeRange(0, [mutableAttributedString length]) options:0 usingBlock:^(id value, NSRange range, BOOL * __unused stop) {
            //获取字体对象
            UIFont *font = (UIFont *)value;
            //如果存在字体对象
            if (font) {
                //声明字体名称变量
                NSString *fontName;
                //获取字体的大小
                CGFloat pointSize;
                //字体对象是UIFont类
                if ([font isKindOfClass:[UIFont class]]) {
                    //获取字体名称
                    fontName = font.fontName;
                    //获取字体大小
                    pointSize = font.pointSize;
                } else {
                    //通过CFStringRef对象转为NSString获取字体名称
                    fontName = (NSString *)CFBridgingRelease(CTFontCopyName((__bridge CTFontRef)font, kCTFontPostScriptNameKey));
                    //获取字体大小
                    pointSize = CTFontGetSize((__bridge CTFontRef)font);
                }
                //从指定范围内的字符中删除字体属性
                [mutableAttributedString removeAttribute:(NSString *)kCTFontAttributeName range:range];
                //设置给定名称的新字体引用。
                CTFontRef fontRef = CTFontCreateWithName((__bridge CFStringRef)fontName, floorf(pointSize * scale), NULL);
                //将字体名称和计算字体大小的值的属性添加到指定范围内的字符
                [mutableAttributedString addAttribute:(NSString *)kCTFontAttributeName value:(__bridge id)fontRef range:range];
                //释放CTFontRef对象
                CFRelease(fontRef);
            }
        }];
        //返回新的属性字符串
        return mutableAttributedString;
    }
    
    

截屏2022-09-01 16.56.33.png

截屏2022-09-01 16.57.53.png

    
    
    - (void)beginEditing;
    

**函数描述** ： **由子类重写以缓冲或优化对调用方字符或属性的一系列更改**
，直到它收到匹配的endEditing消息，在此消息上，它可以合并更改并通知任何观察者它已更改。可以嵌套beginEditing和endEditing消息对。

    
    
    - (void)endEditing;
    

**函数描述** ： **由子类重写，以合并自上一个beginEditing消息以来所做的更改** ，并将更改通知任何观察者。

#### 文本的预定义字符属性Key - 样式属性的名称Key

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSFontAttributeName API_AVAILABLE(macos(10.0), ios(6.0)); 
    

**常量描述** ： 这个属性的值是一个UIFont对象，使用此属性 **可更改文本范围的字体** 。如果未指定此属性，则该字符串默认使用Helvetica
12 point(Neue)字体。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSForegroundColorAttributeName API_AVAILABLE(macos(10.0), ios(6.0));
    

**常量描述** ： 此属性的值是UIColor对象，使用此属性可以 **指定渲染期间文本的颜色** 。如果未指定此属性，则文本将呈现为黑色。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSBackgroundColorAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 此属性的值是UIColor对象，使用此属性 **指定文本后面背景区域的颜色** 。如果未指定此属性，则不会绘制背景色。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSLigatureAttributeName API_AVAILABLE(macos(10.0), ios(6.0)); 
    

**常量描述** ： 设置 **连体属性** ，取值为NSNumber 对象(整数)，0 表示没有连体字符，1 表示使用默认的连体字符。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSKernAttributeName API_AVAILABLE(macos(10.0), ios(6.0)); 
    

**常量描述** ： 此属性的值是包含浮点值的NSNumber对象。 **设定字符间距**
，字距调整可防止特定字符之间出现不需要的空格，具体取决于字体。值0表示已禁用紧排，此属性的默认值为0。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSUnderlineStyleAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 此属性的值是包含整数的NSNumber对象，并与NSUnderlineStyle中描述的常量之一相对应。此值
**指示文本是否带下划线** ，此属性的默认值为NSUnderlineStyleNone。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSUnderlineColorAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 设置 **下划线颜色** ，此属性的值是UIColor对象。默认值为nil。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSStrokeColorAttributeName API_AVAILABLE(macos(10.0), ios(6.0));
    

**常量描述** ：
这个参数的值是一个UIColor对象。如果它没有定义(这是默认情况)，它被假设为与NSForegroundColorAttributeName的值相同，否则它描述
**轮廓颜色** 。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSStrokeWidthAttributeName API_AVAILABLE(macos(10.0), ios(6.0));
    

**常量描述** ： 此属性的值是包含浮点值的NSNumber对象。此值表示更改 **笔划宽度**
的量，并指定为字体点大小的百分比。指定0(默认值)不进行其他更改，负值填充效果，正值中空效果。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSTextEffectAttributeName API_AVAILABLE(macos(10.10), ios(7.0));
    

**常量描述** ： 设置 **文本特殊效果** ，取值为 NSString 对象，目前只有图版印刷效果可用。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSLinkAttributeName API_AVAILABLE(macos(10.0), ios(7.0));
    

**常量描述** ： 设置 **链接属性** ，点击后调用浏览器打开指定URL地址。
**不能在UILabel和UITextField使用，只能用UITextView来进行** 。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSBaselineOffsetAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： **文本位置的垂直偏移**
。此属性的值是一个NSNumber对象，包含一个浮点值，该值指示字符与基线的偏移量(以点为单位)。默认值为0，正值上偏，负值下偏。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSObliquenessAttributeName API_AVAILABLE(macos(10.0), ios(7.0));
    

**常量描述** ： 此属性的值是一个NSNumber对象，其中包含一个浮点值，指示要应用于 **字形的倾斜**
。默认值为0，表示没有倾斜，正值右倾，负值左倾。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSExpansionAttributeName API_AVAILABLE(macos(10.0), ios(7.0));  
    

**常量描述** ： 此属性的值是一个包含浮点值的NSNumber对象，设置 **文本横向拉伸属性** ，默认值为0，正值横向拉伸文本，负值横向压缩文本。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSWritingDirectionAttributeName API_AVAILABLE(macos(10.6), ios(7.0));
    

**常量描述** ： 此属性的值是一个NSArray对象，设置 **文字书写方向** ，从左向右书写或者从右向左书写。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSVerticalGlyphFormAttributeName API_AVAILABLE(macos(10.7), ios(6.0)); 
    

**常量描述** ： 此属性的值是包含整数的NSNumber对象。值0表示水平文本，值1表示垂直文本。
**在iOS中，始终使用水平文本，并且未定义指定不同的值** 。

![\\color{red}{部分属性样式示例代码：
}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E9%83%A8%E5%88%86%E5%B1%9E%E6%80%A7%E6%A0%B7%E5%BC%8F%E7%A4%BA%E4%BE%8B%E4%BB%A3%E7%A0%81%EF%BC%9A%20%7D)

    
    
    @implementation TestTTTAttributedLabelViewController
    
    - (void)viewDidLoad {
        [super viewDidLoad];
        self.navigationItem.title = @"TTTAttributedLabel";
        
        NSString *termLabelText = @"距离成熟还有：30天";
        
        UILabel *testLabel = [[UILabel alloc]initWithFrame:CGRectZero];
        testLabel.font = [UIFont systemFontOfSize:15];
        [self.view addSubview:testLabel];
        
        [testLabel mas_makeConstraints:^(MASConstraintMaker *make) {
            make.center.equalTo(self.view);
        }];
        
        NSRange range = [termLabelText rangeOfString:@"："];
        NSMutableAttributedString *attributedTermLabelText = [[NSMutableAttributedString alloc]initWithString:termLabelText];
        
        [attributedTermLabelText addAttributes:@{
            //文本字体
            NSFontAttributeName : [UIFont systemFontOfSize:20],
            //文本颜色
            NSForegroundColorAttributeName:[UIColor redColor],
            //文本背景色
            NSBackgroundColorAttributeName : [UIColor greenColor],
            //文本字间距
            NSKernAttributeName:@(5.0),
            //下划线
            NSUnderlineStyleAttributeName : @(NSUnderlineStyleSingle),
            //下划线颜色
            NSUnderlineColorAttributeName : [UIColor blueColor],
            //笔画宽度
            NSStrokeWidthAttributeName:@(3.5),
            //文本特殊效果，目前只有图版印刷效果可用
            NSTextEffectAttributeName : NSTextEffectLetterpressStyle,
            //设置基线偏移值,正值上偏，负值下偏。
            NSBaselineOffsetAttributeName:@(5.0),
            //文本倾斜，正值右倾，负值左倾
            NSObliquenessAttributeName : @(-0.5),
            //文本横向拉伸,正值横向拉伸文本，负值横向压缩文本。
            NSExpansionAttributeName:@(0.5),
            //设置文字书写方向@[@(1)]从左到右，@[@(3)]从右到左
            NSWritingDirectionAttributeName:@[@(3)],
            
        } range:NSMakeRange(range.location + 1, termLabelText.length - (range.location + 2))];
        
        testLabel.attributedText = attributedTermLabelText;
        
    }
    
    @end
    

样式如图 ：

截屏2020-06-10下午9.04.26.png

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSAttachmentAttributeName API_AVAILABLE(macos(10.0), ios(7.0));
    

**常量描述** ： 设置 **文本附件** ，取值为NSTextAttachment对象， **常用于文字图片混排** 。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSShadowAttributeName API_AVAILABLE(macos(10.0), ios(6.0));  
    

**常量描述** ： 此属性的值是NSShadow对象。此属性的默认值为nil。表示与文本字体色相同。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSStrikethroughStyleAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 设置 **删除线**
，此属性的值是包含整数的NSNumber对象。此值指示文本是否有一条线穿过它，并与NSUnderlineStyle中描述的常量之一相对应。此属性的默认值为NSUnderlineStyleNone。

![\\color{red}{例如：设置一条删除线
}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%EF%BC%9A%E8%AE%BE%E7%BD%AE%E4%B8%80%E6%9D%A1%E5%88%A0%E9%99%A4%E7%BA%BF%20%7D)

    
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        self.view.backgroundColor = [UIColor whiteColor];
        UILabel *label2 = [[UILabel alloc]initWithFrame:CGRectZero];
        label2.attributedText = [self attributeSingleLine:@"我被划线了，要失业了"];
        label2.textColor = [UIColor redColor];
        label2.numberOfLines = 0;
        label2.allowsDefaultTighteningForTruncation = NO;
        [self.view addSubview:label2];
        [label2 mas_makeConstraints:^(MASConstraintMaker *make) {
            make.center.equalTo(self.view);
            make.left.equalTo(self.view.mas_left).offset(100);
            make.right.equalTo(self.view.mas_right).offset(-100);
        }];
    }
    
    ///文本添加删除线
    - (NSAttributedString *)attributeSingleLine:(NSString *)str{
        //富文本设置（删除线）
        NSMutableAttributedString *Att = [[NSMutableAttributedString alloc]initWithString:str];
        NSUInteger length = [Att length];
        [Att addAttribute:NSStrikethroughStyleAttributeName value:@(NSUnderlinePatternSolid | NSUnderlineStyleSingle) range:NSMakeRange(0, length)];
        return Att;
    
    }
    

样式如图 ：

截屏2020-12-22上午9.50.53.png

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSStrikethroughColorAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 设置 **删除线颜色** ，此属性的值是UIColor对象。默认值为nil，表示与文本字体色相同。

    
    
    UIKIT_EXTERN NSAttributedStringKey const NSParagraphStyleAttributeName API_AVAILABLE(macos(10.0),
    

**常量描述** ： 此属性的值是NSParagraphStyle对象。设置 **文本段落排版格式** ，如设置首行，行间距，对齐方式等。

![\\color{red}{例如 ：调整文本间距
}](https://math.jianshu.com/math?formula=%5Ccolor%7Bred%7D%7B%E4%BE%8B%E5%A6%82%20%EF%BC%9A%E8%B0%83%E6%95%B4%E6%96%87%E6%9C%AC%E9%97%B4%E8%B7%9D%20%7D)

    
    
    - (void)viewDidLoad {
    
        [super viewDidLoad];
        self.view.backgroundColor = [UIColor whiteColor];
        UILabel *label2 = [[UILabel alloc]initWithFrame:CGRectZero];
        label2.attributedText = [self getAttributedWithString:@"测试标签,内容也挺多的，最起码要能换个行吧，要不怎么测试行间距呢，没办法测试的啊" WithLineSpace:10 kern:10 font:[UIFont systemFontOfSize:18.0]];
        label2.textColor = [UIColor redColor];
        label2.numberOfLines = 0;
        label2.allowsDefaultTighteningForTruncation = NO;
        [self.view addSubview:label2];
        [label2 mas_makeConstraints:^(MASConstraintMaker *make) {
            make.center.equalTo(self.view);
            make.left.equalTo(self.view.mas_left).offset(100);
            make.right.equalTo(self.view.mas_right).offset(-100);
        }];
    }
    
    /**
     调整文本间距
     @parameter string 要调整的文本
     @parameter lineSpace 行间距
     @parameter kern 字符间距
     @parameter font 字体
     */
    - (NSAttributedString *)getAttributedWithString:(NSString *)string WithLineSpace:(CGFloat)lineSpace kern:(CGFloat)kern font:(UIFont *)font{
        NSMutableParagraphStyle *paragraphStyle = [NSMutableParagraphStyle new];
        //调整行间距
        paragraphStyle.lineSpacing = lineSpace;
        NSDictionary *attriDict = @{NSParagraphStyleAttributeName:paragraphStyle,NSKernAttributeName:@(kern),
                                    NSFontAttributeName:font};
        NSMutableAttributedString *attributedString = [[NSMutableAttributedString alloc]initWithString:string attributes:attriDict];
        return attributedString;
    }
    
    

样式如图 ：

截屏2020-12-22上午9.41.06.png

**注：文本如果设置了间距，那么计算文本高度时一定要将间距计算进去，否则会影响文本高度计算的结果** 。例如计算这段文本：

不加间距的情况下：

    
    
    CGSize size = [@"测试标签,内容也挺多的，最起码要能换个行吧，要不怎么测试行间距呢，没办法测试的啊" boundingRectWithSize:CGSizeMake([UIScreen mainScreen].bounds.size.width, MAXFLOAT)
                                                  options:NSStringDrawingUsesLineFragmentOrigin | NSStringDrawingUsesFontLeading
                                         attributes:@{NSFontAttributeName:[UIFont systemFontOfSize:18.0],
                                                      
                                                    }
                                                  context:nil].size;
        NSLog(@"%f",size.height);
    

输出高度为:

截屏2020-12-22上午10.01.12.png

在标签中显示的实际文本高度为：

截屏2020-12-22上午10.01.59.png

加上字符间距与行间距的情况下：

    
    
    NSMutableParagraphStyle *paragraphStyle = [[NSParagraphStyle defaultParagraphStyle] mutableCopy];
        paragraphStyle.lineSpacing = 10;
        
        CGSize size = [@"测试标签,内容也挺多的，最起码要能换个行吧，要不怎么测试行间距呢，没办法测试的啊" boundingRectWithSize:CGSizeMake([UIScreen mainScreen].bounds.size.width - 200, MAXFLOAT)
                                                  options:NSStringDrawingUsesLineFragmentOrigin | NSStringDrawingUsesFontLeading
                                         attributes:@{NSFontAttributeName:[UIFont systemFontOfSize:18.0],
                                                      NSParagraphStyleAttributeName : paragraphStyle,
                                                      NSKernAttributeName:@(10),
                                                    }
                                                  context:nil].size;
        NSLog(@"%f",size.height);
    

输出高度则比较接近，为：

截屏2020-12-22上午10.11.00.png

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [bash](https://www.jianshu.com/p/62627fb82138)

官网 中文版本 好的网站 Content-type: text/htmlBASH Section: User ...

[不排版](https://www.jianshu.com/u/97702e424c5d)阅读 4,090评论 0赞 5

  * [面试题](https://www.jianshu.com/p/971865470673)

Swift1> Swift和OC的区别1.1> Swift没有地址/指针的概念1.2> 泛型1.3> 类型严谨 对...

[cosWriter](https://www.jianshu.com/u/8626d3f52ac7)阅读 10,702评论 1赞 32

  * [一方水土一方乐 笔记（二）](https://www.jianshu.com/p/0affa1402e0a)

内蒙古长短调 杨玉成老师授课

[如果我名王玉珏](https://www.jianshu.com/u/7a827c01c37c)阅读 107评论 0赞 1

  * [如何在互联网时代当老板？经商的理念](https://www.jianshu.com/p/ac70bb160689)

如何在互联网时代当老板？ 1、建立一个QQ群，把所有团队成员都拉进去，老板讲什么，团队成员都知道，团队成员讲什么。...

[做一个正能量的人](https://www.jianshu.com/u/d3fb2fae3ab6)阅读 503评论 0赞 4

  * [无题](https://www.jianshu.com/p/1bb8d17a9ef7)

我把心举过头顶 献给穹宇 它却投我以阴影 错不在爱， 而在沿爱而伸的路径

[柴小扉](https://www.jianshu.com/u/45be0458a688)阅读 272评论 7赞 5

 