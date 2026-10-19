**作者：京东零售 郭旭锋**

# 1 为什么需要事件分发

和其他平台类似，Android 中 View 的布局是一个树形结构，各个 ViewGroup 和 View
是按树形结构嵌套布局的，从而会出现用户触摸的位置坐标可能会落在多个 View 的范围内，这样就不知道哪个 View
来响应这个事件，为了解决这一问题，就出现了事件分发机制。

# 2 事件分发的关键方法

Android 中事件分发是从 Activity 开始的，可以看看各组件中事件分发的关键方法

组件| dispatchTouchEvent| onInterceptTouchEvent| onTouchEvent  
---|---|---|---  
Activity| √| ×| √  
ViewGroup| √| √| √  
View| √| ×| √  
  
 **Activity** ：没有 onInterceptTouchEvent 方法，因为如果 Activity 拦截事件，将导致整个页面都没有响应，而
Activity 是系统应用和用户交互的媒介，不能响应事件显然不是系统想要的结果。所以 Activity 不需要拦截事件。

 **ViewGroup** ：三个方法都有，Android 中 ViewGroup 是一个布局容器，可以嵌套多个 ViewGroup 和
View，事件传递和拦截都由 ViewGroup 完成。

 **View** ：事件传递的最末端，要么消费事件，要么不消费把事件传递给父容器，所以也不需要拦截事件。

# 3 事件分发流程分析

### 3.1 事件分发流程概览

Activity 并不是一个 View，那么 Activity 是如何将事件分发到页面的 ViewGroup 和 View 的呢。我们先看看源码

    
    
    # Activity
    public boolean dispatchTouchEvent(MotionEvent ev) {
        if (ev.getAction() == MotionEvent.ACTION_DOWN) {
            onUserInteraction();
        }
        // 调用 Window 对象的方法，开始事件分发
        if (getWindow().superDispatchTouchEvent(ev)) {
            return true;
        }
        // 如果事件分发返回 false，也即事件没被消费，则调用自己的 onTouchEvent 方法
        return onTouchEvent(ev);
    }
    
    public boolean onTouchEvent(MotionEvent event) {
        if (mWindow.shouldCloseOnTouch(this, event)) {
            finish();
            return true;
        }
        return false;
    }

可以看到，Activity 中的事件分发方法 dispatchTouchEvent 调用了 getWindow
().superDispatchTouchEvent (ev) 方法，而这里的 WIndow 实际上是 PhoneWindow。

简单来说，Window 是一个抽象类，是所有视图的最顶层容器，视图的外观和行为都归他管，无论是背景显示、标题栏还是事件处理都是他管理的范畴，而
PhoneWindow 作为 Window 的唯一亲儿子（唯一实现类），自然就是 View 界的皇帝了。

下来看看 PhoneWindow 的代码

    
    
    # PhoneWindow
    @Override
    public boolean superDispatchTouchEvent(MotionEvent event) {
        return mDecor.superDispatchTouchEvent(event);
    }

PhoneWindow 中又调用了 mDecor.superDispatchTouchEvent (event) 方法。mDecor 是 DecorView
对象，再看看 DecorView 的代码

    
    
    # DecorView
    public class DecorView extends FrameLayout implements RootViewSurfaceTaker, WindowCallbacks {
        public boolean superDispatchTouchEvent(MotionEvent event) {
            return super.dispatchTouchEvent(event);
        }
    }
    
    # FrameLayout
    public class FrameLayout extends ViewGroup {
    }
    
    # ViewGroup
    public abstract class ViewGroup extends View implements ViewParent, ViewManager {
        public boolean dispatchTouchEvent(MotionEvent ev) {
            ......
        }
    }
    
    # View
    public class View implements Drawable.Callback, KeyEvent.Callback, AccessibilityEventSource {
        public boolean dispatchTouchEvent(MotionEvent ev) {
            ......
        }
    }

可以看到，DecorView 实际上就是 ViewGroup，事件分发方法最终调用到了 ViewGroup 的 dispatchTouchEvent
(MotionEvent ev) 方法。

DecorView 是 PhoneWindow 的一个对象，其职位就是跟在 PhoneWindow 身边专业为 PhoneWindow
服务的，除了自己要干活之外，也负责消息的传递，PhoneWindow 的指示通过 DecorView 传递给下面的 View，而下面 View 的信息也通过
DecorView 回传给 PhoneWindow。

