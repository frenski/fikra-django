// Basic DOM actions
var showEl = function (elem, displ_type) {
  var dtype = 'block';
  if (typeof displ_type !== 'undefined') {
    dtype = displ_type;
  }
  elem.style.display = dtype;
};

var hideEl = function (elem) {
  elem.style.display = 'none';
};

var toggle = function (elem, displ_type) {
  var dtype = 'block';
  if (typeof displ_type !== 'undefined') {
    dtype = displ_type;
  }
  if (window.getComputedStyle(elem).display === dtype) {
    hideEl(elem);
    return;
  }
  showEl(elem);
};
