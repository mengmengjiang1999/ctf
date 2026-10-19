iOS Review | 你所不知道的10种Layer

[ 清無](https://www.jianshu.com/u/484e1c9f1ae9)关注赞赏支持

# iOS Review | 你所不知道的10种Layer

### 1\. CALayer

##### UIView和CALayer的关系

UIView和CALayer的关系

  * 一个View只能有一个Root Layer；
  * 一个Layer可以包含多个Sub Layer；
  * View只负责子元素的布局`Layout`和事件处理`Events`；
  * Layer负责View上内容的绘制`drawRect`和显示，以及动画`CAAnimation`；

##### CALayer Basic Properties

  * corner 圆角

    
    
    let layer = view.layer
    layer.masksToBounds = true // 必须为true
    layer.cornerRadius = 10
    

  * border 边框

    
    
    let layer = view.layer
    layer.borderColor = UIColor.red.cgColor
    layer.borderWidth = 10
    

  * shadow 投影

    
    
    let layer = view.layer
    layer.shadowColor = UIColor.green.cgColor
    layer.shadowRadius = 10 // 半径
    layer.shadowOpacity = 0.5 // 透明度
    layer.shadowOffset = CGSize(width: 0, height: 10) // 偏移: x, y
    

  * contents 只能设置为图片`CGImage / NSImage`

    
    
    let layer = view.layer
    layer.contentsGravity = kCAGravityCenter
    layer.contentsScale = UIScreen.main.scale
    layer.contents = UIImage.init(named: "star")?.cgImage
    

  * shouldRasterize 栅格化

    * 默认是false，设置为true时，layer只被渲染一次（相当于一张静态图片）；
    * 这适用于做一些与appearance无关的动画（如posistion, scale, rotate）等；
    * 可以很大程度提升性能（如果layer上内容比较复杂的话）；
  * drawsAsynchronously 异步绘制

    * 和shouldRasterize的功能相反，为异步连续多次绘制；
    * 默认是false，为true时，如果layer必须得连续重新绘制时，可以提升性能（例如粒子发射layer）；

### 2\. CAScrollLayer

  * CAScrollLayer其实是一个比较简单功能的类，它只有一个有用的方法`scroll(to p: CGPoint)`和`scroll(to r: CGRect)`；
  * 只能部分地滚动，如果要实现全部的滚动，只能用UIScrollView；
  * 不过它可以结合UIImageView和UIPanGesture简单模拟UIScrollView；
  * 可以设置滚动模式为水平、垂直、二者、不可；

    
    
    scrollingViewLayer.scrollMode = kCAScrollBoth
    

ScrollingView + UIImageView

  * 自定义Scrolling View

    
    
    import QuartzCore
    
    class ScrollingView: UIView {
      override class var layerClass : AnyClass {
        return CAScrollLayer.self
      }
    }
    

  * 手势处理

    
    
        @IBAction func panRecognized(_ sender: UIPanGestureRecognizer) {
    // 计算滚动点
            var newPoint = scrollingView.bounds.origin
            newPoint.x -= sender.translation(in: scrollingView).x
            newPoint.y -= sender.translation(in: scrollingView).y
            sender.setTranslation(CGPoint.zero, in: scrollingView)
    // 滚动到新点
            scrollingViewLayer.scroll(to: newPoint)
        }
    

CAScrollLayer

### 3\. CATextLayer

  * CATextLayer是一个在指定Rect的Layer里快速绘制纯文本或富文本的layer类；
  * 它可以设置字体、字体大小、字体颜色、对齐方式、多行/单行显示模式、文本截断模式等，所有属性均可动画显示；

    
    
        let string = String.init(repeating: "这是测试CATextLayer的文字--", count: 10)
    
        textLayer.string = string // 可以是NSAttributedString
        textLayer.font = CTFontCreateWithName("Noteworthy-Light" as CFString, 0, nil)
        textLayer.fontSize = 18
        textLayer.foregroundColor = UIColor.red.cgColor // 字体颜色
        textLayer.isWrapped = true // 单行/多行
        textLayer.alignmentMode = kCAAlignmentLeft
        textLayer.truncationMode = kCATruncationEnd
        textLayer.contentsScale = UIScreen.main.scale
    

CATextLayer

### 4\. AVPlayerLayer

  * AVPlayerLayer是AVFoundation库中的一个视频播放layer，用法较为简单；
  * 层级关系为AVPlayerLayer>AVPlayer>AVPlayerItem；

    
    
    var player: AVPlayer!
    
    override func viewDidLoad() {
      super.viewDidLoad()
    
      // 1
      let playerLayer = AVPlayerLayer()
      playerLayer.frame = someView.bounds
      
      // 2
      let url = Bundle.main.url(forResource: "someVideo", withExtension: "m4v")
      player = AVPlayer(url: url!)
      
      // 3
    
      // 播放完成后执行的操作--无、暂停、下一个`advance`（只适用于AVQueuePlayer）
      player.actionAtItemEnd = .none 
      playerLayer.player = player
      someView.layer.addSublayer(playerLayer)
      
      // 4
      NotificationCenter.default.addObserver(self,
                                             selector: #selector(playerDidReachEnd),
                                             name: .AVPlayerItemDidPlayToEndTime,
                                             object: player.currentItem)
    }
    
    deinit {
      NotificationCenter.default.removeObserver(self)
    }
    

AVPlayerLayer

### 5\. CAGradientLayer

  * 顾名思义为渐变层，专门用来做渐变色的。
  * 用法很简单，设置一组colors、startPoint和endPoint就可以了，如果了解PS的话，相信很容易理解startPoint和endPoint；
  * 当然，它只支持线性渐变；

    
    
    func cgColor(red: CGFloat, green: CGFloat, blue: CGFloat) -> CGColor {
      return UIColor(red: red/255.0, green: green/255.0, blue: blue/255.0, alpha: 1.0).cgColor
    }
    
    let gradientLayer = CAGradientLayer()
    gradientLayer.frame = someView.bounds
    gradientLayer.colors = [cgColor(red: 209.0, green: 0.0, blue: 0.0),
                            cgColor(red: 255.0, green: 102.0, blue: 34.0),
                            cgColor(red: 255.0, green: 218.0, blue: 33.0),
                            cgColor(red: 51.0, green: 221.0, blue: 0.0),
                            cgColor(red: 17.0, green: 51.0, blue: 204.0),
                            cgColor(red: 34.0, green: 0.0, blue: 102.0),
                            cgColor(red: 51.0, green: 0.0, blue: 68.0)]
    
    gradientLayer.startPoint = CGPoint(x: 0, y: 0)
    gradientLayer.endPoint = CGPoint(x: 0, y: 1)
    someView.layer.addSublayer(gradientLayer)
    

  * 当然你也可以通过设置locations来控制每个颜色的渐变起始位置；

    
    
    gradientLayer.locations: [NSNumber] = [:]
    

垂直渐变

水平渐变

### 6\. CAReplicatorLayer

  * CAReplicatorLayer是将一个layer复制了`instanceCount`次，主要用来做一些动画；

  * 另外它可以设置复制间隔`instanceDelay`、和主要色`instanceColor`（针对subLayer起作用），以及复制层的颜色偏移（即过渡值），分别有`instanceRedOffset`、`instanceGreenOffset`、`instanceBlueOffset`和`instanceAlphaOffset`属性；

  * 如果设置了instanceColor为whiteColor，即RGBA均为1，则instanceRedOffset设置范围为`-1~0`，对应颜色component的范围则是`0~1`；

  * 最终的instanceColor即为RGBA三者offset值计算的混合色；

    
    
    // 复制器层
    replicatorLayer.backgroundColor = UIColor.clear.cgColor
    replicatorLayer.instanceCount = 30
    replicatorLayer.instanceDelay = CFTimeInterval(1 / 30.0)
    replicatorLayer.preservesDepth = false
    replicatorLayer.instanceColor = UIColor.red.cgColor
    replicatorLayer.instanceRedOffset = 0
    replicatorLayer.instanceGreenOffset = -1
    replicatorLayer.instanceBlueOffset = -1
    replicatorLayer.instanceAlphaOffset = -1 / Float(replicatorLayer.instanceCount)
    replicatorLayer.instanceTransform = CATransform3DMakeRotation(CGFloat.pi * 2 / 30, 0, 0, 1)
    
    // 实例层
    let layerWidth: CGFloat = 10
    let instanceLayer = CALayer()
    instanceLayer.backgroundColor = UIColor.white.cgColor
    let midX = replicatorLayer.bounds.midX - layerWidth / 2
    instanceLayer.frame = CGRect(x: midX, y: 0, width: layerWidth, height: layerWidth * 3)
    replicatorLayer.addSublayer(instanceLayer)
    

RGBA offset = 0, -1, -1, (-1 / Float(replicatorLayer.instanceCount))

    
    
    // 动画
    let fadeAnimation = CABasicAnimation.init(keyPath: "opacity")
    fadeAnimation.fromValue = 1
    fadeAnimation.toValue = 0
    fadeAnimation.duration = 1
    fadeAnimation.repeatCount = Float(Int.max)
    instanceLayer.opacity = 0
    instanceLayer.add(fadeAnimation, forKey: "FadeAnimation")
    

动画效果

### 7\. CATiledLayer

  * 瓷砖层，也叫马赛克层，相信很多人不太了解。
  * 它必将实用的一个地方是可以异步绘制，这在处理需要很占内存的视图时很有好处，比如讲一张全景photo加载到scrollView上，非常耗内存，这是可以用CATiledLayer异步绘制只在当前屏幕区域内的小图。
  * 另外它还有两个提高绘制精度的属性`levelsOfDetail`和`levelsOfDetailBias`后者是抗锯齿的级别，数值越高显示效果越细腻，单位像素点越多；
  * 使用该类要自定义view基于UIView，重写`drawRect`方法来实现内容的绘制，但注意不能直接设置layer.contents；

levelsOfDetailBias = 1

levelsOfDetailBias = 5

    
    
    class TiledBackgroundView: UIView {
    
        let sideLength: CGFloat = 50
        override class var layerClass: AnyClass{
            return CATiledLayer.self
        }
        
        override func draw(_ rect: CGRect) {
            let context = UIGraphicsGetCurrentContext()
            let red = CGFloat(drand48())
            let green = CGFloat(drand48())
            let blue = CGFloat(drand48())
            context?.setFillColor(red: red, green: green, blue: blue, alpha: 1)
            context?.fill(rect)
        }
    
        required init?(coder aDecoder: NSCoder) {
            super.init(coder: aDecoder)
            
            let layer = self.layer as! CATiledLayer
            let scale = UIScreen.main.scale
            layer.contentsScale = scale
            layer.tileSize = CGSize(width: sideLength * scale, height: sideLength * scale)
        }
    
    }
    

image.png

  * 将大图切割成多个小图

    
    
    extension UIImage {
      
      class func saveTileOfSize(_ size: CGSize, name: String) -> () {
        let cachesPath = NSSearchPathForDirectoriesInDomains(.cachesDirectory, .userDomainMask, true)[0] as String
        let filePath = "\(cachesPath)/\(name)_0_0.png"
        let fileManager = FileManager.default
        let fileExists = fileManager.fileExists(atPath: filePath)
            
        if fileExists == false {
          var tileSize = size
          let scale = Float(UIScreen.main.scale)
          
          if let image = UIImage(named: "\(name).jpg") {
            let imageRef = image.cgImage
            let totalColumns = Int(ceilf(Float(image.size.width / tileSize.width)) * scale)
            let totalRows = Int(ceilf(Float(image.size.height / tileSize.height)) * scale)
            let partialColumnWidth = Int(image.size.width.truncatingRemainder(dividingBy: tileSize.width))
            let partialRowHeight = Int(image.size.height.truncatingRemainder(dividingBy: tileSize.height))
            
            DispatchQueue.global(qos: .default).async {
              for y in 0..<totalRows {
                for x in 0..<totalColumns {
                  if partialRowHeight > 0 && y + 1 == totalRows {
                    tileSize.height = CGFloat(partialRowHeight)
                  }
                  
                  if partialColumnWidth > 0 && x + 1 == totalColumns {
                    tileSize.width = CGFloat(partialColumnWidth)
                  }
                  
                  let xOffset = CGFloat(x) * tileSize.width
                  let yOffset = CGFloat(y) * tileSize.height
                  let point = CGPoint(x: xOffset, y: yOffset)
                  
                  if let tileImageRef = imageRef?.cropping(to: CGRect(origin: point, size: tileSize)), let imageData = UIImagePNGRepresentation(UIImage(cgImage: tileImageRef)) {
                    let path = "\(cachesPath)/\(name)_\(x)_\(y).png"
                    try? imageData.write(to: URL(fileURLWithPath: path), options: [])
                  }
                }
              }
            }
          }
        }
      }
      
    }
    

  * 异步绘制小图

    
    
    override func draw(_ rect: CGRect) {
        let firstColumn = Int(rect.minX / sideLength)
        let lastColumn = Int(rect.maxX / sideLength)
        let firstRow = Int(rect.minY / sideLength)
        let lastRow = Int(rect.maxY / sideLength)
        
        for row in firstRow...lastRow {
            for column in firstColumn...lastColumn{
                guard let image = imageForTile(atColumn: column, row: row) else { continue }
                let x = sideLength * CGFloat(column)
                let y = sideLength * CGFloat(row)
                let tileRect = CGRect.init(x: x, y: y, width: sideLength, height: sideLength)
                image.draw(in: tileRect)
            }
        }
    }
    
    func imageForTile(atColumn column: Int, row: Int) -> UIImage? {
        let filePath = "\(cachesPath)/\(fileName)_\(column)_\(row).png"
        return UIImage(contentsOfFile: filePath)
    }
    

异步绘制分块图像

### 8\. CAShapeLayer

  * 这个图形类相信大家都比较熟悉了，基于QuartzCore图形绘制库；
  * 使用方法也比较简单，建议使用[PaintCode](https://link.jianshu.com?t=https://www.paintcodeapp.com)这个软件测试和学习；

### 9\. CATransformLayer

  * 这是一个可以transform子层的抽象layer类，对它设置backgroundColor等都不会起作用，得addSublayer才能达到想要的效果；
  * 主要通过`sublayerTransform`属性来重新绘制subLayers，已达到3D变换的效果；
  * 它也没法接受events，只能通过检测对sublayer的event来处理touch等事件；

CATransformLayer

`创建六面体`

    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 前
        var layer = sideLayer(color: .red)
        transformLayer.addSublayer(layer)
        layer.transform = CATransform3DMakeTranslation(0.0, 0.0, sideLength / 2)
        
        // 后
        layer = sideLayer(color: .green)
        transformLayer.addSublayer(layer)
        layer.transform = CATransform3DMakeTranslation(0.0, 0.0, -sideLength / 2)
        
        // 上
        layer = sideLayer(color: .orange)
        transformLayer.addSublayer(layer)
        var transform = CATransform3DMakeTranslation(0.0, sideLength / 2, 0.0)
        transform = CATransform3DRotate(transform, degreesToRadians(90.0), 1.0, 0.0, 0.0)
        layer.transform = transform
        
        // 下
        layer = sideLayer(color: .blue)
        transformLayer.addSublayer(layer)
        transform = CATransform3DMakeTranslation(0.0, -sideLength / 2, 0.0)
        transform = CATransform3DRotate(transform, degreesToRadians(90.0), 1.0, 0.0, 0.0)
        layer.transform = transform
        
        // 左
        layer = sideLayer(color: .cyan)
        transformLayer.addSublayer(layer)
        transform = CATransform3DMakeTranslation(-sideLength / 2, 0.0, 0.0)
        transform = CATransform3DRotate(transform, degreesToRadians(90.0), 0.0, 1.0, 0.0)
        layer.transform = transform
        
        // 右
        layer = sideLayer(color: .purple)
        transformLayer.addSublayer(layer)
        transform = CATransform3DMakeTranslation(sideLength / 2, 0.0, 0.0)
        transform = CATransform3DRotate(transform, degreesToRadians(90.0), 0.0, 1.0, 0.0)
        layer.transform = transform
        
        rotate(xOffset: 200, yOffset: 200)
    }
    
    func sideLayer(color: UIColor) -> CALayer {
        let layer = CALayer()
        layer.backgroundColor =
            color.withAlphaComponent(0.6).cgColor
        layer.frame = CGRect(origin: .zero, size: CGSize(width: sideLength, height: sideLength))
        layer.position = CGPoint(x: transformLayerView.bounds.midX, y: transformLayerView.bounds.midY)
        return layer
    }
    
    func degreesToRadians(_ degrees: Double) -> CGFloat {
        return CGFloat(degrees * .pi / 180.0)
    }
    

`旋转变换`

    
    
    func rotate(xOffset: Double, yOffset: Double) {
        let totalOffset = sqrt(xOffset * xOffset + yOffset * yOffset)
        let totalRotation = CGFloat(totalOffset * .pi / 180.0)
        let xRotationalFactor = CGFloat(totalOffset) / totalRotation
        let yRotationalFactor = CGFloat(totalOffset) / totalRotation
        let currentTransform = CATransform3DTranslate(transformLayer.sublayerTransform, 0.0, 0.0, 0.0)
        let x = xRotationalFactor * currentTransform.m12 - yRotationalFactor * currentTransform.m11
        let y = xRotationalFactor * currentTransform.m22 - yRotationalFactor * currentTransform.m21
        let z = xRotationalFactor * currentTransform.m32 - yRotationalFactor * currentTransform.m31
        let rotation = CATransform3DRotate(transformLayer.sublayerTransform, totalRotation, x, y, z)
        transformLayer.sublayerTransform = rotation
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let location = touches.first?.location(in: transformLayerView) else {
            return
        }
        rotate(xOffset: Double(location.x / 50), yOffset: Double(location.y / 50))
    }
    

`hitTest`

    
    
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let location = touches.first?.location(in: transformLayerView) else {
            return
        }
        for layer in transformLayer.sublayers! where layer.hitTest(location) != nil {
            print("Touched Sublayer")
        }
    }
    

