import os
from datetime import datetime
import json
from subprocess import call
from time import sleep
from tornado import ioloop
from tornado.httpclient import AsyncHTTPClient
import tornado.ioloop
import tornado.web

from helpers import now_in_interval
from logger import logger

logger.info('Running...')


class Config:
    host = 'http://192.168.1.150'
    static_path = os.path.join(os.path.dirname(__file__), "static")


class State:
    STATES = ['off', 'auto', 'on']

    new_mail = None
    beep = None
    beep_times = [
        None, None,
        None, None
    ]
    error = None
    valid_before = datetime.now()

    @classmethod
    def now_beep_enabled(cls):
        from1_s = cls.beep_times[0]
        to1_s = cls.beep_times[1]
        if from1_s and to1_s and not now_in_interval(from1_s, to1_s):
            from2_s = cls.beep_times[2]
            to2_s = cls.beep_times[3]
            logger.debug('Time control 1: ok')
            if from2_s and to2_s:
                if not now_in_interval(from2_s, to2_s):
                    logger.debug('Time control 2: ok')
                    return True
            else:
                return True
        logger.debug('Time control: disabled')
        return False

    @classmethod
    def as_dict(cls):
        return {
            'newMail': cls.new_mail,
            'beep': cls.beep,
            'beepTimes': cls.beep_times,
            'error': cls.error
        }

    @classmethod
    def restore(cls):
        f = open('state.json')
        try:
            l = f.readline()
            state = json.loads(l)
            cls.beep = state['beep']
            cls.beep_times = state['beepTimes']
        except Exception as e:
            logger.exception(e)
        finally:
            f.close()

    @classmethod
    def save(cls):
        f = open('state.json', 'w')
        try:
            l = json.dumps({
                'beep': cls.beep,
                'beepTimes': cls.beep_times
            })
            f.write(l)
        except Exception as e:
            logger.exception(e)
        finally:
            f.close()


class StaticFileHandler(tornado.web.StaticFileHandler):

    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

def request_new_mail_s(result):
    try:
        result = json.loads(result.body.decode())['result']
        name, code = result.split(':')
        code = int(code)
        if code == 0:
            State.new_mail = False
        elif code == 1:
            State.new_mail = True
    except Exception as e:
        State.error = str(datetime.now()) + ' ::: ' + str(e)

def request_new_mail():
    http_client = AsyncHTTPClient()
    try:
        url = Config.host + '/content'
        http_client.fetch(url,
                          request_new_mail_s,
                          connect_timeout=10)
    except Exception as e:
        logger.exception(e)
        State.error = str(datetime.now()) + ' ::: ' + str(e)


def unlock_mailbox(handler):
    http_client = AsyncHTTPClient()
    try:
        url = Config.host + '/unlock'
        http_client.fetch(url,
                          lambda x: handler.finish(200),
                          connect_timeout=10)
    except Exception as e:
        logger.exception(e)
        State.error = str(datetime.now()) + ' ::: ' + str(e)
        handler.finish(500)


def beep(times=20):
    for i in range(0, times):
        call('beep')
        sleep(0.5)


class DoorbellHandler(tornado.web.RequestHandler):

    def get(self):
        self.finish('ok')
        logger.info('Doorbell!')
        logger.debug('State: %s' % State.beep)
        if State.beep == 'on':
            beep()
        elif State.beep == 'auto':
            if State.now_beep_enabled():
                beep()


class StateHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish(json.dumps(State.as_dict()))

    def post(self):
        state = json.loads(self.request.body.decode())
        beep = state['beep']
        beep_times = state['beepTimes']
        State.beep = beep
        State.beep_times = beep_times
        State.save()

class UnlockHandler(tornado.web.RequestHandler):

    def get(self):
        unlock_mailbox(self)


class MainHandler(tornado.web.RequestHandler):
   def get(self):
        try:
            with open(os.path.join(Config.static_path, 'index.html')) as f:
                self.finish(f.read())
        except IOError as e:
            self.write("404: Not Found")


def make_app():
    return tornado.web.Application([
        (r"/db", DoorbellHandler),
        (r"/state", StateHandler),
        (r"/static/(.*)", StaticFileHandler, dict(path=Config.static_path)),
        (r"/unlock", UnlockHandler),
        (r"/", MainHandler)
    ])

ioloop.PeriodicCallback(callback=request_new_mail, callback_time=20 * 1000, io_loop=ioloop.IOLoop.instance()).start()

if __name__ == "__main__":
    app = make_app()
    app.listen(10001)
    tornado.ioloop.IOLoop.current().add_callback(State.restore)
    tornado.ioloop.IOLoop.current().add_callback(request_new_mail)
    tornado.ioloop.IOLoop.current().start()
