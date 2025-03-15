def revenue_calculate_to_order(items: dict[str:float]) -> float:
    total: float = 0.0

    for i in items.values():
        total += i

    return total
