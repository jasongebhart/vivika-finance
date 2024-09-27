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


function toggleCollapsible_old(buttonId, contentId) {
    const content = document.getElementById(contentId);
    const button = document.getElementById(buttonId);

    if (content.style.maxHeight) {
        // If the content is expanded, collapse it
        content.style.maxHeight = null;
        button.classList.remove('active');
    } else {
        // If the content is collapsed, expand it
        content.style.maxHeight = content.scrollHeight + "px";
        button.classList.add('active');
    }
}

function toggleCollapsible(buttonId, contentId, isNavSection = false) {
    const content = document.getElementById(contentId);
    const button = document.getElementById(buttonId);

    if (isNavSection) {
        // For the navigation section, collapse all other navigation sections
        const allContents = document.querySelectorAll('.nav-collapsible-content');
        const allButtons = document.querySelectorAll('.nav-collapsible');

        allContents.forEach((otherContent) => {
            if (otherContent !== content) {
                otherContent.style.maxHeight = null;
            }
        });

        allButtons.forEach((otherButton) => {
            if (otherButton !== button) {
                otherButton.classList.remove('active');
            }
        });
    }

    // Toggle the selected section
    if (content.style.maxHeight) {
        // Collapse the selected section
        content.style.maxHeight = null;
        button.classList.remove('active');
    } else {
        // Expand the selected section
        content.style.maxHeight = content.scrollHeight + "px";
        button.classList.add('active');
    }
}


