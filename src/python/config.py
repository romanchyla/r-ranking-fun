


# End of the configuration; below is code that updates the current
# config based on the environmental variables. This is the mechanism
# used for communication of settings between Java<->Python

_ID = 'RANKFUN'

import sys 
import os 

def update_values():
    '''We'll check all MONTYSOLR variables for their counterparts in
    the environment and update the config if they are found. Note, that 
    doing this, we include even variables that are not defined in
    config
    '''
    main = sys.modules[__name__]
    for var in dir(main):
        if _ID in var:
            if os.getenv(var, None):
                val = os.getenv(var) # always a string
                if ',' in val:
                    val = val.split(',')
                elif val.lower() == 'true':
                    val = True
                elif val.lower() == 'false':
                    val = False
                    
                setattr(main, var, val)
                
update_values()

#sys.stderr.write("\n".join([str(sys.path), 'prefix', sys.prefix, 'executable', sys.executable, 'exec_prefix', sys.exec_prefix]))

import logging 

logging_level = logging.DEBUG
log = None
_loggers = []

def get_logger(name):
    """Creates a logger for you - with the parent logger and
    common configuration"""
    if name[0:4] != 'rfun' and len(name) > 4:
        sys.stderr.write("Warning: you are creating a logger without 'rfun' as a root (%s),"
        "this means that it will not share montysolr settings and cannot be administered from one place" % name)
    if log:
        logger = log.manager.getLogger(name)
    else:
        logger = logging.getLogger(name)
        hdlr = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s:%(lineno)d    %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging_level)
        logger.propagate = 0
    if logger not in _loggers:
        _loggers.append(logger)
    return logger