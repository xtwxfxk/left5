# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import email, json, pymysql, os, cPickle, gzip, random, urllib, datetime, posixpath, traceback
from PIL import Image
from lxml.html import fromstring
import lxml.etree, lxml.html
from lxml.html.clean import clean_html

from lutils import todir2

from lutils.futures.thread import LThreadPoolExecutor

amazon_data_root = 'I:\\cache_amazon'

page_root = 'I:\\cache_amazon\\pages'
image_root = 'I:\\cache_amazon\\images'


def meta(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)


        meta_title = doc.xpath('//meta[@name="title"]')[0].attrib['content']
        meta_keywords = doc.xpath('//meta[@name="keywords"]')[0].attrib['content']
        meta_description = doc.xpath('//meta[@name="description"]')[0].attrib['content']

        result['meta_title'] = meta_title.replace('Amazon.com:', '').replace('Amazon.com :', '').replace('- - Amazon.com', '').replace('- Amazon.com', '').replace('Amazon.com', '').strip()
        result['meta_keywords'] = meta_keywords.replace('Amazon.com:', '').replace('Amazon.com :', '').replace('- - Amazon.com', '').replace('- Amazon.com', '').replace('Amazon.com', '').strip()
        result['meta_description'] = meta_description.replace('Amazon.com:', '').replace('Amazon.com :', '').replace('- - Amazon.com', '').replace('- Amazon.com', '').replace('Amazon.com', '').strip()
        return result

    return wrapped

