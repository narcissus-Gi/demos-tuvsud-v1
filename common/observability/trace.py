# 记录一次 LangGraph 执行轨迹
# 例如
# normalize 开始/结束
# authorize 开始/结束
# retrieve 开始/结束
# generate 开始/结束
# validate 开始/结束
# respond 开始/结束
# 主要用于：
# - 解释流程为什么进入某条分支
# - 定位工具或模型失败
# - 统计模型调用和工具尝试次数
# - 展示达到上限后为何停止
# 不需要记录模型的隐藏思维过程。