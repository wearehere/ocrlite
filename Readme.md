
# Readme

## 1. Brief

It is not convient that most experimental OCR libraries have a error, until I find some good projects as follows:



* https://github.com/hiroi-sora/Umi-OCR It provice will established UI, have pdf reconstruction, and use RapidAI as basement with a pretty well effect. But it does not support command line operation, and it uses C/S architecture, which is not suitable for automated processing.
* https://github.com/PaddlePaddle/PaddleOCR Wonderful OCR engine
* https://github.com/RapidAI/RapidOCR　 Optimize PaddleOCR




## 2. Project

Make a command line tool with reference to Umi-OCR, and add a option to get tagged picture with text for other purpose. It use following important python libraries

```sh
pip3 install --upgrade pymupdf
pip3 install --upgrade Pillow
pip3 install rapidocr_onnxruntime
```

the models carried with rapidocr_onnxruntime installation are

* ch_ppocr_mobile_v2.0_cls_infer.onnx
* ch_PP-OCRv4_rec_infer.onnx
* ch_PP-OCRv4_det_infer.onnx



### 2.1 key data structure

result

```json
{
    "code":100,
    "page":"",
    "fileName":"",
    "path":"",
    "time":0,
    "timestamp":12121,
    "score":0.99273,
    "data":[{
        "text":"ABCD",
        "score":019281,
        "box":[(x1,y1),(x2,y2),(x3,y3),(x4,y4)],
        "from"=["text"|"ocr"]]
    }]
}
```





## 3. Usage

```sh
usage: main.py [-h] --input INPUT [--inputpassword INPUTPASSWORD] [--outputdir OUTPUTDIR] [--output_pdf] [--output_imgtxt] [--output_json] [--output_csv] [--debug]
```

* --input source pdf file
* --inputpassword password of pdf if required
* --output output directory for files
* --output_pdf flag, to output pdf with embbed text
* --output_imgtxt　flag, to out the image-text pair which may used for future paddle traning
* --output_json flag, to output json format
* --debug flag, show debug information



## 4. Swedish

Swedish is a subset of Latin, so it can be treated as Latin.

```sh
pip install paddleocr_convert
paddleocr_convert -p \
	https://paddleocr.bj.bcebos.com/PP-OCRv3/multilingual/latin_PP-OCRv3_rec_infer.tar \
	-o models \
	-txt_path \
	https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/release/2.6/ppocr/utils/dict/latin_dict.txt
cp models/latin_PP-OCRv3_rec_infer/latin_PP-OCRv3_rec_infer.onnx \
	python3.10/site-packages/rapidocr_onnxruntime/models
```

make modification for rapidocr_onnxruntime's config.yaml

```
.....
Rec:
    intra_op_num_threads: *intra_nums
    inter_op_num_threads: *inter_nums

    use_cuda: false

    model_path: models/latin_PP-OCRv3_rec_infer.onnx

    rec_img_shape: [3, 48, 320]
    rec_batch_num: 6
......
```
