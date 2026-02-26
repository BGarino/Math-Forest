"""
Calculates diamond rewards based on level and performance.
"""

BASE_REWARD = 5
PERFECT_BONUS = 10
SPEED_BONUS = 5


class RewardSystem:
    @staticmethod
    def calculate(level: int, correct: int, total: int,
                  time_taken: float = 60.0) -> int:
        """Returns diamond reward."""
        if total == 0:
            return 0
        accuracy = correct / total
        base = BASE_REWARD + (level // 10)
        reward = int(base * accuracy)
        if accuracy == 1.0:
            reward += PERFECT_BONUS
        if time_taken < 30:
            reward += SPEED_BONUS
        return max(reward, 1)

    @staticmethod
    def stars(correct: int, total: int) -> int:
        if total == 0:
            return 0
        ratio = correct / total
        if ratio == 1.0:
            return 3
        elif ratio >= 0.7:
            return 2
        else:
            return 1
