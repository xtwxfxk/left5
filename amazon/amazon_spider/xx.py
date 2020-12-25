# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

aa = '''ID;Active (0/1);Name *;Categories (x,y,z...);Price tax excluded or Price tax included;Tax rules ID;Wholesale price;On sale (0/1);Discount amount;Discount percent;Discount from (yyyy-mm-dd);Discount to (yyyy-mm-dd);Reference #;Supplier reference #;Supplier;Manufacturer;EAN13;UPC;Ecotax;Width;Height;Depth;Weight;Quantity;Minimal quantity;Visibility;Additional shipping cost;Unity;Unit price;Short description;Description;Tags (x,y,z...);Meta title;Meta keywords;Meta description;URL rewritten;Text when in stock;Text when backorder allowed;Available for order (0 = No, 1 = Yes);Product available date;Product creation date;Show price (0 = No, 1 = Yes);Image URLs (x,y,z...);Delete existing images (0 = No, 1 = Yes);Feature(Name:Value:Position);Available online only (0 = No, 1 = Yes);Condition;Customizable (0 = No, 1 = Yes);Uploadable files (0 = No, 1 = Yes);Text fields (0 = No, 1 = Yes);Out of stock;ID / Name of shop;Advanced stock management;Depends On Stock;Warehouse
1;1;iPod Nano;iPods;100;1;80;1;;5.5;2013-06-01;2018-12-31;RP-demo_1;RF-demo_1;Applestore;Apple;1234567890123;;1;0.6;0.2;0.4;0.068357;160;1;;;;;<p>New design.</p>;<p>New design.</p>;apple, ipod, nano;Meta title-Nano;Meta keywords-Nano;Meta description-Nano;iPod-Nano;In Stock;Current supply. Ordering availlable;1;2013-03-01;2013-01-01;1;http://localhost/prestashop/img/p/1/5/15.jpg;0;;0;new;0;0;0;0;0;0;0;0'''

aa = '''ID;Active (0/1);Name *;Categories (x,y,z...);Price tax excluded or Price tax included;Tax rules ID;Wholesale price;On sale (0/1);Discount amount;Discount percent;Discount from (yyyy-mm-dd);Discount to (yyyy-mm-dd);Reference #;Supplier reference #;Supplier;Manufacturer;EAN13;UPC;Ecotax;Width;Height;Depth;Weight;Quantity;Minimal quantity;Visibility;Additional shipping cost;Unity;Unit price;Short description;Description;Tags (x,y,z...);Meta title;Meta keywords;Meta description;URL rewritten;Text when in stock;Text when backorder allowed;Available for order (0 = No, 1 = Yes);Product available date;Product creation date;Show price (0 = No, 1 = Yes);Image URLs (x,y,z...);Delete existing images (0 = No, 1 = Yes);Feature(Name:Value:Position);Available online only (0 = No, 1 = Yes);Condition;Customizable (0 = No, 1 = Yes);Uploadable files (0 = No, 1 = Yes);Text fields (0 = No, 1 = Yes);Out of stock;ID / Name of shop;Advanced stock management;Depends On Stock;Warehouse
9;1;BL-5 Extended 3800mAh 7.4V Li ion Battery for Baofeng UV-5R 5RE F8+ F9;Electronics,Portable Audio & Video,CB & Two-Way Radios,Accessories,Battery Chargers;99;1;78;1;55;;2013-06-01;2020-12-31;;;;LEFT;1234567890123;719970635722;1;0.6;0.2;0.4;333;100;1;;22;;;short desc;long desc;left,category;meta title product;meta keywords;meta description;AAAAA-BL-5-Extended-3800mAh-7-4V-Li-ion-Battery-for-Baofeng-UV-5R-5RE-F8-F9;In Stock;Current supply. Ordering availlable;1;2013-01-01;2013-01-01;1;http://g02.a.alicdn.com/kf/HTB1IbkkLVXXXXXfXFXXq6xXFXXXr/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g01.a.alicdn.com/kf/HTB1_binJVXXXXcfXpXXq6xXFXXX7/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g02.a.alicdn.com/kf/HTB1_XyuJVXXXXXwXpXXq6xXFXXXG/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g01.a.alicdn.com/kf/HTB1pb1mJVXXXXcPXpXXq6xXFXXX7/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g02.a.alicdn.com/kf/HTB1XhSsJVXXXXarXpXXq6xXFXXXV/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg;0;;0;new;0;0;0;0;0;0'''

# aa = '''Product ID*;Product Reference;Attribute (Name:Type:Position)*;Value (Value:Position)*;Supplier reference;Reference;EAN13;UPC;Wholesale price;Impact on price;Ecotax;Quantity;Minimal quantity;Impact on weight;Default (0 = No, 1 = Yes);Combination available date;Choose among product images by position (1,2,3...);Image URL;Delete existing images (0 = No, 1 = Yes);ID / Name of shop;Advanced Stock Managment;Depends on stock;Warehouse
# 1;;Color:color:0, Disk space:select:1;Blue:0, 16GB:1;RF-Nano-Blue-16GB;RP-Nano-Blue-16GB;0000080446392;116052426077;100;40;0;10;1;0;0;2014-01-01;1;http://g02.a.alicdn.com/kf/HTB1WN81LXXXXXcKXXXXq6xXFXXXY/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg_50x50.jpg;1;0;0;0;'''

