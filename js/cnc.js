var resizeSlides = function() {
  $('.slides').css({'height':Math.round($('.slides').width()*125/160)+'px'});
};
var resizeVideo = function() {
  $('#video').css({'height':Math.round($('#video').width()*9/16)+'px'});
};
$(window).resize(resizeSlides);
$(document).ready(resizeSlides);
$(window).resize(resizeVideo);
$(document).ready(resizeVideo);
