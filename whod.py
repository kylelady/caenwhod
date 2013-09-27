#!/usr/bin/env python2.7

from fabric.api import env, execute, run
import getpass
import json
import logging
import sys

import jsocket

logger = logging.getLogger('caenwhod')
logger.setLevel(logging.INFO)

caen_hosts = ['caen-vnc%02d.engin.umich.edu' % n for n in range(1, 9)]

users = set()

def get_users():
    results = run('''who | awk '{print $1}' ''')
    for user in results.split():
        if user != '':
            users.add(user)


class CAENWhoDaemon(jsocket.ThreadedServer):
    def __init__(self):
        super(CAENWhoDaemon, self).__init__()
        self.timeout = 2.0

    def _process_message(self, obj):
        if obj != '':
            if obj['message'] == 'query caenlogin':
                logger.info('new connection.')
                users = set()
                execute(get_users, hosts=caen_hosts)
                logger.info('users obtained')
                self.send_obj(json.dumps(list(users)))
                logger.info('users sent')


if __name__ == '__main__':
    env.password = getpass.getpass()
    execute(get_users, hosts=caen_hosts)

    print '*********** Users'
    print users

    server = CAENWhoDaemon()
    logger.info('starting...')
    server.start()
    logger.info('started!')

    server.join()
