# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os, time, traceback, urlparse, base64, StringIO, cPickle, hashlib, gzip, logging, logging.config, datetime, json
from lxml.etree import XMLSyntaxError

from PIL import Image
from lutils import isfloat
from lutils.lrequest import LRequest
from lutils.captcha.gsa_captcha import GsaCaptcha
from lxml import etree

logger = logging.getLogger('verbose')

def cache(update=True):
    def _cache(method):
        def wrapped(self, asin, is_cache=True, **kwargs):
            logger.info('Product: %s' % asin)

            md5 = hashlib.md5(asin)
            key = md5.hexdigest()
            cache_name = '%s.gz' % md5.hexdigest()

            product_info = self.load_cache(cache_name)
            if 'modified_date' in product_info and (datetime.datetime.now() - product_info['modified_date']).days < self.CACHE_EXPIRED_DAYS and is_cache:
                logger.info('Use Cache: %s' % asin)

            else:
                url = 'https://www.%s/dp/%s' % (self.domain, asin)
                self.load(url)

                product_info['url'] = url
                product_info['page'] = self.lr.body
                product_info['modified_date'] = datetime.datetime.now()

                self.save_cache(cache_name, product_info)

            return method(self, asin, is_cache=is_cache, product_info=product_info, key=key, cache_name=cache_name)

        return wrapped
    return _cache


def load_html(method):
    def wrapped(self, asin, is_cache=True, **kwargs):
        assert 'product_info' in kwargs

        try:
            product_info = kwargs.get('product_info')

            self.lr.loads(product_info['page'], url=product_info['url'])

            return method(self, asin, is_cache=is_cache, **kwargs)
        except XMLSyntaxError:
            self.remove_cache(kwargs.get('cache_name'))
            raise RuntimeError('Redo: %s' % asin)

    return wrapped

def image_urls(method):
    def wrapped(self, asin, is_cache=True, **kwargs):
        if self.lr.body.find("'colorImages': { 'initial': ") > -1:
            image_urls = []
            for item in json.loads(self.lr.body.split("'colorImages': { 'initial': ", 1)[1].splitlines()[0][:-2]):
                if 'hiRes' in item and item['hiRes']:
                    image_urls.append(item['hiRes'])
        else:

            logger.error('Not Match Image: %s: %s' % (asin, kwargs.get('cache_name')))

        return method(self, asin, is_cache=is_cache, image_urls=image_urls, **kwargs)

    return wrapped

def image_data(method):
    def wrapped(self, asin, is_cache=True, **kwargs):

        for i, url in enumerate(kwargs.get('image_urls', [])):
            name = '%s_%02d.jpg' % (kwargs.get('key'), (i+1))
            if not self.exists_image(name):
                logger.info('Load Image: %s' % url)
                self.lr.load(url, is_xpath=False)
                self.save_image(name, self.lr.body)


        return method(self, asin, is_cache=is_cache, **kwargs)

    return wrapped



