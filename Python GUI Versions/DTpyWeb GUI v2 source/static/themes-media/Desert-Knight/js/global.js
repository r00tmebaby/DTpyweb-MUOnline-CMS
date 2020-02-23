/////////// Time /////////////////

function checkTime(i) {
  if (i < 10) {
    i = "0" + i;
  }
  return i;
}
function startTime() {
  var today = new Date();
  var h = today.getHours();
  var m = today.getMinutes();
  // add a zero in front of numbers<10
  m = checkTime(m);
  document.getElementById('time').innerHTML = h + "<span>:</span>" + m;
  t = setTimeout(function() {
    startTime()
  }, 500);
}
startTime();


var width = 200; 
var count = 1;

var carousel = document.getElementById('carousel');
var list = carousel.querySelector('ul');
var listElems = carousel.querySelectorAll('li');

var position = 0;

carousel.querySelector('.prev').onclick = function() {
  position = Math.min(position + width * count, 0)
  list.style.marginLeft = position + 'px';
};

carousel.querySelector('.next').onclick = function() {
  position = Math.max(position - width * count, -width * (listElems.length - count));
  list.style.marginLeft = position + 'px';
};

