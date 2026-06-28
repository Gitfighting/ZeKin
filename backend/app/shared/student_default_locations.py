"""演示/默认学生寝室与实习单位坐标（GCJ-02，与高德地图一致）。

坐标来源：OpenStreetMap Nominatim 检索「南华大学雨母校区」「湘南湘西高新软件园」，
可用 scripts/verify_amap_geocode.py 配置 AMAP_WEB_KEY 后在高德侧复核。
"""

DEFAULT_DORMITORY_LABEL = "三省园一栋"

DEFAULT_DORMITORY_ADDRESS = (
    "湖南省衡阳市蒸湘区衡祁路228号南华大学(雨母校区)三省园一栋"
)

# 南华大学雨母校区（衡祁路228号）GCJ-02
DEFAULT_DORMITORY_LONGITUDE = 112.511184
DEFAULT_DORMITORY_LATITUDE = 26.8835

DEFAULT_INTERNSHIP_COMPANY = "湘南湘西高新软件园"

DEFAULT_INTERNSHIP_ADDRESS = (
    "湖南省衡阳市蒸湘区采霞街8号湘南湘西高新软件园2栋6楼"
)

# 湘南湘西高新软件园（采霞街）GCJ-02
DEFAULT_INTERNSHIP_LONGITUDE = 112.548458
DEFAULT_INTERNSHIP_LATITUDE = 26.879334
