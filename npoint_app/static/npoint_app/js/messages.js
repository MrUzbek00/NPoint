// static/npoint_app/js/messages.js
(function ($) {
  $(function () {
    var headerClassByTag = {
      success: 'bg-success text-white',
      error:   'bg-danger text-white',
      warning: 'bg-warning',
      info:    'bg-info text-white',
      debug:   'bg-secondary text-white'
    };

    $('#toast-container .toast').each(function () {
      var $t = $(this);
      var tag = ($t.data('tag') || 'info').split(' ')[0];
      var cls = headerClassByTag[tag] || headerClassByTag.info;

      $t.find('.toast-header').addClass(cls);
      $t.toast({ autohide: true, delay: 4000 }).toast('show');
    });

    // Optional helper to trigger toasts from your own JS
    window.flash = function (type, text, delay) {
      var cls = headerClassByTag[type] || headerClassByTag.info;
      var $toast = $(`
        <div class="toast shadow mb-2" role="alert" aria-live="assertive" aria-atomic="true"
             data-autohide="true" data-delay="${delay || 4000}">
          <div class="toast-header ${cls}">
            <strong class="mr-auto">${type[0].toUpperCase() + type.slice(1)}</strong>
            <small class="text-muted">now</small>
            <button type="button" class="ml-2 mb-1 close" data-dismiss="toast"><span>&times;</span></button>
          </div>
          <div class="toast-body"></div>
        </div>`);
      $toast.find('.toast-body').text(text);
      $('#toast-container').append($toast);
      $toast.toast('show');
    };
  });
})(jQuery);