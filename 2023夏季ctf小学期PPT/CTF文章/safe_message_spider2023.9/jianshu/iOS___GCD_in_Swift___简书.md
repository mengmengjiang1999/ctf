iOS | GCD in Swift

[ 清無](https://www.jianshu.com/u/484e1c9f1ae9)关注赞赏支持

# iOS | GCD in Swift

In this Grand Central Dispatch tutorial, you’ll delve into basic GCD concepts,
including:

  * Multithreading
  * Dispatch queues
  * Concurrency

Multi-core devices, on the other hand, execute multiple threads at the same
time via parallelism.

GCD is built on top of threads. Under the hood, it manages a shared thread
pool. With GCD, you add blocks of code or work items to dispatch queues and
GCD decides which thread to execute them on.

You submit units of work to this queue, and GCD executes them in a FIFO order
(first in, first out), guaranteeing that the first task submitted is the first
one started.

Dispatch queues are thread-safe, meaning you can simultaneously access them
from multiple threads.

Concurrent queues allow multiple tasks to run at the same time. The queue
guarantees tasks start in the order you add them. Tasks can finish in any
order, and you have no knowledge of the time it will take for the next task to
start, nor the number of tasks running at any given time.

# Queue Types

GCD provides three main types of queues:

  * **Main queue** : Runs on the main thread and is a serial queue.
  * **Global queues** : Concurrent queues shared by the whole system. Four such queues exist, each with different priorities: high, default, low and background. The background priority queue has the lowest priority and is throttled in any I/O activity to minimize negative system impact.
  * **Custom queues** : Queues you create that can be serial or concurrent. Requests in these queues end up in one of the global queues.

# QoS

When sending tasks to the global concurrent queues, you don’t specify the
priority directly. Instead, you specify a quality of service (QoS) class
property. This indicates the task’s importance and guides GCD in determining
the priority to give to the task.

The QoS classes are:

  * **User-interactive** : This represents tasks that must complete immediately to provide a nice user experience. Use it for UI updates, event handling and small workloads that require low latency. The total amount of work done in this class during the execution of your app should be small. This should run on the main thread.
  * **User-initiated** : The user initiates these asynchronous tasks from the UI. Use them when the user is waiting for immediate results and for tasks required to continue user interaction. They execute in the high-priority global queue.
  * **Utility** : This represents long-running tasks, typically with a user-visible progress indicator. Use it for computations, I/O, networking, continuous data feeds and similar tasks. This class is designed to be energy efficient. This gets mapped into the low-priority global queue.
  * **Background** : This represents tasks the user isn’t directly aware of. Use it for prefetching, maintenance and other tasks that don’t require user interaction and aren’t time-sensitive. This gets mapped into the background priority global queue.

> In general, you want to use async when you need to perform a network-based
> or CPU-intensive task in the background without blocking the current thread.

# Delaying Tasks Execution

Why not use Timer? You could consider using it if you have repeated tasks that
are easier to schedule with Timer. Here are two reasons to stick with dispatch
queue’s `asyncAfter()`:

    
    
    // 1
    let delayInSeconds = 2.0
    
    // 2
    DispatchQueue.main.asyncAfter(deadline: .now() + delayInSeconds) { [weak self] in
      guard let self = self else {
        return
      }
    
      if !PhotoManager.shared.photos.isEmpty {
        self.navigationItem.prompt = nil
      } else {
        self.navigationItem.prompt = "Add photos with faces to Googlyify them!"
      }
    
      // 3
      self.navigationController?.viewIfLoaded?.setNeedsLayout()
    }
    
    

  * One is readability. To use Timer, you have to define a method, then create the timer with a selector or invocation to the defined method. With `DispatchQueue.main.asyncAfter()`, you simply add a closure.
  * Timer is scheduled on run loops, so you’d also have to make sure you scheduled it on the correct run loop — and in some cases for the correct run loop modes. In this regard, working with dispatch queues is easier.

# Readers-Writers Problem

The Swift collection types like Array and Dictionary aren’t thread-safe when
declared mutable.

    
    
    private var unsafePhotos: [Photo] = []
      
    var photos: [Photo] {
      return unsafePhotos
    }
    

> It may look like there’s a lot of copying in your code when passing
> collections back and forth. Don’t worry about the memory usage implications
> of this. The Swift collection types are optimized to make copies only when
> necessary, for instance, when your app modifies an array passed by value for
> the first time.

The getter for this property is termed a read method, as it’s reading the
mutable array. The caller gets a copy of the array and is protected against
inappropriately mutating the original array. However, this doesn’t provide any
protection against one thread calling the write method `addPhoto(_:)` while
another thread simultaneously calls the getter for the `photos` property.

GCD provides an elegant solution of creating a [read/write
lock](https://links.jianshu.com/go?to=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FRead%2Fwrite_lock_pattern)
using _dispatch barriers_. Dispatch barriers are a group of functions acting
as a serial-style bottleneck when working with concurrent queues.

When you submit a DispatchWorkItem to a dispatch queue, you can set flags to
indicate that it should be the only item executed on the specified queue for
that particular time. This means all items submitted to the queue prior to the
dispatch barrier must complete before DispatchWorkItem executes.

Barrier Flow

Notice how in normal operation, the queue acts just like a normal concurrent
queue. But when the barrier is executing, it essentially acts as a serial
queue. That is, the barrier is the only thing executing. After the barrier
finishes, the queue goes back to being a normal concurrent queue.

    
    
    private let concurrentPhotoQueue =
      DispatchQueue(
        label: "com.raywenderlich.GooglyPuff.photoQueue",
        attributes: .concurrent)
    
    func addPhoto(_ photo: Photo) {
      // 1
      concurrentPhotoQueue.async(flags: .barrier) { [weak self] in
        guard let self = self else {
          return
        }
    
        // 2
        self.unsafePhotos.append(photo)
    
        // 3
        DispatchQueue.main.async { [weak self] in
          self?.postContentAddedNotification()
        }
      }
    }
    

To ensure thread safety with your writes, you need to perform reads on
concurrentPhotoQueue. You need return data from the function call, so an
asynchronous dispatch won’t cut it. In this case, `sync` would be an excellent
candidate.

> You need to be careful, though. Imagine if you call `sync` and target the
> current queue you’re already running on. This would result in a `deadlock`
> situation.

# Deadlocks

In your case, the sync call will wait until the closure finishes, but the
closure can’t finish — or even start! — until the currently executing closure
finishes, which it can’t! This should force you to be conscious of which queue
you’re calling from — as well as which queue you’re passing in.

Here’s a quick overview of when and where to use sync:

  * Main queue: Be very careful for the same reasons as above. This situation also has potential for a deadlock condition, which is especially bad on the main queue because the whole app will become unresponsive.
  * Global queue: This is a good candidate to sync work through dispatch barriers or when waiting for a task to complete so you can perform further processing.
  * Custom serial queue: Be very careful in this situation. If you’re running in a queue and call sync targeting the same queue, you’ll definitely create a deadlock.

    
    
    var photos: [Photo] {
      var photosCopy: [Photo] = []
    
      // 1
      concurrentPhotoQueue.sync {
        // 2
        photosCopy = self.unsafePhotos
      }
      return photosCopy
    }
    

# Using Dispatch Groups

How can you monitor these concurrent asynchronous events to achieve this?

With dispatch groups, you can group together multiple tasks. Then, you can
either wait for them to complete or receive a notification once they finish.
Tasks can be asynchronous or synchronous and can even run on different queues.

`DispatchGroup` manages dispatch groups. You’ll first look at its `wait`
method. This synchronous method blocks your current thread until all the
group’s enqueued tasks finish.

    
    
    // 1
    DispatchQueue.global(qos: .userInitiated).async {
      var storedError: NSError?
    
      // 2
      let downloadGroup = DispatchGroup()
      for address in [
        PhotoURLString.overlyAttachedGirlfriend,
        PhotoURLString.successKid,
        PhotoURLString.lotsOfFaces
      ] {
        guard let url = URL(string: address) else { return }
    
        // 3
        downloadGroup.enter()
        let photo = DownloadPhoto(url: url) { _, error in
          storedError = error
    
          // 4
          downloadGroup.leave()
        }   
        PhotoManager.shared.addPhoto(photo)
      }   
    
      // 5      
      downloadGroup.wait()
    
      // 6
      DispatchQueue.main.async {
        completion?(storedError)
      }   
    }
    

Call `enter()` to manually notify the group that a task has started. You must
balance out the number of `enter()` calls with the number of `leave()` calls,
or your app will crash.

You can use `wait(timeout:)` to specify a timeout and bail out on waiting
after a specified time.

# Dispatch Groups Notify

    
    
    // 2    
    downloadGroup.notify(queue: DispatchQueue.main) {
      completion?(storedError)
    }
    

`notify(queue:work:)` serves as the asynchronous completion closure. It runs
when there are no more items left in the group. You also specify that you want
to schedule the completion work to run on the main queue.

    
    
    let _ = DispatchQueue.global(qos: .userInitiated)
    DispatchQueue.concurrentPerform(iterations: addresses.count) { index in
      let address = addresses[index]
      guard let url = URL(string: address) else { return }
      downloadGroup.enter()
      let photo = DownloadPhoto(url: url) { _, error in
        storedError = error
        downloadGroup.leave()
      }
      PhotoManager.shared.addPhoto(photo)
    }
    

This implementation includes a curious line of code: `let _ =
DispatchQueue.global(qos: .userInitiated)`. This causes GCD to use a queue
with a `.userInitiated` quality of service for the concurrent calls.

When is it appropriate to use
`DispatchQueue.concurrentPerform(iterations:execute:)`? You can rule out
serial queues because there’s no benefit there – you may as well use a normal
for loop. It’s a good choice for concurrent queues that contain looping,
though, especially if you need to keep track of progress.

# Canceling Dispatch Blocks

Be aware that you can only cancel a DispatchWorkItem before it reaches the
head of a queue and starts executing.

    
    
    // 1
    addresses += addresses + addresses
    
    // 2
    var blocks: [DispatchWorkItem] = []
    
    for index in 0..<addresses.count {
      downloadGroup.enter()
    
      // 3
      let block = DispatchWorkItem(flags: .inheritQoS) {
        let address = addresses[index]
        guard let url = URL(string: address) else {
          downloadGroup.leave()
          return
        }
        let photo = DownloadPhoto(url: url) { _, error in
          storedError = error
          downloadGroup.leave()
        }
        PhotoManager.shared.addPhoto(photo)
      }
      blocks.append(block)
    
      // 4
      DispatchQueue.main.async(execute: block)
    }
    
    // 5
    for block in blocks[3..<blocks.count] {
    
      // 6
      let cancel = Bool.random()
      if cancel {
    
        // 7
        block.cancel()
    
        // 8
        downloadGroup.leave()
      }
    }
    

  * You dispatch the block asynchronously to the main queue. For this example, using the main queue makes it easier to cancel select blocks since it's a serial queue. The code that sets up the dispatch blocks is already executing on the main queue. Thus, you know that the download blocks will execute at some later time.

  * If the random value is true, you cancel the block. This can only cancel blocks that are still in a queue and haven't began executing. You can't cancel a block in the middle of execution.

  * Here, you remember to remove the canceled block from the dispatch group.

# Using Semaphores

Take a brief look at how you can use semaphores to test asynchronous code.

    
    
    let url = try XCTUnwrap(URL(string: urlString))
    
    // 1
    let semaphore = DispatchSemaphore(value: 0)
    _ = DownloadPhoto(url: url) { _, error in
      if let error = error {
        XCTFail("\(urlString) failed. \(error.localizedDescription)")
      }
    
      // 2
      semaphore.signal()
    }
    let timeout = DispatchTime.now() + .seconds(defaultTimeoutLengthInSeconds)
    
    // 3
    if semaphore.wait(timeout: timeout) == .timedOut {
      XCTFail("\(urlString) timed out")
    } 
    

  * You create a semaphore and set its `start value`. This represents the number of things that can access the semaphore without needing to increment it. Another name for incrementing a semaphore is signaling it.
  * You `signal` the semaphore in the completion closure. This increments its count and signals that the semaphore is available to other resources.
  * You `wait` on the semaphore with a given timeout. This call blocks the current thread until you signal the semaphore. A non-zero return code from this function means that the timeout period expired. In this case, the test fails because the network should not take more than 10 seconds to return — a fair point!

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [iOS并发编程--GCD、操作队列、线程](https://www.jianshu.com/p/42c2687a59e0)

现在iOS的多线程方案主要有以下这几种： GCD（Grand Central Dispatch）：使用dispat...

[寒光冷剑](https://www.jianshu.com/u/5a7e2a639843)阅读 1,302评论 0赞 2

  * [ GCD再学习笔记](https://www.jianshu.com/p/43489bf2fa7c)

一、What is GCD? GCD is the marketing name for libdispatch,...

[_浅墨_](https://www.jianshu.com/u/9a969b4dae83)阅读 350评论 0赞 1

  * [GCD in Swfit 3.0](https://www.jianshu.com/p/28044b17f94b)

这里包括了Queue, Group, Barrier, Semaphore等内容。基本上常用的GCD对象和方法在S...

[uncle_charlie](https://www.jianshu.com/u/dbf0c7d3aa4b)阅读 1,422评论 0赞 5

  * [iOS多线程浅汇-原理篇](https://www.jianshu.com/p/7e945d533f2d)

一、前言 多线程这个词对于大家来说并不陌生，但是真正能够熟知多线程的坑点只在少数，iOS中并行也一直被认为是恶魔，...

[和珏猫](https://www.jianshu.com/u/4b41bb7890f8)阅读 233评论 0赞 0

  * [iOS多线程浅汇-原理篇](https://www.jianshu.com/p/bd0743d12e94)

一、前言 多线程这个词对于大家来说并不陌生，但是真正能够熟知多线程的坑点只在少数，iOS中并行也一直被认为是恶魔，...

[nuclear](https://www.jianshu.com/u/fa87412c58bc)阅读 1,632评论 7赞 40

 