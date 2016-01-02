// qoolbar.js - a menu of qiki verb icons to apply to things on a web page.

(function(qoolbar, $) {
    if (typeof $ != 'function') {
        console.error("The qoolbar.js module requires jQuery.")
    }

    qoolbar._ajax_url = null;
    qoolbar.ajax_url = function(url) {
        qoolbar._ajax_url = url;
    };

    qoolbar.html = function(selector) {
        qoolbar.post(
            'qoolbar_list',
            function(response) {
                $(selector)
                    .html(qoolbar._build(response.verbs));
                $(selector + ' .qool-verb').draggable({
                    helper: 'clone',
                    cursor: '-moz-grabbing',
                    // TODO:  grab?  -webkit-grab?  move?  http://stackoverflow.com/a/26811031/673991
                    scroll: false,
                    start: function() {
                        qoolbar._associationInProgress();
                    },
                    stop: function() {
                        qoolbar._associationResolved();
                    }
                });
            },
            function(error_message) {
                console.error(error_message);
            }
        );
    };

    qoolbar.drop_object = function(selector) {
        var objects = $(selector);
        var objects_without_idn = objects.filter(':not([data-idn])');
        if (objects_without_idn.length > 0) {
            console.error(
                "Drop objects need a data-idn attribute. " +
                objects_without_idn.length + " out of " +
                objects.length + " are missing one."
            );
        }

    };

    qoolbar.post = function(action, callback_done, callback_fail) {
        $.post(qoolbar._ajax_url, {
            'action': action,
            'csrfmiddlewaretoken': $.cookie('csrftoken')
        }).done(function(response_body) {
            var response_object = jQuery.parseJSON(response_body);
            callback_done(response_object);
        }).fail(function(jqXHR) {
            callback_fail(jqXHR.responseText);
        });
    };

    qoolbar._build = function(verbs) {
        var return_value = $("<div/>");
        var num_verbs = verbs.length;
        for (var i_verb=0 ; i_verb < num_verbs ; i_verb++) {
            // THANKS:  (avoiding for-in loop on arrays) http://stackoverflow.com/a/3010848/673991
            var verb = verbs[i_verb];
            var img_html = $('<img/>')
                .attr('src', verb.icon_url)
                .attr('title', verb.name);
            var verb_html = $('<span/>')
                .html(img_html)
                .addClass('qool-verb qool-verb-' + verb.name)
                .attr('data-verb', verb.name);
            return_value.append(verb_html);
        }
        return_value.addClass('qoolbar fade_until_hover');
        return return_value;
    };

    qoolbar._associationInProgress = function() {   // indicating either (1) nouns are selected, or (2) a verb is dragging
        $(document.body).css('background-color', 'rgb(200,200,200)');
    };

    qoolbar._associationResolved = function() {   // indicating normalcy
        $(document.body).css('background-color', 'rgb(215,215,215)');
    };

}(window.qoolbar = window.qoolbar || {}, jQuery));
// THANKS:  http://www.adequatelygood.com/JavaScript-Module-Pattern-In-Depth.html
// THANKS:  http://appendto.com/2010/10/how-good-c-habits-can-encourage-bad-javascript-habits-part-1/
