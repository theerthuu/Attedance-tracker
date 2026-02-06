def calculate_stats(attended, total, target):
    if total == 0:
        return {"percentage": 0, "needed": 0}

    percentage = (attended / total) * 100
    needed = 0

    while percentage < target:
        attended += 1
        total += 1
        needed += 1
        percentage = (attended / total) * 100

    return {"percentage": percentage, "needed": needed}
