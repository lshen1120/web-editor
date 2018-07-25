# coding=utf-8
import codecs
import json
import logging
import os

from webeditor.app import handlers

cur_dir = os.getcwd()


class IndexHandler(handlers.HTMLBaseHandler):
    def get(self):
        self.render('index.html')


class FileEditorHandler(handlers.HTMLBaseHandler):
    def get(self):
        self.render('file_editor.html')



class TreeHandler(handlers.APIBaseHandler):
    def get(self):

        sub_dir = self.get_argument('path', '')
        full_path = os.path.join(cur_dir, sub_dir)

        files = []
        dirs = []
        path_list = os.listdir(full_path)

        for path in path_list:
            file_full_path = os.path.join(full_path, path)
            if os.path.isfile(file_full_path):
                files.append({
                    'path': file_full_path[cur_dir.__len__() + 1:],
                    'name': path
                })
            else:
                is_empty = True
                if os.listdir(file_full_path):
                    is_empty = False
                dirs.append({
                    'path': file_full_path[cur_dir.__len__() + 1:],
                    'name': path,
                    'is_empty': is_empty
                })
        result = []
        for dir in dirs:
            result.append({
                'id': dir['path'],
                'text': dir['name'],
                'children': not dir['is_empty'],
                'li_attr': {
                    "path": dir['path'],
                    "is_file": False
                }
            })
        for file in files:
            result.append({
                'id': file['path'],
                'text': file['name'],
                'children': False,
                "icon": "jstree-file",
                'li_attr': {
                    "path": file['path'],
                    "is_file": True
                }

            })
        self.set_status(200)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data = json.dumps(result)
        self.write(data)


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


class ResourceHandler(handlers.APIBaseHandler):
    def get(self):
        sub_dir = self.get_argument('path', '')
        full_path = os.path.join(cur_dir, sub_dir)
        try:
            if get_FileSize(full_path) > 5:
                self.write_json(u'无法打开此文件', error=400)
                return
            with codecs.open(full_path, 'r', encoding='utf8') as f:
                lines = f.readlines()
            self.write_json(''.join(lines))
        except Exception:
            self.write_json(u'无法打开此文件', error=400)

    def put(self, *args, **kwargs):
        sub_dir = self.get_argument('path', '')
        full_path = os.path.join(cur_dir, sub_dir)
        value = self.request.body_arguments['text'][0]
        try:
            with codecs.open(full_path, 'w', encoding='utf8') as f:
                f.write(value)
            self.write_json(u'保存成功')
        except Exception as ex:
            logging.error(ex)
            self.write_json(u'保存失败', error=500)
