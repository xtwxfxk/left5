# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import datetime



def cache(update=True):
    def _cache(detail):
        def wrapped(self, asin, is_cache=True):

            from amazon import Amazon
            md5 = hashlib.md5(asin)
            key = '%s.gz' % md5.hexdigest()

            product_info = Amazon.load_cache(key)
            if 'modified_date' in product_info and (datetime.datetime.now() - product_info['modified_date']).days < Amazon.CACHE_EXPIRED_DAYS:
                pass

            else:
                self.load('https://www.amazon.com/dp/%s' % asin)

                page = self.lr.body
                image_urls = []

                for ele in self.lr.xpaths('//div[@class="imgTagWrapper"]/img'):
                    if 'data-old-hires' in ele.attrib:
                        image_urls.append(ele.attrib['data-old-hires'])

                product_info['page'] = page
                product_info['image_urls'] = image_urls
                product_info['modified_date'] = datetime.datetime.now()

                Amazon.save_cache(key, product_info)


            return detail(self, asin, is_cache=is_cache, page_info=product_info)

        return wrapped
    return _cache



def load_html(detail):
    def wrapped(self, product_url, is_cache=True, **kwargs):
        assert 'page_info' in kwargs
        assert 'image_data' in kwargs

        page_info = kwargs.get('page_info')

        self.lr.loads(page_info['page'], url=page_info['url'])

        return detail(self, product_url, is_cache=is_cache, **kwargs)

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