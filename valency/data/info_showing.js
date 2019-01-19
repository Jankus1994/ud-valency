function show( clicked_button, div_id) {
    clicked_button.value = 'SPAM'
    var item = document.getElementById( div_id);
    if ( item ) {
        if ( item.className == 'hidden' ){
            item.className = 'shown';
            clicked_button.value = 'hide'
        } else {
            item.className = 'hidden';
            clicked_button.value = 'show'
        }
    }
}
