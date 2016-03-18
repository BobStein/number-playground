// qoolbar.js - a menu of qiki verb icons to apply to things on a web page.
'use strict';

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
            {},
            function(response) {
                $(selector)
                    .html(qoolbar._build(response.verbs));
                //noinspection JSUnusedGlobalSymbols
                $(selector + ' .qool-verb').draggable({
                    helper: 'clone',
                    cursor: '-moz-grabbing',
                    // TODO:  grabby cursor?  -webkit-grab?  move?  http://stackoverflow.com/a/26811031/673991
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
        //noinspection JSUnusedGlobalSymbols
        objects.droppable({
            accept: ".qool-verb",
            hoverClass: 'drop-hover',
            drop: function(event, ui) {
                var $source = ui.draggable;
                var $destination = $(event.target);
                var verb_name = $source.data('verb');
                var destination_idn = $destination.data('idn');
                qoolbar.post(
                    'sentence',
                    {
                        vrb: verb_name,
                        obj: destination_idn,
                        num_add: '0q82',
                        txt: ''
                    },
                    function(response) {
                        if (response.is_valid) {
                            // alert(response.report);
                            window.location.reload(true);
                        } else {
                            alert(response.error_message);
                        }
                    })
            }
        });
    };

    qoolbar.post = function(action, variables, callback_done, callback_fail) {
        var fail_function;
        if (typeof callback_fail === 'undefined') {
            fail_function = qoolbar._default_fail_callback;
        } else {
            fail_function = callback_fail;
        }
        variables.action = action;
        variables.csrfmiddlewaretoken = $.cookie('csrftoken');
        $.post(qoolbar._ajax_url, variables).done(function(response_body) {
            var response_object = jQuery.parseJSON(response_body);
            callback_done(response_object);
        }).fail(function(jqXHR) {
            fail_function(jqXHR.responseText);
        });
    };

    qoolbar._default_fail_callback = function(error_message) {
        alert(error_message);
    };

    /**
     * Build the qoolbar div, with verb spans.
     * @param verbs
     * @returns {*|HTMLElement}
     * @private
     */
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

    qoolbar._is_anybody_editing = false;

    qoolbar.click_to_edit = function(selector) {
        if (selector === undefined) {
            selector = '.qool-icon';
        }
        $(selector).on('click', function (event) {
            var was_already_editing = $(this).hasClass('qool-editing');
            qoolbar._end_all_editing();
            if (!was_already_editing) {
                $(this).addClass('qool-editing');
                qoolbar._is_anybody_editing = true;
                var old_num = $(this).data('num');
                var input = $('<input/>', {
                    type: 'text',
                    class: 'qool-icon-entry',
                    value: old_num
                });
                $(this).append(input);
                input.select();
            }
            event.stopPropagation();
        });
        $(selector).on('click', '.qool-icon-entry', function (event) {
            // Clicking the input field itself should not cancel editing.
            // THANKS:  For nested click ignoring, http://stackoverflow.com/a/2364639/673991
            event.stopPropagation();
        });

        $('body').on('keydown', '.qool-icon-entry', 'return', function(event) {
            event.preventDefault();
            var new_num = $(this).val();
            alert(new_num);
            qoolbar._end_all_editing();
        });

        $('body').on('keydown', '.qool-icon-entry', 'esc', function(event) {
            event.preventDefault();
            qoolbar._end_all_editing();
        });

        $(document).on('blur', '.qool-icon-entry', function() {
            // THANKS:  For event on dynamic selector, http://stackoverflow.com/a/1207393/673991
            if (qoolbar) {
                qoolbar._end_all_editing();
            }
        });
    };

    qoolbar._qool_icon_entry_keypress = function() {

    };

    qoolbar._end_all_editing = function() {
        if (qoolbar._is_anybody_editing) {
            qoolbar._is_anybody_editing = false;
            $('.qool-editing').removeClass('qool-editing');
            $('.qool-icon-entry').remove();
        }
    };

}(window.qoolbar = window.qoolbar || {}, jQuery));
// THANKS:  http://www.adequatelygood.com/JavaScript-Module-Pattern-In-Depth.html
// THANKS:  http://appendto.com/2010/10/how-good-c-habits-can-encourage-bad-javascript-habits-part-1/
