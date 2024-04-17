import sys
import logging
import argparse
import time
from umi.tag_pages.BatchDOC import BatchDOC

def main():
    parser = argparse.ArgumentParser(description='ocr files')
    parser.add_argument('--input', type=str, required=True, help='Path of input file, guess type by file suffix')
    parser.add_argument('--inputpassword', type=str, required=False, help='Input file password')
    parser.add_argument('--outputdir', type=str, required=False, help='Directory of output files')
    parser.add_argument('--output_pdf', action='store_true', required=False, help='save output to pdf')
    parser.add_argument('--output_imgtxt', action='store_true', required=False, help='save image/text pair for future traning')
    parser.add_argument('--output_json', action='store_true', required=False, help='save image/text pair for future traning')
    parser.add_argument('--output_csv', action='store_true', required=False, help='save image/text pair for future traning')
    parser.add_argument('--debug', action='store_true', required=False, help='output debug information')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    inputfiles = args.input.split(',')

    docs = BatchDOC.addDocs(inputfiles)
    logging.info(f'found valid docs :{len(docs)} docs')
    for docinfo in docs:
        logging.info(docinfo)

    # outputtype = args.output.split('.')[-1]

    batchdoc = BatchDOC()
    config = {
         "tbpu.ignoreArea":[],
         "tbpu.ignoreRangeStart":-1,
         "tbpu.ignoreRangeEnd":-1,
         "mission.dirType":"source",
         "mission.datetimeFormat":"%Y%m%d%H%M%S",
         "mission.ingoreBlank":True,
         "mission.fileNameFormat":"%name-%date",
        #  "mission.filesType.pdfLayered":True,
         "mission.filesType.imgtext":True,
         "doc.extractionMode":"fullPage"
         }
    ## imageOnly fullPage

    ## read the source of output/__init__.py
    if args.output_pdf:
        config["mission.filesType.pdfLayered"] = True

    if args.output_imgtxt:
        config["mission.filesType.imgtext"] = True

    if args.output_json:
        config["mission.filesType.jsonl"] = True

    if args.output_csv:
        config["mission.filesType.OutputCsv"] = True

    if args.outputdir:
        config["mission.dirType"] = "target"
        config["mission.dir"] = args.outputdir

    for docinfo in docs:
        docinfo["range_start"] = 1
        docinfo["range_end"] = docinfo["page_count"]
        docinfo["password"] = ""
        if args.inputpassword:
            docinfo["password"] = args.inputpassword

    batchdoc.msnDocs(docs, config)  ## add doc and start parse.
    # batchdoc.msnStart()
    while(True):
        time.sleep(1)
        if(batchdoc.taskRemain() == 0):
            break


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    # sys.argv = ['',
    #             '--input', '../result/CCF_001021.pdf',
    #             '--outputdir', '../result',
    #             '--output_imgtxt']
    main()
