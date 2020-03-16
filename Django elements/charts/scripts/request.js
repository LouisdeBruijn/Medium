// form dynamic request for charts
document.body.addEventListener( 'click', function (event) {
    if( event.target.className === 'form-check-input dataset' ) {
        const form = event.target.form;
        const data = new FormData(form);

        const request = new XMLHttpRequest();
        request.open(form.method, form.action, true);
        request.send(data);

        request.addEventListener("load", function () {
            if (this.readyState === 4 && this.status === 200) {

                // catch JsonResponse from Django
                const response = JSON.parse(this.responseText);

                // display message
                const messages = document.getElementById("messages-list");
                messages.innerHTML += response.msg;
                fade_alerts();

                // load content
                const element = document.getElementById("demographics-content");
                const section = element.parentNode;
                section.removeChild(element);
                section.innerHTML = response.demographics;

                // extract variables for charts
                const label = response.label;
                const [users_l, users_v, users_c] = response.doughnut;
                const [hashtag_l, hashtag_v, hashtag_c] = response.hashtag;
                const creation = response.creation;
                const [text_l, text_v, text_c] = response.words;
                const [tfidf_l, tfidf_v, tfidf_c] = response.tfidf;

                [usersDoughnut, hashtagBar, creationTime, textBar, tfidfBar] = returnCharts(label, users_l, users_v, users_c, hashtag_l, hashtag_v, hashtag_c, creation, text_l, text_v, text_c, tfidf_l, tfidf_v, tfidf_c);
                showCharts(usersDoughnut, hashtagBar, creationTime, textBar, tfidfBar);
            }
        });
    }
});

// Simulate a click on radio-button so that it loads demographic content
var hatEvalData = document.getElementById("dataset_a");
hatEvalData.click();
