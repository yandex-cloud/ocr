#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import argparse
import base64
import re
import requests
import sys

__all__ = []

MAX_RETRY_COUNT = 10
url = "https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze"


def do_ocr_request(image_path, key):
    try:
        dataBin = open(image_path, "rb").read()
    except:
        print("Can't load image ", image_path)
        return None
    curData = {
        "analyze_specs": [{
            "content": base64.b64encode(dataBin),
            "features": [{
                "type": "TEXT_DETECTION",
                "text_detection_config": {
                    "language_codes": ["en", "ru"]
                }
            }]
        }]
    }
    try:
        ocr_result = requests.post(url, data=json.dumps(curData), headers={"Authorization": "Api-Key {}".format(key)}, verify=False)
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
        description='Extracting Yandex.Vision OCR result.'
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
                assert(len(ocr_responce["results"]) == 1)
                assert(len(ocr_responce["results"][0]['results'][0]) == 1)
                for page in ocr_responce["results"][0]['results'][0]['textDetection']['pages']:
                    if 'blocks' not in page:
                        continue
                    for block in page["blocks"]:
                        if 'lines' not in block:
                            continue
                        for line in block["lines"]:
                            if 'words' not in line:
                                continue
                            for word in line["words"]:
                                vertices = word["boundingBox"]["vertices"]
                                x_all = [int(v["x"]) for v in vertices if "x" in v]
                                y_all = [int(v["y"]) for v in vertices if "y" in v]
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
                                recognition = word["text"].encode("utf8")
                                f_out.write("{},{},{},{},{},{},{},{},{}\n".format(x1,y1,x2,y1,x2,y2,x1,y2, recognition))
