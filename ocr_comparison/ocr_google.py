#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argparse
import re
import requests
import base64
import os
import sys

__all__ = []

MAX_RETRY_COUNT = 10
goolge_vision_url = 'https://vision.googleapis.com/v1/images:annotate?key={key}'


def do_ocr_request(image_path, key):
    try:
        dataBin = open(image_path, "rb").read()
    except:
        print("Can't load image ", image_path)
        return None
    curData = {
        "requests":
            [{
                "image": {
                    "content": base64.b64encode(dataBin)
                },
                "features": [{
                    "type": "TEXT_DETECTION"
                }],
                "imageContext":{
                    "languageHints": ['en', 'ru']
                }
            }]
    }
    try:
        ocr_result = requests.post(goolge_vision_url.format(key=key), data=json.dumps(curData), verify=False)
    except Exception as ex:
        print ("Exception during request! {}".format(str(ex)))
        return None
    if ocr_result.status_code != 200:
        print ("Daemon return code {}".format(ocr_result.status_code))
        print (ocr_result.content)
        return None
    else:
        return json.loads(ocr_result.content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extracting Google Vision API OCR result.'
    )
    parser.add_argument(
        '--in_folder', '-i',
        default=None,
        required=True,
        help='Input folder')
    parser.add_argument(
        '--out_folder', '-o',
        default=None,
        required=True,
        help='Output folder')
    parser.add_argument(
        '--key',
        default=None,
        required=True,
        help='Api key')

    args = parser.parse_args()

    infolder = args.in_folder
    outfolder = args.out_folder
    key = args.key

    for root, _, files in os.walk(infolder):
        for file_ in files:
            if not re.match(".*(\.jpg|\.JPG|\.jpeg|\.JPEG|\.png|\.PNG)", file_):
                continue
            image_path = os.path.join(root, file_)
            rel_image_path = os.path.relpath(image_path, infolder)
            rel_base_path = rel_image_path[:rel_image_path.rfind('.')]
            result_path = os.path.join(outfolder, "res_" + rel_base_path + ".txt")
            if not os.path.exists(os.path.dirname(result_path)):
                os.makedirs(os.path.dirname(result_path))
            retry_count = 0
            ocr_responce = do_ocr_request(image_path, key)
            while retry_count < MAX_RETRY_COUNT and not ocr_responce:
                retry_count += 1
                ocr_responce = do_ocr_request(image_path, key)
            if retry_count == MAX_RETRY_COUNT:
                print ("ERROR: Max request count is reached! Failing...")
                sys.exit(1)
            with open(result_path, 'w') as f_out:
                assert(len(ocr_responce["responses"]) <= 1)
                if "textAnnotations" in ocr_responce["responses"][0] and not len(ocr_responce["responses"][0]["textAnnotations"]) == 0:
                    ocr_responce = ocr_responce["responses"][0]["textAnnotations"]
                    for region in ocr_responce[1:]: # 0-th element is whole image annotation, others - single words annotations
                        vertices = region["boundingPoly"]["vertices"]
                        x_all = [v["x"] for v in vertices if "x" in v]
                        y_all = [v["y"] for v in vertices if "y" in v]
                        if len(x_all) > 0:
                            minx = min(x_all)
                            maxx = max(x_all)
                        else:
                            minx = 0
                            maxx = 0
                        if len(y_all) > 0:
                            miny = min(y_all)
                            maxy = max(y_all)
                        else:
                            miny = 0
                            maxy = 0
                        x1 = max(0, int(minx))
                        y1 = max(0, int(miny))
                        x2 = max(x1 + 1, int(maxx))
                        y2 = max(y1 + 1, int(maxy))
                        recognition = region["description"].encode("utf8")
                        f_out.write("{},{},{},{},{},{},{},{},{}\n".format(x1,y1,x2,y1,x2,y2,x1,y2, recognition))
