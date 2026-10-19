Swift-按钮扩展(图片位置/倒计时/点击事件闭包回调)

[ SK丿希望](https://www.jianshu.com/u/19fd33d39249)关注赞赏支持

# Swift-按钮扩展(图片位置/倒计时/点击事件闭包回调)

### 实现效果(是用Xib创建也支持代码)

image.png

### 代码演示

    
    
      override func viewDidLoad() {
            super.viewDidLoad()
            // 图片在上
            button.hw_locationAdjust(buttonMode: .Top, spacing: 10)
            // 图片在左
            button1.hw_locationAdjust(buttonMode: .Left, spacing: 10)
            // 图片在右
            button2.hw_locationAdjust(buttonMode: .Right, spacing: 10)
            // 图片在下 
            button3.hw_locationAdjust(buttonMode: .Bottom, spacing: 10)
            // 快速添加点击事件
            codeButton.addAction { [weak self] in
                // 倒计时
                self?.codeButton.countDown(count: 60, countDownBgColor: UIColor.lightGray)
            }
     }
    

### 实现原理

    
    
    import UIKit
    
    // MARK: - 快速设置按钮 并监听点击事件
    typealias  buttonClick = (()->()) // 定义数据类型(其实就是设置别名)
    extension UIButton{
        
        // 改进写法【推荐】
        private struct RuntimeKey {
            static let actionBlock = UnsafeRawPointer.init(bitPattern: "actionBlock".hashValue)
            /// ...其他Key声明
        }
        /// 运行时关联
        private var actionBlock: buttonClick? {
            set {
                objc_setAssociatedObject(self, UIButton.RuntimeKey.actionBlock!, newValue, .OBJC_ASSOCIATION_COPY_NONATOMIC)
            }
            get {
                return objc_getAssociatedObject(self, UIButton.RuntimeKey.actionBlock!) as? buttonClick
            }
        }
        /// 点击回调
        @objc private func tapped(button:UIButton){
            if self.actionBlock != nil {
                self.actionBlock!()
            }
        }
        /// 添加点击事件
        func addAction(action:@escaping buttonClick) {
            self.addTarget(self, action:#selector(tapped(button:)) , for:.touchUpInside)
            self.actionBlock = action
        }
        /// 快速创建
        convenience init(setImage:String, action:@escaping buttonClick){
            self.init()
            self.frame = frame
            self.setImage(UIImage(named:setImage), for: UIControlState.normal)
            self.addAction {
                action()
            }
            self.sizeToFit()
        }
        /// 快速创建
        convenience init(action:@escaping buttonClick){
            self.init()
            self.addAction {
                action()
            }
            self.sizeToFit()
        }
        /// 快速创建按钮 setImage: 图片名 frame:frame action:点击事件的回调
        convenience init(setImage:String, frame:CGRect, action: @escaping buttonClick){
            self.init( setImage: setImage, action: action)
            self.frame = frame
        }
        convenience init(titleString:String, action:@escaping buttonClick){
            self.init()
            self.frame = frame
            self.setTitle(titleString, for: .normal)
            self.addAction {
                action()
            }
            self.sizeToFit()
        }
        /// 快速创建按钮 titleString:title  frame:frame action:点击事件的回调
        convenience init(titleString:String, frame:CGRect, action: @escaping buttonClick){
            self.init(titleString: titleString, action: action)
            self.frame = frame
        }
    }
    
    // MARK: - 倒计时
    extension UIButton{
        // MARK:倒计时 count:多少秒 默认倒计时的背景颜色gray
        /// 倒计时 count:多少秒 默认倒计时的背景颜色gray
        public func countDown(count: Int){
            self.countDown(count: count, countDownBgColor: UIColor.gray)
        }
        // MARK:倒计时 count:多少秒 countDownBgColor:倒计时背景颜色
        /// 倒计时 count:多少秒 countDownBgColor:倒计时背景颜色
        public func countDown(count: Int,countDownBgColor:UIColor){
            // 倒计时开始,禁止点击事件
            isEnabled = false
            // 保存当前的背景颜色
            let defaultColor = self.backgroundColor
            // 设置倒计时,按钮背景颜色
            backgroundColor = countDownBgColor
            var remainingCount: Int = count {
                willSet {
                    titleLabel?.text = "\(newValue)s"
                    setTitle("\(newValue)s", for: .normal)
                    if newValue <= 0 {
                        titleLabel?.text = "发送验证码"
                        setTitle("发送验证码", for: .normal)
                    }
                }
            }
            // 在global线程里创建一个时间源
            let codeTimer = DispatchSource.makeTimerSource(queue:DispatchQueue.global())
            // 设定这个时间源是每秒循环一次，立即开始
            codeTimer.schedule(deadline: .now(), repeating: .seconds(1))
            // 设定时间源的触发事件
            codeTimer.setEventHandler(handler: {
                // 返回主线程处理一些事件，更新UI等等
                DispatchQueue.main.async {
                    // 每秒计时一次
                    remainingCount -= 1
                    // 时间到了取消时间源
                    if remainingCount <= 0 {
                        self.backgroundColor = defaultColor
                        self.isEnabled = true
                        codeTimer.cancel()
                    }
                }
            })
            // 启动时间源
            codeTimer.resume()
        }
    }
    // MARK: - 调整位置相关
    enum HWButtonMode {
        case Top
        case Bottom
        case Left
        case Right
    }
    extension UIButton {
        /// 快速调整图片与文字位置
        ///
        /// - Parameters:
        ///   - buttonMode: 图片所在位置
        ///   - spacing: 文字和图片之间的间距
        @discardableResult
        func hw_locationAdjust(buttonMode: HWButtonMode,
                               spacing: CGFloat) -> UIButton {
            let imageSize = self.imageRect(forContentRect: self.frame)
            let titleFont = self.titleLabel?.font!
            let titleSize = titleLabel?.text?.size(withAttributes: [kCTFontAttributeName as NSAttributedStringKey: titleFont!]) ?? CGSize.zero
            var titleInsets: UIEdgeInsets
            var imageInsets: UIEdgeInsets
            switch (buttonMode){
            case .Top:
                titleInsets = UIEdgeInsets(top: (imageSize.height + titleSize.height + spacing)/2,
                                           left: -(imageSize.width), bottom: 0, right: 0)
                imageInsets = UIEdgeInsets(top: -(imageSize.height + titleSize.height + spacing)/2, left: 0, bottom: 0, right: -titleSize.width)
            case .Bottom:
                titleInsets = UIEdgeInsets(top: -(imageSize.height + titleSize.height + spacing)/2,
                                           left: -(imageSize.width), bottom: 0, right: 0)
                imageInsets = UIEdgeInsets(top: (imageSize.height + titleSize.height + spacing)/2, left: 0, bottom: 0, right: -titleSize.width)
            case .Left:
                titleInsets = UIEdgeInsets(top: 0, left: 0, bottom: 0, right: -spacing)
                imageInsets = UIEdgeInsets(top: 0, left: 0, bottom: 0, right: 0)
            case .Right:
                titleInsets = UIEdgeInsets(top: 0, left: -(imageSize.width * 2), bottom: 0, right: 0)
                imageInsets = UIEdgeInsets(top: 0, left: 0, bottom: 0,
                                           right: -(titleSize.width * 2 + spacing))
            }
            self.titleEdgeInsets = titleInsets
            self.imageEdgeInsets = imageInsets
            return self
        }
    }
    
    

[Dome](https://share.weiyun.com/53uaPQc)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS工具和框架1](https://www.jianshu.com/p/0321333fba35)

1、通过CocoaPods安装项目名称项目信息 AFNetworking网络请求组件 FMDB本地数据库组件 SD...

[爱运动爱学习](https://www.jianshu.com/u/949e63975031)阅读 15,747评论 3赞 114

  * [ch2- 什么是shell](https://www.jianshu.com/p/b79c767469a9)

以下都是对 The Linux command line 一书所做的笔记,以求日后忘记时候可以翻阅 为什么使用Li...

[Klaas](https://www.jianshu.com/u/a643473aae8c)阅读 210评论 0赞 0

  * [如何成为一个高手](https://www.jianshu.com/p/d5c2c55d4760)

开篇 如何成为一个高手？先看看高手是如何炼成的。 本周，通过三种不同的方式，与三位高手进行“对话”： 1. 采铜 ...

[我是榴莲骑士](https://www.jianshu.com/u/450770b62a66)阅读 1,851评论 0赞 3

  * [用Drupal建立网站](https://www.jianshu.com/p/d7a93b8efa88)

Have Drupal up and running and wondering "now what"? You’...

[王乂](https://www.jianshu.com/u/aec7b94dfe64)阅读 1,342评论 0赞 4

  * [不一样的高度，看到的风景是不一样的](https://www.jianshu.com/p/3ea2d116d926)

副标题 致30岁的自己 我的大学时代过得并不快乐，反而每天都很忧郁并忧愁。一方面来讲，学习还算是比较刻苦，但是并没...

[风止了](https://www.jianshu.com/u/7184b445678f)阅读 2,330评论 2赞 9

 