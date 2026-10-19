Runtime中的Method Swizzle

[ BrianWang](https://www.jianshu.com/u/00084b53d83c)关注赞赏支持

# Runtime中的Method Swizzle

## 示例: 一键改字体

**1.** 工程的Info.plist文件中需添加:

Info.plist添加内容.png

  

其中loveway.ttf为字体册资源文件的名称.

**2.** Category类  
`UILabel+FontChange.h`

    
    
    //
    //  UILabel+FontChange.h
    //  FontChangeProject
    //
    //  Created by Brian on 16/02/13.
    //  Copyright © 2016年 Mac. All rights reserved.
    //
    
    #import <UIKit/UIKit.h>
    
    @interface UILabel (FontChange)
    
    @end
    

`UILabel+FontChange.m`

    
    
    //
    //  UILabel+FontChange.m
    //  FontChangeProject
    //
    //  Created by Brian on 16/02/13.
    //  Copyright © 2016年 Mac. All rights reserved.
    //
    
    #import "UILabel+FontChange.h"
    #import <objc/runtime.h>
    
    #define CustomFontName @"FZLBJW--GB1-0" // 字体册.ttf文件中字体的名称
    
    @implementation UILabel (FontChange)
    
    + (void)load {
        // 方法交换应该保证在程序中只会被执行一次
        static dispatch_once_t onceToken;
        dispatch_once(&onceToken, ^{
            
            // 1. 获取UILabel的生命周期方法的selector
            SEL originalSel = @selector(willMoveToSuperview:);
            
            // 2. 获取自己实现的将要被交换的方法的selector
            SEL overrideSel = @selector(myWillMoveToSuperview:);
            
            // 3. 实现方法交换
            MethodSwizzle([self class], originalSel, overrideSel);
        });
    }
    
    void MethodSwizzle(Class cls, SEL originalName, SEL overrideName) {
        // 获取类中的某个实例的方法(减号方法)
        Method originalMethod = class_getInstanceMethod(cls, originalName);
        Method overrideMethod = class_getInstanceMethod(cls, overrideName);
        
        /** 原理: 有两种情况要考虑一下,
            第一种情况是:要复写的方法(override)并没有在目标类中实现;
            第二种情况是:这个方法(override)已经存在于目标类中了.
         这两种情况要区别对待.
         
         对于第一种情况,应当先在目标类中增加一个新的实现方法(override),运行时函数class_addMethod()如果
         发现该方法已经存在,会返回NO;
         
         对于第二种情况,因为class_getInstanceMethod会返回父类的实现,如果直接替换,就会替换掉父类的实现,而不是目标类中的实现. 
         这时需要在一个合适的位置来调用MethodSwizzle()方法, 在+ (void)load方法中调用就可以直接完成交换.
        */
        
        
        // class_addMethod()方法会让originalName方法指向新的实现overrideMethod
        BOOL result = class_addMethod(cls, originalName, method_getImplementation(overrideMethod), method_getTypeEncoding(overrideMethod));
        if (result) {
            // 如果添加成功, 表示originalName方法已指向新的实现overrideMethod, 然后再使用class_replaceMethod()将新的方法overrideName指向原先的实现originalMethod, 就完成了交换.
            class_replaceMethod(cls, overrideName, method_getImplementation(originalMethod), method_getTypeEncoding(originalMethod));
        } else {
            // 如果添加失败,就是第二种情况,这时可以直接通过method_exchangeImplementations来完成交换.
            method_exchangeImplementations(originalMethod, overrideMethod);
        }
    }
    
    - (void)myWillMoveToSuperview:(UIView *)newSuperview {
        [self myWillMoveToSuperview:newSuperview];
        
        // 自己的处理代码...
        
        if ([self isKindOfClass:NSClassFromString(@"UIButtonLabel")]) {
            return;
        }
        if (self) {
            if (self.tag == 10086) {
                self.font = [UIFont systemFontOfSize:self.font.pointSize];
            } else {
                if ([UIFont fontNamesForFamilyName:CustomFontName]) {
                    self.font = [UIFont fontWithName:CustomFontName size:self.font.pointSize];
                }
            }
        }
    }
    
    @end
    

`Tips: 获取字体册中的字体名称`

    
    
    /**
     读取ttf或otf字体册中的字体名称 (先在Info.plist中把字体文件名添加到Fonts provided by application一项中)
    
     @param path 字体册文件的路径 如:[[NSBundle mainBundle] pathForResource:@"font12" ofType:@"ttf"]
     @param size 字体大小 如:18
     @return 字体
     */
    - (UIFont *)customFontWithPath:(NSString *)path size:(CGFloat)size {
        NSURL *fontUrl = [NSURL fileURLWithPath:path];
        CGDataProviderRef fontDataProvider = CGDataProviderCreateWithURL((__bridge CFURLRef)fontUrl);
        CGFontRef fontRef = CGFontCreateWithDataProvider(fontDataProvider);
        CGDataProviderRelease(fontDataProvider);
        CTFontManagerRegisterGraphicsFont(fontRef, NULL);
        NSString *fontName = CFBridgingRelease(CGFontCopyPostScriptName(fontRef));
        NSLog(@"fontName = %@", fontName);
        UIFont *font = [UIFont fontWithName:fontName size:size];
        CGFontRelease(fontRef);
        return font;
    }
    
    /**
     读取ttc字体册中的字体名称 (先在Info.plist中把字体文件名添加到Fonts provided by application一项中)
    
     @param path 字体册文件的路径 如:[[NSBundle mainBundle] pathForResource:@"font12" ofType:@"ttc"]
     @param size 字体大小 如:18
     @return 字体数组
     */
    - (NSArray *)customFontArrayWithPath:(NSString *)path size:(CGFloat)size {
        CFStringRef fontPath = CFStringCreateWithCString(NULL, [path UTF8String], kCFStringEncodingUTF8);
        CFURLRef fontUrl = CFURLCreateWithFileSystemPath(NULL, fontPath, kCFURLPOSIXPathStyle, 0);
        CFArrayRef fontArray = CTFontManagerCreateFontDescriptorsFromURL(fontUrl);
        CTFontManagerRegisterFontsForURL(fontUrl, kCTFontManagerScopeNone, NULL);
        
        NSMutableArray *customFontArray = [NSMutableArray array];
        for (CFIndex i = 0; i < CFArrayGetCount(fontArray); i++) {
            CTFontDescriptorRef descriptor = CFArrayGetValueAtIndex(fontArray, i);
            CTFontRef fontRef = CTFontCreateWithFontDescriptor(descriptor, size, NULL);
            NSString *fontName = CFBridgingRelease(CTFontCopyName(fontRef, kCTFontPostScriptNameKey));
            NSLog(@"fontName[%ld] = %@", i, fontName);
            UIFont *font = [UIFont fontWithName:fontName size:size];
            [customFontArray addObject:font];
        }
        return customFontArray; 
    }
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS WebSocket长链接（Swift）](https://www.jianshu.com/p/48941c44ad32)

WebSocket-Swift Starscream的使用 WebSocket 是 HTML5 一种新的协议。它实...

[神合](https://www.jianshu.com/u/5567c741f6a7)阅读 20,838评论 8赞 179

  * [iOS开发常用三方库集合OC版(三方库、插件、博客等等)](https://www.jianshu.com/p/4145a80dec45)

Swift版本点击这里欢迎加入QQ群交流: 594119878最新更新日期：18-09-17 About A cu...

[ylgwhyh](https://www.jianshu.com/u/e94387132cd6)阅读 23,611评论 7赞 248

  * [双宋cp公布婚讯，你的反应是？](https://www.jianshu.com/p/3c3e5aede63f)

7月5日,韩国艺人宋仲基与宋慧乔今天突然通过经纪公司宣布将于10月31日举行婚礼。 去年热播《太...

[黎明时分的燕子](https://www.jianshu.com/u/05b48da51c45)阅读 233评论 0赞 2

  * [我们和学生一起已没有什么优势](https://www.jianshu.com/p/b3c70a8bdbcb)

这句话不是我说的，来自特级教师王树华。 下午和同事一起去扬州新东方外国语学校听了一节王老师的课，紧接着是一个关于《...

[潘佳梅原创](https://www.jianshu.com/u/dadd74489b77)阅读 235评论 0赞 3

  * [常规固定思维](https://www.jianshu.com/p/9438a4855bac)

2015.07.25 星期六 佛山 阵雨 平时累了，周末就得休息？ 打销售电话在网络时代已经没用了？ 我们到了60...

[邱比货代君](https://www.jianshu.com/u/076af4af8252)阅读 358评论 0赞 1

 