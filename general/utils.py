import os
import csv
import mimetypes

from wsgiref.util import FileWrapper

from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.forms.models import model_to_dict


def download_response(queryset, path, result_csv_fields):
    result = open(path, 'w')
    result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
    result_csv.writeheader()

    for game in queryset:
        game_ = model_to_dict(game, fields=result_csv_fields)

        try:
            result_csv.writerow(game_)
        except Exception, e:
            print game_

    result.close()

    wrapper = FileWrapper( open( path, "r" ) )
    content_type = mimetypes.guess_type( path )[0]

    response = HttpResponse(wrapper, content_type = content_type)
    response['Content-Length'] = os.path.getsize( path ) 
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str( os.path.basename( path ) ) 

    return response
