"use strict";

jQuery(document).ready(function ($) {
  var keyword = $('#searchbox').val(),
      staticUrl = window.location.href.split('?')[0],
      delimiter = ',';
  $('#keyword').val(keyword);
  $('#library-search').submit(function (event) {
    event.preventDefault();
    $('#keyword').val($('#searchbox').val());
    $('#library-filters').trigger('change');
  });
  $('#library-filters').change(function () {
    var queryString = $(this).serialize().replace(/(?<=([^\?\&\=]+=)([^\&\=]+))(\&\1)/g, delimiter);
    var url = !queryString ? staticUrl : staticUrl + '?' + queryString;
    window.location.replace(url);
  });
});