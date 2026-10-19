iconfont for iOS

[ 大刘](https://www.jianshu.com/u/148b1cad85ce)关注赞赏支持

# iconfont for iOS

  1. **托入iconfont资源**  
在<https://www.iconfont.cn/>中的购物车里下载代码，把里面的.ttf托入工程

  2. 向系统注册此ttf

    
    
    NSURL *fontFileUrl = [[NSBundle mainBundle] URLForResource:@“yourResourceName” withExtension:@"ttf"];
    CGDataProviderRef fontDataProvider = CGDataProviderCreateWithURL((__bridge CFURLRef)url);
    CGFontRef newFont = CGFontCreateWithDataProvider(fontDataProvider);
    CGDataProviderRelease(fontDataProvider);
    CTFontManagerRegisterGraphicsFont(newFont, NULL);
    CGFontRelease(newFont);
    
    // 注册后可以获取字体(注册只需要一次)
    [UIFont fontWithName:name size:size]
    

  3. **在label中使用字体**

    
    
     UILabel *label = ...
     label.font = get the font here ...
     label.text = ...
    

**示例代码：**

<https://github.com/ACommonChinese/iconFont-iOS>

Simulator Screen Shot - iPhone 8 - 2019-03-05 at 11.47.11.png

