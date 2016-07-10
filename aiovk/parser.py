import html.parser
import urllib.parse


class AuthPageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.url = ''
        self.message = ''
        self.recording = 0
        self.captcha_url = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            attrs = dict(attrs)
            if attrs['type'] != 'submit':
                self.inputs.append((attrs['name'], attrs.get('value', '')))
        elif tag == 'form':
            for name, value in attrs:
                if name == 'action':
                    self.url = value
        elif tag == 'img':
            attrs = dict(attrs)
            if attrs.get('id', '') == 'captcha':
                self.captcha_url = attrs['src']
        elif tag == 'div':
            attrs = dict(attrs)
            if attrs.get('class', '') == 'service_msg service_msg_warning':
                self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'div':
            self.recording = 0

    def handle_data(self, data):
        if self.recording:
            self.message = data


class TwoFactorCodePageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.url = ''
        self.message = ''
        self.recording = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            attrs = dict(attrs)
            if attrs['type'] != 'submit':
                self.inputs.append((attrs['name'], attrs.get('value', '')))
        elif tag == 'form':
            for name, value in attrs:
                if name == 'action':
                    self.url = urllib.parse.urljoin('https://m.vk.com/', value)
        elif tag == 'div':
            attrs = dict(attrs)
            if attrs.get('class', '') == 'service_msg service_msg_warning':
                self.recording = 1

    def handle_endtag(self, tag):
        if tag == 'div':
            self.recording = 0

    def handle_data(self, data):
        if self.recording:
            self.message += data


class AccessPageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []
        self.url = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            attrs = dict(attrs)
            if attrs['type'] != 'submit':
                self.inputs.append((attrs['name'], attrs.get('value', '')))
        elif tag == 'form':
            for name, value in attrs:
                if name == 'action':
                    self.url = value
