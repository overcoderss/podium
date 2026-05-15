function initCard(cardid){
    const teamCard = document.getElementById(cardid);
    const elements = teamCard.getElementsByClassName('arrow-but');
    const arrowBut = elements[0];


    arrowBut.addEventListener('click', function(event) {
        debugger;
        //event.stopPropagation();
        let element = event.target;
        let arr = element.getElementsByClassName('arrow');
        let arrow = arr[0];
        let isUp = arrow.classList.contains('up');
        let isDown = arrow.classList.contains('down');
        const parent = element.closest('.team-card');
        const bottom = parent.querySelector('.bottom');


        if (isUp){
            arrow.classList.remove('up');
            arrow.classList.add('down');
            bottom.classList.add('but-none');

        } else if(isDown){
            arrow.classList.remove('down');
            arrow.classList.add('up');
            bottom.classList.remove('but-none');
        }

    });
}

function hideContent(){
    let arr = document.getElementsByClassName('right-content');
    for (let i = 0; i < arr.length; i++) {
        let e = arr[i];
        e.classList.add('but-none');
    }
}

function initMenuThing(){
    let arr = document.getElementsByClassName('menu-item');
    for (let i = 0; i < arr.length; i++) {
        let e = arr[i];
        e.classList.remove('menu-item-active');
    }
}


function showMenuItem(contentItemClass){
    hideContent();
    initMenuThing();
    let arr = document.getElementsByClassName(contentItemClass);
    for (let i = 0; i < arr.length; i++) {
        arr[i].classList.remove('but-none');
    }
}

function initMenuItem(menuItemClass, contentItemClass){
    debugger;
    let menuItem = document.getElementsByClassName(menuItemClass);
    let menuItemIt = menuItem[0];
   // initMenuThing();
    menuItemIt.classList.add('menu-item-active');
    menuItemIt.addEventListener('click', function(event) {
        debugger;
        showMenuItem(contentItemClass);
    });
}

function showContent(){
    initMenuItem('menu-1', 'con-1');
    initMenuItem('menu-2', 'content-2');
    initMenuItem('menu-3', 'content-3');
    initMenuItem('menu-4', 'initials');
}


function init() {
    debugger;
    initCard("team-card-1");
    hideContent();
    showContent();
    initMenuThing();
    showMenuItem('con-1');
    let menuItem = document.getElementsByClassName('menu-1');
    menuItem[0].classList.add('menu-item-active');
}


document.addEventListener("DOMContentLoaded", function () {
    init();
});