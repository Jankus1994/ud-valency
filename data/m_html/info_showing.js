function verb_but_func( clicked_button, verb_id) {
	if ( clicked_button.value == "show" ) {
	    item_function = show;
	    clicked_button.value = "hide";
	} else {
	    item_function = hide_frame;
	    clicked_button.value = "show";
	}
    var frames = document.querySelectorAll("[data_group='" + verb_id + "']");
    var frame_num;
    for ( frame_num = 0; frame_num < frames.length; frame_num++ ) {
        var frame = frames[ frame_num ];
        item_function( frame);
    }
}
function frame_but_func( clicked_button, frame_id) {
	if ( clicked_button.value == "show" ) {
	    item_function = show;
	    clicked_button.value = "hide";
	} else {
	    item_function = hide_link;
	    clicked_button.value = "show";
	}
    var links = document.querySelectorAll("[data_group='" + frame_id + "']");
    var link_num;
    for ( link_num = 0; link_num < links.length; link_num++ ) {
        var link = links[ link_num ];
        item_function( link);
    }
}
function link_but_func( clicked_button, link_id) {
	if ( clicked_button.value == "show" ) {
	    item_function = show;
	    clicked_button.value = "hide";
	} else {
	    item_function = hide_exam;
	    clicked_button.value = "show";
	}
    var exams = document.querySelectorAll("[data_group='" + link_id + "']");
    var exam_num;
    for ( exam_num = 0; exam_num < exams.length; exam_num++ ) {
        var exam = exams[ exam_num ];
        item_function( exam);
    }
}

function show( item) {
    item.className = "shown";
}

function hide_frame( frame) {
    var links = document.querySelectorAll("[data_group='" + frame.id + "']");
    var link_num;
    for ( link_num = 0; link_num < links.length; link_num++ ) {
        var link = links[ link_num ];
        hide_link( link);
    }
    var frame_button_id = frame.id.concat( "_but");
	var frame_button = document.getElementById( frame_button_id);
    frame_button.value = "show";
    frame.className = "hidden";
}
function hide_link( link) {
    var exams = document.querySelectorAll("[data_group='" + link.id + "']");
    var exam_num;
    for ( exam_num = 0; exam_num < exams.length; exam_num++ ) {
        var exam = exams[ exam_num ];
        hide_exam( exam);
    }
    var link_button_id = link.id.concat( "_but");
	var link_button = document.getElementById( link_button_id);
    link_button.value = "show";
    link.className = "hidden";
}
function hide_exam( exam) {
    exam.className = "hidden";
}

// ===== MONO ======

function mono_verb_but_func( clicked_button, verb_id) {
	if ( clicked_button.value == "show" ) {
	    item_function = show;
	    clicked_button.value = "hide";
	} else {
	    item_function = mono_hide_frame;
	    clicked_button.value = "show";
	}
    var frames = document.querySelectorAll("[data_group='" + verb_id + "']");
    var frame_num;
    for ( frame_num = 0; frame_num < frames.length; frame_num++ ) {
        var frame = frames[ frame_num ];
        item_function( frame);
    }
}
function mono_frame_but_func( clicked_button, frame_id) {
	if ( clicked_button.value == "show" ) {
	    item_function = show;
	    clicked_button.value = "hide";
	} else {
	    item_function = hide_exam;
	    clicked_button.value = "show";
	}
    var exams = document.querySelectorAll("[data_group='" + frame_id + "']");
    var exam_num;
    for ( exam_num = 0; exam_num < exams.length; exam_num++ ) {
        var exam = exams[ exam_num ];
        item_function( exam);
    }
}
function mono_hide_frame( frame) {
    var exams = document.querySelectorAll("[data_group='" + frame.id + "']");
    var exam_num;
    for ( exam_num = 0; exam_num < exams.length; exam_num++ ) {
        var exam = exams[ exam_num ];
        hide_exam( exam);
    }
    var frame_button_id = frame.id.concat( "_but");
	var frame_button = document.getElementById( frame_button_id);
    frame_button.value = "show";
    frame.className = "hidden";
}