# _*_ coding:utf-8 _*_
# author:@shenyi
import os
import re
import traceback
from selenium import webdriver


class PyFilter:

    def __init__(self):
        self.curpath = os.path.dirname(os.path.realpath(__file__))
        self.filehandler = open('apimethod.md', 'w')
        self.log = open('errlog.log', 'w')
        self.driver = webdriver.PhantomJS('phantomjs.exe')
        self.driver.implicitly_wait(30)

    def hasfile(self, rsion_path, suffix):
        for files in os.walk(rsion_path.decode('utf-8')):
            for i in files:
                if isinstance(i, list):
                    for j in i:
                        ret = j.split('.')
                        if len(ret) > 1 and ret[1] in suffix:
                            return True

    def getAPIdoc(self, pypath):
        pycontent = open(pypath.decode('utf-8')).read()
        func_apidoc = re.findall(r'.*[def|class]\s.+\n.+"""([\s\S]*?)"""', pycontent)
        func_name = re.findall(r'[def|class]\s?[\s\S].*\)', pycontent)
        cn_content = []
        if func_apidoc:
            try:
                for i in zip(func_name, func_apidoc):  # 每个方法一个循环
                    slice = self.transByPh(i[1])
                    cn_content.append('* *' + i[0] + '*')  # markdown:* *方法名*
                    cn_content.append('-'*4)
                    cn_content.append(slice)
                    cn_content.append('-'*4)
            except Exception as e:
                print e
                self.filehandler.write('--- phantomjs or regex err for getAPIdoc method ---\r\n')
                self.filehandler.flush()
        return cn_content

    def transByPh(self, content):  # 使用phantomJS
        self.driver.get('https://translate.google.cn/')
        self.driver.find_element_by_xpath('//div[@id="gt-src-wrap"]//textarea[@id="source"]').send_keys(content.decode('utf-8'))
        trans_node = self.driver.find_element_by_xpath('//div[@id="gt-res-c"]//span[@id="result_box"]/span')
        return trans_node.find_element_by_xpath('..//..').text

    def transByAPI(self, content):
        pass

    def rsionpath(self):
        toppath = os.path.split(os.path.realpath(self.curpath))[1]
        self.filehandler.write(toppath)
        self.filehandler.write('\n')
        self.filehandler.write('='*4)
        self.filehandler.write('\n')
        self.filehandler.flush()
        try:
            for files in os.walk(self.curpath.decode('utf-8')):
                for filename in files:
                    if not isinstance(filename, list):  # 判断为目录
                        dirname = filename.encode('utf-8')
                        # print filename
                        # TODO 在当前目录下再递归一次，如果该目录下没有符合的文件，则继续递归，之后改成一次性递归加判断
                        if self.hasfile(dirname, '.py'):
                            indent_wide = '\t' * (len(os.path.split(dirname)[0].split('\\')) - 2)
                            indent_wide_md = '#' * (len(os.path.split(dirname)[0].split('\\')))
                            print indent_wide,
                            print '[ {} ]'.format(os.path.split(dirname)[1])
                            # self.filehandler.write('<i class="icon-folder-open"></i> ')  # notepad++ markdown预览器不支持这段
                            self.filehandler.write(indent_wide_md)
                            self.filehandler.write(' [ {} ]'.format(os.path.split(dirname)[1]))
                            self.filehandler.write('\r\n')
                            self.filehandler.flush()
                        # print indent_wide + '|\n' + 'filename'
                    else:
                        for i in filename:
                            i = i.encode('utf-8')
                            if i.endswith('.py'):
                                print indent_wide,
                                print '\000'*4 + i
                                ret1 = self.getAPIdoc(dirname + '\\' + i)
                                self.filehandler.write(i)  # py文件名
                                self.filehandler.write('\n')
                                for j in ret1:
                                    print j.encode('gbk', 'ignore')
                                    # self.filehandler.write('> ' + j.encode('utf-8'))
                                    self.filehandler.write(j.encode('utf-8'))
                                    self.filehandler.write('\r\n')
                                    self.filehandler.flush()
                                self.filehandler.flush()
        except Exception as e:
            print e
            print traceback.format_exc()
            self.log.write('Err:{}'.format(e))
            self.log.write('Err:{}'.format(traceback.format_exc()))
            self.log.flush()
        finally:
            self.closeFiles()
            self.log.close()
            self.closeDriver()

    def closeFiles(self):
        self.filehandler.close()

    def closeDriver(self):
        self.driver.close()
        self.driver.quit()


def checkPhan():
    if 'phantomjs.exe' not in os.listdir('.'):
        raise RuntimeError('The current directory does not exist phantomjs.exe')


if __name__ == '__main__':
    checkPhan()
    p = PyFilter()
    p.rsionpath()
    print 'input ENTER close current window'
    raw_input(unicode('按回车键退出...', 'utf-8').encode('gbk'))

