"""天气工具

模拟天气查询（实际项目中可接入真实天气 API）。
"""

import random
from datetime import datetime


class WeatherTool:
    """天气查询工具（模拟）"""

    name = "weather"
    description = "查询指定城市的天气情况。输入：城市名称（如 北京、上海）"

    # 模拟天气数据
    _weather_types = ["晴", "多云", "阴", "小雨", "中雨", "雷阵雨"]
    _temperature_ranges = {
        "北京": (15, 30),
        "上海": (18, 32),
        "广州": (22, 35),
        "深圳": (23, 34),
        "杭州": (17, 31),
        "成都": (16, 29),
        "武汉": (17, 33),
        "西安": (14, 31),
        "重庆": (19, 35),
        "南京": (16, 32),
    }

    def run(self, city: str) -> str:
        """查询天气

        Args:
            city: 城市名称
        """
        city = city.strip().replace("市", "").replace("天气", "")

        # 使用伪随机但确定性的方式生成天气（同一城市同一天结果一致）
        seed = hash(city + datetime.now().strftime("%Y%m%d"))
        rng = random.Random(seed)

        temp_range = self._temperature_ranges.get(city, (10, 30))
        temp = rng.randint(temp_range[0], temp_range[1])
        weather = rng.choice(self._weather_types)
        humidity = rng.randint(40, 90)
        wind = rng.randint(1, 5)

        return (
            f"【{city}】今日天气：\n"
            f"- 天气状况：{weather}\n"
            f"- 温度：{temp}°C\n"
            f"- 湿度：{humidity}%\n"
            f"- 风力：{wind}级\n"
            f"\n（注：此工具为模拟数据，实际项目中可接入真实天气 API）"
        )

    def __call__(self, city: str) -> str:
        return self.run(city)
