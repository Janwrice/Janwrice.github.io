# 递归
## 0x01 递归的四要素
递归函数定义、基础情况处理、递归调用、递推到当前层。

基础情况，就是递归流程的“底”。一个递归流程可以有多个“底”。

四个要素缺一不可，顺序不能随意更改。

如以下这个以递归方法计算阶乘的程序：
```
int Recursive(int n){ //函数定义
    if(n == 1) return 1; //基础情况处理
    int result = n * Recursive(n - 1); //递归调用
    if(n == end) cout << result;
    return result; //递推到当前层
}
```
递归方法计算斐波那契数列第n项的程序：
```
int Recursive(int n){
    if(n <= 1) return n;
    int result = Recursive(n - 1) + Recursive(n - 2);
    if(n == end) cout << result << endl;
    return result;
}
```
阶乘中的递归调用，其表达式中只有一个调用。它的递归树上每个节点只有一个分支，递归树也就只有一个“底”

而斐波那契数列中，递归调用的表达式中有两个调用。它的递归树上每个节点有两个分支。

递归算法的时间复杂度是指数级的，随着递归深度的增加，将进行大量运算。

可以通过“记忆化递归”的方式来优化代码。
