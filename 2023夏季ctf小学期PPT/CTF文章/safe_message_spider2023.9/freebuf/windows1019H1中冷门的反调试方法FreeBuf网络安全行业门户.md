windows 19H1中PsSuspendProcess新加了一点代码:

![1610210043_5ff9dafbe8a318c3037ca.png!small](https://image.3001.net/images/20210110/1610210043_5ff9dafbe8a318c3037ca.png!small)

以前的是没有的:

![1610210001_5ff9dad11e7c31e16e7eb.png!small?1610210002258](https://image.3001.net/images/20210110/1610210001_5ff9dad11e7c31e16e7eb.png!small?1610210002258)

    
    
    if ( !targetThread->Tcb.MiscFlags.BypassProcessFreeze )

总所周知 调试器都要用这个函数挂起线程、进程  
因此如果我们给线程设置一个参数(THREAD_CREATE_FLAGS_BYPASS_PROCESS_FREEZE为0x40):

    
    
    NtCreateThreadEx(&handle, MAXIMUM_ALLOWED, nullptr, NtCurrentProcess(),
                     &printer, nullptr, THREAD_CREATE_FLAGS_BYPASS_PROCESS_FREEZE,
                     0, 0, 0, nullptr);

那么这个线程将无法暂停!  
那么 如何利用为反调试呢?  
继续看KeSuspendThread:

![1610210122_5ff9db4acfb7129cc2646.png!small](https://image.3001.net/images/20210110/1610210122_5ff9db4acfb7129cc2646.png!small)

可以看到 Thread->Tcb.SuspendCount 在成功暂停线程的时候会增加! 也就是说我们可以利用那个新的flag阻止线程暂停
这样子这个count就不会增加 当调试器调用NtResumeProcess的时候 计数就会减少! 利用这一点我们就可以知道自己是否被调试:

    
    
    for(size_t i = 0; i < 128; ++i)
      NtSuspendThread(thread, nullptr);
    
    while(true) {
      if(NtSuspendThread(thread, nullptr) != STATUS_SUSPEND_COUNT_EXCEEDED)
        std::puts("I was suspended\n");
      Sleep(1000);
    }

