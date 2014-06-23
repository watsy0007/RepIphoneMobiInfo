#coding:utf8


import urllib.request
from bs4 import BeautifulSoup

def filterData(data):
    return data.replace(' ','')\
        .replace('市','')\
        .replace('中国','')\
        .replace('黑龙江','')\
        .replace('吉林','')\
        .replace('辽宁','')\
        .replace('河北','')\
        .replace('北京','')\
        .replace('山东','')\
        .replace('江苏','')\
        .replace('上海','')\
        .replace('浙江','')\
        .replace('福建','')\
        .replace('广东','')\
        .replace('广西','')\
        .replace('云南','')\
        .replace('贵州','')\
        .replace('四川','')\
        .replace('湖北','')\
        .replace('湖南','')\
        .replace('安徽','')\
        .replace('河南','')\
        .replace('山西','')\
        .replace('陕西','')\
        .replace('宁夏','')\
        .replace('青海','')\
        .replace('内蒙古','')\
        .replace('新疆','')\
        .replace('西藏','')

def getPhonePlace(phoneNumber):
    url = 'http://www.ip138.com:8080/search.asp?action=mobile&mobile=' + phoneNumber
    data = urllib.request.urlopen(url).read().decode('gb2312').encode('utf8')
    bs = BeautifulSoup(data)
    # print(bs)
    res = bs.find_all('td',{'class':'tdc2'})
    # print(res)
    if len(res) == 5:
        place = res[2].contents[-1]
        nStart = 0
        if place.find('联通') >= 0 :
            nStart = place.find('联通')
        elif place.find('电信') >=0 :
            nStart = place.find('电信')
        elif place.find('移动') >= 0:
            nStart = place.find('移动')
        place = place[0:nStart+2]
        place = '%s%s' % (res[1].contents[-1].replace(' ','').replace('市',''),
                          filterData(place))
        return place
    return ''

def getPhoneNumberAndPlace(line):
    #正常手机号
    numIndex = line.find('pref:')
    phoneNum = ''
    isPhoneNumber = False
    if numIndex > 0:
        phoneNum = line[numIndex+5:len(line)]
        phoneNum = phoneNum.replace('-','').replace(' ','').replace('+86','').strip()
        isPhoneNumber = True
    else:
        #异常手机号或者家用电话
        numIndex = line.find('VOICE:')
        if numIndex > 0:
            phoneNum = line[numIndex+6:len(line)]
            phoneNum = phoneNum.replace('-','').replace(' ','').replace('+86','').strip()

    place = getPhonePlace(phoneNum)
    return isPhoneNumber,phoneNum,place


def getItemPhoneNumber(line):
    numIndex = line.find('TEL:')
    isPhoneNumber = True
    if numIndex >= 0:
        phoneNum = line[numIndex+4:len(line)]
        if phoneNum[0] == '0' or phoneNum[0] == '+':
            isPhoneNumber = False
        phoneNum = phoneNum.replace('-','').replace(' ','').replace('+86','').strip()
        place = getPhonePlace(phoneNum)
        return isPhoneNumber,phoneNum,place
    return ''

def main():
    with open('contact.vcf') as fcon:
        with open('newcontact.vcf','w') as wcon:
            lines = ''
            index = 1
            nums = 0
            bSkipItem = False
            for line in fcon.readlines():
                if line == 'BEGIN:VCARD\n':
                    lines = line
                elif line.find('TEL;') >= 0:
                    #替换TEL;type.....
                    isPhoneNumber,phoneNum,place = getPhoneNumberAndPlace(line)
                    if place:
                        line = 'item%d.TEL;type=pref:%s\nitem%d.X-ABLabel:%s\n' % (index,phoneNum,index,place)
                        index += 1
                    elif isPhoneNumber:
                        line = 'TEL;type=CELL;type=VOICE;type=pref:%s\n' % (phoneNum)
                    else:
                        line = 'TEL;type=CELL;type=VOICE:%s\n' % (phoneNum)
                    nums += 1
                    lines = '%s%s' % (lines, line)
                elif line.find('TEL:') >= 0:
                    #替换 TEL:15013...
                    isPhoneNumber,phoneNum,place = getItemPhoneNumber(line)
                    if place:
                        line = 'item%d.TEL:%s\nitem%d.X-ABLabel:%s\n' % (index, phoneNum, index, place)
                        bSkipItem = True
                    else:
                        line = 'item%d.TEL:%s\n' % (index, phoneNum)
                    lines = '%s%s' % (lines, line)
                else:
                    if line.find('FN:振平') >= 0:
                        pass
                    #跳过item
                    if bSkipItem:
                        bSkipItem = False
                        #因为跳过:X-LABEL 所有次数要加1
                        index += 1
                        continue
                    itemStart = line.find('item')
                    itemNext = line.find('.X-ABLabel')
                    if itemStart >= 0 :
                        itemEnd = line.find('.')
                        line = 'item%d%s\n' % (index, line[itemEnd:-1])
                        #这里+1的作用是跳过x-label
                        if itemNext != -1:
                            index += 1

                    lines = '%s%s' % (lines, line)
                if line == 'END:VCARD\n':
                    index = 1
                    wcon.write(lines)

        print ('%d条记录' % nums)
if __name__ == '__main__':
    main()