import logging.config
import logging.handlers
import time

import DBUtils
import extractUtils

logging.config.fileConfig('ExtractLog.conf')
logger = logging.getLogger('PcapExtractEngine')


if __name__ == '__main__':

    logger.debug("PcapExtract Engine Start...")

    while True:
        db_connection = DBUtils.get_db_connection()
        pcapFileDict = DBUtils.get_unextracted_pcaps()
        if len(pcapFileDict) > 0:
            logger.debug(pcapFileDict)
            logger.debug("pcapFileDict size: %s" % len(pcapFileDict))
            for captureLog in pcapFileDict:
                try:
                    extractUtils.extractHTTPMetadata(captureLog, db_connection)
                    #logger.debug("updating capture log flag, logID: %s" % captureLog["logID"])
                    DBUtils.updateCaptureLogFlag(captureLog["logID"])
                except Exception as e:
                    logger.error("extract error! logID %s" % captureLog["logID"])
                    logger.error(e)
                    continue

        else:
            db_connection.close()
            logger.debug("no pcap file need extract, waiting for next time...")
            time.sleep(60)