def categories(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        _categories = []
        eles = self.lr.xpaths('//div[@id="wayfinding-breadcrumbs_container"]//a')
        for ele in eles:
            _categories.append(ele.text.strip())

        result[AmazonBase.CATEGORIES] = _categories
        return result

    return wrapped

def name(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        result['product_url'] = self.lr.current_url
        title_ele = self.lr.xpath('//span[@id="productTitle"]')
        if title_ele is not None:
            result['product_name'] = title_ele.text.strip()

        return result

    return wrapped

def price(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        result['price'] = '0'
        price_ele = self.lr.xpath('//span[@id="priceblock_ourprice"]')
        if price_ele is not None:
            result['price'] = price_ele.text.strip()
        else:
            price_ele = self.lr.xpath('//span[@id="priceblock_saleprice"]')
            if price_ele is not None:
                result['price'] = price_ele.text.strip()

        return result

    return wrapped

def brand(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        brand = ''
        brand_url = ''
        brand_ele = self.lr.xpath('//a[@id="brand"]')
        if brand_ele is not None and hasattr(brand_ele, 'text') and brand_ele.text is not None:
            brand = brand_ele.text.strip()
            brand_url = urlparse.urljoin(self.lr.current_url, brand_ele.attrib['href'])
        result['brand'] = brand
        result['brand_url'] = brand_url

        return result

    return wrapped

def merchant(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        merchant = ''
        merchant_ele = self.lr.xpath('//div[@id="merchant-info"]')
        if merchant_ele is not None:
            if merchant_ele.text.find('Ships from and sold by Amazon.com') > -1:
                merchant = u'amazon.com'
            elif "".join([x for x in merchant_ele.itertext()]).strip().find('Fulfilled by Amazon') > -1:
                merchant = u'FBA'
        result['merchant'] = merchant

        return result

    return wrapped

def sold_by(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        sold_by = ''
        sold_by_url = ''
        merchant_a_eles = self.lr.xpaths('//div[@id="merchant-info"]/a')
        if merchant_a_eles is not None and len(merchant_a_eles) > 0:
            if merchant_a_eles[0].text.find('Fulfilled by Amazon') < 0:
                sold_by = merchant_a_eles[0].text.strip()
                sold_by_url = urlparse.urljoin(self.lr.current_url, merchant_a_eles[0].attrib['href'])
        result['sold_by'] = sold_by
        result['sold_by_url'] = sold_by_url

        return result

    return wrapped

def reviews(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        reviews = ''
        if self.lr.body.find('acrCustomerReviewText') > -1:
            review_ele = self.lr.xpath('//span[@id="acrCustomerReviewText"]')
            if review_ele is not None:
                reviews = review_ele.text.strip()
        result['review'] = reviews

        return result

    return wrapped

def star(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        star = ''
        star_ele = self.lr.xpath('//span[@id="acrPopover"]//i[contains(@class, "a-icon-star")]/span')
        if star_ele is not None:
            star = star_ele.text.strip()
        result['star'] = star

        return result

    return wrapped

def ranks_str(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        ranks = []
        if self.lr.body.find('Best Sellers Rank') > -1:
            product_sections1_tr_eles = self.lr.xpaths('//table[@id="productDetails_detailBullets_sections1"]//tr')
            for tr_ele in product_sections1_tr_eles:
                th_ele = tr_ele.xpath('./th')
                if th_ele is not None and len(th_ele) > 0 and th_ele[0].text.find('Best Sellers Rank') > -1:
                    rank_eles = tr_ele.xpath('./td/span/span')

                    for ele in rank_eles:
                        rank_count_text = ele.text.split(' ')[0]
                        rank_a_ele = ele.xpath('./a[last()]')
                        rank_keyword = ''
                        rank_url = ''
                        if rank_a_ele and len(rank_a_ele) > 0:
                            rank_keyword = rank_a_ele[0].text.strip()
                            rank_url = urlparse.urljoin(product_url, rank_a_ele[0].attrib['href'])

                        ranks.append([rank_count_text, rank_keyword, rank_url])

            rank_li_ele = self.lr.xpath('//li[@id="SalesRank"]')
            if rank_li_ele is not None:
                rank_inner_str = (rank_li_ele.text + ''.join(map(etree.tostring, rank_li_ele))).strip()
                if rank_inner_str.find('See Top 100') > -1:
                    # top_count_text = rank_li_ele.text.strip().split(' ')[0]

                    top_count_text = rank_inner_str.split('#', 1)[1].split(' in ')[0]

                    _ele = rank_li_ele.xpath('./a')
                    if _ele and len(_ele) > 0:
                        top_href = _ele[0].attrib['href']
                        top_keyword_text = _ele[0].text.strip()

                        ranks.append([top_count_text, top_keyword_text, top_href])

                _li_eles = rank_li_ele.xpath('./ul/li')
                for _li_ele in _li_eles:
                    rank_count_ele = _li_ele.xpath('./span[@class="zg_hrsr_rank"]')
                    if rank_count_ele and len(rank_count_ele) > 0:
                        rank_count_text = rank_count_ele[0].text.strip()

                        rank_a_ele = _li_ele.xpath('./span[@class="zg_hrsr_ladder"]//a')
                        if rank_a_ele and len(rank_a_ele) > 0:
                            rank_keyword = rank_a_ele[-1].text.strip()
                            rand_href = rank_a_ele[-1].attrib['href']

                            ranks.append([rank_count_text, rank_keyword, rand_href])


        result['ranks'] = ranks

        return result

    return wrapped

def other_seller(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        other_url = ''
        other_text = ''
        if self.lr.body.find('Other Sellers on Amazon') > -1:
            other_ele = self.lr.xpath('//div[@id="mbc"]//span[@class="a-size-small"]/a')
            if other_ele is not None:
                other_url = urlparse.urljoin(self.lr.current_url, other_ele.attrib['href'])
                other_text = other_ele.text.strip()
        result['other_url'] = other_url
        result['other_text'] = other_text

        return result

    return wrapped

def weight_ounces(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        result = detail(self, product_url, is_cache=is_cache, **kwargs)

        ele = self.lr.xpath('//div[@id="prodDetails"]//td[contains(text(), "ounces")]') # //div[@id="prodDetails"]//tbody/tr/td[contains(text(), "ounces")]

        if ele is not None:
            w = ele.text.strip().split(' ', 1)[0]
            if isfloat(w):
                result[AmazonBase.WEIGHT_OUNCES] = float(w)

        return result

    return wrapped

class AmazonBase(object):

    CACHE_ROOT = ''
    CACHE_PAGES_ROOT = ''
    CACHE_IMAGES_ROOT = ''

    CACHE_EXPIRED_DAYS = 15

    captcha = None

    def __init__(self, cache_root, **kwargs):

        self.lr = LRequest(string_proxy=kwargs.get('string_proxy', ''))

        self.captcha = GsaCaptcha(ip=kwargs.get('gsa_ip', '192.168.1.188'), port=kwargs.get('gsa_port', '8000'))

        self.CACHE_ROOT = cache_root
        self.CACHE_PAGES_ROOT = kwargs.get('cache_page', os.path.join(self.CACHE_ROOT, 'pages'))
        self.CACHE_IMAGES_ROOT = kwargs.get('cache_image', os.path.join(self.CACHE_ROOT, 'images'))

        if not os.path.exists(self.CACHE_ROOT): os.makedirs(self.CACHE_ROOT)
        if not os.path.exists(self.CACHE_PAGES_ROOT): os.makedirs(self.CACHE_PAGES_ROOT)
        if not os.path.exists(self.CACHE_IMAGES_ROOT): os.makedirs(self.CACHE_IMAGES_ROOT)

        self.domain = kwargs.get('domain', 'amazon.com')

        self.CACHE_EXPIRED_DAYS = kwargs.get('cache_expired_days', 15)

    def load(self, url, is_xpath=True):
        logger.info('Load Url: %s' % url)
        self.lr.load(url, is_xpath=is_xpath)
        if self.check_captcha():
            self.lr.load(url, is_xpath=is_xpath)

    def check_captcha(self):
        if self.captcha is not None:
            captcha_img_ele = self.lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')
            if captcha_img_ele is not None:
                while 1:
                    logger.info('Need Captcha')

                    try:
                        if captcha_img_ele is not None:

                            form = self.lr.get_forms()[0]
                            self.lr.load(captcha_img_ele.attrib['src'])
                            cap = self.captcha.decode_stream(self.lr.body)
                            logger.info('Captcha: %s' % cap)

                            form['field-keywords'] = cap
                            self.lr.load(form.click())
                        else:
                            return True

                        captcha_img_ele = self.lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')

                    except KeyboardInterrupt:
                        raise
                    except IndexError:
                        self.lr.load(self.lr.current_url)
                        captcha_img_ele = self.lr.xpath('//form[contains(@action, "Captcha")]//img[contains(@src, "captcha")]')
                        if captcha_img_ele is None:
                            return True
                    except:
                        # open(os.path.join('I:\\captcha_error_page', '%s.html' % time.time()), 'w').write(self.lr.body)
                        logger.error(traceback.format_exc())

            return False
        else:
            raise RuntimeError('Not Captcha Server...')

    def exists_cache(self, cache_name):
        cache_path = os.path.join(self.CACHE_PAGES_ROOT, cache_name[0], cache_name[1], cache_name)
        return os.path.exists(cache_path)

    def remove_cache(self, cache_name):
        cache_path = os.path.join(self.CACHE_PAGES_ROOT, cache_name[0], cache_name[1], cache_name)

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except:
                pass

    def load_cache(self, cache_name):
        cache_path = os.path.join(self.CACHE_PAGES_ROOT, cache_name[0], cache_name[1], cache_name)

        if os.path.exists(cache_path):
            try:
                return cPickle.loads(gzip.GzipFile(cache_path, 'rb').read())
            except:
                return {}

        return {}

    def save_cache(self, cache_name, data):
        _p = os.path.join(self.CACHE_PAGES_ROOT, cache_name[0], cache_name[1])
        if not os.path.exists(_p): os.makedirs(_p)

        cache_path = os.path.join(self.CACHE_PAGES_ROOT, cache_name[0], cache_name[1], cache_name)

        gzip_file = gzip.open(cache_path, 'wb')
        gzip_file.write(cPickle.dumps(data))
        gzip_file.close()

    def exists_image(self, name):
        image_path = os.path.join(self.CACHE_IMAGES_ROOT, name[0], name[1], name)
        return os.path.exists(image_path)

    def save_image(self, name, data):
        _p = os.path.join(self.CACHE_IMAGES_ROOT, name[0], name[1])
        if not os.path.exists(_p): os.makedirs(_p)

        image_path = os.path.join(self.CACHE_IMAGES_ROOT, name[0], name[1], name)
        open(image_path, 'wb').write(data)


    @staticmethod
    def wrapped_url(url):
        return url.split('/ref', 1)[0]


    @cache()
    @load_html
    @name
    @price
    @brand
    @merchant
    @sold_by
    @reviews
    @star
    @ranks_str
    @other_seller
    @weight_ounces
    def product_detail(self, asin, is_cache=True, **kwargs):

        return kwargs.get('product_info', {})



    @cache()
    @load_html
    @image_urls
    @image_data
    def product(self, asin, is_cache=True, **kwargs):
        return kwargs.get('product_info', {})



