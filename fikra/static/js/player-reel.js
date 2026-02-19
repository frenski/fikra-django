// Player js for vizlaipedia

document.addEventListener("DOMContentLoaded", function() {
	// main vars
	var urlDir = Config.urls.staticPath;
	var played = false;
	var butStopPlayActive = false;
	var urlToPlay = urlDir + _VPD.FileToPlay;
	var urlToLike = "/node_update/add_like/" + _VPD.NodeId;
	var autoplay = (typeof _VPD.autoPlay === 'undefined') ? false:_VPD.autoPlay;
	var aspectRatio = (typeof _VPD.aspectRatio === 'undefined') ? 1.77777:_VPD.aspectRatio;
	var textLocaleFileName = "text.json";
	var urlLocale = '';
	var lang = _VPD.language;
	var canvasDomIdPrefix = 'main-canvas';
	var curReelId = 0;
	var canvasDomId = canvasDomIdPrefix + curReelId;
	const timeBetweenReels = 5;
	const touchPreventEventId = '1';
	var xDown = null;
	var yDown = null;

	// elements
	var main = document.getElementById('main');
	var canvasContainer = document.getElementById('canvas-container');
	var plIFrame = document.getElementById('player' + curReelId);
	var playerLoader = document.getElementById('player-loader');
	var playerLoaderNum = document.getElementById('player-loader-number');
	var playStopBut = document.getElementById('playstopbutton');
	var volCtr = document.getElementById('controlbar-volumecontrol');
	var volCtrInput = document.getElementById('controlbar-volumecontrol-input');
	var volCtrIco = document.getElementById('controlbar-volumecontrol-icon');
	var butLike = document.getElementById('button-social-like');
	var butLikeCount = document.getElementById('button-social-like-count');
	var changeLangForm = document.getElementById('changelang-form');
	var changeLangSelect = document.getElementById('node-change-language');
	var metadataBlock = document.getElementById('metadata');
	var metaTitle = document.getElementById('metadata-title');
	var metaDescription = document.getElementById('metadata-description')
	var infoBut = document.getElementById('infobutton');
	var backBut = document.getElementById('backbutton');
	var metaCloseBut = document.getElementById('metadata-closebut');
	var reelsWrapper = document.getElementById('reels-wrapper');
	var reelsUnfoldBut = document.getElementById('reels-unfold-button');
	var reels = document.getElementById('reels');
	var playerLoadPH = document.getElementById('player-load-ph');
	var ifPlayerCont = document.getElementById('ifplayers-container');
	const dropAminEl = document.getElementById('lt-player-main');
	var nextNotice = document.getElementById('next-notice');
	var nextNoticeTime = document.getElementById('next-notice-time');
	var touchEl = document.getElementById('touch-element');
	var mobileNav = document.getElementById('mobile-nav');
	var ctrTlinePref = 'controlbar-timeline';
	var ctrTimerPref = 'controlbar-timer';
	var metadataUnfoldClass = 'metadata-unfold';
	var vcUnfoldClass = 'vc-unfold';
	var vcInputUnfoldClass = 'vcinput-unfold';
	var reelsUnfoldClass = 'reels-unfold';
	var breadcrumbPrevClass="breadcrumbs-prev";
	var reelNavUpClass = "reel-navigation-up";
	var reelNavDownClass = "reel-navigation-down";
	var reelCurrentClass = "reel-current";
	var playStopButPromoteClass = "playstopbutton-promote";
	var playStopButPromoteHalfClass = "playstopbutton-promote-half";
	var playerLoaderHidClass = 'player-loader-hidden';
	var playerIfClass = 'player-iframe';
	var playerIfClassPrev = 'player-iframe-prev';
	var playerIfClassNext = 'player-iframe-next';
	var playerSuffId = 'player';
	var reelSuffId = 'reel';
	var ctrTimerTotalClass = 'controlbar-timer-total';
	var nextNoticeShowClass = 'next-notice-show';
	var nextInterval = null;
	var timerInterval = null;
	var timeTotal = 0;
	var timeTotalNum = 0;
	var timelineActive = false;
	var timelineLevel = _VPD.timelineLevel;
	var muted = false;
	var firstPlay = true;

	let dropAnim = lottie.loadAnimation({
		container: dropAminEl,
		renderer: 'svg',
		loop: false,
		autoplay: false,
		path: "/static/anims/drop1.json",
		initialSegment:[11,32],
		onComplete: function(){
			console.log('onComplete');
		}
	});

	// setting size
	if (aspectRatio < 1.1) {
		document.body.classList.add('player-square-size');
	}

	var scrollTo = function(element, to, duration) {
    if (duration <= 0) return;
    var difference = to - element.scrollTop;
    var perTick = difference / duration * 10;

    setTimeout(function() {
        element.scrollTop = element.scrollTop + perTick;
        if (element.scrollTop === to) return;
        scrollTo(element, to, duration - 10);
    }, 10);
	}

	var getAbsolutePosition = function(element) {
		var r = { x: element.offsetLeft, y: element.offsetTop };
		if (element.offsetParent) {
			var tmp = getAbsolutePosition(element.offsetParent);
			r.x += tmp.x;
			r.y += tmp.y;
		}
		return r;
	};

	var addPlCallbacks = function () {
		if (ifPlayer) {
			ifPlayer.pauseCallback = function () {
				played = false;
				if (ifPlayer.getActionRequired() == true ) {
					playStopBut.style.backgroundImage = "url('/static/img/button-play-inactive.png')";
					playStopBut.removeEventListener("click", playButClick);
					butStopPlayActive = false;
					timelineActive = false;
				} else {
					playStopBut.style.backgroundImage = "url('/static/img/button-play.png')";
				}
			}
			ifPlayer.playCallback = function () {
				played = true;
				playStopBut.style.backgroundImage = "url('/static/img/button-pause.png')";
				activatePPButton();
			// 	// activateTimeline();
			// 	timerInterval = setInterval(function(){
			// 		setTime();
			// 	}, 200);
			}
		}
	}

	var setNewIfPlayer = function() {
		if (typeof plIFrame !=='undefined' && plIFrame) {
			if (typeof plIFrame.contentWindow._VPD.player !== 'undefined'
					&& plIFrame.contentWindow._VPD.player.length > 0
					&& plIFrame.contentWindow._VPD.player[0]) {
				ifPlayer = plIFrame.contentWindow._VPD.player[0];
				addPlCallbacks();
			}
		}
	}

	var setVolVal = function(volVal) {
		if (typeof(ifPlayer) !== 'undefined' && ifPlayer) {
			ifPlayer.setVolume(volVal);
		}
		volCtrInput.style.backgroundImage =
			'-webkit-gradient(linear, left top, right top, '
			+ 'color-stop(' + volVal + ', #241f51), '
			+ 'color-stop(' + volVal + ', #C5C5C5)'
			+ ')';
		if (muted && volVal !== 0) {
			volCtrIco.style.backgroundImage = "url('/static/img/ico-volume.png')";
			muted = false;
		}

		if (!muted && volVal === 0) {
			volCtrIco.style.backgroundImage = "url('/static/img/ico-volume-muted.png')";
			muted = true;
		}
	}

	var setVolumeControl = function() {
		var val = (volCtrInput.value - volCtrInput.getAttribute('min')) /
			(volCtrInput.getAttribute('max') - volCtrInput.getAttribute('min'));
		setVolVal (val);
	}

	var promotePlayBut = function() {
		dropAminEl.style.display = "block";
		dropAnim.playSegments([11,32],true);
		setTimeout(function(){
			playStopBut.classList.add(playStopButPromoteClass);
		}, 400);
	}

	var promotePlayButHalf = function() {
		dropAminEl.style.display = "block";
		dropAnim.playSegments([11,29],true);
		setTimeout(function(){
			playStopBut.classList.add(playStopButPromoteHalfClass);
		}, 400);
	}

	var demotePlayBut = function() {
		if (playStopBut.classList.contains(playStopButPromoteClass)) {
			dropAnim.playSegments([32,11],true);
			playStopBut.classList.remove(playStopButPromoteClass);
			setTimeout(function(){
				// dropAminEl.style.display = "none";
				playerLoader.style.display = "none";
			}, 500);
		}
		if (playStopBut.classList.contains(playStopButPromoteHalfClass)) {
			dropAnim.playSegments([29,11],true);
			playStopBut.classList.remove(playStopButPromoteHalfClass);
			setTimeout(function(){
				// dropAminEl.style.display = "none";
			}, 500);
		}
	}

	var playButClick = function(e) {
		e.stopPropagation();
		if (played) {
			pause();
		} else {
			play();
			demotePlayBut();
		}
	}

	var opts = {
		'sizeFixedTo':'canvas-container',
		'sizeRatio': aspectRatio
	}

	var checkLoadStatus = setInterval(function() {
		var loaded = 0;
		setNewIfPlayer();
		if (typeof(ifPlayer) !== 'undefined' && ifPlayer) {
			var plLoaded = ifPlayer.getAssetsLoadedStatus();
			// console.log(plLoaded);
			if (!isNaN(plLoaded)) {
				loaded = Math.round(plLoaded*100);
			}
			playerLoaderNum.innerHTML = loaded + "%";
			if (loaded == 100) {
				firstLoaded ();
			}
		}
		// if (explotPlayer[curReelId]) {
		// 	loaded = Math.round(explotPlayer[curReelId].getAssetsLoadedStatus()*100);
		// }
		// playerLoaderNum.innerHTML = loaded + "%";
	}, 50);

	var msToTime = function(s) {
		var ms = s % 1000;
		s = (s - ms) / 1000;
		var secs = s % 60;
		s = (s - secs) / 60;
		var mins = s % 60;

		if (String(mins).length == 1) mins = "0" + mins;
		if (String(secs).length == 1) secs = "0" + secs;

		return  mins + ':' + secs;
	}

	var playButClickReload = function (e) {
		e.stopPropagation();
		ifPlayer = null;
		clearInterval(nextInterval);
		var url = plIFrame.src.replace('autoplay=0', 'autoplay=1');
		// plIFrame.contentWindow.location.reload();
		plIFrame.src = url;
		var reloadInt = setInterval(function(){
			if (typeof (plIFrame.contentWindow._VPD.player[0] !== 'undefined') &&
					plIFrame.contentWindow._VPD.player[0]) {
				setNewIfPlayer();
				clearInterval(reloadInt);
				playStopBut.addEventListener('click', playButClick);
				playStopBut.removeEventListener('click', playButClickReload);
				demotePlayBut();
				if (nextNotice.classList.contains(nextNoticeShowClass)){
					nextNotice.classList.remove(nextNoticeShowClass);
				}
				setTimeout(function(){
					nextNotice.style.display = "none";
				},400);
				activateIfCanvasTouch();
				play();
			}
		}, 200);
	}

	var end = function() {
		console.log("END");
		// explotPlayer[curReelId].pause();
		if (typeof(ifPlayer) !== 'undefined' && ifPlayer) {
			ifPlayer.pause();
			played = false;
		}
		clearInterval(timerInterval);
		playStopBut.style.backgroundImage
			= "url('/static/img/button-replay.png')";
		var ctrTimer = document.getElementById(ctrTimerPref+curReelId);
		ctrTimer.innerHTML = timeTotal;
		promotePlayButHalf();
		playStopBut.removeEventListener('click', playButClick);
		playStopBut.addEventListener('click', playButClickReload);
		if (document.getElementById(reelSuffId + (curReelId+1))) {
			nextNotice.style.display = "block";
			setTimeout (function(){
				if (!nextNotice.classList.contains(nextNoticeShowClass)){
					nextNotice.classList.add(nextNoticeShowClass);
				}
			}, 50);
			var timeLeft = timeBetweenReels;
			nextNoticeTime.innerHTML = timeLeft;
			nextInterval = setInterval(function(){
				timeLeft --;
				nextNoticeTime.innerHTML = timeLeft;
				if (timeLeft <= 0) {
					playStopBut.addEventListener('click', playButClick);
					playStopBut.removeEventListener('click', playButClickReload);
					goToIfPlayer (curReelId + 1);
				}
			}, 1000);
		}
	}

	var pause = function() {
		// explotPlayer[curReelId].pause();
		// played = false;
		clearInterval(timerInterval);
		// setNewIfPlayer();
		if (typeof(ifPlayer) !== 'undefined' && ifPlayer) {
			ifPlayer.pause();
			played = false;
		}
		playStopBut.style.backgroundImage
			= "url('/static/img/button-play.png')";
	}

	var setTime = function() {
		if (typeof ifPlayer !== 'undefined') {
			const curTime = ifPlayer.getTimeElapsed();
			const timeTotal = ifPlayer.getTimeTotal();
			// console.log(curTime, timeTotal);
			if (curTime >= timeTotal) {
				end();
			}
			var percTime = curTime/timeTotal;
			var ctrTline = document.getElementById(ctrTlinePref + curReelId);
			ctrTline.style.backgroundImage =
					'-webkit-gradient(linear, left top, right top, '
					+ 'color-stop(' + percTime + ', #241f51), '
					+ 'color-stop(' + percTime + ', #C5C5C5)'
					+ ')';
			var ctrTimer = document.getElementById(ctrTimerPref+curReelId);
			ctrTimer.innerHTML = msToTime(curTime);
		}
	}

	var play = function() {
		if (firstPlay) {
			playerLoadPH.parentNode.removeChild(playerLoadPH);
			firstPlay = false;
		}
		playStopBut.style.backgroundImage
			= "url('/static/img/button-pause.png')";
		// explotPlayer[curReelId].play();
		// played = true;
		setNewIfPlayer();
		if (typeof(ifPlayer) !== 'undefined' && ifPlayer) {
			ifPlayer.play();
			played = true;
			timerInterval = setInterval(function(){
				setTime();
			}, 200);
		}

	}

	var activatePPButton = function() {
  	if (!butStopPlayActive) {
			playStopBut.addEventListener('click', playButClick);
    	butStopPlayActive = true;
  	}
	}

	var firstLoaded = function(){
		if (volCtrInput) setVolumeControl();

		var ctrTimer = document.getElementById(ctrTimerPref+curReelId);
		if (ctrTimer) ctrTimer.innerHTML = '00:00';

		playerLoader.className = playerLoaderHidClass;
		clearInterval(checkLoadStatus);
		setTimeout(function(){
			promotePlayBut();
		}, 600);

		if (playStopBut) {
			playStopBut.style.backgroundImage
				= "url('/static/img/button-play.png')";
		}

		if (playStopBut) {
			activatePPButton();
		}

		if (volCtrInput) {
			volCtrInput.addEventListener('input', function() {
				setVolumeControl ();
			});
		}

		if (volCtrIco) {
			volCtrIco.addEventListener('click', function() {
				if (volCtr.classList.contains(vcUnfoldClass)) {
					volCtr.classList.remove(vcUnfoldClass);
				} else {
					volCtr.classList.add(vcUnfoldClass);
				}

				if (volCtrInput.classList.contains(vcInputUnfoldClass)) {
					volCtrInput.classList.remove(vcInputUnfoldClass);
				} else {
					volCtrInput.classList.add(vcInputUnfoldClass);
				}
			});
		}

		window.addEventListener('blur', function() {
			// 	if (played && explotPlayer[curReelId].playing) {
			// 	pause();
			// }
		});

		activateIfCanvasTouch();

	}

	var resizeReelsWrapper = function () {
		if (window.innerWidth < 768) {
			const prefH = mobileNav.offsetHeight + canvasContainer.offsetHeight;
			const h = window.innerHeight - prefH - 22;
			console.log(window.innerWidth);
			reelsWrapper.style.height = h + "px";
		}
	}

	resizeReelsWrapper();

	reels.scrollTo(0, 0);

	window.addEventListener('resize', function(){
		resizeReelsWrapper();
	});


	// Setting up the like button
	if (butLike) {
		butLike.addEventListener('click', function() {
			var lxhr = new XMLHttpRequest();
			lxhr.open('GET', urlToLike);
			lxhr.setRequestHeader('X-CSRFToken', cookies['csrftoken']);
			lxhr.onload = function() {
					if (lxhr.status === 200) {
					butLikeCount.innerHTML = lxhr.responseText;
				} else {
					alert( _LANGVARS.games.likeCountIssue );
				}
			}
			lxhr.send();
			return false;
		});
	}


	// Formatting total times
	totalTimes = document.getElementsByClassName(ctrTimerTotalClass);
	for (var i=0; i<totalTimes.length; i++) {
		const ttval = parseFloat(totalTimes[i].innerHTML);
		const ttPretty = msToTime(ttval*1000);
		totalTimes[i].innerHTML = ttPretty;
	}

	// Adding events
	infoBut.addEventListener('click', function() {
		metadataBlock.classList.add(metadataUnfoldClass);
	});

	metaCloseBut.addEventListener('click', function() {
		metadataBlock.classList.remove(metadataUnfoldClass);
	});

	reelsUnfoldBut.addEventListener('click', function(){
		if (reelsWrapper.classList.contains(reelsUnfoldClass)) {
			reelsWrapper.classList.remove(reelsUnfoldClass);
			resizeReelsWrapper();
		} else {
			reelsWrapper.style.removeProperty('height');
			reelsWrapper.classList.add(reelsUnfoldClass);
		}
	});

	backBut.addEventListener('click', function(){
		var breadcrumbPrev = document.getElementsByClassName(breadcrumbPrevClass)[0];
		const urlPrev = breadcrumbPrev.getAttribute('href');
		window.location.href = urlPrev;
	});

	nextNotice.addEventListener('click', function(){
		playStopBut.addEventListener('click', playButClick);
		playStopBut.removeEventListener('click', playButClickReload);
		goToIfPlayer (curReelId + 1);
	});

	var addIfPlayer = function(id, pos="") {
		var nReel = document.getElementById(reelSuffId + id);
		if (nReel) {
			if (!ifPlayerCont.contains(document.getElementById(playerSuffId + id))){
				const src = nReel.dataset.src;
				const duration = nReel.dataset.durationcoef;
				var newIf = document.createElement("iframe");
				newIf.setAttribute('id', playerSuffId + id);
				const url = _VPD.urlPiece + '?file=' + src + '&duration=' + duration +
					_VPD.urlPieceDefaultParams;
				newIf.setAttribute('src', url);
				var extraClass = "";
				if (pos == "before") extraClass = " " + playerIfClassPrev;
				if (pos == "after") extraClass = " " + playerIfClassNext;
				newIf.className = playerIfClass + extraClass;
				newIf.dataset.id = id;
				if (pos == 'before') {
					ifPlayerCont.prepend(newIf);
				} else {
					ifPlayerCont.append(newIf);
				}
			}
		}
		return document.getElementById(playerSuffId + id);
	}

	var removeIfPlayer = function(id) {
		var pl = document.getElementById(playerSuffId + id);
		if (pl) {
			pl.remove();
		}
	}

	var getTouches = function(evt) {
		return evt.touches ||
					 evt.originalEvent.touches;
	}

	var touchStart = function (evt) {
		const firstTouch = getTouches(evt)[0];
		xDown = firstTouch.clientX;
		yDown = firstTouch.clientY;
	}

	var touchMove = function (evt, fireDiff=0) {
		if ( ! xDown || ! yDown ) {
				return;
		}

		var xUp = evt.changedTouches[0].clientX;
		var yUp = evt.changedTouches[0].clientY;
		// console.log(yDown, yUp);

		var xDiff = xDown - xUp;
		var yDiff = yDown - yUp;

		// console.log(yDiff);

		if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
				if ( xDiff > fireDiff ) {
					/* right swipe */
				} else {
					/* left swipe */
				}
		} else {
				if ( yDiff > fireDiff ) {
					/* down swipe */
					console.log('DOWN');
					if (document.getElementById(reelSuffId + (curReelId+1))) {
						goToIfPlayer(curReelId+1);
					}
				} else if (yDiff < -fireDiff) {
					/* top swipe */
					console.log('UP');
					if (curReelId > 0) {
						goToIfPlayer(curReelId-1);
					}
				}
		}
		/* reset values */
		xDown = null;
		yDown = null;
	}

	var activateIfCanvasTouch = function() {
		const reel = document.getElementById(reelSuffId + curReelId);
		if (reel) {
			var touchAllowed = true;
			if ("preventevents" in reel.dataset) {
				const prevEvents = reel.dataset.preventevents;
				if (prevEvents.indexOf(touchPreventEventId) > -1){
					 touchAllowed = false;
				}
			}
			if (touchAllowed) {
				var ifCanvas = plIFrame.contentWindow.document.getElementById('main-canvas0');
				if (ifCanvas) {
					ifCanvas.addEventListener('touchstart', function(evt){
						// console.log("touch started");
						touchStart(evt);
					}, false);
					ifCanvas.addEventListener('touchmove', function(evt){
						touchMove(evt);
						// console.log("T move");
					}, false);
				}
			}
		}
	}

	// Actions for when the reel item playButClick

	var goToIfPlayer = function (plId){
		plId = parseInt(plId);
		clearInterval(nextInterval);
		reel = document.getElementById(reelSuffId + plId);
		if (reel) {
			if (nextNotice.classList.contains(nextNoticeShowClass)){
				nextNotice.classList.remove(nextNoticeShowClass);
			}
			setTimeout(function(){
				nextNotice.style.display = "none";
			},300);
			demotePlayBut();
			pause();
			// processes reels
			scrollTo(reels, reel.offsetTop - reel.offsetHeight/3, 500);
			reel.classList.add(reelCurrentClass);
			const currReel = document.getElementById(reelSuffId + curReelId);
			currReel.classList.remove(reelCurrentClass);
			reel.classList.add(reelCurrentClass);

			// processes iframe players
			var lastIfPlayer = document.getElementById(playerSuffId + curReelId);
			var newPos = 'after';
			if (plId > curReelId) {
				lastIfPlayer.classList.add(playerIfClassPrev);
			} else {
				lastIfPlayer.classList.add(playerIfClassNext);
				newPos = 'before';
			}

			var addedPl = addIfPlayer (plId, newPos);
			if (addedPl.classList.contains(playerIfClassPrev)) addedPl.classList.remove(playerIfClassPrev);
			if (addedPl.classList.contains(playerIfClassNext)) addedPl.classList.remove(playerIfClassNext);

			setTimeout(function(){
				if (ifPlayerCont.hasChildNodes()) {
					var cn = ifPlayerCont.children;
					for (i = 0; i < cn.length; i++) {
						const cId = cn[0].dataset.id;
						if (cId > (plId+1) || cId < (plId-1)) {
							removeIfPlayer(cId);
						}
          }
				}
				removeIfPlayer(plId - 2);
				removeIfPlayer(plId + 2);
				if (document.getElementById(reelSuffId + (plId-1))) {
					// console.log("ADDING Item before");
					addIfPlayer (plId - 1, 'before');
				}
				console.log(reelSuffId + (plId+1));
				if (document.getElementById(reelSuffId + (plId+1))) {
					// console.log("ADDING Item after");
					addIfPlayer (plId + 1, 'after');
				}
				curReelId = plId;
				plIFrame = document.getElementById(playerSuffId + curReelId);
				activateIfCanvasTouch();
				play();
			},500);
		}
	}

	var reelBlocks = document.getElementsByClassName(reelSuffId);
	for (var i=0; i<reelBlocks.length; i++) {
		reelBlocks[i].addEventListener('click', function(){
			const id = this.dataset.id;
			goToIfPlayer(id);
		});
	}


	var reelMoveDown = function (){
		event.stopPropagation();
		goToIfPlayer (curReelId + 1);
		// pause();
		// const currReel = document.getElementById('reel' + curReelId);
		// currReel.classList.remove(reelCurrentClass);
		// // Moving up the current iframe player
		// var curIfPlayer = document.getElementById(playerSuffId + curReelId);
		// if (!curIfPlayer.classList.contains(playerIfClassPrev)) {
		// 	curIfPlayer.classList.add(playerIfClassPrev);
		// }
		// curReelId ++;
		// plIFrame = document.getElementById(playerSuffId + curReelId);
		// const nextReel = document.getElementById('reel' + curReelId);
		// scrollTo(reels, nextReel.offsetHeight * curReelId, 500);
		// nextReel.classList.add(reelCurrentClass);
		// // Moving up the new current iframe player
		// var nextIfPlayer = document.getElementById(playerSuffId + curReelId);
		// if (nextIfPlayer.classList.contains(playerIfClassNext)) {
		// 	nextIfPlayer.classList.remove(playerIfClassNext);
		// }
		// // Adding new iframe players
		// removeIfPlayer(curReelId - 2);
		// addIfPlayer (curReelId + 1, 'after');
		// setTimeout(function(){
		// 	play();
		// },600);
	}

	var reelMoveUp = function(){
		event.stopPropagation();
		goToIfPlayer (curReelId - 1);
		// pause();
		// const currReel = document.getElementById('reel' + curReelId);
		// currReel.classList.remove(reelCurrentClass);
		// var curIfPlayer = document.getElementById(playerSuffId + curReelId);
		// if (!curIfPlayer.classList.contains(playerIfClassNext)) {
		// 	curIfPlayer.classList.add(playerIfClassNext);
		// }
		// curReelId --;
		// plIFrame = document.getElementById(playerSuffId + curReelId);
		// const prevReel = document.getElementById('reel' + curReelId);
		// scrollTo(reels, prevReel.offsetHeight * curReelId, 500);
		// prevReel.classList.add(reelCurrentClass);
		// var prevIfPlayer = document.getElementById(playerSuffId + curReelId);
		// if (prevIfPlayer.classList.contains(playerIfClassPrev)) {
		// 	prevIfPlayer.classList.remove(playerIfClassPrev);
		// }
		// // addIfPlayer (curReelId + 1);
		// removeIfPlayer(curReelId - 2);
		// addIfPlayer (curReelId - 1, 'before');
		// setTimeout(function(){
		// 	play();
		// },500);
	}

	const allReelNavDown = document.getElementsByClassName(reelNavDownClass);
	for (i = 0; i < allReelNavDown.length; i++) {
		allReelNavDown[i].addEventListener('click', function() {
			reelMoveDown();
		});
	}

	const allReelNavUp = document.getElementsByClassName(reelNavUpClass);
	for (i = 0; i < allReelNavUp.length; i++) {
    allReelNavUp[i].addEventListener('click', function() {
			reelMoveUp();
    });
	}

	// ifPlayerCont.addEventListener('touchstart', function(evt){
	// 	console.log("TOUCH START");
	// 	// evt.stopPropagation();
	// 	const firstTouch = getTouches(evt)[0];
	// 	xDown = firstTouch.clientX;
	// 	yDown = firstTouch.clientY;
	// }, false);
	//
	// ifPlayerCont.addEventListener('touchmove', function(evt){
	// 	// evt.stopImmediatePropagation();
	// 	if ( ! xDown || ! yDown ) {
	// 			return;
	// 	}
	//
	// 	var xUp = evt.touches[0].clientX;
	// 	var yUp = evt.touches[0].clientY;
	//
	// 	var xDiff = xDown - xUp;
	// 	var yDiff = yDown - yUp;
	//
	// 	if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
	// 			if ( xDiff > 0 ) {
	// 					/* right swipe */
	// 			} else {
	// 					/* left swipe */
	// 			}
	// 	} else {
	// 			if ( yDiff > 0 ) {
	// 				console.log('DOWN');
	// 			} else {
	// 				console.log('UP');
	// 			}
	// 	}
	// 	/* reset values */
	// 	xDown = null;
	// 	yDown = null;
	// }, false);

	// touchEl.addEventListener('click', function(evt){
		// console.log(evt.target);
		// if (ifPlayer) {
		// 	evt.target = ifPlayer;
		// }
	// 	evt.stopImmediatePropagation();
	// });

	// ifPlayerCont.addEventListener('click', function(evt){
	// 	console.log('CLicked');
	// });

});
