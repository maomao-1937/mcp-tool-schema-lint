# mcp-tool-schema-lint

检查 MCP tools/list 快照的基础协议结构错误，以及可能影响工具理解的 schema 描述缺口。

适用对象：希望在向客户端或 Agent 暴露工具 schema 前快速离线检查的 MCP 开发者。

## 快速开始

需要 Python 3.11 或更新版本，无第三方依赖。CLI 从标准输入读取一份 JSON，并输出一行确定性 JSON。

```console
python mcp_tool_schema_lint.py < examples/input.json
```

输出：

```json
{"error_count":0,"issues":[],"ok":true,"tool_count":1,"warning_count":0}
```

运行测试和精确示例检查：

```console
python -m unittest discover -s tests -v
python examples/run_examples.py
```

输入限制为 256 KiB；畸形 JSON、重复键或过深输入会返回固定错误码。输出不会回显 schema 描述或值，问题指针可能包含 schema 对象键名。程序不会启动或连接 MCP 服务。

## 问题证据与范围

MCP Python SDK 迁移指南记录了更严格的协议校验和 Tool.inputSchema 必须声明 object 类型的要求；MCP Inspector issue #1388 则提出在工具表单中展示数据类型与校验细节。本工具把协议错误与建议性警告分开。

这些证据仅说明具体报告和公开记录的行为，不能证明问题发生频率，也不能预测 GitHub Star。

## 限制

只检查文档说明的 JSON Schema 子集，不是完整的 draft 验证器，也不测试任何 MCP 客户端行为。描述字段检查属于建议。

## 许可证与署名

MIT。本仓库使用原创代码和合成样例，不包含上游代码或素材。

## 已验证环境

Windows Python 3.11.15；GitHub Actions Ubuntu 与 Windows，Python 3.11。
