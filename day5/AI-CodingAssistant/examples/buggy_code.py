"""用于演示代码审查的故意含错代码，不要用于生产环境。"""

history = []

def bad_rate(rows):
    rates = [r["defect_count"] / r["total_count"]
             for r in rows]
    return sum(rates) / len(rates)