Android
中的事件分发是责任链模式的一种变形。事件由上往下传递，如果事件没有被消费则继续传递到下一层，如果事件被消费则停止传递，如果到最下层事件则没有被消费，则事件会层层传递给上一层处理。我们都知道事件分发的源头在
Activity 中的 dispatchTouchEvent 方法中，事件从这里开始，分发到布局中的各个 View 中，不断递归调用
ViewGroup/View 的 dispatchTouchEvent 方法。通过上面分析可以看到，Activity
在接受到上层派发来的事件后，会把事件传递到自己的 dispatchTouchEvent 方法中，然后 Activity 会把触摸、点击事件传递给自己的
mWindow 对象，最终传递给 DecorView 的 dispatchTouchEvent 方法，实际调用的是 ViewGroup 的
dispatchTouchEvent 方法。

## 3.2 事件分发源码分析

经过分析，可以知道 Android 中事件分发的关键方法就是 ViewGroup 和 View 中的相关方法，如下

    
    
    # View
    public class View implements Drawable.Callback, KeyEvent.Callback, AccessibilityEventSource {
    
        public boolean dispatchTouchEvent(MotionEvent event) {
            // ... 省略部分代码
            boolean result = false;
            // ... 省略部分代码
            if (onFilterTouchEventForSecurity(event)) {
                // ... 省略部分代码
                // 1. 主要调用 onTouchEvent 方法，返回 true 说明事件被消费，否则没被消费
                if (!result && onTouchEvent(event)) {
                    result = true;
                }
            }
            // ... 省略部分代码
            return result;
        }
        
        public boolean onTouchEvent(MotionEvent event) {
            // ... 省略部分代码
            // 2. 默认可点击则返回 true，也就是消费事件。Button 或设置过 OnClickListener，则 View 可点击
            if (clickable || (viewFlags & TOOLTIP) == TOOLTIP) {
                switch (action) {
                    case MotionEvent.ACTION_UP:
                        // ... 省略部分代码
                        break;
                    case MotionEvent.ACTION_DOWN:
                        // ... 省略部分代码
                        break;
                    case MotionEvent.ACTION_CANCEL:
                        // ... 省略部分代码
                        break;
                    case MotionEvent.ACTION_MOVE:
                        // ... 省略部分代码
                        break;
                }
                return true;
            }
    
            return false;
        }
    }

View 中的方法逻辑比较简单，如备注 1 所示，dispatchTouchEvent 主要就是做一些安全检查，检查通过后会调用 onTouchEvent
方法。而 onTouchEvent 方法中逻辑如备注 2 所示，如果 View 是可点击的，则默认会认为消费事件，否则不消费，一般 Button
控件，或设置过 OnClickListener 的控件，View 会被默认设置为可点击。

