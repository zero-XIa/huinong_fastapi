# Dart 编码约束

> 适用于 Flutter 3.x + Dart 3，启用空安全。

## 核心语法约束
- 禁止使用 `new` 关键字
- 禁止使用已弃用的组件：`RaisedButton` → `ElevatedButton`，`FlatButton` → `TextButton`，`OutlineButton` → `OutlinedButton`
- 禁止使用 `List()` 构造函数，改用 `[]` 或 `List.filled`
- 禁止使用 `Map()` 构造函数，改用 `{}`
- 禁止使用 `int.parse()` 不捕获异常，推荐 `int.tryParse`
- 异步操作必须使用 `async/await`，避免 `.then`

## 空安全规则
- 变量默认非空，可空类型需显式声明 `?`，例如 `String? name`
- 访问可空变量时使用 `?.` 或 `!`（确保非空）
- 使用 `late` 修饰延迟初始化的非空变量

## UI 编码规范
- 按钮：`ElevatedButton`、`TextButton`、`OutlinedButton`
- 列表：使用 `ListView.builder` 并指定 `itemCount`
- 图片：`Image.network`、`Image.asset`、`Image.file`
- 路由：`Navigator.pushNamed` / `pushReplacementNamed`
- 状态管理：使用 `Provider` 或 `setState`，避免复杂全局变量

## 导入规范
- 材料设计：`import 'package:flutter/material.dart';`
- 网络请求：使用项目中已封装的 `Dio` 单例，不直接创建 `Dio` 实例

## 示例正确代码片段
```dart
// 按钮
ElevatedButton(
  onPressed: _isLoading ? null : () => _login(),
  child: _isLoading ? CircularProgressIndicator() : Text('登录'),
)

// 异步
Future<void> fetchData() async {
  try {
    final data = await api.getUser();
    // 处理数据
  } catch (e) {
    debugPrint('错误: $e');
  }
}
```

