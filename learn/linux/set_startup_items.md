---
layout: default
title: "Linux 设置开机启动项"
---
如果你打开搜索引擎搜索“Linux 如何设置开机启动项”时，可能会看到下面这个文章：

[linux设置开机自启动的三种方法](https://blog.csdn.net/hualinger/article/details/125321966)

这篇文章中通过配置`/etc/rc.local`的方法来设置开机启动项

但如果你使用的是较新的 Linux 如 debian12，大概率你会发现你的电脑根本没有`/etc/rc.local`这个文件，创建文件写入文本可能也是不起作用的。

那么如何简洁的为 Linux 设置开机启动项呢？

实际上很简单，

## 我们可以使用 **crontab** 功能来实现这点：

```
$ su
$ crontab -e
```

执行后，这时可能会问你选什么编辑器，选择后，在打开的文件尾部输入

```
@reboot /home/start.sh
```

其中，@reboot 表示重启开机的时候运行一次；

`/home/start.sh`即你需要自启动的可执行文件。如果需要 root，也可以直接在其前加 root 实现 root 权限执行。

除了 @reboot 参数，也有其他参数可选：

```
@reboot      Run once, at startup.
@yearly       Run once a year, "0 0 1 1 *".
@annually    (same as @yearly)
@monthly    Run once a month, "0 0 1 * *".
@weekly     Run once a week, "0 0 * * 0".
@daily        Run once a day, "0 0 * * *".
@midnight   (same as @daily)
@hourly      Run once an hour, "0 * * * *".
```