### 10\. CAEmitterLayer

  * 顾名思义，CAEmitterLayer主要配合CAEmitterCell来发射粒子，比较高效；
  * 设置`emitterCells`属性可以在一个layer上添加多个cell发射器；
  * 可以设置`emitterPosition`设置发射器的位置；

`setupEmitterLayer`

    
    
    func setupEmitterLayer() {
        emitterLayer.emitterCells = [emitterCell]
        emitterLayer.seed = UInt32(Date().timeIntervalSince1970)
        emitterLayer.renderMode = kCAEmitterLayerAdditive
        emitterLayer.drawsAsynchronously = true
        setEmitterPosition(CGPoint(x: view.bounds.midX, y: view.bounds.midY))
    }
    

`setupEmitterCell`

    
    
    func setupEmitterCell(){
        emitterCell.contents = UIImage.init(named: "smallStar")?.cgImage
        
        emitterCell.velocity = 50.0
        emitterCell.velocityRange = 500.0
        
        emitterCell.color = UIColor.black.cgColor
        emitterCell.redRange = 1.0
        emitterCell.greenRange = 1.0
        emitterCell.blueRange = 1.0
        emitterCell.alphaRange = 0.0
        emitterCell.redSpeed = 0.0
        emitterCell.greenSpeed = 0.0
        emitterCell.blueSpeed = 0.0
        emitterCell.alphaSpeed = -0.5
        
        let zeroDegreesInRadians = degreesToRadians(0.0)
        emitterCell.spin = degreesToRadians(130.0)
        emitterCell.spinRange = zeroDegreesInRadians
        emitterCell.emissionRange = degreesToRadians(360.0)
        
        emitterCell.lifetime = 1.0
        emitterCell.birthRate = 250.0
        emitterCell.xAcceleration = -800.0
        emitterCell.yAcceleration = 1000.0
    }
    

