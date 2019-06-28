import logging

def custom_logger(name):
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(name)-12s %(levelname)-8s %(message)s',
                        filename='log.txt',
                        filemode='a')

    formatter = logging.Formatter('[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    #logging.getLogger('').addHandler(console)
    logger = logging.getLogger(name).addHandler(console)
    return logger
        
