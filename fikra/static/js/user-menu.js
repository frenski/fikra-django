
document.addEventListener("DOMContentLoaded", function() {

  var userMenu = document.getElementById('user-menu');
  var userBlock = document.getElementById('user-block');

  var mainMenuToggle = document.getElementById('main-menu-toggle');
  var mainMenuList = document.getElementById('main-menu-list');

  var mainMenuVisible = false;

  // User menu show hidden
  if (userBlock) {
    userBlock.addEventListener("mouseenter", function( event ) {
      showEl(userMenu);
      event.stopPropagation();
    });

    userBlock.addEventListener("mouseleave", function( event ) {
      hideEl(userMenu);
    });
  }

  if (mainMenuList) {
    mainMenuToggle.addEventListener("click", function( event ) {
      if (!mainMenuVisible) {
        showEl(mainMenuList);
        mainMenuVisible = true;
      } else {
        hideEl(mainMenuList);
        mainMenuVisible = false;
      }

      event.stopPropagation();
    });
  }

});
