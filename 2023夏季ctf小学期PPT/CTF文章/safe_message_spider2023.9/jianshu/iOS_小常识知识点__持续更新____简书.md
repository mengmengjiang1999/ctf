iOS-小常识知识点 (持续更新)

[ Mn_Su](https://www.jianshu.com/u/7e310d5c0c93)关注赞赏支持

# iOS-小常识知识点 (持续更新)

 **第一.app如何添加AirDrop文件分享功能**

    
    
        苹果在iOS 7 SDK中集成了UIActivityViewController类，可以让你很简单地就能把AirDrop功能整合进app中!
        MobileVLCKit 第三方 多格式支持 视频播放!
    

**第二.内存泄露分析及解决**

    
    
        静态分析内存泄露 使用Xcode自带的Analyze功能（Product-> Analyze）（Shift + Command + B），对代码进行静态分析，对于内存泄露（Potential Memory Leak）, 未使用局部变量(dead store)，逻辑错误(Logic Flaws)以及API使用问题(API-usage)等明确的展示出来。 静态分析的内存泄露情况比较简单，开发者都能很快的解决。这里不做赘述。
    
        动态分析内存泄露 使用Xcode自带的Profile功能（Product-> Profile）（Command + i）弹出工具框，选择Leaks打开，选择运行设备点左上角的Record录制按钮，项目就会在已选好的设备上运行，并开始录制内存检测情况。选Leaks查看泄露情况，在Leaks的详细菜单Details选项里选调用树Call Tree，可查看所有内存泄露发生在哪些地方。再在右侧的齿轮设置-Call Tree-勾选Hide System Libraries，则可直接看内存泄露发生的函数名、方法名。点击函数名、方法名，可直接跳到函数方法的细节，可以看到哪一句代码出现了内存泄露，以及泄露了多少内存。
    接下来就要回到Xcode，找到出现内存泄露的函数方法，仔细分析如何出现的内存泄露; 一般使用ARC，按照上面一提到的内存理解和编码习惯是不会出现内存泄露的。但我们在开发过程中，经常要使用第三方的一些类库，特别是涉及到加密的类库，用c或c++来编码的加密解密方法，会出现内存泄露。此时，我们要明白这些内存分配，需要手动释放。要一步一步看，哪里分配了内存，在使用完之后一定要记得释放free它。
    
    调试内存泄露是一件让人头疼的事，如果你不想头疼，请保持良好的编码习惯。并在开发到一个阶段时，就要及时对应用进行内存泄露分析。发现问题，及时修复。
    

**第三.block循环利用导致内存泄漏**

    
    
        A *a = [[A alloc] init];
         a.finishBlock = ^(NSDictionary paraments){ [a doSomething]; }; 
        对于这种在block块里引用对象a的情况，要在创建对象a时加修饰符block来防止循环引用。
         block A *a = [[A alloc] init]; 
         a.finishBlock = ^(NSDictionary paraments){ [a doSomething]; }; 
        或 A __block a = [[A alloc] init]; a.finishBlock = ^(NSDictionary paraments){ [a doSomething]; };
         或者，需要在block中调用用self的方法、属性、变量时，可以这样写__weak typeof(self) weakSelf = self;在block中使用weakSelf。
        __weak typeof(self) weakSelf = self; [b doSomethingWithFinishBlock:^{ weakSelf.text = @"内存检测"; [weakSelf doSomething]; }]; 
    

**第四.label 的空格属性和局部字段颜色**

    
    
        设置 label 的 autoresizingMask 为 NO ,可以使用空格间隔字符串!
    
           [thirdLab setAttributedText:[self changeLabelWithText:@"点击按钮去注册"]];
    
        //获取要调整颜色的文字位置,调整颜色  ,改变字体大小和字间距
        -(NSMutableAttributedString*)changeLabelWithText:(NSString*)needText  
        {            
            NSMutableAttributedString *attrString = [[NSMutableAttributedString alloc] initWithString:needText];
            
            [attrString addAttribute:NSFontAttributeName value:[UIFont systemFontOfSize:20] range:NSMakeRange(0,1)];
            [attrString addAttribute:NSForegroundColorAttributeName value:[UIColor colorWithRed:51/255.0 green:3/255.0 blue:4/255.0 alpha:1] range:NSMakeRange(0,1)];
      
            [attrString addAttribute:NSKernAttributeName value:@1.0f range:NSMakeRange(0, needText.length)];
    
            [attrString addAttribute:NSFontAttributeName value:[UIFont systemFontOfSize:16] range:NSMakeRange(1,needText.length-1)];
            [attrString addAttribute:NSForegroundColorAttributeName value:[UIColor blackColor] range:NSMakeRange(1,needText.length-1)];
        
            return attrString;            
        }
    

**第五.过滤字符串**

    
    
        // 定义一个特殊字符的集合
        NSCharacterSet *set = [NSCharacterSet characterSetWithCharactersInString:
        @"@／：；（）¥「」＂、[]{}#%-*+=_\\|~＜＞$€^•'@#$%^&*()_+'\""];
        // 过滤字符串的特殊字符
        NSString *newString = [trimString stringByTrimmingCharactersInSet:set];    
    

**第六.iOS应用直接退出**

    
    
        - (void)exitApplication {
            AppDelegate *app = [UIApplication sharedApplication].delegate;
            UIWindow *window = app.window;
        
            [UIView animateWithDuration:1.0f animations:^{
                window.alpha = 0;
            } completion:^(BOOL finished) {
                exit(0);
            }];
        }
    

**第七.label 行间距**

    
    
        -（void）test{
            NSMutableAttributedString *attributedString =    
           [[NSMutableAttributedString alloc] initWithString:self.contentLabel.text];
            NSMutableParagraphStyle *paragraphStyle =  [[NSMutableParagraphStyle alloc] init];  
           [paragraphStyle setLineSpacing:3];
        
            //调整行间距       
           [attributedString addAttribute:NSParagraphStyleAttributeName 
                                 value:paragraphStyle 
                                 range:NSMakeRange(0, [self.contentLabel.text length])];
             self.contentLabel.attributedText = attributedString;
        }
    

**第八.设置滑动的时候隐藏 navigationbar**

    
    
        第1种:
            navigationController.hidesBarsOnSwipe = Yes
        
        第2种:
            //1.当我们的手离开屏幕时候隐藏
        - (void)scrollViewWillEndDragging:(UIScrollView *)scrollView withVelocity:(CGPoint)velocity targetContentOffset:(inout CGPoint *)targetContentOffset
        { 
            if(velocity.y > 0) 
            {
            [self.navigationController setNavigationBarHidden:YES animated:YES];
            } else {
            [self.navigationController setNavigationBarHidden:NO animated:YES]; 
            }
        }
        velocity.y这个量，在上滑和下滑时，变化极小（小数），但是因为方向不同，有正负之分，这就很好处理  了。
    

**第九.屏幕截图**

    
    
         // 1. 开启一个与图片相关的图形上下文
        UIGraphicsBeginImageContextWithOptions(self.view.bounds.size,NO,0.0);
    
        // 2. 获取当前图形上下文
        CGContextRef ctx = UIGraphicsGetCurrentContext();
    
        // 3. 获取需要截取的view的layer
        [self.view.layer renderInContext:ctx];
    
        // 4. 从当前上下文中获取图片
        UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
    
        // 5. 关闭图形上下文
        UIGraphicsEndImageContext();
    
        // 6. 把图片保存到相册
        UIImageWriteToSavedPhotosAlbum(image, nil, nil, nil);
    

**第十.导航栏、状态栏和tabbar相关**

    
    
    1.导航栏
    
        //隐藏导航栏上的返回字体    
        //Swift
        UIBarButtonItem.appearance().setBackButtonTitlePositionAdjustment(UIOffsetMake(0, -60), forBarMetrics: .Default)
        //OC
        [[UIBarButtonItem appearance] setBackButtonTitlePositionAdjustment:UIOffsetMake(0, -60) forBarMetrics:UIBarMetricsDefault];
    
         //自定义导航栏的左右按钮
            UIButton *searchBtn = [[UIButton alloc] initWithFrame:CGRectMake(SCREEN_WIDTH - 90, 0, 30, 44)];
            UIBarButtonItem *seaBtn = [[UIBarButtonItem alloc] initWithCustomView:searchBtn];
            self.navigationItem.rightBarButtonItem = seaBtn;
    
    2.状态栏
    
        //所有控制器状态栏字体颜色
        状态栏字体颜色不同的办法        
        1）、在info.plist中，将View controller-based status bar appearance设为NO.
        
        2）、在app delegate中：
    
        [UIApplication sharedApplication].statusBarStyle = UIStatusBarStyleLightContent;
    
        //单独某个控制器字体颜色
        3）、在个别状态栏字体颜色不一样的vc中
        
        -(void)viewWillAppear:(BOOL)animated{
            [UIApplication sharedApplication].statusBarStyle = UIStatusBarStyleDefault;
        }
    
     3.tabbar
    
        
        + (void)load
        {
            // 获取当前类的tabBarItem
            UITabBarItem *item = [UITabBarItem appearanceWhenContainedIn:self, nil];
            
            // 更改tabbar 选中字体颜色
            UITabBar *tabbar = [UITabBar appearanceWhenContainedIn:self, nil];
            tabbar.tintColor = [UIColor orangeColor];
            
            // 设置所有item的选中时颜色
            // 设置选中文字颜色
            // 创建字典去描述文本
            NSMutableDictionary *attSelect = [NSMutableDictionary dictionary];
            // 文本颜色 -> 描述富文本属性的key -> NSAttributedString.h
            attSelect[NSForegroundColorAttributeName] = [UIColor orangeColor];
            [item setTitleTextAttributes:attSelect forState:UIControlStateSelected];
            
            // 通过normal状态设置字体大小
            // 字体大小 跟 normal
            NSMutableDictionary *attrNormal = [NSMutableDictionary dictionary];
            // 设置字体
            attrNormal[NSFontAttributeName] = [UIFont systemFontOfSize:13];
            [item setTitleTextAttributes:attrNormal forState:UIControlStateNormal];
            
            // 文字偏移量
            //[item setTitlePositionAdjustment:<#(UIOffset)#>];
            
            // icon偏移量
            // item.imageInsets = UIEdgeInsetsMake(<#CGFloat top#>, <#CGFloat left#>, <#CGFloat bottom#>, <#CGFloat right#>);
        }
    

**第十一.去掉 tabbar 和 navgationbar 的黑线**

    
    
          //去掉tabBar顶部线条
        CGRect rect = CGRectMake(0, 0, 1, 1);
        UIGraphicsBeginImageContext(rect.size);
        CGContextRef context = UIGraphicsGetCurrentContext();
        CGContextSetFillColorWithColor(context, [[UIColor clearColor] CGColor]);
        CGContextFillRect(context, rect);
        UIImage *img = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
        [self.tabBar setBackgroundImage:img];
        [self.tabBar setShadowImage:img];
        //[self.navigationController.navigationBar setBackgroundImage:img];
        //self.navigationController.navigationBar.shadowImage = ima;
        
        self.tabBar.backgroundColor = SLIVERYCOLOR;
    

**第十二.判断字符串中是否含有中文**

    
    
        -(BOOL)isChinese:(NSString *)str{
            NSString *match=@"(^[\u4e00-\u9fa5]+$)";
            NSPredicate *predicate = [NSPredicate predicateWithFormat:@"SELF matches %@", match];
            return [predicate evaluateWithObject:str];
        }
    

**第十三.解决父视图和子视图的手势冲突**

    
    
        /** 解决手势冲突 */
        - (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldReceiveTouch:(UITouch *)touch{
            if ([touch.view isDescendantOfView:cicView]) {
                return NO;
            }
            return YES;
        }
    

**第十四.NSDate与NSString的相互转化**

    
    
        -(NSString *)dateToString:(NSDate *)date {
          // 初始化时间格式控制器
          NSDateFormatter *matter = [[NSDateFormatter alloc] init];
          // 设置设计格式
          [matter setDateFormat:@"yyyy-MM-dd hh:mm:ss zzz"];
          // 进行转换
          NSString *dateStr = [matter stringFromDate:date];
          return dateStr;
        }
        -(NSDate *)stringToDate:(NSString *)dateStr {
        
          // 初始化时间格式控制器
          NSDateFormatter *matter = [[NSDateFormatter alloc] init];
          // 设置设计格式
          [matter setDateFormat:@"yyyy-MM-dd hh:mm:ss zzz"];
          // 进行转换
          NSDate *date = [matter dateFromString:dateStr];
          return date;
        }
    

**第十五.Xcode 8 注释设置**

    
    
        打开终端，命令运行： sudo /usr/libexec/xpccachectl
        然后必须重启电脑后生效
    

**十六.删除storyboard的方法**

    
    
        一般情况下，我们有时候不想用storyboard，但是直接删除的话，Xcode就会报错。那我今天就来讲一下，正确删除storyboard的方法。
        
        第一，直接将工程中的storyboard直接删除掉，这样你觉得就OK了？你错了，还是要有第二步的。
        
        第二，找到plist文件，将plist文件中的Main storyboard file base name删除掉，如图所示
    

**十七.ASCII 和 NSString 的相互转换**

    
    
        // NSString to ASCII
        NSString *string = @"A";
        int asciiCode = [string characterAtIndex:0]; //65
        
        //ASCII to NSString
        int asciiCode = 65;
        NSString *string =[NSString stringWithFormat:@"%c",asciiCode]; //A
    

**十八.获取当前连接的wifi名称**

    
    
            NSString *wifiName = @"Not Found";
    
            CFArrayRef myArray = CNCopySupportedInterfaces();
        
            if (myArray != nil) {
        
                CFDictionaryRef myDict = CNCopyCurrentNetworkInfo(CFArrayGetValueAtIndex(myArray, 0));
        
                if (myDict != nil) {
        
                    NSDictionary *dict = (NSDictionary*)CFBridgingRelease(myDict);
        
                    wifiName = [dict valueForKey:@"SSID"];
        
                }
        
            }
        
            NSLog(@"wifiName:%@", wifiName);
    

**十九.苹果自带的下拉刷新方法**

    
    
            //设置下拉刷新 UIRefreshControl *refresh = [[UIRefreshControl alloc] init];
    
            NSDictionary dict = @{NSForegroundColorAttributeName:[UIColor redColor]}; 
            NSAttributedString string = [[NSAttributedString alloc] initWithString:@"帮你署最新。。" attributes:dict]; 
            refresh.attributedTitle = string;
    
            [self.tableView addSubview:refresh];
    

**二十.显示和隐藏系统文件**

    
    
            显示Mac隐藏文件的命令：
    
            defaults write com.apple.finder AppleShowAllFiles -bool true
            
            隐藏Mac隐藏文件的命令：
            
            defaults write com.apple.finder AppleShowAllFiles -bool false
    

**二十一.跨控制器跳转返回**

    
    
        for (UIViewController *controller in self.navigationController.viewControllers) { 
            if ([controller isKindOfClass:[@“你要返回的控制器类名” class]]) {
                 [self.navigationController popToViewController:controller animated:YES];
             }
         }
    

**二十二. layer.cornerRadius 圆角流畅性的优化**

    
    
    第一种：CornerRadius
    
        loginBtn.layer.cornerRadius = 10;
        loginBtn.layer.shouldRasterize = YES;
        loginBtn.layer.rasterizationScale = [UIScreen mainScreen].scale;
    
    第二种：UIBezierPath 和 CAShapeLayer
    
        UIBezierPath *maskPath = [UIBezierPath bezierPathWithRoundedRect:_draw.bounds byRoundingCorners:UIRectCornerAllCorners cornerRadii:_draw.bounds.size];
        CAShapeLayer *maskLayer = [[CAShapeLayer alloc]init];
        // 设置大小
        maskLayer.frame = _draw.bounds;
        // 设置图形样子
        maskLayer.path = maskPath.CGPath;
        _draw.layer.mask = maskLayer;
    
    第三种：设置上半部分圆角
    
        _titleLabel.layer.masksToBounds = YES;
    
        CAShapeLayer *maskLayer = [CAShapeLayer layer];
        maskLayer.path = [UIBezierPath bezierPathWithRoundedRect:_titleLabel.bounds byRoundingCorners: UIRectCornerBottomLeft | UIRectCornerBottomRight cornerRadii: (CGSize){5.0f, 5.0f}].CGPath;
        
        _titleLabel.layer.mask = maskLayer;
    

**二十三.导航栏和下方视图间隔距离消失 以及 导航栏和下方视图不重叠**

    
    
        //不间隔
        self.automaticallyAdjustsScrollViewInsets=YES;
    
        //不重叠
        self.edgesForExtendedLayout = UIRectEdgeNone
    

**二十四.毛玻璃效果(ios8.0以后的版本)**

    
    
        UIVisualEffectView *visualEffectView = [[UIVisualEffectView alloc] initWithEffect:[UIBlurEffect effectWithStyle:UIBlurEffectStyleLight]];
        visualEffectView.frame = CGRectMake(0, 0, 320*[FlexibleFrame ratio], 180*[FlexibleFrame ratio]);
        visualEffectView.alpha = 1.0;
    

**二十五.工作中常用的第三方**

[ 传送
](https://links.jianshu.com/go?to=http%3A%2F%2Fblog.cocoachina.com%2Farticle%2F12350)

**二十六.PCH文件中的小玩意**

    
    
        创建.pch文件时 , BuildSetting 中的 Prefix Header 中的路径开头可以写  $(SRCROOT)/工程地址, 这样写的好处可以使你的挪动代码不用手动更换路径!
    

**二十七.如何点击谷歌地图获取所在位置经纬度?**

[ 链接 ](https://www.jianshu.com/p/ec6d154e3928)

    
    
        调用谷歌地图 mapView:didTapAtCoordinate:  方法,即可获得!
    

**二十八.AppIcon 和 launch image 尺寸相关**

[ 传送
](https://links.jianshu.com/go?to=http%3A%2F%2Fblog.csdn.net%2Fhqc17%2Farticle%2Fdetails%2F52355137)

** 二十九.iO中判断两个数组是否相同**

    
    
        NSArray *array1 = [NSArray arrayWithObjects:@"a", @"b", @"c",  nil];
        NSArray *array2 = [NSArray arrayWithObjects:@"d", @"a", @"c",  nil];
        bool bol = false;
        
        //创建俩新的数组
        NSMutableArray *oldArr = [NSMutableArray arrayWithArray:array1];
        NSMutableArray *newArr = [NSMutableArray arrayWithArray:array2];
        
        //对数组1排序。
        [oldArr sortUsingComparator:^NSComparisonResult(id obj1, id obj2){
            return obj1 > obj2;
        }];
        
        //对数组2排序。
        [newArr sortUsingComparator:^NSComparisonResult(id obj1, id obj2){
            return obj1 > obj2;
        }];
        
        if (newArr.count == oldArr.count) {
            
            bol = true;
            for (int16_t i = 0; i < oldArr.count; i++) {
                
                id c1 = [oldArr objectAtIndex:i];
                id newc = [newArr objectAtIndex:i];
                
                if (![newc isEqualToString:c1]) {
                    bol = false;
                    break;
                }
            }
        }
        
        if (bol) {
            NSLog(@" ------------- 两个数组的内容相同！");
        }
        else {
            NSLog(@"-=-------------两个数组的内容不相同！");
        }
    

**三十.屏幕渲染--颜色渐变**

    
    
            CAGradientLayer *gradientLayer = [CAGradientLayer layer];
            gradientLayer.colors = @[(__bridge id)[UIColor whiteColor].CGColor,(__bridge id)[UIColor grayColor].CGColor,(__bridge id)[UIColor whiteColor].CGColor];
            gradientLayer.locations = @[@0.2,@0.65,@0.75];
            gradientLayer.startPoint = CGPointMake(0, 0);
            gradientLayer.endPoint = CGPointMake(1.0, 0);
            gradientLayer.frame = CGRectMake(0, 100, [UIScreen mainScreen].bounds.size.width, 2);
            [self.view.layer addSublayer:gradientLayer];
    

**三十一.快速求和，最大值，最小值，平均值**

    
    
        NSArray *array = [NSArray arrayWithObjects:@"2.0", @"2.3", @"3.0", @"4.0", @"10", nil]; 
        CGFloat sum = [[array valueForKeyPath:@"@sum.floatValue"] floatValue]; 
        CGFloat avg = [[array valueForKeyPath:@"@avg.floatValue"] floatValue]; 
        CGFloat max =[[array valueForKeyPath:@"@max.floatValue"] floatValue]; 
        CGFloat min =[[array valueForKeyPath:@"@min.floatValue"] floatValue];
    

**三十二.对比时间差**

Paste_Image.png

    
    
        -(int)max:(NSDate *)datatime
        {
            //创建日期格式化对象
            NSDateFormatter *dateFormatter=[[NSDateFormatter alloc] init];
            [dateFormatter setDateFormat:@"YYYY-MM-dd hh:mm:ss"];
            NSDate *  senddate=[NSDate date];
            NSString *  locationString=[dateFormatter stringFromDate:senddate];
            NSDate *date=[dateFormatter dateFromString:locationString];
            //取两个日期对象的时间间隔：
            //这里的NSTimeInterval 并不是对象，是基本型，其实是double类型，是由c定义的:typedef double NSTimeInterval;
            NSTimeInterval time=[date timeIntervalSinceDate:datatime];
            int days=((int)time)/(3600*24);
            return days;
        }
    

**三十三.请求定位权限以及定位属性**

    
    
        _在地图页面放入下面代码:_
            //定位管理器
            _locationManager=[[CLLocationManager alloc]init];
            //如果没有授权则请求用户授权
            if ([CLLocationManager authorizationStatus]==kCLAuthorizationStatusNotDetermined){
                [_locationManager requestWhenInUseAuthorization];
            }else if([CLLocationManager authorizationStatus]==kCLAuthorizationStatusAuthorizedWhenInUse){
                //设置代理
                _locationManager.delegate=self;
                //设置定位精度
                _locationManager.desiredAccuracy=kCLLocationAccuracyBest;
                //定位频率,每隔多少米定位一次
                CLLocationDistance distance=10.0;//十米定位一次
                _locationManager.distanceFilter=distance;
                //启动跟踪定位
                [_locationManager startUpdatingLocation];
            }
    

**三十四.将几张图片合成为一张**

    
    
        - (UIImage *)composeWithHeader:(UIImage *)header content:(UIImage *)content footer:(UIImage *)footer{
            CGSize size = CGSizeMake(content.size.width, header.size.height +content.size.height +footer.size.height);
            UIGraphicsBeginImageContext(size);
            [header drawInRect:CGRectMake(0,
                                          0,
                                          header.size.width,
                                          header.size.height)];
            [content drawInRect:CGRectMake(0,
                                           header.size.height,
                                           content.size.width,
                                           content.size.height)];
            [footer drawInRect:CGRectMake(0,
                                          header.size.height+content.size.height,
                                          footer.size.width,
                                          footer.size.height)];
         
            UIImage *image = UIGraphicsGetImageFromCurrentImageContext();
            UIGraphicsEndImageContext();
            return image;
    }
    

**三十五.按钮的选择状态及与BarButton的结合使用**

    
    
          self.barRightBtn = [UIButton buttonWithType:UIButtonTypeCustom];
            self.barRightBtn.frame = CGRectMake(WIDTH-20, 30, 80, 30);
            [self.barRightBtn setTitle:@"停止扫描" forState:UIControlStateNormal];
            [self.barRightBtn setTitle:@"开始扫描" forState:UIControlStateSelected];
        
            [self.barRightBtn setTitleColor:BLUECOLOR forState:UIControlStateNormal];
            self.barRightBtn.titleLabel.font = [UIFont systemFontOfSize:18];
            [[self.barRightBtn rac_signalForControlEvents:UIControlEventTouchUpInside] subscribeNext:^(id x) {
                self.barRightBtn.selected = !self.barRightBtn.selected;
                
                if (self.barRightBtn.selected) {
                    [self endScanIbeacon];
                }else{
                    [self startScanIbecan];
                }
            }];
            
            UIBarButtonItem *barBtn = [[UIBarButtonItem alloc] initWithCustomView:self.barRightBtn];
            self.navigationItem.rightBarButtonItem = barBtn;
    

**三十六.自定义ttf字体**

    
    
        1.将xx.ttf字体库加入工程里;
    

FAA2B395-A0C2-4E61-9AC0-9F1967DD0CAA.png

    
    
        2.在工程的xx-Info.plist文件中新添加一行Fonts provided by application，加上字体库的名称;
    

Paste_Image.png

    
    
        3.引用字体库的名称，设置字体： [UIFontfontWithName:@"fontname" size:24];
    

Paste_Image.png

    
    
        4.如果不知道字体名称，可以遍历字体进行查询;或者选中项目中的导入字体，然后showInFinder,双击打开查看最上面的字体介绍：
    
             for(NSString *fontfamilyname in [UIFont familyNames])  
          {  
              NSLog(@"family:'%@'",fontfamilyname);  
              for(NSString *fontName in [UIFont fontNamesForFamilyName:fontfamilyname])  
              {  
                  NSLog(@"\tfont:'%@'",fontName);  
              }  
              NSLog(@"-------------");  
          }  
    

**三十七.导航栏字体颜色改变**

_有时候想改变某个控制器中状态栏的字体颜色,单纯的在控制器添加 [[UIApplication sharedApplication]
setStatusBarStyle:UIStatusBarStyleLightContent],发现添加后无改变!这时候就需要设置另外一个属性!_

    
    
        1.在 info.plist 中，将 View controller-based status bar appearance 设为 NO;
        2. 在对应控制器添加[[UIApplication sharedApplication] setStatusBarStyle:UIStatusBarStyleLightContent];
    

**三十八.类似于 modal 效果的弹出视图**

    
    
            //初始化
           PopView *pop = [[PopView alloc] initWithFrame:CGRectMake(0, HEIGHT, WIDTH, HEIGHT-150)];
            pop.bgImaView.image = [UIImage imageNamed:[NSString stringWithFormat:@"backgaund_%ld",(long)index]];
            [self.view addSubview:pop];
    
            //点击后frame改变,动画展示上滑 (类似于 btn 点击事件)
            [UIView animateWithDuration:0.5 animations:^{
                pop.frame = CGRectMake(0, 150, WIDTH, HEIGHT-150);
            }];
    
            //在点击改变frame,动画展示下滑
            [UIView animateWithDuration:0.5 animations:^{
                pop.frame = CGRectMake(0, HEIGHT, WIDTH, HEIGHT-150);
            }];
    

**三十九.masonry 动画效果有时候不实现需要添加此方法**

Paste_Image.png

**四十.设置手机声音震动**

    
    
        #import <AudioToolbox/AudioToolbox.h>
        #import <UIKit/UIKit.h>  
        - (void)vibrate   {    
              AudioServicesPlaySystemSound(kSystemSoundID_Vibrate);
    

**四十一.判断一个点是否在一个区域，判断一个区域是否在一个区域 **

    
    
       1.CGRect 和 CGPoint 对比 （判断一个点是否在一个区域）
    
            BOOL a = CGRectContainsPoint(_view.frame, point)
    
       2.CGRect 和 CGRect 对比 （判断一个区域是否在一个区域）
    
            BOOL b = CGRectContainsRect(_view.frame，_btn.frame)
    
       3. CGPoint 和 CGPoint 对比 （判断两个点是否相同）
    
            BOOL c = CGPointEqualToPoint(point1, point2);
    

**四十二,图片的简单压缩**

    
    
          1.  //背景视图 (此种压缩有白边出现)
            UIImageView *bgIma = [[UIImageView alloc] initWithFrame:BOUNDS];
            NSString *bgFile = [NSString stringWithFormat:@"%@/%@",[[NSBundle mainBundle] resourcePath,@"zsBg.png"]; //图片缓存处理
            UIImage *image = [[UIImage alloc] initWithContentsOfFile:bgFile];
            NSData *data = UIImageJPEGRepresentation(image, 1.0);
            bgIma.image = [UIImage imageWithData:data];
            [self addSubview:bgIma];
    
          2.封装方法
        - (UIImage *)imageWithImage:(UIImage*)image scaledToSize:(CGSize)newSize
        {
            // Create a graphics image context
            UIGraphicsBeginImageContext(newSize);
            // Tell the old image to draw in this new context, with the desired
            // new size
            [image drawInRect:CGRectMake(0,0,newSize.width,newSize.height)];
            // Get the new image from the context
            UIImage* newImage = UIGraphicsGetImageFromCurrentImageContext();
            // End the context
            UIGraphicsEndImageContext();
            // Return the new image.
            return newImage;
        }
    
        ((UIImageView *)view).image = [self imageWithImage:[UIImage imageNamed:self.notiArr[index]] scaledToSize:CGSizeMake(WIDTH-20, HEIGHT-64-10-180)] ;
    

** 四十三.横竖屏详细相关（全局竖屏，特殊控制器横屏）**

    
    
        1.点项目 - Targets - General - Deployment Info ，如图
    

C70563D6-8465-4F95-A2BA-B26519663417.png

    
    
        2.在 appdelegate 头文件中添加属性
    
            /// 判断是否横竖屏
            @property (nonatomic,assign)BOOL allowRotation;
    
        3.在 appdelegate 实现文件中实现方法
    
            /* 横竖屏 */
            - (UIInterfaceOrientationMask)application:(UIApplication *)application supportedInterfaceOrientationsForWindow:(UIWindow *)window {
                if (self.allowRotation) {
                    return  UIInterfaceOrientationMaskAllButUpsideDown;
                }
                return UIInterfaceOrientationMaskPortrait;
            }
    
        4.在需要横屏的文件中，导入头文件 #import "AppDelegate.h" ，添加如此代码
    
            /// 横竖屏相关
            AppDelegate *app =(AppDelegate *)[[UIApplication sharedApplication] delegate];
            app.allowRotation = YES;
    

**四十四.后台无线定位**

3754AB9E-4846-4668-ABB4-287C78C229A2.png

**四十五.使用Xcode查找项目中的中文字符串,以方便实现国际化的需求**

    
    
        1.打开”Find Navigator” (小放大镜模样 --- > 🔍)
        2.切换搜索模式到 “Find > Regular Expression”
        3.输入@"[^"]*[\u4E00-\u9FA5]+[^"\n]*?" (swift请去掉”@” 输入@"[^"]*[\u4E00-\u9FA5]+[^"\n]*?" 就好了)  
    

**四十六.判断 iOS 系统版本**

    
    
        _判断 iOS 系统版本大于10_
    
        #define IOS_VERSION_10 (NSFoundationVersionNumber > NSFoundationVersionNumber_iOS_9_x_Max)?(YES):(NO)  
    
        _判断 iOS系统具体版本_
    
        1.预编译文件(.pch文件)定义
        #define iPHONEType struct utsname systemInfo;uname(&systemInfo);
    
        引用
        iPHONEType
        NSString *platform = [NSString stringWithCString:systemInfo.machine encoding:NSASCIIStringEncoding];
    
        2.[UIDevice currentDevice].systemVersion.floatValue ,例如:
        
            if ([UIDevice currentDevice].systemVersion.floatValue < 7.0f) {
                    Method newMethod = class_getInstanceMethod(self, @selector(compatible_setSeparatorInset:));
                    // 增加Dummy方法
                    class_addMethod(
                            self,
                            @selector(setSeparatorInset:),
                            method_getImplementation(newMethod),
                            method_getTypeEncoding(newMethod));
                }
    

**四十七.判断 label 文字行数**

    
    
        - (NSArray *)getLinesArrayOfStringInLabel:(UILabel *)label{
                NSString *text = [label text];
                UIFont *font = [label font];
                CGRect rect = [label frame];
            
                CTFontRef myFont = CTFontCreateWithName(( CFStringRef)([font fontName]), [font pointSize], NULL);
                NSMutableAttributedString *attStr = [[NSMutableAttributedString alloc] initWithString:text];
                [attStr addAttribute:(NSString *)kCTFontAttributeName value:(__bridge  id)myFont range:NSMakeRange(0, attStr.length)];
                CFRelease(myFont);
                CTFramesetterRef frameSetter = CTFramesetterCreateWithAttributedString(( CFAttributedStringRef)attStr);
                CGMutablePathRef path = CGPathCreateMutable();
                CGPathAddRect(path, NULL, CGRectMake(0,0,rect.size.width,100000));
                CTFrameRef frame = CTFramesetterCreateFrame(frameSetter, CFRangeMake(0, 0), path, NULL);
                NSArray *lines = ( NSArray *)CTFrameGetLines(frame);
                NSMutableArray *linesArray = [[NSMutableArray alloc]init];
                for (id line in lines) {
                    CTLineRef lineRef = (__bridge  CTLineRef )line;
                    CFRange lineRange = CTLineGetStringRange(lineRef);
                    NSRange range = NSMakeRange(lineRange.location, lineRange.length);
                    NSString *lineString = [text substringWithRange:range];
                    CFAttributedStringSetAttribute((CFMutableAttributedStringRef)attStr, lineRange, kCTKernAttributeName, (CFTypeRef)([NSNumber numberWithFloat:0.0]));
                    CFAttributedStringSetAttribute((CFMutableAttributedStringRef)attStr, lineRange, kCTKernAttributeName, (CFTypeRef)([NSNumber numberWithInt:0.0]));
                    //NSLog(@"''''''''''''''''''%@",lineString);
                    [linesArray addObject:lineString];
                }
            
                CGPathRelease(path);
                CFRelease( frame );
                CFRelease(frameSetter);
                return (NSArray *)linesArray;
            }
    

**四十八.性能优化的小玩意 (Debug模式)**

    
    
        1. Product→Scheme→Edit Scheme 中 Run - Arguments - Environment Variables 设置Name为OS_ACTIVITY_MODE,Value为disable; //去除Xcode无效数据,也就是 去除 所有 NSLog 打印信息
    
        2.写到 .PCH 文件中 ,用来代替工程中的 NSLog 打印
    
            #ifdef DEBUG
            #define SLog(format, ...) printf("class: <%p %s:(%d) > method: %s \n%s\n", self, [[[NSString stringWithUTF8String:__FILE__] lastPathComponent] UTF8String], __LINE__, __PRETTY_FUNCTION__, [[NSString stringWithFormat:(format), ##__VA_ARGS__] UTF8String] )
            #else
            #define SLog(format, ...)
            #endif 
    
        3. release模式下 系统自动注释slog , 以便于优化性能
    

**四十九.筛选字符串(去除空格 换行符 回车符 首尾两端)**

    
    
        - (NSString *)returnCustomString:(NSString *)string
        {
            [[[[[string stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] stringByReplacingOccurrencesOfString:@"/r" withString:@""] stringByReplacingOccurrencesOfString:@"/n" withString:@""] stringByReplacingOccurrencesOfString:@" " withString:@""] stringByReplacingOccurrencesOfString:@"/tab" withString:@""];
            
            return string;
        }
    

**五十.数组和字典打印输出中文（新建一个分类，粘贴如下代码）**

    
    
        @implementation NSDictionary (LOG)
    
        - (NSString *)descriptionWithLocale:(id)locale
        {
            // 1.定义一个可变的字符串, 保存拼接结果
            NSMutableString *strM = [NSMutableString string];
            [strM appendString:@"{\n"];
            // 2.迭代字典中所有的key/value, 将这些值拼接到字符串中
            [self enumerateKeysAndObjectsUsingBlock:^(id key, id obj, BOOL *stop) {
                [strM appendFormat:@"\t%@ = %@,\n", key, obj];
            }];
            [strM appendString:@"}"];
            
            // 删除最后一个逗号
            if (self.allKeys.count > 0) {
                NSRange range = [strM rangeOfString:@"," options:NSBackwardsSearch];
                [strM deleteCharactersInRange:range];
            }
            
            // 3.返回拼接好的字符串
            return strM;
        }
        
        
        @end
        
        
        @implementation NSArray (LOG)
        - (NSString *)descriptionWithLocale:(id)locale
        {
            // 1.定义一个可变的字符串, 保存拼接结果
            NSMutableString *strM = [NSMutableString string];
            [strM appendString:@"(\n"];
            // 2.迭代字典中所有的key/value, 将这些值拼接到字符串中
            [self enumerateObjectsUsingBlock:^(id obj, NSUInteger idx, BOOL *stop) {
                [strM appendFormat:@"\t%@,\n", obj];
            }];
            [strM appendString:@")\n"];
            
            // 删除最后一个逗号
            if (self.count > 0) {
                NSRange range = [strM rangeOfString:@"," options:NSBackwardsSearch];
                [strM deleteCharactersInRange:range];
            }
            
            // 3.返回拼接好的字符串
            return strM;
        }
        @end
    

**五十一 . 十六进制转十进制**

    
    
        - (NSString *)turn16to10:(NSString *)str {
            if (str.length>10) {
                str =[str substringFromIndex:str.length-10];
            }
            NSLog(@"字符=%@", str);
            unsigned long long result = 0;
            NSScanner *scanner = [NSScanner scannerWithString:str];
            [scanner scanHexLongLong:&result];
            NSString *tempInt =[NSString stringWithFormat:@"%llu", result];
            if (tempInt.length>7) {
                tempInt =[tempInt substringFromIndex:tempInt.length-7];
            }
            NSLog(@"数字=%@", tempInt);
            return tempInt;
        }
    

**五十二.禁止苹果自带的侧滑返回功能**

    
    
    第一种方法：
        1.在需要禁止的控制器里面关闭侧滑返回
            - (void)viewDidAppear:(BOOL)animated  
            {  
                [super viewDidAppear:animated];  
                // 禁用返回手势  
                if ([self.navigationController respondsToSelector:@selector(interactivePopGestureRecognizer)]) {  
                    self.navigationController.interactivePopGestureRecognizer.enabled = NO;  
                }  
            }  
    
        2.如果只是单个页面关闭，其他页面可以侧滑返回
    
                - (void)viewWillDisappear:(BOOL)animated  
                {  
                    [super viewWillDisappear:animated];  
                    // 开启返回手势  
                    if ([self.navigationController respondsToSelector:@selector(interactivePopGestureRecognizer)]) {  
                        self.navigationController.interactivePopGestureRecognizer.enabled = YES;  
                    }  
                }
    
    第二种方法：
    
        -(void)popGestureChange:(UIViewController *)vc enable:(BOOL)enable{
              if ([vc.navigationController respondsToSelector:@selector(interactivePopGestureRecognizer)]) {
                    //遍历所有的手势
                    for (UIGestureRecognizer *popGesture in vc.navigationController.interactivePopGestureRecognizer.view.gestureRecognizers) {
                  popGesture.enabled = enable;
                    }
               }
        }
      这个函数的使用可以在viewDidAppear调用，调用完之后记得在viewDidDisappear恢复原先的设置
    

**五十三、合并framework**

    
    
        1.常规的需要合并 真机版framework 和模拟器版framework ，需要用到 lipo指令：lipo -create 真机版本路径 模拟器版本路径 -output 合并后的文件路径 （注：空格不能省去）！示例：
    
            路径1：/Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/Products/Release-iphoneos/IJKMediaFramework.framework/IJKMediaFramework
    
            路径2：/Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/Products/Release-iphonesimulator/IJKMediaFramework.framework/IJKMediaFramework
    
            合并后的路径及名称：/Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/IJKMediaFramework 
    
            lipo -create /Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/Products/Release-iphoneos/IJKMediaFramework.framework/IJKMediaFramework /Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/Products/Release-iphonesimulator/IJKMediaFramework.framework/IJKMediaFramework -output /Users/XXX/Library/Developer/Xcode/DerivedData/IJKMediaPlayer-giggdwtupptvcyalfbtxfhwssrix/Build/IJKMediaFramework 
    
        2.报错及注意点
    
            1）指令之间的空格不能省去
            2）报错：fatal error: can't map input file 
    
                原因是因为 framework 路径格式输入错误，需要将 xxxFramework.framework 改成 xxxFramework.framework/xxxFramework
    
            3）报错：can't move temporary file
    
                原因是因为 合并后的 路径格式输入错误，需要在路径后面加入合并后你起的文件名称 ，/Users/Zhuge_Su/Desktop 改成 /Users/Zhuge_Su/Desktop/xxx.framework  （xxx需要自己自定义）
    

**五十四、更改 textfield 占位符 相关**

    
    
           UIColor *color = [UIColor whiteColor];  
          _userName.attributedPlaceholder = [[NSAttributedString alloc] initWithString:@"用户名" attributes:@{NSForegroundColorAttributeName: color}];
    

**五十五、tableview 从第四行或者第五行显示 解决方法**

    
    
        在动态布局tableview行高的时候，会出现tableview cell 从第四行或者第五行开始加载，解决方案：昨个判断 如果动态行高大于0 显示动态行高；如果动态行高等于0 ，默认返回一个 1或者 2值 ，举例：
    
          - (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath{
            if (self.totalCellHeight > 0) {
                return self.totalCellHeight;
            } else{
                return 1;
            }
            return 0;
        }
    

**五十四.IPV6环境搭建**

[ Enter your link description here:
](https://links.jianshu.com/go?to=http%3A%2F%2Fwww.cocoachina.com%2Fios%2F20160613%2F16626.html)

**五十五.加急审核链接**

    
    
    [ 链接 ](https://developer.apple.com/appstore/contact/appreviewteam/index.html)
    

**五十六.上架审核的小注意点**

    
    
    1.检查全局断点是否都清除完毕;
    
    2.检查 EditScheme 是否都是release状态;
    
    3.检查所有数据是否包含 测试,demo 等中英文字样;
    
    4.检查 后台模式,去除掉不需要使用的后台模式,尤其是定位相关;相关文字描述要描述清楚;
    
    5.为以防万一,未开发的项目还是隐藏的好(看个人人品);
    
    6.产品流程上,可点击和不可点击状态要有不同显示或者提示;
    

**五十七.app在app store 上的地址**

    
    
    http://itunes.apple.com/cn/app/idXXXXXXXXXX?mt=8 (XXXXXXXXXX 是你app 在itunes connect上创建的app id)
    itms-apps://itunes.apple.com/app/id1144099528
    

**五十八、Xcode断点失效解决方法**

    
    
    1.首先点击菜单product->Debug workflow取消选中show Disassembly when debug 是否勾选,如果勾选点击取消
    

图片.png

    
    
    2. Build Setting 中 Generate Debug Symbols 设置为 Yes
    

图片.png

    
    
    3.Build Setting中将`Enable Clang Module Debugging`设置为`NO`即可",
    

**五十九、更改项目名字**

[传送门](https://www.jianshu.com/p/2887d6fb5769)

**六十、下载Xcode中的版本**

[传送门1](https://www.jianshu.com/p/88d453ba0b92)  
[传送门2](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FRayJiang16%2FiOSDeviceSupport)

**六十一、iPhone X tabbar重影**

    
    
    -(void)viewWillLayoutSubviews{
      [super viewWillLayoutSubviews];
    
      for (UIView *child in self.tabBarController.tabBar.subviews) {
          if ([child isKindOfClass:NSClassFromString(@"UITabBarButton")]) {
              [child removeFromSuperview];
          }
      }
    

}

**六十二、转让app**

[传送门](https://www.jianshu.com/p/0a99a3092111)

**六十三、苹果开发者相关**

    
    
     电话： 4006701855
     网址：https://developer.apple.com
     3.2.1审核相关网址：https://tieba.baidu.com/p/5659292532?red_tag=2857790889
                                   https://www.cnblogs.com/zk1947/p/8425506.html
    

**六十四、iTerm 自动补全相关**

    
    
    打开终端，输入 : 
    
      nano .inputrc
    
      在文件里面写上：
    
      set completion-ignore-case on
      set show-all-if-ambiguous on
      TAB: menu-complete
    
      ctrl + o ,回车，重启终端，自动补全按tap键就ok。
    

更改iterm2的颜色  
[传送门](https://www.jianshu.com/p/e7655f6ecb97)

**六十五、描述文件相关**

    
    
           1.查看描述文件的位置
    
                 所有的描述文件安装后，都保存在Provisioning Profiles目录下。完整路径为：~/Library/MobileDevice/Provisioning Profiles
    
    
          2.查看描述文件的内容
    
          在终端使用命令查看：/usr/bin/security cms -D -i 文件路径 
    

**六十六、如何解决“app已损坏，打不开。你应该将它移到废纸篓。**

    
    
           命令行运行：
          修改系统配置：系统偏好设置… -> 安全性与隐私。修改为任何来源
          如果没有这个选项的话 ,打开终端，执行
    
          sudo spctl --master-disable 
          sudo spctl --master-disable Rference
    

**六十七、新建Xcode指定默认类名前缀**

51530583gw1eqccvyqgd1j20ow0sednl.jpg

**六十八、测试iOS版的App注意事项**

    
    
          1、app使用过程中，接听电话，可以测试不同的通话时间的长短，对于通话结束后，原先打开的app的响应，比如是否停留在原先界面，继续操作时的相应速度等。
          2、app使用过程中，有推送消息时，对app的使用影响。
          3、设备在充电时，app的响应以及操作流畅度。
          4、设备在不同电量时（低于10%，50%95%），app的响应以及操作流畅度
          5、意外断电时，app数据丢失情况
          6、网络环境变化时，app的应对情况如何：是否有是当提示？从有网络环境到无网络环境时，app的反馈如何？从无网络环境回到有网络环境时，是否能自动加载数据，多久才能开始加载数据
          7、多点触摸的情况
          8、跟其他app之间互相切换时的响应
          9、进程关闭再重新打开的反馈
          10、iOS系统语言环境变化时
    

**六十九、QQ ID 转 十六进制**

    
    
    echo 'ibase=10;obase=16;101553465'|bc
    

**七十、查看cocoapods版本和.a版本**

    
    
    pod search GoogleWebRTC （查看cocoapods下三方版本）
    lipo -info XXX.a (cd到.a目录下，输出指令)
    

**七十一、查看cocoapods版本和.a版本**

    
    
    self.areaIcon.image = [[UIImage imageNamed:@"ico_title_city.png"] imageWithRenderingMode:UIImageRenderingModeAlwaysTemplate];
    self.areaIcon.tintColor = [UIColor whiteColor];
    

**七十二、根据滚动距离调整导航视图透明度**

    
    
    - (void)scrollViewDidScroll:(UIScrollView *)scrollView{
    
        CGFloat y = scrollView.contentOffset.y;
        self.navBarContainer.alpha = y/(546 * (kDeviceWidth / 750.0) - MSUNavHeight);
        CGFloat alpha = self.navBarContainer.alpha * 3;
        self.leftButton.alpha = 1 - alpha;
    }
    

**七十三、当前页面设置后切换整个App设置**

1.不含子视图的切换 （项目视图层级比较多，所以多了一层）

    
    
    MSUMainTabbarController *tab = [[MSUMainTabbarController alloc] init];
    tab.selectedIndex = 3;
    
    MSUMainNavigationController *mainNav = (MSUMainNavigationController *)tab.selectedViewController;
    TUNewPersonController *new = (TUNewPersonController *)mainNav.visibleViewController;
    new.selectedIndex = index;
    
    ///解决动画bug
    dispatch_async(dispatch_get_main_queue(), ^{
        [[[UIApplication sharedApplication] delegate] window].rootViewController = tab;
        //一些UI提示，可以提供更友好的用户交互（也可以删掉）
        [SVProgressHUD showWithStatus:@"正在切换"];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(.5 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            [SVProgressHUD dismiss];
        });
    });
    

2.包含子视图的切换（项目视图层级比较多，所以多了一层）

    
    
    MSUMainTabbarController *tab = [[MSUMainTabbarController alloc] init];
    tab.selectedIndex = 3;
    
    MSUMainNavigationController *mainNav = (MSUMainNavigationController *)tab.selectedViewController;
    TUNewPersonController *new = (TUNewPersonController *)mainNav.visibleViewController;
    new.selectedIndex = 0;
    
    MSUMainNavigationController *newNav = (MSUMainNavigationController *)new.selectedViewController;
    
    TUPersonSettingController *set = [[TUPersonSettingController alloc] init];
    TULampSetController *lamp = [[TULampSetController alloc] init];
    newNav.viewControllers = @[set,lamp];
    
    ///解决动画bug
    dispatch_async(dispatch_get_main_queue(), ^{
        g_window.rootViewController = tab;
        [[NSNotificationCenter defaultCenter] postNotificationName:TUSettingChange object:nil];
        //一些UI提示，可以提供更友好的用户交互（也可以删掉）
        [SVProgressHUD showWithStatus:@"正在切换"];
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(.5 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
            [SVProgressHUD dismiss];
        });
    });
    

**七十四、多Configuration配置环境**

    
    
    1.在Project - Info - Configuration 新增需要的configuration环境
    

图片.png

    
    
    2.在PODS - Info - Configuration  新增需要的configuration环境
    

图片.png

    
    
    3.pod install 后 ，查看Project 和 PODS 里面的Build setting 对应的Preproessor Macro 里面的键值对
    

图片.png

    
    
    4.使用
    

图片.png

**七十五、大文件下载 -- lfs**

    
    
     brew install git-lfs
     git lfs install
    

[下载链接](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fgit-
lfs%2Fgit-lfs)

**七十六、xcode搜索 <replace>汉字替换正则匹配**  
1.@". _[\u4e00-\u9fa5]+._ "  
2.:@"["]*[\u4E00-\u9FA5]+["\n] _?"  
3.@"[^"]_[\u4E00-\u9FA5]+[^"\n] _?"  
4.(@"[^"]_[\u4E00-\u9FA5]+[^"\n]*?")  
LCLocalizedString(nil, $1)  

image.png

**七十七、查询某个framework是否支持bitcode**

    
    
    otool -l framework二进制文件地址 | grep __LLVM | wc -l
    为0表示不支持
    

image.png

**七十八、label的展开和收起**

    
    
     /// 是否展示展开/收起
    - (void)setupAddMoreBtn
    {
      BOOL isShowAll = self.model.isShowAll;
      self.contentLabel.numberOfLines = isShowAll ? 0 : 2;
    
      NSString *contentStr = self.model.content;
      if ([LCPathTools checkIsJsonString:self.model.content]) {
          LCCommunityContentModel *contentModel = [LCCommunityContentModel yy_modelWithJSON:self.model.content];
          contentStr = contentModel.content;
      }
      NSMutableAttributedString *attStr = [self getFinalContentStrWithContent:contentStr];
      YYTextLayout *layoutWidth = [YYTextLayout layoutWithContainerSize:CGSizeMake(LCDeviceWidth - LC_X(87), CGFLOAT_MAX) text:attStr.copy];
    
      if (layoutWidth.rowCount > 2) {
        NSString *str = isShowAll ? LCLocalizedString(@"App_domestic_2501", @"收起") : LCLocalizedString(@"App_domestic_3237", @"展开");
        NSMutableAttributedString *showAtt = [self getFinalContentStrWithContent:[NSString stringWithFormat:@"...    %@", str]];
        if (isShowAll) {
            showAtt = [self getFinalContentStrWithContent:[NSString stringWithFormat:@"    %@", str]];
        }
        
        NSRange expandRange = [showAtt.string rangeOfString:str];
        [showAtt addAttribute:NSForegroundColorAttributeName value:[LCApperance mainYellowColor] range:expandRange];
        
        YYTextHighlight *hi = [YYTextHighlight new];
        [showAtt yy_setTextHighlight:hi range:expandRange];
        MJWeakSelf;
        hi.tapAction = ^(UIView *containerView, NSAttributedString *text, NSRange range, CGRect rect) {
            weakSelf.model.isShowAll = !isShowAll;
            [weakSelf setupAddMoreBtn];
        };
        
        if (isShowAll) {
            [attStr appendAttributedString:showAtt];
            self.contentLabel.truncationToken = nil;
        } else {
            YYLabel *seeMore = [YYLabel new];
            seeMore.attributedText = showAtt;
            [seeMore sizeToFit];
            
            NSAttributedString *truncationToken = [NSAttributedString yy_attachmentStringWithContent:seeMore contentMode:UIViewContentModeRight attachmentSize:showAtt.size  alignToFont:showAtt.yy_font alignment:YYTextVerticalAlignmentCenter];
            self.contentLabel.truncationToken = truncationToken;
        }
        YYTextLayout *layoutWidth = [YYTextLayout layoutWithContainerSize:CGSizeMake(LCDeviceWidth - LC_X(87), CGFLOAT_MAX) text:attStr.copy];
        
        //文本高度
        CGFloat contentH = layoutWidth.textBoundingSize.height;
        CGFloat scrollH = contentH;
        
        // 最大限制<场景分带链接和不带链接>
        CGFloat linkH = self.leftImageView.isHidden ? 0 : LC_DeviceX(24);
        CGFloat maxLimit = [LCPathTools checkIsJsonString:self.model.content] ? LC_DeviceX(112)+linkH : LC_DeviceX(136)+linkH;
    
        if (isShowAll) {
            if (contentH > maxLimit) {
                scrollH = maxLimit;
            }
        } else {
            if (contentH > LC_X(44)) {
                scrollH = LC_X(40)+linkH;
                contentH = LC_X(40);
            }
        }
        [self.scrollView mas_updateConstraints:^(MASConstraintMaker *make) {
            make.height.mas_equalTo(scrollH);
        }];
        [self.contentLabel mas_updateConstraints:^(MASConstraintMaker *make) {
            make.height.mas_equalTo(contentH);
            make.bottom.equalTo(self.scrollView.mas_bottom).offset(-linkH);
        }];
      } else {
        CGFloat linkH = self.leftImageView.isHidden ? 0 : LC_DeviceX(24);
        [self.scrollView mas_updateConstraints:^(MASConstraintMaker *make) {
            make.height.mas_equalTo(44+linkH);
        }];
        [self.contentLabel mas_updateConstraints:^(MASConstraintMaker *make) {
            make.height.mas_equalTo(44);
        }];
      }
      self.contentLabel.attributedText = attStr;
    }
    

