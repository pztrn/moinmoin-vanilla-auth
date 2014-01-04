#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# MoiVan - MoinMoin and Vanilla SSO.
# Copyright (c) 2014, Stanislav N. aka pztrn.

# Dependencies:
#   * pyphpass (https://github.com/exavolt/python-phpass)

import sys

# phpass directory path
phpass_path = "/data/TEMP/moivan/phpass"
if not phpass_path in sys.path:
    sys.path.insert(0, phpass_path)

import phpass

from MoinMoin import user
from MoinMoin.auth import MoinAuth, ContinueLogin
from MoinMoin import log
logging = log.getLogger(__name__)


class MoivanAuth(MoinAuth):
    name = 'moin'
    
    def __init__(self, dbconfig = None, autocreate = False):
        MoinAuth.__init__(self)
        
        self.dbconfig = dbconfig
        self.autocreate = autocreate
        
        self.phpass = phpass.PasswordHash()
        
    def login_hint(self, request):
        _ = request.getText
        # Password recover and new account creation is DISABLED!
        return _('New account creation and password restoring disabled, use <a href="http://games.pztrn.name/">our forum</a>.')
        
    def login(self, request, user_obj, **kw):
        username = kw.get('username')
        password = kw.get('password')
        
        if self.dbconfig is None:
            logging.exception("Please configure this authentication agent (mysql config missing)")
            return None, None, None
            
        try:
            import MySQLdb
        except:
            logging.exception("Failed to import MySQL connector!")
            return None, None, None
            
        try:
            db = MySQLdb.connect(host=self.dbconfig['host'], user=self.dbconfig['user'],
                passwd=self.dbconfig['passwd'], db=self.dbconfig['dbname'])
        except:        
            logging.exception("authorization failed due to exception when connecting to DB, traceback follows...")
            return None, None, None
            
        # Okay, let's start!
        query = """SELECT
                        Password, Name, Email
                FROM
                    GDN_User
                WHERE
                    GDN_User.Name = '%s';
        """ % username
        logging.debug("Executing query: " + query)
        c = db.cursor(MySQLdb.cursors.DictCursor)
        c.execute(query)
        vanilla_data = c.fetchone()
        # Hashed password is here. Compare it.
        valid = self.phpass.check_password(password, vanilla_data["Password"])
        logging.debug("Valid state: " + str(valid))
        if valid:
            u = user.User(request, name=vanilla_data["Name"], auth_username=vanilla_data["Name"],
                          auth_method=self.name)

            changed = False
            if u.aliasname != vanilla_data["Name"]:
                u.aliasname = vanilla_data["Name"]
                changed = True
            if u.email != vanilla_data["Email"]:
                u.email = vanilla_data["Email"]
                changed = True
                
            if u and self.autocreate:
                u.create_or_update(changed)
            if u and u.valid:
                return ContinueLogin(u) # True to get other methods called, too
            else:
                logging.debug("%s: could not authenticate user %r (not valid)" % (self.name, username))
                return ContinueLogin(user_obj, _("Invalid username or password."))
        return user_obj, True # continue with next method in auth list
