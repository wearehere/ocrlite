

import fitz  # PyMuPDF
import logging
from PIL import Image
from io import BytesIO

class FitzFile:

    @staticmethod
    def get_doc_metainfo(path):
        f = FitzFile(path)
        if f.open():
            mtinfo = f.get_metainfo()
            f.close()
            return mtinfo
        return None

    '''
        FitzFile is a wrapper for fitz.Document
        minsize: # 最小渲染分辨率
    '''
    def __init__(self,path, password=""):
        self._path = path
        # self._minsize = minsize
        self._password = password
        self._doc = None
        self._authenticate = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        try:
            self._doc = fitz.open(self._path)
        except Exception as e:
            logging.debug(f"[FitzFile.open]Error open file {self._path} {e}")
            return False
        if self._doc:
            if self._doc.is_encrypted and not self._doc.authenticate(self._password):
                self._authenticate = False
            else:
                self._authenticate = True
        return True

    def close(self):
        if(self._doc):
            self._doc.close()

    def get_metainfo(self):
        if not self._doc:
            return None
        return {
            "encrypted":self._doc.is_encrypted,
            "authenticate":self._authenticate,
            "pagecount":self._doc.page_count,
        }

    def get_img_fullpage(self, pageno = 0, minsize = 1080):
        if pageno < 0 or pageno >= self._doc.page_count:
            logging.debug(f"[get_imag_fullpage]Error page no {pageno}")
            return None
        page = self._doc[pageno]
        rect = page.rect
        w, h = abs(rect[2] - rect[0]), abs(rect[3] - rect[1])
        m = min(w, h)
        if m < minsize:
            zoom = minsize / max(m, 1)
            matrix = fitz.Matrix(zoom, zoom)
        else:
            zoom = 1
            matrix = fitz.Identity
        p = page.get_pixmap(matrix=matrix)
        bytes = p.tobytes("png")
        return {
            "bytes": bytes, "xy": (0,0), "scale": 1 / zoom,
            "bbox":rect
        }

    def get_blocks(self, pageno, txtflag = True, imgflag = True):
        if pageno < 0 or pageno >= self._doc.page_count:
            logging.debug(f"[get_imag_fullpage]Error page no {pageno}")
            return None
        page = self._doc[pageno]
        # 获取元素 https://pymupdf.readthedocs.io/en/latest/_images/img-textpage.png
        # 确保越界图像能被采集 https://github.com/pymupdf/PyMuPDF/issues/3171
        p = page.get_text("dict", clip=fitz.INFINITE_RECT())
        blocks = {"imgs":[], "txts":[]}
        for t in p["blocks"]:
            bbox = t["bbox"]
            if t["type"] == 0 and txtflag:
                for line in t["lines"]:
                    for span in line["spans"]:
                        b = span["bbox"]
                        size = span["size"]  # 字体大小
                        box = [
                            [b[0], b[1]],
                            [b[2], b[1]],
                            [
                                b[2],
                                b[1] + size,
                            ],  # 使用字体大小作为行高，而不是 b[3]
                            [b[0], b[1] + size],
                        ]
                        blocks["txts"].append({
                            "box": box,
                            "text": span["text"],
                            "score": 1,
                            "from": "text",  # 来源：直接提取文本
                            "bbox":span["bbox"]
                        })

            elif t["type"] == 1 and imgflag:
                # 图片视觉大小
                w1, h1 = bbox[2] - bbox[0], bbox[3] - bbox[1]
                # 图片实际大小
                with Image.open(BytesIO(t["image"])) as pimg:
                    w2, h2 = pimg.size
                scale = w1 / w2  # 图片缩放比例
                blocks["imgs"].append({
                    "bytes": t["image"], "xy": (bbox[0], bbox[1]), "scale": scale,
                    "bbox":t["bbox"]
                })