`其他设置`

    
    
    func setEmitterPosition(_ position: CGPoint) {
        emitterLayer.emitterPosition = position
    }
    
    func degreesToRadians(_ degrees: Double) -> CGFloat {
        return CGFloat(degrees * .pi / 180.0)
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        guard let location = touches.first?.location(in: view) else {
            return
        }
        setEmitterPosition(location)
    }
    

CAEmitterLayer

>
> 以上就是全部的CALayer相关的知识了，工程文件见[https://github.com/BackWorld/LayerPlayer](https://link.jianshu.com?t=https://github.com/BackWorld/LayerPlayer)

如果对你有帮助，别忘了点个👍或关注下哦~

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [ios-layer](https://www.jianshu.com/p/1d6db37577dd)

转载：http://www.jianshu.com/p/32fcadd12108 每个UIView有一个伙伴称为l...

[F麦子](https://www.jianshu.com/u/c71ea24e5e2d)阅读 5,319评论 0赞 13

  * [iOS-Core-Animation之六----专用图层](https://www.jianshu.com/p/fe1eeb12bbf3)

>复杂的组织都是专门化的 >Catharine R. Stimpson 到目前为止，我们已经探讨过`CALayer...

[夜空下最亮的亮点](https://www.jianshu.com/u/1c148336322c)阅读 814评论 0赞 2

  * [programming iOS - layer](https://www.jianshu.com/p/32fcadd12108)

每个UIView有一个伙伴称为layer，一个CALayer。UIView实际上并没有把自己画到屏幕上;它绘制本身...

[shenzhenboy](https://www.jianshu.com/u/7b50760a56ac)阅读 2,839评论 0赞 17

  * [iOS-CoreAnimation提供的不同功能的CAlayer](https://www.jianshu.com/p/95957d931d94)

一、CAShapelayer 我们知道可以不使用图片情况下利用CGpath去构建任意形状的阴影。其实我们也可...

[小猫仔](https://www.jianshu.com/u/56ada7bab1bc)阅读 1,202评论 0赞 4

  * [ IOS中CALayer的使用 ](https://www.jianshu.com/p/55e0fa27f817)

在iOS中随处都可以看到绚丽的动画效果，实现这些动画的过程并不复杂，今天将带大家一窥ios动画全貌。在这里你可以看...

[每天刷两次牙](https://www.jianshu.com/u/b38cb01817ff)阅读 7,983评论 6赞 28

 