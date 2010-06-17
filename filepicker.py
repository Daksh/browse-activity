# Copyright (C) 2007, One Laptop Per Child
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os
import tempfile
import shutil
import re

import gtk
import hulahop

from sugar.graphics.objectchooser import ObjectChooser
from sugar.activity.activity import get_activity_root


_temp_dirs_to_clean = []

#TODO port to webkit
def cleanup_temp_files():
    while _temp_dirs_to_clean:
        temp_dir = _temp_dirs_to_clean.pop()
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            logging.debug('filepicker.cleanup_temp_files: no file %r'
                          % temp_dir)


class FilePicker:
    #_com_interfaces_ = interfaces.nsIFilePicker

    cid = '{57901c41-06cb-4b9e-8258-37323327b583}'
    description = 'Sugar File Picker'

    def __init__(self):
        self._title = None
        self._parent = None
        self._file = None

    def appendFilter(self, title, filter):
        logging.warning('FilePicker.appendFilter: UNIMPLEMENTED')

    def appendFilters(self, filterMask):
        logging.warning('FilePicker.appendFilters: UNIMPLEMENTED')

    def init(self, parent, title, mode):
        self._title = title
        self._file = None
        self._parent = hulahop.get_view_for_window(parent).get_toplevel()

        if mode != interfaces.nsIFilePicker.modeOpen:
            raise xpcom.COMException(NS_ERROR_NOT_IMPLEMENTED)

    def show(self):
        chooser = ObjectChooser(parent=self._parent)
        jobject = None
        try:
            result = chooser.run()
            if result == gtk.RESPONSE_ACCEPT:
                jobject = chooser.get_selected_object()
                logging.debug('FilePicker.show: %r', jobject)

                if jobject and jobject.file_path:
                    tmp_dir = tempfile.mkdtemp(prefix='', \
                            dir=os.path.join(get_activity_root(), 'tmp'))
                    self._file = os.path.join(tmp_dir,
                            _basename_strip(jobject))

                    os.rename(jobject.file_path, self._file)

                    global _temp_dirs_to_clean
                    _temp_dirs_to_clean.append(tmp_dir)

                    logging.debug('FilePicker.show: file=%r', self._file)
        finally:
            if jobject is not None:
                jobject.destroy()
            chooser.destroy()
            del chooser

        if self._file:
            return interfaces.nsIFilePicker.returnOK
        else:
            return interfaces.nsIFilePicker.returnCancel

    def set_defaultExtension(self, default_extension):
        logging.warning('FilePicker.set_defaultExtension: UNIMPLEMENTED')

    def get_defaultExtension(self):
        logging.warning('FilePicker.get_defaultExtension: UNIMPLEMENTED')
        return None

    def set_defaultString(self, default_string):
        logging.warning('FilePicker.set_defaultString: UNIMPLEMENTED')

    def get_defaultString(self):
        logging.warning('FilePicker.get_defaultString: UNIMPLEMENTED')
        return None

    def set_displayDirectory(self, display_directory):
        logging.warning('FilePicker.set_displayDirectory: UNIMPLEMENTED')

    def get_displayDirectory(self):
        logging.warning('FilePicker.get_displayDirectory: UNIMPLEMENTED')
        return None

    def set_filterIndex(self, filter_index):
        logging.warning('FilePicker.set_filterIndex: UNIMPLEMENTED')

    def get_filterIndex(self):
        logging.warning('FilePicker.get_filterIndex: UNIMPLEMENTED')
        return None

    def get_file(self):
        logging.debug('FilePicker.get_file: %r' % self._file)
        if self._file:
            cls = components.classes["@mozilla.org/file/local;1"]
            local_file = cls.createInstance(interfaces.nsILocalFile)
            local_file.initWithPath(self._file)
            return local_file
        else:
            return None

    def get_Files(self):
        logging.warning('FilePicker.get_Files: UNIMPLEMENTED')
        return None

    def get_FileURL(self):
        logging.warning('FilePicker.get_FileURL: UNIMPLEMENTED')
        return None

#components.registrar.registerFactory(FilePicker.cid,
#                                        FilePicker.description,
#                                        '@mozilla.org/filepicker;1',
#                                        Factory(FilePicker))


def _basename_strip(jobject):
    name = jobject.metadata.get('title', 'untitled')
    name = name.replace(os.sep, ' ').strip()

    root_, mime_extension = os.path.splitext(jobject.file_path)

    if not name.endswith(mime_extension):
        if re.search('\.\S+$', name) is None:
            # add mime_type extension only
            # if 'title' doesn't have any extensions
            name += mime_extension

    return name
