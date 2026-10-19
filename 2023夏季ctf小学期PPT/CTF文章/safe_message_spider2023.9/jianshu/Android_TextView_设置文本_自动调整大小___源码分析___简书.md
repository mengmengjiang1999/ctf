Android TextView 设置文本 自动调整大小 - 源码分析

[ 行走中的3卡](https://www.jianshu.com/u/78fd7b6b7c1d)关注赞赏支持

# Android TextView 设置文本 自动调整大小 - 源码分析

TextView 的文本内容,可以提供多种语言翻译。  
例如中文 和 英文, 设置同个字体大小, 可能在中文下 **显示不全** 等.

TextView 提供 API：setAutoSizeTextTypeUniformWithConfiguration  
可以做到根据文本 **内容** 去 动态 **自动调整大小** 。

## 1\. 简单使用

样例：

    
    
    textView1.setAutoSizeTextTypeUniformWithConfiguration(1, 300, 1, TypedValue.COMPLEX_UNIT_PX);
    

第一个参数是最小值,第二个参数是最大值, 知道这两个即可.

## 2\. 源码分析

### 2.1 setAutoSizeTextTypeUniformWithConfiguration

    
    
    package android.widget;
    
    @RemoteView
    public class TextView extends View implements ViewTreeObserver.OnPreDrawListener {
    
        public void setAutoSizeTextTypeUniformWithConfiguration(int autoSizeMinTextSize,
                int autoSizeMaxTextSize, int autoSizeStepGranularity, int unit) {
            if (supportsAutoSizeText()) {
                ...
    
                if (setupAutoSizeText()) {
                    autoSizeText();
                    invalidate();
                }
            }
    

分析：  
(1) 第一个参数是最小值, 第二个参数是最大值  
(2) supportsAutoSizeText() 在TextView 里返回值是true  
(3) 重点是 autoSizeText() , 它会设置一个合适的值

### 2.2 autoSizeText 源码

    
    
        private void autoSizeText() {
                    ...
                    final float optimalTextSize = findLargestTextSizeWhichFits(TEMP_RECTF);
    
                    if (optimalTextSize != getTextSize()) {
                        setTextSizeInternal(TypedValue.COMPLEX_UNIT_PX, optimalTextSize,
                                false /* shouldRequestLayout */);         
                    ...
    

可以看出,  
(1)调用findLargestTextSizeWhichFits 找到一个新的大小值 optimalTextSize  
(2) optimalTextSize 与现在的字体大小比较, 不同则重新设置

### 2.3 findLargestTextSizeWhichFits 源码

核心代码

    
    
        /**
         * Performs a binary search to find the largest text size that will still fit within the size
         * available to this view.
         */
        private int findLargestTextSizeWhichFits(RectF availableSpace) {
            final int sizesCount = mAutoSizeTextSizesInPx.length;
            if (sizesCount == 0) {
                throw new IllegalStateException("No available text sizes to choose from.");
            }
    
            int bestSizeIndex = 0;
            int lowIndex = bestSizeIndex + 1;
            int highIndex = sizesCount - 1;
            int sizeToTryIndex;
            while (lowIndex <= highIndex) {
                sizeToTryIndex = (lowIndex + highIndex) / 2;
                if (suggestedSizeFitsInSpace(mAutoSizeTextSizesInPx[sizeToTryIndex], availableSpace)) {
                    bestSizeIndex = lowIndex;
                    lowIndex = sizeToTryIndex + 1;
                } else {
                    highIndex = sizeToTryIndex - 1;
                    bestSizeIndex = highIndex;
                }
            }
    
            return mAutoSizeTextSizesInPx[bestSizeIndex];
        }
    

可以看出,它是在一个数组里, 通过二分查找, 找到最合适的大小值并返回(在TextView 大小范围内).

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Android 设置TextView自动调整字体大小](https://www.jianshu.com/p/5c29f891e23c)

Android 设置TextView自动调整字体大小 意为：TextView字体大小随着控件的大小变化而变化，An...

[张荣旗](https://www.jianshu.com/u/94f444f1682b)阅读 26,962评论 5赞 27

  * [Android官方的TextView字体大小自适应](https://www.jianshu.com/p/cbae4658d05d)

遇见问题：当一个控件显示的文字有点长的时候，可能在屏幕小的设备上就会变得显示不完整，特别是那种不允许文字省略的按钮...

[我说的这句话是谎话](https://www.jianshu.com/u/0ea144bfc1ef)阅读 19,914评论 0赞 13

  * [Android | 自动调整文本大小的 TextViews](https://www.jianshu.com/p/d6be9cccc50c)

简评：Auto-Sizing TextViews —— 当 TextView 的布局边界尺寸发生变化时，文本大小可...

[极小光](https://www.jianshu.com/u/644fb0e0b9e1)阅读 5,357评论 0赞 4

  * [TextView自动调整字体大小](https://www.jianshu.com/p/2bd2a48c3893)

系统SDK版本大于等于26，直接使用TextView就可以。 系统SDK版本小于26，需要使用support包，s...

[leilifengxingmw](https://www.jianshu.com/u/3c9c20cce3d0)阅读 1,612评论 0赞 5

  * [Android 巧用二分法自动调整字体大小](https://www.jianshu.com/p/ec3cf23044b6)

开篇 不BB， 直奔主题。 场景 固定宽度的TextView，在不同尺寸的手机上显示效果不一样：小屏上会显...

[SwitchLife](https://www.jianshu.com/u/b5b414cbad2f)阅读 598评论 0赞 3

 