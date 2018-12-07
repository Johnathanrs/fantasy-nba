function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

if(inIframe()) {
} else {
    // $('.container-fluid').remove();
    $('nav').toggleClass('d-none');
}
