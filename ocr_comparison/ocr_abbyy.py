# -*- coding: utf-8 -*-
import xml.dom.minidom
import os
import argparse
import re
import subprocess as sb
import sys

MAX_RETRY_COUNT = 10


def do_ocr_request(image_path, result_path):
    cmd = ['python', 'process.py', image_path, result_path, '-l', 'Russian', '-xml']
    ocr_process = sb.Popen(cmd, stderr=sb.STDOUT, bufsize=0, env=dict(os.environ))
    retcode = ocr_process.wait()
    return retcode == 0


def get_attr(node, attr):
    for (name, value) in node.attributes.items():
        if not name == attr:
            continue
        return value
    print ("Can't find attribute {}".format(attr))
    return None


def get_box(node):
    x = int(get_attr(node, 'l'))
    y = int(get_attr(node, 't'))
    w = int(get_attr(node, 'r')) - x + 1
    h = int(get_attr(node, 'b')) - y + 1
    return (x, y, w, h)


def get_box_orig(node):
    x = int(get_attr(node, 'l'))
    y = int(get_attr(node, 't'))
    x2 = int(get_attr(node, 'r'))
    y2 = int(get_attr(node, 'b'))
    return (x, y, x2, y2)


def getText(character):
    nodes = character.childNodes
    text = ""
    for node in nodes:
        if node.nodeType == node.TEXT_NODE:
            text = text + node.data
    return text


def add_coord(coord, new_box):
    if coord is None:
        coord = [new_box[0], new_box[1], new_box[2], new_box[3]]
        return coord
    coord[0] = min(coord[0], new_box[0])
    coord[1] = min(coord[1], new_box[1])
    coord[2] = max(coord[2], new_box[2])
    coord[3] = max(coord[3], new_box[3])
    return coord


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extracting Abbyy Online SDK OCR result.'
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
        '--psw',
        default=None,
        required=True,
        help='Api password')
    parser.add_argument(
        '--id',
        default=None,
        required=True,
        help='Application id')

    args = parser.parse_args()
    infolder = args.in_folder
    outfolder = args.out_folder
    os.environ["ABBYY_PWD"] = args.psw
    os.environ["ABBYY_APPID"] = args.id

    for root, _, files in os.walk(infolder):
        for file_ in files:
            if not re.match(".*(\.jpg|\.JPG|\.jpeg|\.JPEG|\.png|\.PNG|\.gif|\.GIF)", file_):
                continue
            image_path = os.path.join(root, file_)
            print image_path
            rel_image_path = os.path.relpath(image_path, infolder)
            rel_base_path = rel_image_path[:rel_image_path.rfind('.')]
            result_path = os.path.join(outfolder, "res_" + rel_base_path + ".txt")
            result_path_tmp = os.path.join(outfolder, "res_" + rel_base_path + ".tmp.txt")
            if not os.path.exists(os.path.dirname(result_path)):
                os.makedirs(os.path.dirname(result_path))
            if os.path.exists(result_path):
                continue
            retry_count = 0
            ocr_responce = do_ocr_request(image_path, result_path_tmp)
            while retry_count < MAX_RETRY_COUNT and not ocr_responce:
                retry_count += 1
                ocr_responce = do_ocr_request(image_path, result_path_tmp)
            if retry_count == MAX_RETRY_COUNT:
                print ("ERROR: Max request count is reached! Failing...")
                sys.exit(1)
            with open(result_path, 'w') as f_out:
                with open(result_path_tmp, 'r') as f:
                    doc = xml.dom.minidom.parse(f)
                node = doc.documentElement
                blocks = node.getElementsByTagName('block')
                for block in blocks:
                    paragraphs = block.getElementsByTagName("par")
                    for paragraph in paragraphs:
                        lines = paragraph.getElementsByTagName("line")
                        for line in lines:
                            words = []
                            cur_word = ""
                            word_box = None
                            characters = line.getElementsByTagName("charParams")
                            for character in characters:
                                char_box = get_box_orig(character)
                                ch = getText(character)
                                if len(ch) == 0:
                                    continue
                                if ch == " ":
                                    if len(cur_word) > 0:
                                        words.append({"word": cur_word, "x": word_box[0], "y": word_box[1], "w": word_box[2] - word_box[0] + 1, "h": word_box[3] - word_box[1] + 1})
                                    cur_word = ""
                                    word_box = None
                                else:
                                    cur_word += ch
                                    word_box = add_coord(word_box, char_box)
                            if len(cur_word) > 0:
                                words.append({"word": cur_word, "x": word_box[0], "y": word_box[1], "w": word_box[2] - word_box[0] + 1, "h": word_box[3] - word_box[1] + 1})
                                cur_word = ""
                                word_box = None
                            for word in words:
                                x1 = word["x"]
                                y1 = word["y"]
                                x2 = x1 + word["w"]
                                y2 = y1 + word["h"]
                                recognition = word["word"].encode("utf8")
                                f_out.write("{},{},{},{},{},{},{},{},{}\n".format(x1,y1,x2,y1,x2,y2,x1,y2, recognition))
            os.remove(result_path_tmp)
