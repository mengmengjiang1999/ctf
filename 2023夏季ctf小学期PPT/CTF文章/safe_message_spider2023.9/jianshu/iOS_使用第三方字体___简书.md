iOS 使用第三方字体

[ Eyes_cc](https://www.jianshu.com/u/4604e8b9261d)关注赞赏支持

# iOS 使用第三方字体

##### 前言

介绍两种字体使用方式：静态字体和动态字体。

##### 一、使用静态字体

1、将第三方字体拖入工程  
2、打开Build Phase -- Copy Bundle Resources,确保刚添加的字体在列表中，否则需要手动加到这里

  

示例.png

  

3、在Info.plist文件中添加Fonts provided by
application的配置项，其中每一个Item对应的是字体文件的名称，如huakangshaonv.ttf。

  

示例

  
4、使用第三方字体  

示例

##### 二、使用动态字体

在网易新闻iOS客户端中可以使用自定义的字体，对于未下载的字体可先下载然后安装下次就能自动设置为该字体，效果如下：

  

示例

  

1、下载字体文件

    
    
    - (NSString *)downloadZipFile:(NSString *)fileUrl toPath:(NSString *)path
    {
        NSError *error = nil;
        NSURL *url = [NSURL URLWithString:fileUrl];
        NSString *fileName = [url lastPathComponent];
        NSData *data = [NSData dataWithContentsOfURL:url options:0 error:&error];
        if(!error)
        {
            NSString *zipPath = [path stringByAppendingPathComponent:fileName];
            [data writeToFile:zipPath options:0 error:&error];
            if(!error)
            {
                return zipPath;
            }
        }
        return nil;
    }
    

2、解压zip压缩包  
iOS中解压zip压缩文件非常方便，使用[ZipArchive](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fmattconnolly%2FZipArchive)这个开源项目按照如下的方式即可快速解压zip文件。

    
    
    - (NSString *)expandZipFile:(NSString *)src toPath:(NSString *)desc
    {
        ZipArchive *za = [[ZipArchive alloc] init];
        if ([za UnzipOpenFile:src])
        {
            BOOL ret = [za UnzipFileTo:desc overWrite:YES];//解压文件
            if(ret)
            {
                NSString *zipName = [src lastPathComponent];//获取zip文件的文件名
                [[NSFileManager defaultManager] removeItemAtPath:zipPath error:nil];//删除zip压缩包
                zipName = [zipName substringToIndex:[zipName rangeOfString:@".zip"].location];//获取解压到的文件夹
                return [self.downloadPath stringByAppendingPathComponent:zipName];
            }
        }
        return nil;
    }
    

3、注册指定路径下的字体文件  
`下载回来的字体文件如果不做处理是不能直接使用的，使用前需要先注册然后才能使用，注册方式如下：`  
需要先引入`CoreText`框架,  
`#import <CoreText/CoreText.h>`

    
    
    - (void)registerFont:(NSString *)fontPath
    {
        NSData *dynamicFontData = [NSData dataWithContentsOfFile:fontPath];
        if (!dynamicFontData)
        {
            return;
        }
        CFErrorRef error;
        CGDataProviderRef providerRef = CGDataProviderCreateWithCFData((__bridge CFDataRef)dynamicFontData);
        CGFontRef font = CGFontCreateWithDataProvider(providerRef);
        if (! CTFontManagerRegisterGraphicsFont(font, &error))
        {
            //注册失败
            CFStringRef errorDescription = CFErrorCopyDescription(error);
            NSLog(@"Failed to load font: %@", errorDescription);
            CFRelease(errorDescription);
        }
        CFRelease(font);
        CFRelease(providerRef);
    }
    

4、判断字体是否加载  
`在使用字体文件前最好是先判断字体是否已经被加载过了，判断方式如下：`

    
    
    - (BOOL)isFontDownloaded:(NSString *)fontName
    {
        UIFont* aFont = [UIFont fontWithName:fontName size:12.0];
        BOOL isDownloaded = (aFont && ([aFont.fontName compare:fontName] == NSOrderedSame || [aFont.familyName compare:fontName] == NSOrderedSame));
        return isDownloaded;
    }
    

5、其他说明  
`经测试注册过的字体在应用关闭后下次开启应用，判断字体是否加载时返回为NO，为了保证正常使用需要每次启动应用的时候先遍历一遍字体文件夹将里面的字体文件都再次注册一遍即可。参考代码如下:`

    
    
    //注册fonts目录下面的所有字体文件
    NSArray *ary = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:self.downloadPath error:nil];
    for (NSString *p1 in ary)
    {
        NSString *t1 = [self.downloadPath stringByAppendingPathComponent:p1];
        NSArray *ary1 = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:t1 error:nil];
        for (NSString *p1 in ary1)
        {
            NSString *t2 = [t1 stringByAppendingPathComponent:p1];
            if([t2 rangeOfString:@".ttf"].location != NSNotFound)
            {
                [self registerFont:t2];
            }
        }
    }
    

