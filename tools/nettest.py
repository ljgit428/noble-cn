# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, json, sys
UA = {'User-Agent': 'Mozilla/5.0'}
def probe(name, url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            b = r.read()[:120]
        print(name, 'OK', b)
    except Exception as e:
        print(name, 'FAIL', type(e).__name__, str(e)[:120])
q = urllib.parse.quote('A doctor')
probe('clients5', 'https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl=zh-CN&q=' + q)
probe('mymemory', 'https://api.mymemory.translated.net/get?q=' + q + '&langpair=en|zh-CN')
probe('google', 'https://www.google.com')
