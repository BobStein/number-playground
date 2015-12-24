// qoolbar.js - a menu of qiki verb icons to apply to things on a web page.

(function(qoolbar, $) {
    if (typeof $ != 'function') {
        console.error("The qoolbar module requires jQuery.")
    }

    qoolbar.html = function() {
        return "<div>qoolbar goes here</div>";
    };

}(window.qoolbar = window.qoolbar || {}, jQuery));

// THANKS:  http://www.adequatelygood.com/JavaScript-Module-Pattern-In-Depth.html
// THANKS:  http://appendto.com/2010/10/how-good-c-habits-can-encourage-bad-javascript-habits-part-1/
