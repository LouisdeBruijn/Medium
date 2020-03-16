from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .data_preparation import user_demographics, hashtag_demographics, creation_date_demographics, text_demographics, demographics_info


@require_http_methods(["GET", "POST"])
def demographics(request):

    if request.method == 'POST':
        route = request.POST.get('dataset')
        label = request.POST.get('label')

        text_l, text_v, text_c = text_demographics(route, label, vectorizer='count')
        tfidf_l, tfidf_v, tfidf_c = text_demographics(route, label, vectorizer='tfidf')
        created = creation_date_demographics(route, label)
        hashtag_labels, hashtag_values, hashtag_palette = hashtag_demographics(route, label)
        users_labels, users_values, palette = user_demographics(route, label)

        demographics_ctx = demographics_info(route, label)

        content = render_to_string("includes/demographics.html", demographics_ctx)
        msg = render_to_string("includes/message.html", {"tags": "success", "message": "Demographics loaded"})

        response = {
            "demographics": content,
            "msg": msg,
            "doughnut": [users_labels, users_values, palette],
            "hashtag": [hashtag_labels, hashtag_values, hashtag_palette],
            "creation": created,
            "words": [text_l, text_v, text_c],
            "tfidf": [tfidf_l, tfidf_v, tfidf_c]
        }

        return JsonResponse(response)

    return render(request, 'demographics.html', {})