下面看看 ViewGroup 代码

    
    
    # ViewGroup
    public abstract class ViewGroup extends View implements ViewParent, ViewManager {
    
        public boolean dispatchTouchEvent(MotionEvent ev) {
            // ... 省略部分代码
            boolean handled = false;
            if (onFilterTouchEventForSecurity(ev)) {
                final int action = ev.getAction();
                final int actionMasked = action & MotionEvent.ACTION_MASK;
    
                // 1. 如果是 DOWN 事件，则重置事件状态
                if (actionMasked == MotionEvent.ACTION_DOWN) {
                    // Throw away all previous state when starting a new touch gesture.
                    // The framework may have dropped the up or cancel event for the previous gesture
                    // due to an app switch, ANR, or some other state change.
                    cancelAndClearTouchTargets(ev);
                    resetTouchState();
                }
    
                final boolean intercepted;
                // 2. 如果是 DOWN 事件，会判断当前 ViewGroup 是否要拦截事件。这里受两个因素影响:
                //    一是 FLAG_DISALLOW_INTERCEPT，如果设置不拦截，则不会调用 onInterceptTouchEvent，直接设置为不拦截
                //    二是没设置 FLAG_DISALLOW_INTERCEPT 标志，默认允许拦截，会调用 onInterceptTouchEvent 方法
                // 3. 如果不是 DOWN 事件，可能是 MOVE 或 UP 事件，mFirstTouchTarget 是记录需要继续进行事件分发的下一级子 View，包括ViewGroup 或 View，这里也分为两种情况
                //    如果 mFirstTouchTarget 不为空，说明需要继续向下一级子 View/ViewGroup 分发事件，这时说明上次 DOWN 事件找到了下级有消费事件的子 View，且无拦截事件
                //    如果 mFirstTouchTarget 为空，说明没找到要消费事件的子 View，或事件被拦截了
                if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget != null) {
                    final boolean disallowIntercept = (mGroupFlags & FLAG_DISALLOW_INTERCEPT) != 0;
                    if (!disallowIntercept) {
                        intercepted = onInterceptTouchEvent(ev);
                        ev.setAction(action); // restore action in case it was changed
                    } else {
                        intercepted = false;
                    }
                } else {
                    // There are no touch targets and this action is not an initial down
                    // so this view group continues to intercept touches.
                    intercepted = true;
                }
                // ... 省略部分代码
                TouchTarget newTouchTarget = null;
                boolean alreadyDispatchedToNewTouchTarget = false;
                // 4. 下面逻辑主要就是遍历寻找能消费事件的 View,如果事件被拦截，则不需要再寻找
                if (!canceled && !intercepted) {
                    // ... 省略部分代码
                    // 5. 只有 DOWN 事件才需要寻找，其他事件时已经确定是否找到，都不需要再找消费事件的 View 了
                    if (actionMasked == MotionEvent.ACTION_DOWN
                            || (split && actionMasked == MotionEvent.ACTION_POINTER_DOWN)
                            || actionMasked == MotionEvent.ACTION_HOVER_MOVE) {
                        // ... 省略部分代码
                        final int childrenCount = mChildrenCount;
                        if (newTouchTarget == null && childrenCount != 0) {
                            // ... 省略部分代码
                            final View[] children = mChildren;
                            for (int i = childrenCount - 1; i >= 0; i--) {
                                // ... 省略部分代码
                                final int childIndex = getAndVerifyPreorderedIndex(childrenCount, i, customOrder);
                                final View child = getAndVerifyPreorderedView(preorderedList, children, childIndex);
                                // 6. 这个方法是关键
                                //    如果 child 不为空，则会再调用 child.dispatchTouchEvent 方法，达到层层递归的效果
                                //    如果 child 为空，则会调用 super.dispatchTouchEvent 方法，super 是 View，实际上调用了 onTouchEvent 方法，自己判断是否消费事件
                                if (dispatchTransformedTouchEvent(ev, false, child, idBitsToAssign)) {
                                    // ... 省略部分代码
                                    // 7. 返回 true，说明找到了消费事件的 View，下面方法会给 mFirstTouchTarget 赋值，下面 mFirstTouchTarget 将不为空
                                    //    注：mFirstTouchTarget 并不是最终消费事件的 View，而是下一级包含消费事件 View 的链表对象，或是直接消费事件的 View 的链表对象
                                    //    每一个 ViewGourp 都会记录一个 mFirstTouchTarget，mFirstTouchTarget.child 记录了下一层消费事件的 ViewGroup 或 View
                                    //    同时，alreadyDispatchedToNewTouchTarget 变量会设置为 true
                                    newTouchTarget = addTouchTarget(child, idBitsToAssign);
                                    alreadyDispatchedToNewTouchTarget = true;
                                    break;
                                }
                                // ... 省略部分代码
                            }
                            // ... 省略部分代码
                        }
                        // ... 省略部分代码
                    }
                }
    
                // Dispatch to touch targets.
                if (mFirstTouchTarget == null) {
                    // 8. 当没有找到消费事件的 View，或事件被拦截，mFirstTouchTarget 都不会被赋值，这里 child 为空，会调用自己的 onTouchEvent 方法
                    handled = dispatchTransformedTouchEvent(ev, canceled, null, TouchTarget.ALL_POINTER_IDS);
                } else {
                    // Dispatch to touch targets, excluding the new touch target if we already
                    // dispatched to it.  Cancel touch targets if necessary.
                    TouchTarget predecessor = null;
                    TouchTarget target = mFirstTouchTarget;
                    while (target != null) {
                        final TouchTarget next = target.next;
                        // 9. 说明找到了消费事件的 View，并且已经分发，直接设置为已处理
                        if (alreadyDispatchedToNewTouchTarget && target == newTouchTarget) {
                            handled = true;
                        } else {
                            final boolean cancelChild = resetCancelNextUpFlag(target.child) || intercepted;
                            // 10. 此方法和备注 6 和 8 都一样，这里多了 cancel 的处理逻辑。如果事件被拦截，需要给原来消费事件的 View 发一个 CANCEL 事件
                            if (dispatchTransformedTouchEvent(ev, cancelChild, target.child, target.pointerIdBits)) {
                                handled = true;
                            }
                            if (cancelChild) {
                                if (predecessor == null) {
                                    mFirstTouchTarget = next;
                                } else {
                                    predecessor.next = next;
                                }
                                target.recycle();
                                target = next;
                                continue;
                            }
                        }
                        predecessor = target;
                        target = next;
                    }
                }
                // ... 省略部分代码
            }
            // ... 省略部分代码
            return handled;
        }
        
        public boolean onInterceptTouchEvent(MotionEvent ev) {
            if (ev.isFromSource(InputDevice.SOURCE_MOUSE)
                    && ev.getAction() == MotionEvent.ACTION_DOWN
                    && ev.isButtonPressed(MotionEvent.BUTTON_PRIMARY)
                    && isOnScrollbarThumb(ev.getX(), ev.getY())) {
                return true;
            }
            // 默认不拦截
            return false;
        }
        
        // 没有覆写这个方法，实际调用的是 View 的 onTouchEvent 方法
        public boolean onTouchEvent(MotionEvent event) {
        }
            
    }

