# -*- coding: utf-8 -*-
# @File   :constant.py
# @Author :Abr
# @Date   :18-8-17
# @Desc   :常量


# 图片验证码Redis有效期， 单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码Redis有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 七牛空间域名
QINIU_DOMIN_PREFIX = "http://bkt.clouddn.com/"

# 首页展示最多的新闻数量
HOME_PAGE_MAX_NEWS = 10

# 用户的关注每一页最多数量
USER_FOLLOWED_MAX_COUNT = 4

# 用户收藏每页显示最多新闻数量
USER_COLLECTION_MAX_NEWS = 10

# 其他用户每一页最多新闻数量
OTHER_NEWS_PAGE_MAX_COUNT = 10

# 点击排行展示的最多新闻数据
CLICK_RANK_MAX_NEWS = 6

# 管理员页面用户每页多最数据条数
ADMIN_USER_PAGE_MAX_COUNT = 10

# 管理员页面新闻每页多最数据条数
ADMIN_NEWS_PAGE_MAX_COUNT = 10

ONE = 1
TEN = 10
HUNDRED = 100
THOUSAND = 1000
WAN = 10000

REQUEST_EXPIRE = 60 * 10
REQUEST_NONCE_PREFIX = "request_nonce"
REQUEST_NONCE_EXPIRE = 4
