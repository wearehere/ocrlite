'''

https://github.com/Mushroomcat9998/PaddleOCR/blob/main/doc/doc_ch/recognition.md

根据识别情况输出标准格式的图像文件和标注信息，需要进行人工修正

directory as:
--sourcefilename
   |- rec_gt_train.txt
   |- train
        |- img1.jpg
        |- img2.jpg

txt文件格式为

" 图像文件名                 图像标注信息 "

train_data/rec/train/word_001.jpg   简单可依赖
train_data/rec/train/word_002.jpg   用科技让复杂的世界更简单
...


'''

import os, logging
import io, time
from PIL import Image
from .output import Output
from ...utils.fitzfile import FitzFile

class OutputImgTxt(Output):
    def __init__(self, argd):
        self.dir = argd["outputDir"]  # 输出路径（文件夹）
        self.originPath = argd["originPath"]  # 原始文件路径
        self.fileName = argd["outputFileName"]  # 文件名

    def printOut(self, res):  # 输出图片结果
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        traindir = self.dir + "/train"
        if not os.path.exists(traindir):
            os.mkdir(traindir)

        doc = FitzFile(self.originPath)
        if not doc.open():
            logging.debug(f"OutputImgTxt {self.originPath} open failed")
            return

        dt = time.strftime(  # 日期时间字符串（标准格式）
            r"%Y%m%d%H%M%S", time.localtime(time.time())
        )

        imginfo = doc.get_img_fullpage()
        scale = imginfo["scale"]
        img = Image.open(io.BytesIO(imginfo["bytes"]))
        tagfile = open(f"{self.dir}/{dt}_rec_gt_train.txt", "w", encoding="utf-8")
        index = 0
        for tb in res["data"]:
            if "from" in tb and tb["from"] == "text":
                continue  # 跳过直接提取的文本，只写入OCR文本
            imgfn = f"{dt}_{index}.png"
            line = f"{imgfn}  {tb['text']}\n"
            tagfile.write(line)

            box = tb["box"]
            imgrect = [box[0][0],box[0][1],box[2][0],box[2][1]]
            ## multiply imgrect with scale
            imgrect = [int(x / scale) for x in imgrect]
            cropped_img = img.crop(imgrect)
            cropped_img.save(traindir + "/" + imgfn)
            index += 1
        tagfile.close()
        doc.close()
