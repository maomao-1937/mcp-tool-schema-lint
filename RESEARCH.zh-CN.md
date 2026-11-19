# 研究记录：mcp-tool-schema-lint

## 来源中可观察的事实

MCP Python SDK 迁移指南记录了更严格的协议校验和 Tool.inputSchema 必须声明 object 类型的要求；MCP Inspector issue #1388 则提出在工具表单中展示数据类型与校验细节。本工具把协议错误与建议性警告分开。

来源链接见 [RESEARCH.md](RESEARCH.md)。

## 选题判断

检查 MCP tools/list 快照的基础协议结构错误，以及可能影响工具理解的 schema 描述缺口。 这是基于上述观察形成的离线工具设想；来源不能证明发生率、市场规模或预期 Star。
