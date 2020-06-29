import string
from io import BytesIO

import PIL
import img2pdf
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
import logging

logger = logging.getLogger(__name__)


class MergeUploadedFilesToPdfMixin(object):
    """
    Provides a django class-based-view with method to
    allow the developer to easily merge multiple
    uploaded image files to a single pdf file.
    """
    
    @staticmethod
    def _ensure_all_uploaded_files_are_images():
        """
        Makes sure all passed files are actually
        image files
        :return:
        """
        pass
    
    @staticmethod
    def _convert_images(files_list):
        """
        Converts all PNG images to JPG since
        pdf2img does not support images with
        alpha (a.k.a transparency) channel.
        :type files_list: list of uploaded images
        :return: list of converted images
        """
        # This was is going be returned after the main loop
        output_file_list = []
        
        for file in files_list:
            # Try to open the image via PIL
            try:
                as_pil_image = PIL.Image.open(file, mode='r')
            except PIL.UnidentifiedImageError as e:
                __error_msg = string.Template(
                    _('File named "$file_name" was not an PIL accepted image. $exception.')
                )
                raise RuntimeError(__error_msg.substitute(file_name=file, exception=e))
            # Make sure the image format is supported
            if as_pil_image.format not in ('PNG', 'JPEG'):
                __error_msg = string.Template(
                    _('File named "$file_name" format was not either PNG or JPEG,'
                      ' these are the only supported formats.')
                )
                raise RuntimeError(__error_msg.substitute(file_name=file))
            # In case the format as PNG (which has alpha channel), convert it to JPEG.
            if as_pil_image.format == 'PNG':
                __converted_to_jpg = as_pil_image.convert('RGB')
                __byte_io = BytesIO()
                __converted_to_jpg.save(__byte_io, 'JPEG')
                output_file_list.append(ContentFile(__byte_io.getvalue()))
                logger.debug('Successfully converted file "{}" to JPEG.'.format(file))
            else:
                output_file_list.append(file)
        return output_file_list
    
    def merge_to_pdf(self):
        """
        Merges passed images to a single pdf
        :return:
        """
        self._ensure_all_uploaded_files_are_images()
        self._convert_images()
        pdf_file = '/tmp/test.pdf'
        with open(pdf_file, "wb") as f:
            f = img2pdf.convert()
        return pdf_file