可以看到，ViewGroup 中的事件分发逻辑还是比较复杂，但抓住关键点后则很容易能看清它的本来面貌

（1）分发的事件包括 DOWN、MOVE、UP、CANCEL 几种，用户一个完整的动作就是由这几个事件组合而成的

（2）只有 DOWN 事件中会寻找消费事件的目标 View，其他事件不会再寻找

（3）DOWN 事件寻找到目标 View 后，后续其他事件都会直接分发至目标 View

（4）事件可以被拦截，拦截后原目标 View 会收到 CANCEL 事件，后续将不会再收到任何事件（这也是这套机制不支持丰富的嵌套滑动的原因）

### 3.3 事件分发情景分析

 **3.3.1 分发过程没有任何 View 拦截和消费**

![](https://image.3001.net/images/20230421/1682045765_6441fb4595e8c408a1631.png!small)

（1）事件返回时，为了简化理解，dispatchTouchEvent 直接指向了父 View 的 onTouchEvent ，实际上它仅仅是返回给父
View 的 dispatchTouchEvent 一个 false 值（影响了 mFirstTouchTarget 的值），父 View
根据返回值来调用自身的 onTouchEvent 方法

（2）ViewGroup 是根据 onInterceptTouchEvent 的返回值（影响了 mFirstTouchTarget 的值）确定是调用子
View 的 dispatchTouchEvent 还是自身的 onTouchEvent 方法

（3）如果所有 View 都没有消费 DOWN 事件，后续 MOVE 和 UP 不会再往下传递，会直接传递给 Activity 的 onTouchEvent
方法

 **3.3.2 最底层 View 消费事件，且上层 View 没有拦截事件**

![](https://image.3001.net/images/20230421/1682045766_6441fb46746049fcd2600.png!small)

（1）若没有 ViewGroup 对事件进行拦截，而最底层 View 消费了此事件，也就是接收到 DOWN 事件时 View 的 onTouchEvent
返回 true，事件将不会再向上传递给各个 ViewGroup 的 onTouchEvent 方法，而是直接返回，后续的 MOVE 和 UP
事件也将会直接交给 View 进行处理

 **3.3.3 最底层 View 没有消费事件，ViewGroup2 消费了事件，且上层 View 没有拦截事件**

![](https://image.3001.net/images/20230421/1682045767_6441fb4706501f3d4d36d.png!small)

（1）如果 View 没有消费事件，在层层调用父布局的 onTouchEvent 方法时，有 View 消费此事件，如 ViewGroup2
消费此事件，后续 MOVE 和 UP 事件将会传递给 ViewGroup2 的 onTouchEvent 方法，而且不会再调用 ViewGroup2 的
onInterceptTouchEvent 方法

（2）源码 `if (actionMasked == MotionEvent.ACTION_DOWN || mFirstTouchTarget !=
null) {}`这个代码中主要调用 onInterceptTouchEvent () 方法和处理是否拦截

第一次是 DOWN 事件会进行判断，所以会调用 onInterceptTouchEvent 拦截方法

第二次非 DOWN 事件，不会再调用 onInterceptTouchEvent 方法。原因如下：

◦ 如果 DOWN 事件的时候进行过拦截，也就是 onInterceptTouchEvent () 方法返回 true，则
mFirstTouchTarget 必定为 null，不会调用 onInterceptTouchEvent
方法。因为后面不会对这个值赋值，会往下走逻辑，直接调用到此 View 或 ViewGroup 的 onTouchEvent () 方法

◦ 如果 DOWN 事件没有拦截，但子 View 的 onTouchEvent 都返回 false，只有当前 ViewGroup 的
onTouchEvent 返回 true，mFirstTouchTarget 也同样为 null，也不会调用 onInterceptTouchEvent
方法。因为 mFirstTouchTarget 本质是找能接收事件的子 View，所有子 View 都不接收事件，mFirstTouchTarget
就必然为 null

 **3.3.4 ViewGroup2 拦截了并消费了 DOWN 事件，其他 View
没有拦截事件**![](https://image.3001.net/images/20230421/1682045768_6441fb480203b1f87c1df.png!small)

（1）ViewGroup2 拦截 DOWN 事件后，View 不会接收到任何事件。ViewGroup2 消费事件后，后续 MOVE 和 UP 事件会交给
ViewGroup2 的 onTouchEvent 方法进行处理，且不会再调用 ViewGroup2 的 onInterceptTouchEvent 方法

 **3.3.5 View 消费了 DOWN 事件，ViewGroup2 拦截且消费了 MOVE 事件，其他 View 没有拦截事件**

![](https://image.3001.net/images/20230421/1682045768_6441fb4893bc34376d50d.png!small)

（1）View 中 DOWN 事件正常传递

（2）当 ViewGroup2 拦截 MOVE 事件后，当前 mFirstTouchTarget 不为空，首先 View 会收到转换后的 CANCEL
事件，mFirstTouchTarget 会置为空，下次 MOVE 事件由于 mFirstTouchTarget 为空，会调用到自己的
onTouchEvent 方法

 **3.3.6 View 消费 DOWN 事件，ViewGroup2 拦截且消费了 MOVE 事件，一定条件后，ViewGroup1 再次拦截和消费
MOVE 事件，其他 View 没有拦截事件**

![](https://image.3001.net/images/20230421/1682045769_6441fb498757051e778e5.png!small)

### 3.4 事件分发总结

（1）整个分发过程中没有任何拦截和消费，DOWN 事件会层层往下分发，并层层往上返回 false，MOVE 和 UP 事件则会交给 Activity 的
onTouchEvent 方法进行处理，不再往下分发

（2）分发过程中没有任何拦截但有消费，DOWN 事件会层层往下分发，并层层往上返回 false，直到有消费返回 true，MOVE 和 UP
事件则会层层往下分发，最后直接交给消费事件的 View 进行处理，然后层层返回 true

（3）分发过程中有拦截且拦截后消费，DOWN 事件会层层往下分发，直到有拦截后直接交给消费的 View 进行处理，MOVE 和 UP
事件则会层层往下分发，最后直接交给消费事件的 View 进行处理，然后层层返回 true

（4）分发过程中不拦截 DOWN 事件，但拦截 MOVE 事件且拦截后消费，第一次拦截，之前收到 DOWN 事件的子 View 会收到 CANCEL
事件，并层层返回；后续 MOVE 和 UP 会层层往下分发，最后直接交给消费事件的 View 进行处理

（5）分发过程中不拦截 DOWN 事件，但拦截 MOVE 事件且拦截后不消费，第一次拦截，之前收到 DOWN 事件的子 View 会收到 CANCEL
事件，并层层返回；后续 MOVE 和 UP 会层层往下分发，最后交给拦截的 View 进行处理，此时由于拦截的 View 没有消费，会层层往上返回
false，最后会交给 Activity 的 onTouchEvent 方法进行处理

以上，是个人的一些分析和经验，欢迎有兴趣的小伙伴一起学习和探讨！

