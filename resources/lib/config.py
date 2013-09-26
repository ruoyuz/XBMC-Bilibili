#coding: utf8

# B站根地址
BASE_URL = r'http://www.bilibili.tv/'

# B站接口地址（用于获取视频地址）
INTERFACE_URL = r'http://interface.bilibili.tv/playurl?cid={0}'

# B站评论页面地址
COMMENT_URL = r'http://comment.bilibili.tv/{0}.xml'

# 根菜单
ROOT_PATH = [ 'RSS', 'Index', 'Search']

# 列表类型
LIST_TYPE = [ 'Month', 'Alpha' ]

# RSS地址列表
RSS_URLS = [
    {
        'name': u'动画',
        'eng_name': 'anime',
        'url': 'rss-1.xml'
    },
    {
        'name': u'音乐',
        'eng_name': 'music',
        'url': 'rss-3.xml'
    },
    {
        'name': u'游戏',
        'eng_name': 'game',
        'url': 'rss-4.xml'
    },
    {
        'name': u'娱乐',
        'eng_name': 'entertainment',
        'url': 'rss-5.xml'
    },
    {
        'name': u'专辑',
        'eng_name': 'album',
        'url': 'rss-11.xml'
    },
    {
        'name': u'新番连载',
        'eng_name': 'series',
        'url': 'rss-13.xml'
    }
]

# 索引地址列表
INDEX_URLS = [
    {
        'name': u'新番二次元',
        'eng_name': 'anime2',
        'url': 'sitemap/sitemap-33.html'
    },
    {
        'name': u'新番三次元',
        'eng_name': 'anime3',
        'url': 'sitemap/sitemap-34.html'
    },
    {
        'name': u'专辑二次元',
        'eng_name': 'album2',
        'url':  'sitemap/sitemap-32.html'
    },
    {
        'name': u'专辑三次元',
        'eng_name': 'album3',
        'url': 'sitemap/sitemap-15.html'
    },
    {
        'name': u'生活娱乐',
        'eng_name': 'mixup',
        'url': 'sitemap/sitemap-21.html'
    },
    {
        'name': u'影视',
        'eng_name': 'movie',
        'url': 'sitemap/sitemap-23.html'
    },
    {
        'name': u'科普知识',
        'eng_name': 'science',
        'url': 'sitemap/sitemap-37.html'
    },
    {
        'name': u'人文地理',
        'eng_name': 'documentary',
        'url': 'sitemap/sitemap-38.html'
    } 
]
