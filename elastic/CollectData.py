from distutils.command.check import check
from django_elasticsearch_dsl.search import Search
import requests
from lxml import html
import urllib
import urllib.parse
from langdetect import detect
import langid
import re
from elastic.models import ParagraphsCorpus
import nltk
import nltk.data


def url_encode(url):
    com = urllib.parse.urlparse(url)
    encoded = com.scheme + '://' + com.netloc + urllib.parse.quote(com.path)
    return encoded.strip()

def get_corpus(url, title_xpath, en_xpath, vi_xpath, break_word, continue_word):
    if ('%' not in url):
        url = url_encode(url)
    print(url)
    response = requests.get(url)
 
    # get byte string
    byte_data = response.content
    # get filtered source code
    source_code = html.fromstring(byte_data)
    
    title = source_code.xpath(title_xpath)
    title = title[0].text_content()
    print('Title: ', title)
    
    en_content_tags=source_code.xpath(en_xpath)
    vi_content_tags=source_code.xpath(vi_xpath)
    en = []
    en_nltk = []
    vi = []
    vi_nltk = []

    list_vi_xpath = vi_xpath.split('|')
    list_en_xpath = en_xpath.split('|')

    
    check_remove_duplicate_content = False
    for i in range(len(list_vi_xpath)-1):
        for j in range(i+1, len(list_vi_xpath)):
            if(list_vi_xpath[i].strip().replace(' ', '').lower() in list_vi_xpath[j].strip().replace(' ', '').lower() or list_vi_xpath[j].strip().replace(' ', '').lower() in list_vi_xpath[i].strip().replace(' ', '').lower()):
                check_remove_duplicate_content = True
                break
        if(check_remove_duplicate_content == True):
            break
    if(check_remove_duplicate_content == False):
        for i in range(len(list_en_xpath)-1):
            for j in range(i+1, len(list_en_xpath)):
                if(list_en_xpath[i].strip().replace(' ', '').lower() in list_en_xpath[j].strip().replace(' ', '').lower() or list_en_xpath[j].strip().replace(' ', '').lower() in list_en_xpath[i].strip().replace(' ', '').lower()):
                    check_remove_duplicate_content = True
                    break
            if(check_remove_duplicate_content == True):
                break
    
    check_classify_language = False
    if('text()' in vi_xpath or 'text()' in en_xpath):
        check_classify_language = True
    if(check_classify_language == False):
        for i in range(len(list_vi_xpath)):
            for j in range(len(list_en_xpath)):
                if(list_vi_xpath[i].strip().replace(' ', '').lower() in list_en_xpath[j].strip().replace(' ', '').lower() or list_en_xpath[j].strip().replace(' ', '').lower() in list_vi_xpath[i].strip().replace(' ', '').lower()):
                    check_classify_language = True
                    break
            if(check_classify_language == True):
                break
    
    for i in range(len(break_word)):
        break_word[i] = break_word[i].upper().strip()
    print(break_word)

    for i in range(len(continue_word)):
        continue_word[i] = continue_word[i].upper().strip()
    print(continue_word)
    
    print('============== X??? L?? TI???NG ANH ================')
    print(len(en_content_tags))
    for sentence in en_content_tags:
        tmp = sentence
        try:
            tmp = sentence.text_content()
        except:
            pass
        print()
        print('G???p: ', tmp.replace('\n',''))
        if (tmp == ''):
            print('continue')
            continue

        if (check_remove_duplicate_content == True and tmp.replace('\n','') in en):
            print('continue')
            continue
        break_scan = False
        continue_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('G???p break word')
            break
        for i in continue_word:     
            if(i in tmp.upper()):
                continue_scan = True
        if(continue_scan == True):
            print('G???p continue word')
            continue

        ####################################
        if(check_classify_language == False):
            print('KH??NG X??? L?? PH??N LO???I NG??N NG??? - EN')
            
            tmp_split = split_sentence(tmp.replace('\n',''))
            for sen in tmp_split:
                en_nltk.append(sen)
            en.append(tmp.replace('\n',''))
            print('Duy???t')
        ####################################
        else:
            print('X??? L?? PH??N LO???I NG??N NG??? - EN')
            try:
                de  = detect(tmp.lower())
                cl = langid.classify(tmp.lower())[0]
                count_vi = 0
                count_en = 0
                if(de == 'vi' or cl == 'vi'):
                    count_vi += 1
                if(de == 'en' or cl == 'en'):
                    count_en += 1
                #------------------------------
                if(len(tmp.split(' ')) < 15):
                    lang = lang_classify(tmp, 'en')
                    if (lang == 'en'):
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            en_nltk.append(sen)
                        en.append(tmp.replace('\n',''))
                        print('Duy???t')
                elif (de == 'en' and  cl == 'en'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        en_nltk.append(sen)
                    en.append(tmp.replace('\n',''))
                    print('Duy???t')
                    print('th??m v??o en - kh??ng g???i h??m ph??n lo???i')
                elif (count_vi == count_en):
                    lang = lang_classify(tmp, 'en')
                    print('lang: ', lang)
                    if (lang == 'en'):
                        print('th??m v??o en')
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            en_nltk.append(sen)
                        en.append(tmp.replace('\n',''))
                        print('Duy???t')
                elif (de != 'vi' or  cl != 'vi'):
                    lang = lang_classify(tmp, 'en')
                    print('lang: ', lang)
                    if (lang == 'en'):
                        print('th??m v??o en')
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            en_nltk.append(sen)
                        en.append(tmp.replace('\n',''))
                        print('Duy???t')
                else:
                    print('Cho qua')
                ############
                print('EN:', len(en))
            except:
                print('EN:', len(en))
                print('D??nh l???i ?????nh danh')
        print('EN: ', len(en))

    print('============== X??? L?? TI???NG VI???T ================')
    print(len(vi_content_tags))
    for sentence in vi_content_tags:
        tmp = sentence
        try:
            tmp = sentence.text_content()
        except:
            pass
        print()
        print('G???p: ', tmp.replace('\n',''))
        if (tmp == ''):
            print('continue')
            continue

        if (check_remove_duplicate_content == True and tmp.replace('\n','') in vi):
            print('continue')
            continue
        
        break_scan = False
        continue_scan = False
        for i in break_word:     
            if(i in tmp.upper()):
                break_scan = True
        if(break_scan == True):
            print('G???p break word')
            break
        for i in continue_word:     
            if(i in tmp.upper()):
                continue_scan = True
        if(continue_scan == True):
            print('G???p continue word')
            continue

        ####################################
        if(check_classify_language == False):
            print('KH??NG X??? L?? PH??N LO???I NG??N NG??? - VI')
    
            tmp_split = split_sentence(tmp.replace('\n',''))
            for sen in tmp_split:
                vi_nltk.append(sen)
            vi.append(tmp.replace('\n',''))
            print('Duy???t')
        ####################################
        else:
            print('X??? L?? PH??N LO???I NG??N NG??? - VI')
            try:
                de  = detect(tmp.lower())
                cl = langid.classify(tmp.lower())[0]
                count_vi = 0
                count_en = 0
                if(de == 'vi' or cl == 'vi'):
                    count_vi += 1
                if(de == 'en' or cl == 'en'):
                    count_en += 1
                #------------------------------
                if(len(tmp.split(' ')) < 15):
                    lang = lang_classify(tmp, 'vi')
                    if (lang == 'vi'):
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            vi_nltk.append(sen)
                        vi.append(tmp.replace('\n',''))
                        print('Duy???t')
                elif (de == 'vi' and  cl == 'vi'):
                    tmp_split = split_sentence(tmp.replace('\n',''))
                    for sen in tmp_split:
                        vi_nltk.append(sen)
                    vi.append(tmp.replace('\n',''))
                    print('Duy???t')
                elif (count_vi == count_en):
                    lang = lang_classify(tmp, 'vi')
                    if (lang == 'vi'):
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            vi_nltk.append(sen)
                        vi.append(tmp.replace('\n',''))
                        print('Duy???t')
                elif (de != 'en' or  cl != 'en'):
                    lang = lang_classify(tmp, 'vi')
                    if (lang == 'vi'):
                        tmp_split = split_sentence(tmp.replace('\n',''))
                        for sen in tmp_split:
                            vi_nltk.append(sen)
                        vi.append(tmp.replace('\n',''))
                        print('Duy???t')
                else:
                    print('cho qua')
                ############
                print('VI:', len(vi))
            except:
                print('VI:', len(vi))
                print('D??nh l???i ?????nh danh')
        print('VI: ', len(vi))

    '''if(len(en_nltk) == len(vi_nltk)):
        vi_nltk = list(dict.fromkeys(vi_nltk))
        en_nltk = list(dict.fromkeys(en_nltk))'''
        
    min_nltk = len(vi_nltk)
    if(min_nltk > len(en_nltk)):
        min_nltk = len(en_nltk)
        vi_nltk = vi_nltk[:min_nltk]
    else:
        en_nltk = en_nltk[:min_nltk]
    ######################
    # X??? L?? C???T C??U
    if(len(vi_nltk) == 1 and len(en_nltk) == 1):
        print('X??? L?? C???T C??U')
        vi_nltk = split_sentence(vi_nltk[0])
        en_nltk = split_sentence(en_nltk[0])
        if(len(vi) != len(en)):
            nl_vi, nl_en = normalize_sentence(vi, en)
            if(len(nl_vi) == len(nl_en)):
                vi_nltk = nl_vi
                en_nltk = nl_en
    ######################
    check_valid = False
    print('??ang trong h??m collect')
    for l in range(len(vi_nltk)):
        len_vi = len(vi_nltk[l].split(' '))
        len_en = len(en_nltk[l].split(' '))
        '''print('check_len_vi: ', len_vi)
        print('check_len_en: ', len_en)'''
        if(len_vi < 0.35*len_en or len_en < 0.35*len_vi):
            #print('KH??NG CH??NH X??C - CONTINUE')
            check_valid = True
            break
    if(check_valid == False):
        #print('KH??NG CH??NH X??C - CONTINUE')
        return title, vi_nltk, en_nltk
    #else:
    if (check_remove_duplicate_content == True):
        vi = list(dict.fromkeys(vi))
        en = list(dict.fromkeys(en))
    
    print(len(vi))
    print(len(en))

    ######################
    # X??? L?? C???T C??U
    if(len(vi) == 1 and len(en) == 1):
        print('X??? L?? C???T C??U')
        vi = split_sentence(vi[0])
        en = split_sentence(en[0])
        if(len(vi) != len(en)):
            nl_vi, nl_en = normalize_sentence(vi, en)
            if(len(nl_vi) == len(nl_en)):
                vi = nl_vi
                en = nl_en
    ######################
    min = len(vi)
    if(min > len(en)):
        min = len(en)
        vi = vi[:min]
    else:
        en = en[:min]

    '''print('TITLE: ', title)
    print('EN: ', en)
    print('VI: ', vi)'''
    return title, vi, en

# H???m n??y d??ng ????? ph??n c??u cho m???t ??o???n
def split_sentence(text):
    sent_text = nltk.sent_tokenize(text)
    return sent_text

# H??m n??y s??? 'c??? g???ng' s???a l???i chia subtitle theo c??u kh??ng ?????ng nh???t
# V?? trong th???c t??? vi???c d???ch thu???t kh??ng ?????ng nh???t gi???a nh???ng ng?????i d???ch d???n ?????n vi???c d??? li???u kh??ng kh???p nhau v??? c??ch chia c??u
# V?? d???: 1 c??u ??? Ti???ng Anh. L???i ???????c d???ch nhi???u c??u ??? Ti???ng vi???t v?? ng?????c l???i
def normalize_sentence(doc1, doc2):
    length1 = 0
    length2 = 0
    min = 0
    max = 0
    i = 0
    while(i < len(doc1) and i < len(doc2)):
        if (len(doc1) == len(doc2)):
            break
        doc1[i] = doc1[i].replace('  ',' ')
        doc2[i] = doc2[i].replace('  ',' ')
        length1 = len(doc1[i].split(' '))
        length2 = len(doc2[i].split(' '))
        #print(length1, ':', doc1[i])
        
        #print(length2, ':', doc2[i])
        max = length1
        min = length2
        if(length1 < length2):
            max = length2
            min = length1
        error = float(min/max)
        #print(error)
        if (error <= 65):
            #print(doc1[i])
            #print(doc2[i])
            #print('trung error:[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]')
            try:
                if(length1 < length2 and i < len(doc1)-1):
                    doc1[i] = doc1[i] + ' ' + doc1[i+1]
                    del doc1[i+1]
                    i+=1
                if(length1 > length2 and i < len(doc2)-1):
                    doc2[i] = doc2[i] + doc2[i+1]
                    del doc2[i+1]
                    i+=1
            except:
                break
        #print('=====================================================================')
        i+=1
    return doc1, doc2

# H??m n??y d??ng ????? ph??n lo???i ng??n ng??? theo th??nh ph???n ch??? c??i
def lang_classify(text, lang):
    text = text.lower()
    print('vao ham: ', text)
    if(lang == 'vi'):
        other_lang = 'en'
    elif(lang == 'en'):
        other_lang = 'vi'
    count_lang = 0
    count_other_lang = 0
    for i in text.split(' '):
        try:
            de = detect(i)
            cl = langid.classify(i)[0]
            if(de == lang or cl == lang):
                count_lang += 1
            if(de == other_lang or cl == other_lang):
                count_other_lang += 1
        except:
            continue
    count_word  = len(text.split(' '))

    if(count_other_lang <= count_lang):
        print('Duy???t x??? l?? th??? c???p: ', text.replace('\n',''))
        return lang
    else:
        print("Cho qua")
        return other_lang


def highlight_search(text, search):
    insensitive = re.compile(re.escape(search), re.IGNORECASE)
    dem = 1
    list_group = []
    while(len(re.findall(search, text, re.IGNORECASE)) > 0):
        print('lan: ',dem)
        y = re.search(search, text, re.IGNORECASE)
        print(y.group(), y.span())
        list_group.append(y.group())
        text = insensitive.sub('<span class="highlight">{}</span>'.format('/&*replace*&/'), text, 1)
        #print(x)
        dem+=1
    print(list_group)
    insensitive = re.compile(re.escape('/&*replace*&/'), re.IGNORECASE)
    for i in list_group:
        text = insensitive.sub(i, text, 1)
    return text


