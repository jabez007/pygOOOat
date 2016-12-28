import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from getpass import getuser


# Take this class for granted. Just use result of rendering.
class Render(QWebPage):
    """
    https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
    +
    http://stackoverflow.com/questions/5356948/scraping-javascript-driven-web-pages-with-pyqt4-how-to-access-pages-that-need?rq=1
    """

    def __init__(self, url, password):
        self.app = QApplication(sys.argv)

        QWebPage.__init__(self)
        self.loadFinished.connect(self._loadFinished)

        page = QUrl(url)
        page.setUserName(getuser())
        page.setPassword(QString(password))

        self.mainFrame().load(page)
        self.app.exec_()

    def _loadFinished(self, result):
        self.frame = self.mainFrame()
        self.app.quit()

    def get_html(self):
        result = self.frame.toHtml()
        return str(result.toAscii())

# # # #


if __name__ == "__main__":
    from getpass import getpass

    password = getpass()
    r = Render('http://guru',
               password)
    print(r.get_html())
