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
	var explotPlayer = [];
	var plId = 0;
	var canvasDomIdPrefix = 'main-canvas';
	var canvasDomId = canvasDomIdPrefix + plId;
	var xmlLocaleDirName = 'xmllocale';
	var curReelId = 0;
	var firstPlay = true;

	// elements
	var canvasContainer = document.getElementById('canvas-container');
	var playerLoader = document.getElementById('player-loader');
	var playerLoaderNum = document.getElementById('player-loader-number');
	var playStopBut = document.getElementById('playstopbutton');
	var volCtr = document.getElementById('controlbar-volumecontrol');
	var volCtrInput = document.getElementById('controlbar-volumecontrol-input');
	var volCtrIco = document.getElementById('controlbar-volumecontrol-icon');
	var ctrTimer = document.getElementById('controlbar-timer' + curReelId);
	var ctrTline = document.getElementById('controlbar-timeline' + curReelId);
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
	var playerLoaderHidClass = 'player-loader-hidden';
	var metadataUnfoldClass = 'metadata-unfold';
	var vcUnfoldClass = 'vc-unfold';
	var vcInputUnfoldClass = 'vcinput-unfold';
	var reelsUnfoldClass = 'reels-unfold';
	var breadcrumbPrevClass="breadcrumbs-prev";
	var reelNavUpClass = "reel-navigation-up";
	var reelNavDownClass = "reel-navigation-down";
	var reelCurrentClass = "reel-current";
	var playStopButPromoteClass = "playstopbutton-promote";
	var timerInterval = null;
	var timeTotal = 0;
	var timeTotalNum = 0;
	var timelineActive = false;
	var timelineLevel = _VPD.timelineLevel;
	var muted = false;

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

	var setVolVal = function(volVal) {
		explotPlayer[plId].setVolume(volVal);
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

	var playButClick = function() {
		if (played) {
			pause();
		} else {
			play();
			if (playStopBut.classList.contains(playStopButPromoteClass)) {
				playStopBut.classList.remove(playStopButPromoteClass);
			}
		}
	}

	var opts = {
		'sizeFixedTo':'canvas-container',
		'sizeRatio': aspectRatio,
		'locale':lang
	}

	var timelineClick = function(e){
		var parentEl = this.parentElement.offsetLeft;
		var relX = e.pageX - getAbsolutePosition(this).x;
		var rat = relX/this.offsetWidth;
		rat = Math.round(rat * 1000)/1000;
		if (timelineLevel == 2) {
			explotPlayer[plId].gotoTimeByRatio(rat);
		} else if (timelineLevel == 1) {
			explotPlayer[plId].gotoStopTimeByRatio(rat);
		}
	}

	var activateTimeline = function() {
		if (timelineLevel > 0) {
			if (!timelineActive) {
				ctrTline.addEventListener('click', timelineClick);
				timelineActive = true;
			}
		}
	}

	var checkLoadStatus = setInterval(function() {
		var loaded = 0;
		if (explotPlayer[plId]) {
			loaded = Math.round(explotPlayer[plId].getAssetsLoadedStatus()*100);
		}
		playerLoaderNum.innerHTML = loaded + "%";
	}, 10);

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

	var end = function() {
		explotPlayer[plId].pause();
		played = false;
		clearInterval(timerInterval);
		ctrTimer.innerHTML = timeTotal + '/' + timeTotal;
		playStopBut.style.backgroundImage
			= "url('/static/img/button-replay.png')";
		playStopBut.addEventListener('click', function() {
			location.reload();
		});
	}

	var pause = function() {
		explotPlayer[plId].pause();
		// played = false;
		clearInterval(timerInterval);
	}

	var play = function() {
		if (firstPlay) {
			playerLoadPH.parentNode.removeChild(playerLoadPH);
			firstPlay = false;
		}
		playStopBut.style.backgroundImage
			= "url('/static/img/button-pause.png')";
		explotPlayer[plId].play();
		// played = true;
	}

	var setTime = function() {
		var curTime = 0;
		if (typeof explotPlayer[plId] !== 'undefined') {
			curTime = explotPlayer[plId].getTimeElapsed ();
		}
		if (curTime < timeTotalNum) {
			ctrTimer.innerHTML = msToTime(curTime) + '/' + timeTotal;
		} else {
			end();
		}
		var percTime = curTime/timeTotalNum;
		ctrTline.style.backgroundImage =
				'-webkit-gradient(linear, left top, right top, '
				+ 'color-stop(' + percTime + ', #241f51), '
				+ 'color-stop(' + percTime + ', #C5C5C5)'
				+ ')';
	}

	var activatePPButton = function() {
  	if (!butStopPlayActive) {
			playStopBut.addEventListener('click', playButClick);
    	butStopPlayActive = true;
  	}
	}

	// Loading the files
	var processAndPlay = function (overrides) {

		if (typeof overrides !== 'undefined' && overrides) {
			if (overrides.hasOwnProperty('text_objects')) {
				opts['textsOverride'] = overrides['text_objects'];
			}
			if (overrides.hasOwnProperty('variable_objects')) {
				opts['variablesOverride'] = overrides['variable_objects'];
			}
			if (overrides.hasOwnProperty('image_objects')) {
				opts['imagesOverride'] = overrides['image_objects'];
			}
		}

		explotPlayer[plId] = new ExplotPlayer2D(canvasDomId, opts);

		explotPlayer[plId].pauseCallback = function () {
			played = false;
			if (explotPlayer[plId].getActionRequired() == true ) {
				playStopBut.style.backgroundImage = "url('/static/img/button-play-inactive.png')";
				playStopBut.removeEventListener("click", playButClick);
				butStopPlayActive = false;
				ctrTline.removeEventListener('click', timelineClick);
				timelineActive = false;
			} else {
				playStopBut.style.backgroundImage = "url('/static/img/button-play.png')";
			}
		}

		explotPlayer[plId].playCallback = function () {
			played = true;
			playStopBut.style.backgroundImage = "url('/static/img/button-pause.png')";
			activatePPButton();
			activateTimeline();
			timerInterval = setInterval(function(){
				setTime();
			}, 200);
		}

		explotPlayer[plId].reloadRequest = function (newUrl) {

			explotPlayer[plId].destroy();
			explotPlayer[plId] = null;
			delete explotPlayer[plId];
			plId += 1;

			if (document.getElementById(canvasDomId)) {
				document.getElementById(canvasDomId).remove();
			}
			canvasDomId = canvasDomIdPrefix + plId;
			var newCanvas = document.createElement("canvas");
			newCanvas.setAttribute("id", canvasDomId);
			canvasContainer.insertBefore(newCanvas, canvasContainer.firstChild);

			butStopPlayActive = false;
			var newPlayStopBut = playStopBut.cloneNode(true);
			playStopBut.parentNode.replaceChild(newPlayStopBut, playStopBut);
			playStopBut = newPlayStopBut;

			playerLoader = document.createElement('div');
			playerLoader.setAttribute('id', 'player-loader');
			var playerLoaderNum = document.createElement('div');
			playerLoaderNum.setAttribute('id', 'player-loader-number');
			playerLoader.appendChild(playerLoaderNum);
			canvasContainer.appendChild(playerLoader);

			urlToPlay = urlDir + newUrl;
			autoplay = true;
			loadLocaleProcessAndPlay ();
		}

		var xhr = new XMLHttpRequest();
		xhr.open('GET', urlToPlay);
		xhr.setRequestHeader('X-CSRFToken', cookies['csrftoken']);
		xhr.onload = function() {
			if (xhr.status === 200) {

				explotPlayer[plId].loadMovieFromIGML(xhr.responseText, autoplay, function() {

					if (volCtrInput) setVolumeControl();

					timeTotalNum = explotPlayer[plId].getTimeTotal();
					timeTotal = msToTime(timeTotalNum);

					if (ctrTimer) ctrTimer.innerHTML = '00:00/' + timeTotal;

					playerLoader.className = playerLoaderHidClass;
					clearInterval(checkLoadStatus);
					setTimeout(function(){
						playerLoader.parentNode.removeChild(playerLoader);
						playStopBut.classList.add(playStopButPromoteClass);
					}, 600);

					if (playStopBut) {
						playStopBut.style.backgroundImage
							= "url('/static/img/button-play.png')";
					}

					if (playStopBut && ctrTimer) {
						activatePPButton();
						activateTimeline();
					}

					if (volCtrInput) {
						volCtrInput.addEventListener('input', function() {
							setVolumeControl ();
						});
					}

					if (volCtrIco) {
						volCtrIco.addEventListener('click', function() {
							// if (!muted) {
							// 	volCtrInput.value = 0;
							// 	setVolVal(0);
							// } else {
							// 	volCtrInput.value = 100;
							// 	setVolVal(100);
							// }
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
							if (played && explotPlayer[plId].playing) {
							pause();
						}
					});

				});
			} else {
				console.log(xhr)
				alert( _LANGVARS.videos.videoLoadIssue );
			}
		}
		xhr.send();

	}

	var loadLocaleProcessAndPlay = function() {
		// Setting language
		urlLocale = '';
		var urlPath = _VPD.FileToPlay.substring(0, _VPD.FileToPlay.lastIndexOf("/") + 1);
		if (lang) {
			urlLocale = urlDir + urlPath + xmlLocaleDirName + '/' + lang + '/';
		}

		if (urlLocale) {
			var xhr = new XMLHttpRequest();
			xhr.responseType = 'json';
			textLocaleFileName = urlToPlay.substring(urlToPlay.lastIndexOf('/')+1).split('.')[0] + ".json";
			xhr.open('GET', urlLocale + textLocaleFileName);
			xhr.setRequestHeader('X-CSRFToken', cookies['csrftoken']);
			xhr.onload = function() {
				console.log(xhr);
				if (xhr.status === 200) {
					var res = xhr.response;
					if (res) {
						metaTitle.innerHTML = res['meta_info']['title'];
						metaDescription.innerHTML = res['meta_info']['description'];
						processAndPlay(res);
					} else {
						processAndPlay();
					}
				} else {
					processAndPlay();
				}
			}
			xhr.send();
		} else {
			processAndPlay();
		}
	}

	// Setting up the change languages
	if (changeLangSelect) {
		changeLangSelect.addEventListener('change', function() {
			changeLangForm.submit();
		});
	}

	loadLocaleProcessAndPlay();

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

	infoBut.addEventListener('click', function() {
		metadataBlock.classList.add(metadataUnfoldClass);
	});

	metaCloseBut.addEventListener('click', function() {
		metadataBlock.classList.remove(metadataUnfoldClass);
	});

	reelsUnfoldBut.addEventListener('click', function(){
		if (reelsWrapper.classList.contains(reelsUnfoldClass)) {
			reelsWrapper.classList.remove(reelsUnfoldClass);
		} else {
			reelsWrapper.classList.add(reelsUnfoldClass);
		}
	});

	backBut.addEventListener('click', function(){
		var breadcrumbPrev = document.getElementsByClassName(breadcrumbPrevClass)[0];
		const urlPrev = breadcrumbPrev.getAttribute('href');
		window.location.href = urlPrev;
	});

	const allReelNavDown = document.getElementsByClassName(reelNavDownClass);
	for (i = 0; i < allReelNavDown.length; i++) {
		allReelNavDown[i].addEventListener('click', function() {
				const currReel = document.getElementById('reel' + curReelId);
				currReel.classList.remove(reelCurrentClass);
				curReelId ++;
				const nextReel = document.getElementById('reel' + curReelId);
				scrollTo(reels, nextReel.offsetHeight * curReelId, 500);
				nextReel.classList.add(reelCurrentClass);
		});
	}

	const allReelNavUp = document.getElementsByClassName(reelNavUpClass);
	for (i = 0; i < allReelNavUp.length; i++) {
    allReelNavUp[i].addEventListener('click', function() {
				const currReel = document.getElementById('reel' + curReelId);
				currReel.classList.remove(reelCurrentClass);
        curReelId --;
				const prevReel = document.getElementById('reel' + curReelId);
				scrollTo(reels, prevReel.offsetHeight * curReelId, 500);
				prevReel.classList.add(reelCurrentClass);
    });
	}

});
