#coding: utf8

from config import *
import feedparser
import xml.dom.minidom as minidom
import re
import time
import datetime
import os
import tempfile
import utils
import cPickle as pickle
from niconvert import create_website

class Bili():
    def __init__(self, width=720, height=480):
        self.WIDTH = width                                          # 屏幕宽度，用于确定弹幕大小
        self.HEIGHT = height                                        # 屏幕高度，用于确定弹幕大小
        self.BASE_URL = BASE_URL                                    # B站根地址
        self.RSS_URLS = RSS_URLS                                    # B站RSS地址
        self.INDEX_URLS = INDEX_URLS                                # B站索引地址
        self.ROOT_PATH = ROOT_PATH                                  # 根菜单
        self.LIST_TYPE = LIST_TYPE                                  # 列表类型
        self.INTERFACE_URL = INTERFACE_URL                          # 视频地址请求页面地址
        self.COMMENT_URL = COMMENT_URL                              # 评论页面地址
        self.URL_PARAMS = re.compile('cid=(\d+)&aid=\d+')           # 匹配视频请求ID(cid)
        self.URL_PARAMS2 = re.compile("cid:'(\d+)'")                # 匹配另一种页面上的视频请求ID(cid)
        # 匹配视频列表
        self.PARTS = re.compile("<option value=.{1}(/video/av\d+/index_\d+\.html).*>(.*)</option>")
        # 匹配索引视频列表
        self.ITEMS = re.compile('<li.*?pubdate="(.*?)">.*?<a href=".*?av(\d+)/".*?>(.*?)</a></li>')
        # 匹配搜索视频列表
        self.SEARCH = re.compile(r'<a href=".*?av(\d+)/".*?\n.*?\n.*?<div class="t">(.*?)</div>',re.MULTILINE)
        # 匹配去标签
        self.NOTAG = re.compile(r'<[^<]*?>')

        # 生成完整的URL
        for item in self.RSS_URLS:
            item['url'] = self.BASE_URL + item['url']
        for item in self.INDEX_URLS:
            item['url'] = self.BASE_URL + item['url']

    # 根据英文名称返回URL
    def _get_url(self, dict_obj, name):
        for item in dict_obj:
            if item['eng_name'] == name:
                return item['url']

    # 根据英文名称获取RSS页面URL
    def _get_rss_url(self, name):
        return self._get_url(self.RSS_URLS, name)

    # 根据英文名称获取索引页面URL
    def _get_index_url(self, name):
        return self._get_url(self.INDEX_URLS, name)

    # 根据页面内容解析视频请求页面URL
    def _parse_urls(self, page_content):
        url_params = self.URL_PARAMS.findall(page_content)
        interface_full_url = ''
        # 如果使用第一种正则匹配成功
        if url_params and len(url_params) == 1 and url_params[0]:
            interface_full_url = self.INTERFACE_URL.format(str(url_params[0]))
        # 如果匹配不成功则使用第二种正则匹配
        if not url_params:
            url_params = self.URL_PARAMS2.findall(page_content)
            if url_params and len(url_params) == 1 and url_params[0]:
                interface_full_url = self.INTERFACE_URL.format(str(url_params[0]))
        if interface_full_url:
            # 解析RSS页面
            content = utils.get_page_content(interface_full_url)
            doc = minidom.parseString(content)
            parts = doc.getElementsByTagName('durl')
            result = []
            # 找出所有视频地址
            for part in parts:
                urls = part.getElementsByTagName('url')
                if len(urls) > 0:
                    result.append(urls[0].firstChild.nodeValue)
            return (result, self._parse_subtitle(url_params[0]))
        print interface_full_url
        return ([], '')

    # 调用niconvert生成弹幕的ass文件
    def _parse_subtitle(self, cid):
        page_full_url = self.COMMENT_URL.format(cid)
        print page_full_url
        website = create_website(page_full_url)
        if website is None:
            print page_full_url + " not supported"
            return ''
        else:
            text = website.ass_subtitles_text(
                font_name=u'黑体',
                font_size=36,
                resolution='%d:%d' % (self.WIDTH, self.HEIGHT),
                line_count=12,
                bottom_margin=0,
                tune_seconds=0
            )
            f = open(tempfile.gettempdir() + '/tmp.ass', 'w')
            f.write(text.encode('utf8'))
            return 'tmp.ass'

    def _need_rebuild(self, file_path):
        return time.localtime(os.stat(file_path).st_ctime).tm_mday != time.localtime().tm_mday

    # 获取索引项目，并缓存
    def _get_index_items(self, url):
        pickle_file_by_word = tempfile.gettempdir() + '/' + url.split('/')[-1].strip() + '_word_tmp.pickle'
        pickle_file_by_month = tempfile.gettempdir() + '/' + url.split('/')[-1].strip() + '_month_tmp.pickle'
        if os.path.exists(pickle_file_by_word) and os.path.exists(pickle_file_by_month) and not self._need_rebuild(pickle_file_by_word) and not self._need_rebuild(pickle_file_by_month):
            return pickle.load(open(pickle_file_by_word, 'rb')), pickle.load(open(pickle_file_by_month, 'rb'))
        else:
            page_content = utils.get_page_content(url)
            results_dict = dict()
            results_month_dict = dict()
            parts = page_content.split('<h3>')
            for part in parts:
                results = self.ITEMS.findall(part)
                key = part[0]
                results_dict[key] = []
                for r in results:
                    results_dict[key].append((r[1], r[2], r[0]))
                    if r[0] in results_month_dict.keys():
                        results_month_dict[r[0]].append((r[1], r[2]))
                    else:
                        results_month_dict[r[0]] = [(r[1], r[2])]
            word_file = open(pickle_file_by_word, 'wb')
            month_file = open(pickle_file_by_month, 'wb')
            pickle.dump(results_dict, word_file)
            pickle.dump(results_month_dict, month_file)
            return results_dict, results_month_dict

    # 获取搜索项目，并缓存
    def _get_search_items(self, keyword):
        search_url = r'http://www.bilibili.tv/search?keyword='+keyword+'&pagesize=500'
        pickle_file = tempfile.gettempdir() + '/' + keyword + '_tmp.pickle'
        if os.path.exists(pickle_file) and not self._need_rebuild(pickle_file):
            return pickle.load(open(pickle_file, 'rb'))
        else:
            page_content = utils.get_page_content(search_url)
            r = self.SEARCH.findall(page_content)
            results = []
            for li,na in r:
                na  = self.NOTAG.sub('',na)
                results.append((li,na))
            word_file = open(pickle_file, 'wb')
            pickle.dump(results, word_file)
        return results

    # 获取RSS项目，返回合法的菜单列表
    def get_rss_items(self, category):
        rss_url = self._get_rss_url(category)
        parse_result = feedparser.parse(rss_url)
        return [ {
            'title': x.title,
            'link': x.link.replace(BASE_URL+'video/av', '').replace('/', ''),
            'description': x.description,
            'published': x.published
        } for x in parse_result.entries ]

    # 获取索引项目，返回合法的菜单列表
    def get_index_items(self, category, type_id=0):
        if type_id > 1:
            return []
        index_url = self._get_index_url(category)
        parse_result = self._get_index_items(index_url)
        return [ {
            'title': x,
            'link': x,
            'description': x,
            'published': x
        } for x in sorted(parse_result[type_id].keys(), reverse=bool(type_id))]

    # 从缓存中返回搜索视频结果
    def get_video_by_keyword(self, keyword):
        return [ {
            'title': x[1],
            'link': x[0],
            'description': x[1],
            'published': keyword
        } for x in self._get_search_items(keyword)]


    # 从缓存字典中返回视频结果
    def get_video_by_ident(self, category, display_type, ident):
        index_url = self._get_index_url(category)
        parse_result = self._get_index_items(index_url)
        return [ {
            'title': x[1],
            'link': x[0],
            'description': x[1],
            'published': ident
        } for x in parse_result[display_type][ident] ]

    # 根据不同类型返回相应的视频列表
    def get_items(self, target, category=None):
        if target == 'RSS':
            if category:
                return self.get_rss_items(category)
            else:
                return self.RSS_URLS
        elif target == 'Index':
            if category:
                return self.get_index_items(category)
            else:
                return self.INDEX_URLS
        return []

    # 获取一个页面的所有视频
    def get_video_list(self, av_id):
        page_full_url = self.BASE_URL + 'video/av' + str(av_id) + '/'
        page_content = utils.get_page_content(page_full_url)
        parts = self.PARTS.findall(page_content)
        if len(parts) == 0:
            return [(u'播放', 'video/av' + str(av_id) + '/')]
        else:
            return [(part[1], part[0][1:]) for part in parts]

    # 获取视频地址
    def get_video_urls(self, url):
        page_full_url = self.BASE_URL + url
        print page_full_url
        page_content = utils.get_page_content(page_full_url)
        return self._parse_urls(page_content)