aal = []
c = 0
for a in aa.splitlines():
    aas = a.split(';')
    c = len(aas)
    print c
    aal.append(aas)

for i in range(c):
    print '%s @@@ %s' % (aal[0][i], aal[1][i])


'''ID @@@ 9
Active (0/1) @@@ 1
Name * @@@ BL-5 Extended 3800mAh 7.4V Li ion Battery for Baofeng UV-5R 5RE F8+ F9
Categories (x,y,z...) @@@ Electronics,Portable Audio & Video,CB & Two-Way Radios,Accessories,Battery Chargers
Price tax excluded or Price tax included @@@ 99
Tax rules ID @@@ 1
Wholesale price @@@ 78
On sale (0/1) @@@ 1
Discount amount @@@ 55
Discount percent @@@
Discount from (yyyy-mm-dd) @@@ 2013-06-01
Discount to (yyyy-mm-dd) @@@ 2020-12-31
Reference # @@@
Supplier reference # @@@
Supplier @@@
Manufacturer @@@ LEFT
EAN13 @@@ 1234567890123
UPC @@@ 719970635722
Ecotax @@@ 1
Width @@@ 0.6
Height @@@ 0.2
Depth @@@ 0.4
Weight @@@ 333
Quantity @@@ 100
Minimal quantity @@@ 1
Visibility @@@
Additional shipping cost @@@ 22
Unity @@@
Unit price @@@
Short description @@@ short desc
Description @@@ long desc
Tags (x,y,z...) @@@ left,category
Meta title @@@ meta title product
Meta keywords @@@ meta keywords
Meta description @@@ meta description
URL rewritten @@@ AAAAA-BL-5-Extended-3800mAh-7-4V-Li-ion-Battery-for-Baofeng-UV-5R-5RE-F8-F9
Text when in stock @@@ In Stock
Text when backorder allowed @@@ Current supply. Ordering availlable
Available for order (0 = No, 1 = Yes) @@@ 1
Product available date @@@ 2013-01-01
Product creation date @@@ 2013-01-01
Show price (0 = No, 1 = Yes) @@@ 1
Image URLs (x,y,z...) @@@ http://g02.a.alicdn.com/kf/HTB1IbkkLVXXXXXfXFXXq6xXFXXXr/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g01.a.alicdn.com/kf/HTB1_binJVXXXXcfXpXXq6xXFXXX7/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g02.a.alicdn.com/kf/HTB1_XyuJVXXXXXwXpXXq6xXFXXXG/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g01.a.alicdn.com/kf/HTB1pb1mJVXXXXcPXpXXq6xXFXXX7/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg,http://g02.a.alicdn.com/kf/HTB1XhSsJVXXXXarXpXXq6xXFXXXV/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg
Delete existing images (0 = No, 1 = Yes) @@@ 0
Feature(Name:Value:Position) @@@
Available online only (0 = No, 1 = Yes) @@@ 0
Condition @@@ new
Customizable (0 = No, 1 = Yes) @@@ 0
Uploadable files (0 = No, 1 = Yes) @@@ 0
Text fields (0 = No, 1 = Yes) @@@ 0
Out of stock @@@ 0
ID / Name of shop @@@ 0
Advanced stock management @@@ 0'''

'''Product ID* @@@ 1
Product Reference @@@
Attribute (Name:Type:Position)* @@@ Color:color:0, Disk space:select:1
Value (Value:Position)* @@@ Blue:0, 16GB:1
Supplier reference @@@ RF-Nano-Blue-16GB
Reference @@@ RP-Nano-Blue-16GB
EAN13 @@@ 0000080446392
UPC @@@ 116052426077
Wholesale price @@@ 100
Impact on price @@@ 40
Ecotax @@@ 0
Quantity @@@ 10
Minimal quantity @@@ 1
Impact on weight @@@ 0
Default (0 = No, 1 = Yes) @@@ 0
Combination availability date @@@ 2014-01-01
Choose among product images by position (1,2,3...) @@@ 1
Image URL @@@ http://g02.a.alicdn.com/kf/HTB1WN81LXXXXXcKXXXXq6xXFXXXY/Fashionable-Wood-Sunglasses-Men-Reflective-Sports-Sun-Glasses-Outdoors-Square-Eyewear-Gafas-De-Sol-Oculos-De.jpg_50x50.jpg
Delete existing images (0 = No, 1 = Yes) @@@ 1
ID / Name of shop @@@ 0
Advanced Stock Managment @@@ 0
Depends on stock @@@ 0
Warehouse @@@ '''

