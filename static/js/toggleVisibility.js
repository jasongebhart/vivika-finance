// toggleVisibility.js

function toggleSectionVisibilityClass(sectionClass) {
    var sections = document.getElementsByClassName(sectionClass);
    for (var i = 0; i < sections.length; i++) {
        sections[i].classList.toggle('hidden');
    }
}

// function toggleSectionVisibility(sectionId) {
//     var sectionTitle = document.getElementById(sectionId);
//     var sectionContent = document.getElementById(sectionId + "-content");

//     if (sectionTitle && sectionContent) {
//         sectionTitle.classList.toggle('hidden');
//         sectionContent.classList.toggle('hidden');
//     }
// }

// function toggleSectionVisibility(sectionId) {
//     var sectionContent = document.getElementById(sectionId + "-content");
//     if (sectionContent) {
//         sectionContent.classList.toggle('hidden');
//     }
// }

function toggleSectionVisibility(sectionId) {
    const content = document.getElementById(sectionId + '-content');
    if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
    } else {
        content.classList.add('hidden');
    }
}

