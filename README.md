# Vanilla Forums authorization source for MoinMoin

This authorization method will allow you to use as source Vanilla Forums (version 2) database.

## Dependencies

*  Python2 MySQL connector (MySQLdb)

# Usage

Put contents of ``moivan`` directory into ``MOIN_ROOT/MoinMoin/auth/`` , and in add this in ``wikiconfig.py``:

```python

    dbconfig=dict(host = 'hostname',
                user = 'username',
                passwd = 'pass',
                dbname = 'dbname'
                )
                
    from MoinMoin.auth.moivan import MoivanAuth
    auth = [MoivanAuth(dbconfig = dbconfig, autocreate = True)]
    
    actions_excluded = multiconfig.DefaultConfig.actions_excluded + ['newaccount']
```

``actions_excluded`` is required, because all user management will go thru Vanilla Forums.

# Credits

Authorization code: @pztrn

phpass python library: @exavolt (https://github.com/exavolt/python-phpass)