def title(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        title = doc.xpath('//title')[0].text.strip()

        result['title'] = title.replace('Amazon.com:', '').replace('Amazon.com :', '').replace('- - Amazon.com', '').replace('- Amazon.com', '').replace('Amazon.com', '').strip()
        return result

    return wrapped

def category(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        categories = []
        for ele in doc.xpath('//div[@id="wayfinding-breadcrumbs_container"]//li/span/a'):
            categories.append(ele.text.strip())

        result['categories'] = categories
        return result

    return wrapped

def name(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        name = doc.xpath('//span[@id="productTitle"]')[0].text.strip()

        result['name'] = name
        return result

    return wrapped

def price(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        price = 0.0
        low_price = 0.0
        tr_count = len(doc.xpath('//div[@id="price_feature_div"]//tr'))
        if tr_count == 3:
            price = doc.xpath('//div[@id="price_feature_div"]//tr[1]/td[2]/span')[0].text.replace('$', '').replace(',', '').split('-', 1)[0].strip()
            low_price = doc.xpath('//div[@id="price_feature_div"]//tr[2]/td[2]/span')[0].text.replace('$', '').replace(',', '').split('-', 1)[0].strip()

        elif tr_count == 1:
            low_price = doc.xpath('//div[@id="price_feature_div"]//tr[1]/td[2]/span')[0].text.replace('$', '').replace(',', '').split('-', 1)[0].strip() # //span[@id="priceblock_ourprice"]

        if low_price == 0.0:
            low_price = '9.99'

        if price < 1:
            price = str(float(low_price) * 2.5)

        result['price'] = price
        result['low_price'] = low_price

        return result

    return wrapped

def feature(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        features = []
        for ele in doc.xpath('//div[@id="feature-bullets"]//li/span')[1:]:
            features.append(ele.text.strip())

        result['features'] = features

        return result

    return wrapped

def description(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        description = ''
        if kwargs['html'].find('iframeContent') > -1:
            description_doc = fromstring(urllib.unquote(kwargs['html'].split('var iframeContent = "', 1)[1].split('";', 1)[0]))

            eles = description_doc.xpath('//div[@class="productDescriptionWrapper"]') # //div[@id="productDescription"]//div[@class="productDescriptionWrapper"]
            if len(eles) > 0:
                # description = "".join([x for x in eles[0].itertext()]).strip()
                # description = lxml.etree.tostring(eles[0])
                # description = lxml.html.tostring(eles[0])

                for node in eles[0]:
                    description += lxml.html.tostring(node)

                description = description.replace('<div class="emptyClear"> </div>', '').strip()

        result['description'] = description

        return result

    return wrapped

def review(method):
    def wrapped(doc, **kwargs):
        result = method(doc, **kwargs)

        reviews = []
        for ele in doc.xpath('//div[@id="revMHRL"]/div'):
            review = {}
            star = ele.xpath('./div/div/a/i')[0].attrib['class'].split(' ')[-1].replace('a-star-', '').strip()
            review['star'] = star

            user_ele = ele.xpath('./div/span/span/a')
            if len(user_ele) < 1:
                review['user'] = "A Customer"
            else:
                user = user_ele[0].text.strip()
                review['user'] = user

            date = ele.xpath('./div/span/span[@class="a-color-secondary"]')[0].text.replace('on ', '').strip()
            review['date'] = date

            title = ele.xpath('./div/div/a/span[@class="a-size-base a-text-bold"]')[0].text.strip()
            review['title'] = title

            content = ''
            for node in ele.xpath('./div[contains(@id, "revData-")]/div[@class="a-section"]')[0]:
                content += lxml.html.tostring(node)

            if not content:
                content = ele.xpath('./div[contains(@id, "revData-")]/div[@class="a-section"]')[0].text.strip()

            if content:
                # content = content.split('&quot;}"><a', 1)[0]
                content = clean_html(content)
                html = fromstring(content)
                for tag in html.xpath('//a'):
                    tag.getparent().remove(tag)
                for tag in html.xpath('//*'):
                    for n, v in tag.attrib.items():
                        del tag.attrib[n]

                content = lxml.html.tostring(html).strip()

                if content.startswith('<span>'):
                    content = content[6:]
                if content.endswith('</span>'):
                    content = content[:-7]


            review['content'] = content

            reviews.append(review)

        result['reviews'] = reviews

        return result

    return wrapped



@meta
@title
@category
@name
@price
@feature
@description
@review
def get_product(doc, **kwargs):

    return {}


save_image_path = 'G:\\php\\site_p\\images'
def save_image(key, product_name):
    images = []
    for i in range(3):
        path = os.path.join(image_root, key[0], key[1], '%s_%02d.jpg' % (key, i+1))
        if os.path.exists(path):
            image = Image.open(open(path, 'rb'))
            des_large_root = os.path.join(save_image_path, product_name[0], product_name[1])
            if not os.path.exists(des_large_root):
                os.makedirs(des_large_root)

            des_large_name = ''
            if i > 0:
                des_large_name = '%s_%02d.jpg' % (product_name, i)
            else:
                des_large_name = '%s.jpg' % product_name

            des_large_path = os.path.join(des_large_root, des_large_name)
            if not os.path.exists(des_large_path):
                large = 800
                if image.width > large or image.height > large:
                    if image.height >= image.width:
                        factor = large / float(image.height)
                    else:
                        factor = large / float(image.width)
                    image.resize((int(image.width * factor), int(image.height * factor)), Image.ANTIALIAS).save(des_large_path, "JPEG")

            images.append(posixpath.join('/images', des_large_name[0], des_large_name[1], des_large_name))

        else:
            return images

    return images


field_separator = '@@@'
multiple_separator = '|||'

data_path = 'G:\\'


def do():

    for p1 in os.listdir(page_root):
        p1_root = os.path.join(page_root, p1)
        for p2 in os.listdir(p1_root):
            p2_root = os.path.join(p1_root, p2)
            for filename in os.listdir(p2_root):
                page_gz = os.path.join(p2_root, filename)

                product_info = cPickle.loads(gzip.GzipFile(page_gz, 'rb').read())

                asin = product_info['url'].split('/dp/', 1)[1].strip()
                try:
                    product_doc = fromstring(product_info['page'])
                    print page_gz, product_info['url']

                    product_data = get_product(product_doc, html=product_info['page'])

                    images = save_image(filename.split('.', 1)[0], todir2(product_data['name']).lower())
                except :
                    traceback.print_exc()

                else:
                    try:
                        if len(images) > 0:
                            #todo write data to csv

                            print images
                            for k, v in product_data.items():
                                print k, v

                        else:
                            print 'Not Image'

                    except:
                        traceback.print_exc()


                break
            break
        break






if __name__ == '__main__':

    do()

































# print '###############'
# # print product_doc.xpath('//title')[0].text.strip()
# # print product_doc.xpath('//meta[@name="title"]')[0].attrib['content']
# # print product_doc.xpath('//meta[@name="keywords"]')[0].attrib['content']
# # print product_doc.xpath('//meta[@name="description"]')[0].attrib['content']
# #
# # # category
# # for ele in product_doc.xpath('//div[@id="wayfinding-breadcrumbs_container"]//li/span/a'):
# #     print ele.text.strip()
#
# # print product_doc.xpath('//span[@id="productTitle"]')[0].text.strip()
#
# # price
# # tr_count = len(product_doc.xpath('//div[@id="price_feature_div"]//tr'))
# # if tr_count == 3:
# #     print  product_doc.xpath('//div[@id="price_feature_div"]//tr[1]/td[2]/span')[0].text.strip()
# #     print product_doc.xpath('//div[@id="price_feature_div"]//tr[2]/td[2]/span')[0].text.strip()
# #
# # elif tr_count == 1:
# #     print product_doc.xpath('//span[@id="priceblock_ourprice"]')[0].text.strip()
#
# # 5
# # for ele in product_doc.xpath('//div[@id="feature-bullets"]//li/span')[1:]:
# #     print ele.text.strip()
#
# # description
# print '##### description'
# description = ''
# eles = product_doc.xpath('//div[@id="productDescription"]//div[@class="productDescriptionWrapper"]')
# if len(eles) > 0:
#     print '***********'
#     print "".join([x for x in eles[0].itertext()])
#
# print '#########################################'
